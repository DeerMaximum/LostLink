from lost_link.db.db import DB
from lost_link.db.db_models import Embedding

class EmbeddingManager:

    def __init__(self, db: DB):
        self._db = db
        self._session = self._db.create_session()

    def add_embedding(self, embedding: Embedding):
        self._session.add(embedding)

    def remove_embedding(self, embedding: Embedding):
        self._session.delete(embedding)

    def save_updates(self):
        self._session.commit()