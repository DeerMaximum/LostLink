from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.base import Base

# noinspection PyUnresolvedReferences
import models.local_file


class DB:

    def __init__(self, path, debug=False):
        self._engine = create_engine(f"sqlite:///{path}", echo=debug)
        Base.metadata.create_all(self._engine)

    def create_session(self) -> Session:
        return Session(self._engine)