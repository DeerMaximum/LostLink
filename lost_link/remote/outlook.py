import datetime
import os
import uuid

from langchain_chroma import Chroma

from lost_link.ai.embedding_generator import EmbeddingGenerator
from lost_link.db.attachment_manager import AttachmentManager
from lost_link.db.db_models import Attachment
from lost_link.db.embedding_manager import EmbeddingManager
from lost_link.remote.graph_api_access import OutlookAccess
from lost_link.service_locator import ServiceLocator
from lost_link.settings import Settings
from lost_link.const import ALLOWED_EXTENSIONS


class Outlook:

    def __init__(self, api: OutlookAccess, attachment_manager: AttachmentManager, embedding_manager: EmbeddingManager,
                 vector_db: Chroma , tmp_base_path: str, settings: Settings):
        self._api = api
        self._attachment_manager = attachment_manager
        self._embedding_manager = embedding_manager
        self._tmp_base_path = tmp_base_path
        self._vector_db = vector_db
        self._settings = settings
        self._embedding_generator: EmbeddingGenerator = ServiceLocator.get_service("embedding_generator")


    def _process_old_attachments(self, fetch_attachments: list[Attachment]):
        old_attachments_in_db = self._attachment_manager.get_all()

        for old_attachment in old_attachments_in_db:
            in_list = False

            for fetch_attachment in fetch_attachments:
                if fetch_attachment.internet_id == old_attachment.internet_id:
                    in_list = True
                    break

            if not in_list:
                self._embedding_generator.delete_file_embeddings(old_attachment)
                self._attachment_manager.remove_attachment(old_attachment)
                self._attachment_manager.save_updates()

    def _get_new_attachments(self, fetch_attachments: list[Attachment]) -> list[Attachment]:
        new_attachments: list[Attachment] = []

        for fetch_attachment in fetch_attachments:
            if self._attachment_manager.get_attachment_by_internet_id(fetch_attachment.internet_id) is None:
                new_attachments.append(fetch_attachment)

        return new_attachments

    def _process_new_attachment(self, new_attachment: Attachment):
        extension = os.path.splitext(new_attachment.name)[1]
        if extension not in ALLOWED_EXTENSIONS:
            return

        filename = f"{uuid.uuid4().hex}{extension}"
        path = os.path.join(self._tmp_base_path, filename)
        self._api.download_attachment(new_attachment.msg_id, new_attachment.id, path)

        self._embedding_generator.generate_and_store_embeddings(path, Attachment, new_attachment.internet_id)

        os.remove(path)
        self._attachment_manager.add_attachment(new_attachment)
        self._attachment_manager.save_updates()

    def update(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=self._settings.get(Settings.KEY_TARGET_DAYS, 90))
        start_date = now - delta

        msg_tuples = list(set(self._api.get_message_ids(start_date)))
        deleted_internet_ids = list(set(self._api.get_message_ids_trash(start_date)))

        for entry in msg_tuples:
            if entry[1] in deleted_internet_ids:
                msg_tuples.remove(entry)


        attachments: list[Attachment] = []

        for (msg_id, msg_internet_id, subject, web_link, created_date) in msg_tuples:
            attachment_tuples = self._api.get_attachments(msg_id)

            for attachment_tuple in attachment_tuples:
                attachments.append(Attachment(id=attachment_tuple[0],
                                              name=attachment_tuple[1],
                                              msg_id=msg_id,
                                              internet_id=msg_internet_id,
                                              created=created_date,
                                              link=web_link,
                                              subject=subject
                                              ))

        self._process_old_attachments(attachments)

        failed_attachments = []

        for new_attachment in self._get_new_attachments(attachments):
            try:
                self._process_new_attachment(new_attachment)
            except RuntimeError as e:
                failed_attachments.append({"file": "new_attachment.id", "reason": str(e)})
            except Exception:
                failed_attachments.append(new_attachment.id)
                continue

        if len(failed_attachments) > 0:
            msg = "\n".join([f"Konnte E-Mail Anhang {x.get("file")} nicht verarbeiten" + (f": \n\t{x['reason']}" if x['reason'] else "") for x in failed_attachments if len(x) > 0])
            raise RuntimeError(msg)