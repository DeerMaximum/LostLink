from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, ForeignKey, String, Float, DateTime, Boolean


class Base(DeclarativeBase):
    pass

class Embedding(Base):
    __tablename__ = 'embedding'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("local_file.id"))

class LocalFile(Base):
    __tablename__ = 'local_file'

    id: Mapped[uuid.UUID] = mapped_column(UUID(), default=uuid.uuid4)
    path: Mapped[str] = mapped_column(String(), primary_key=True)
    last_change_date: Mapped[float] = mapped_column(Float())
    last_seen: Mapped[datetime] = mapped_column(DateTime())
    edited: Mapped[bool] = mapped_column(Boolean(), default=False)
    deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

    embeddings: Mapped[list[Embedding]] = relationship('Embedding', backref='local_file')