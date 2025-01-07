from dataclasses import dataclass
from datetime import datetime

from lost_link.db.attachment_manager import AttachmentManager
from lost_link.db.db_models import LocalFile, Attachment, OneDriveFile, SharePointFile
from lost_link.db.local_file_manager import LocalFileManager
from lost_link.db.one_drive_file_manager import OneDriveFileManager
from lost_link.db.share_point_file_manager import SharePointFileManager


@dataclass
class ResultEntry:
    filename: str
    last_modified: datetime
    source: str
    open_url: str

    def __lt__(self, other):
        return self.last_modified < other.last_modified


class ResultMapper:

    def __init__(self, local_file_manager: LocalFileManager, attachment_manager: AttachmentManager,
                 onedrive_manager: OneDriveFileManager, share_point_manager: SharePointFileManager):
        self._local_file_manager = local_file_manager
        self._attachment_manager = attachment_manager
        self._onedrive_manager = onedrive_manager
        self._share_point_manager = share_point_manager

    @staticmethod
    def _map_local_file(file: LocalFile) -> ResultEntry:
        return ResultEntry(
            filename=file.path,
            last_modified=datetime.fromtimestamp(file.last_change_date),
            source="Lokale Datei",
            open_url=f"file://{file.path}",
        )

    @staticmethod
    def _map_attachment(file: Attachment) -> ResultEntry:
        return ResultEntry(
            filename=file.subject,
            last_modified=file.created,
            source="E-Mail",
            open_url=file.link
        )

    @staticmethod
    def _map_onedrive(file: OneDriveFile) -> ResultEntry:
        pass

    @staticmethod
    def _map_share_point(file: SharePointFile) -> ResultEntry:
        pass

    def map(self, file_ids: list[str]) -> list[ResultEntry]:
        result = []

        for full_file_id in file_ids:
            file_id = full_file_id.split('?')[0]
            site_id = full_file_id.split('?')[1]

            if (file := self._local_file_manager.get_file_by_id(file_id)) is not None:
                result.append(self._map_local_file(file))
            elif (file := self._attachment_manager.get_attachment_by_internet_id(file_id)) is not None:
                result.append(self._map_attachment(file))
            elif (file := self._onedrive_manager.get_file_by_id(file_id)) is not None:
                result.append(self._map_onedrive(file))
            elif (file := self._share_point_manager.get_file_by_id(site_id, file_id)) is not None:
                result.append(self._map_share_point(file))

        return result
