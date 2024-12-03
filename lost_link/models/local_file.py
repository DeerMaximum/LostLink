from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class LocalFile(Base):
    __tablename__ = 'local_file'

    path: Mapped[str] = mapped_column(String(), primary_key=True)
    last_change_date: Mapped[float] = mapped_column(Float())
    last_seen: Mapped[datetime] = mapped_column(DateTime())
    embeddings_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    edited: Mapped[bool] = mapped_column(Boolean(), default=False)
    deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

