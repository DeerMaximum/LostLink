import os.path
from typing import Any
from uuid import uuid4

from lost_link.db.db_models import Embedding, LocalFile, OneDriveFile, SharePointFile, Attachment


class EmbeddingGenerator:
    def __init__(self, vector_db, embedding_manager, file_converter):
        self._vector_db = vector_db
        self._embedding_manager = embedding_manager
        self._file_converter = file_converter

    def generate_and_store_embeddings(self, file_path: str, file_type: type, file_id: Any, site_id=None):
        """
        Generates embeddings for a given document and stores them in both the vector database and the relational database.

        Args:
            file_path (str): The path to the file.
            file_type (type): The class of the file type (e.g. LocalFile, OneDriveFile, Attachment, etc.).
            file_id: The ID of the file in the corresponding db table.
        """
        if not os.path.exists(file_path):
            return

        documents = self._file_converter.convert(file_path)
        if not documents:
            # Wenn Dokument komplett leer ist, gibt file_converter [] zurück, was bei _vector_db.add_documents dann zu exception führt
            return

        ids = [str(uuid4()) for _ in documents]

        for i in range(len(documents)):
            documents[i].metadata["id"] = ids[i]
            documents[i].metadata["source"] = f"{file_id}?{site_id}"

        self._vector_db.add_documents(documents, ids=ids)

        for i in range(len(documents)):
            embedding = self._create_db_embedding(ids[i], file_type, file_id, site_id)
            if embedding:
                self._embedding_manager.add_embedding(embedding)

        self._embedding_manager.save_updates()

    @staticmethod
    def _create_db_embedding(embedding_id: str, file_type: type, file_id, site_id=None):
        """
        Creates an embedding object based on the type and ID of the source file.

        Args:
            embedding_id (str): The ID of the embedding in the vector database.
            file_type (type): The class of the file type (e.g. LocalFile, OneDriveFile, Attachment, etc.).
            file_id: The ID of the file in the corresponding db table.

        Returns:
            Embedding: An embedding object to be stored in the relational database, or None if the file type is unsupported.
        """
        if file_type == LocalFile:
            return Embedding(id=embedding_id, local_file_id=file_id)
        elif file_type == OneDriveFile:
            return Embedding(id=embedding_id, one_drive_file_id=file_id)
        elif file_type == SharePointFile:
            return Embedding(id=embedding_id, share_point_file_id=file_id, share_point_site_id=site_id)
        elif file_type == Attachment:
            return Embedding(id=embedding_id, attachment_id=file_id)
        else:
            raise RuntimeError(f"Nicht unterstützter Dateityp: {file_type}")

    def delete_file_embeddings(self, file):
        ids_to_delete = [x.id for x in file.embeddings]
        if len(ids_to_delete) > 0:
            self._vector_db.delete(ids_to_delete)

        for embedding in file.embeddings:
            self._embedding_manager.remove_embedding(embedding)

        self._embedding_manager.save_updates()



