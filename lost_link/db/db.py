from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lost_link.db.db_models import Base


class DB:

    def __init__(self, path, debug=False):
        self._engine = create_engine(f"sqlite:///{path}", echo=debug)
        self._session = None
        Base.metadata.create_all(self._engine)

    def __del__(self):
        try:
            if self._session:
                self._session.close()
        # Wenn als Exe das Programm ohne den Code 0 beendet wird, fliegt diese Exception. Ignorieren um Stacktrace auszublenden
        except AttributeError:
            return

    def create_session(self) -> Session:
        if self._session is None:
            self._session = Session(self._engine)
        return self._session