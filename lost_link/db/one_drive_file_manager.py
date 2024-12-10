from sqlalchemy import select

from db.db import DB
from db.db_models import OneDriveFile



class OneDriveFileManager():

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def __del__(self):
        self._session.close()

    def get_file_by_id(self, id) -> OneDriveFile | None:
        stmt = select(OneDriveFile).where(OneDriveFile.id == id)
        return self._session.scalar(stmt)
    
    def add_file(self, file: OneDriveFile):
        self._session.add(file)

    def remove_file(self, file: OneDriveFile):
        self._session.delete(file)

    def save_updates(self):
        self._session.commit()

    