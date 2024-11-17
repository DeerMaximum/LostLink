from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import String, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from lost_link.db import DB

from .base import Base

class LocalFile(Base):
    __tablename__ = 'local_file'

    path: Mapped[str] = mapped_column(String(), primary_key=True)
    last_change_date: Mapped[float] = mapped_column(Float())
    last_seen: Mapped[datetime] = mapped_column(DateTime())
    embeddings_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    edited: Mapped[bool] = mapped_column(Boolean(), default=False)
    deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

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

    def get_all_edited_files(self) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.edited == True)
        return self._session.scalars(stmt).all()

    def get_all_deleted_files(self) -> Sequence[LocalFile]:
        stmt = select(LocalFile).where(LocalFile.deleted == True)
        return self._session.scalars(stmt).all()

    def save_updates(self):
        self._session.commit()