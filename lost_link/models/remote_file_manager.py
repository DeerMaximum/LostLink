from sqlalchemy import select
from db import DB
from models.remote_file import RemoteFile


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

    