from datetime import datetime
from sqlalchemy import Sequence, select
from db import DB
from models.local_file import LocalFile


class LocalFileManager:

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def __del__(self):
        self._session.close()

    def get_file_by_path(self, path) -> LocalFile | None:
        stmt = select(LocalFile).where(LocalFile.path == path)
        return self._session.scalar(stmt)

    def add_file(self, file: LocalFile):
        self._session.add(file)

    def remove_file(self, file: LocalFile):
        self._session.delete(file)

    def get_all_files_seen_before(self, date: datetime) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.last_seen < date)
        return self._session.scalars(stmt).all()

    def save_updates(self):
        self._session.commit()