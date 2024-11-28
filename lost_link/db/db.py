from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lost_link.db.models import Base


class DB:

    def __init__(self, path, debug=False):
        self._engine = create_engine(f"sqlite:///{path}", echo=debug)
        self._session = None
        Base.metadata.create_all(self._engine)

    def __del__(self):
        if self._session:
            self._session.close()

    def create_session(self) -> Session:
        if self._session is None:
            self._session = Session(self._engine)
        return self._session