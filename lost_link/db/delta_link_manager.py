from datetime import datetime
from sqlalchemy import select

from lost_link.db.db import DB
from lost_link.db.db_models import DeltaLink

class DeltaLinkManager:

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def __del__(self):
        self._session.close()

    def get_delta_link(self, domain: str) -> str | None:
        stmt = select(DeltaLink).where(DeltaLink.domain == domain)
        delta_link = self._session.scalar(stmt)
        return delta_link.delta_link if delta_link else None

    def save_delta_link(self, domain: str, delta_link: str):
        existing = self.get_delta_link(domain)
        if existing:
            stmt = select(DeltaLink).where(DeltaLink.domain == domain)
            db_delta_link = self._session.scalar(stmt)
            db_delta_link.delta_link = delta_link
            db_delta_link.last_updated = datetime.utcnow()
        else:
            new_delta_link = DeltaLink(
                domain=domain, delta_link=delta_link, last_updated=datetime.utcnow()
            )
            self._session.add(new_delta_link)
        self._session.commit()