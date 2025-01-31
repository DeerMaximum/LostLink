from datetime import datetime
from typing import Optional

from sqlalchemy.orm import DeclarativeBase
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, CheckConstraint, ForeignKey, String, Float, DateTime, Boolean


class Base(DeclarativeBase):
    pass

class Embedding(Base):
    __tablename__ = 'embedding'
    __table_args__ = (CheckConstraint(
        "local_file_id IS NOT NULL OR attachment_id IS NOT NULL OR one_drive_file_id IS NOT NULL OR (share_point_file_id IS NOT NULL AND share_point_site_id IS NOT NULL)",
        name="not-null"
    ),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    local_file_id: Mapped[uuid.UUID] = mapped_column(UUID(), ForeignKey("local_file.id"), nullable=True)
    one_drive_file_id: Mapped[str] = mapped_column(String(), ForeignKey("one_drive_file.id"), nullable=True)
    share_point_file_id: Mapped[str] = mapped_column(String(), ForeignKey("share_point_file.id"), nullable=True)
    share_point_site_id: Mapped[str] = mapped_column(String(), ForeignKey("share_point_file.site_id"), nullable=True)
    share_point_file: Mapped["SharePointFile"] = relationship(
        "SharePointFile",
        primaryjoin="and_(Embedding.share_point_file_id == SharePointFile.id, Embedding.share_point_site_id == SharePointFile.site_id)",
        foreign_keys="[Embedding.share_point_file_id, Embedding.share_point_site_id]",
        back_populates="embeddings",
    )
    attachment_id: Mapped[str] = mapped_column(String(), ForeignKey("attachment.internet_id"), nullable=True)

class LocalFile(Base):
    __tablename__ = 'local_file'

    id: Mapped[uuid.UUID] = mapped_column(UUID(), default=uuid.uuid4)
    path: Mapped[str] = mapped_column(String(), primary_key=True)
    last_change_date: Mapped[float] = mapped_column(Float())
    last_seen: Mapped[datetime] = mapped_column(DateTime())
    edited: Mapped[bool] = mapped_column(Boolean(), default=False)
    deleted: Mapped[bool] = mapped_column(Boolean(), default=False)

    embeddings: Mapped[list[Embedding]] = relationship('Embedding', backref='local_file')

class OneDriveFile(Base):
    __tablename__ = 'one_drive_file'

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    last_modified_date: Mapped[datetime] = mapped_column(DateTime())

    embeddings: Mapped[list[Embedding]] = relationship('Embedding', backref='one_drive_file')

class SharePointFile(Base):
    __tablename__ = 'share_point_file'

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
    last_modified_date: Mapped[datetime] = mapped_column(DateTime())

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        primaryjoin=(
            "and_(Embedding.share_point_file_id == SharePointFile.id, "
                 "Embedding.share_point_site_id == SharePointFile.site_id)"
        ),
        foreign_keys="[Embedding.share_point_file_id, Embedding.share_point_site_id]",
        back_populates="share_point_file",
    )
    # embeddings: Mapped[list[Embedding]] = relationship('Embedding', backref='share_point_file')

class DeltaLink(Base):
    __tablename__ = 'delta_links'

    domain: Mapped[str] = mapped_column(String, primary_key=True)
    delta_link: Mapped[str] = mapped_column(String, nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, nullable=False)



class Attachment(Base):
    __tablename__ = 'attachment'

    internet_id: Mapped[str] = mapped_column(String(), primary_key=True)
    id: Mapped[str] = mapped_column(String(), nullable=False)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    subject: Mapped[str] = mapped_column(String(), nullable=False)
    msg_id: Mapped[str] = mapped_column(String(), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    link: Mapped[str] = mapped_column(String(), nullable=False)

    embeddings: Mapped[list[Embedding]] = relationship('Embedding', backref='attachment')