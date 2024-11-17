import uuid
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

@dataclass
class Embedding:
    embedding_value: list[float]
    id: str


class EmbeddingGenerator:

    def __init__(self, embedding_model: Embeddings):
        self._embedding_model = embedding_model

    def generate(self, documents: list[Document]) -> list[Embedding]:
        embeddings: list[Embedding] = []

        for doc in documents:
            embedding = self._embedding_model.embed_documents([doc.page_content])[0]
            embeddings.append(Embedding(embedding_value=embedding, id=uuid.uuid4().hex))

        return embeddings