from datetime import datetime
from sqlalchemy import String, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class DeltaLink(Base):
    __tablename__ = 'delta_links'

    domain: Mapped[str] = mapped_column(String, primary_key=True)
    delta_link: Mapped[str] = mapped_column(String, nullable=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


