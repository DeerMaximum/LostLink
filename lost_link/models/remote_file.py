from datetime import datetime
from typing import Optional, Sequence

import requests
from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from db import DB
from .base import Base



class RemoteFile(Base):
    __tablename__ = 'remote_file'

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=True)
    #path: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    embeddings_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    last_modified_date: Mapped[datetime] = mapped_column(DateTime())
    last_seen: Mapped[datetime] = mapped_column(DateTime())


class RemoteFileManager():

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def __del__(self):
        self._session.close()

    def get_file_by_id(self, id) -> RemoteFile | None:
        stmt = select(RemoteFile).where(RemoteFile.id == id)
        return self._session.scalar(stmt)
    
    def add_file(self, file: RemoteFile):
        self._session.add(file)

    def remove_file(self, file: RemoteFile):
        self._session.delete(file)

    def save_updates(self):
        self._session.commit()

    