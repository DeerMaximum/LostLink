from sqlalchemy import select

from lost_link.db.db import DB
from lost_link.db.db_models import OneDriveFile

class OneDriveFileManager():

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def get_file_by_id(self, id) -> OneDriveFile | None:
        stmt = select(OneDriveFile).where(OneDriveFile.id == id)
        return self._session.scalar(stmt)
    
    def add_file(self, file: OneDriveFile):
        self._session.add(file)

    def remove_file(self, file: OneDriveFile):
        self._session.delete(file)

    def save_updates(self):
        self._session.commit()

    