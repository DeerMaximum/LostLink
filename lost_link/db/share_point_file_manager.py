from sqlalchemy import select

from lost_link.db.db import DB
from lost_link.db.db_models import SharePointFile

class SharePointFileManager():

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def get_file_by_id(self, site_id, file_id) -> SharePointFile | None:
        stmt = (
            select(SharePointFile)
            .where(SharePointFile.id == file_id, SharePointFile.site_id == site_id)
        )
        return self._session.scalar(stmt)
    
    def add_file(self, file: SharePointFile):
        self._session.add(file)

    def remove_file(self, file: SharePointFile):
        self._session.delete(file)

    def save_updates(self):
        self._session.commit()

    