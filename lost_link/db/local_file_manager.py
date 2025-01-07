from datetime import datetime
from typing import  Sequence
from uuid import uuid4, UUID

from sqlalchemy import select

from lost_link.db.db import DB
from lost_link.db.db_models import LocalFile

class LocalFileManager:

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def get_file_by_path(self, path) -> LocalFile | None:
        stmt = select(LocalFile).where(LocalFile.path == path)
        return self._session.scalar(stmt)

    def add_file(self, file: LocalFile):
        self._session.add(file)

    def remove_file(self, file: LocalFile):
        self._session.delete(file)

    def get_file_count(self) -> int:
        return self._session.query(LocalFile).count()

    def get_file_by_id(self, file_id: str) -> LocalFile | None:
        try:
            stmt = select(LocalFile).where(LocalFile.id == UUID(file_id))
            return self._session.scalar(stmt)
        except ValueError:
            return None

    def get_all_files_seen_before(self, date: datetime) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.last_seen < date)
        return self._session.scalars(stmt).all()

    def get_all_edited_files(self) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.edited == True)
        return self._session.scalars(stmt).all()

    def get_all_deleted_files(self) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.deleted == True)
        return self._session.scalars(stmt).all()

    def get_all_new_files(self) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.embeddings == None)
        return self._session.scalars(stmt).all()

    def save_updates(self):
        self._session.commit()