from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from .base import Base



class RemoteFile(Base):
    __tablename__ = 'remote_file'

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=True)
    #path: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    embeddings_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    last_modified_date: Mapped[datetime] = mapped_column(DateTime())
    last_seen: Mapped[datetime] = mapped_column(DateTime())
