from typing import Sequence

from sqlalchemy import select

from lost_link.db.db import DB
from lost_link.db.db_models import Attachment


class AttachmentManager:

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def add_attachment(self, attachment: Attachment):
        self._session.add(attachment)

    def get_attachment_by_internet_id(self, att_id: str) -> Attachment | None:
        stmt = select(Attachment).where(Attachment.internet_id == att_id)
        return self._session.scalar(stmt)

    def get_all(self) -> Sequence[Attachment]:
        stmt = select(Attachment)
        return self._session.scalars(stmt).all()

    def remove_attachment(self, attachment: Attachment):
        self._session.delete(attachment)

    def save_updates(self):
        self._session.commit()