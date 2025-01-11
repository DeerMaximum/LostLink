import os
from langchain_chroma import Chroma

from lost_link.ai.embedding_generator import EmbeddingGenerator
from lost_link.ai.file_to_document import FileToDocumentConverter
from lost_link.db.embedding_manager import EmbeddingManager
from lost_link.db.local_file_manager import LocalFileManager, LocalFile
from lost_link.service_locator import ServiceLocator


class LocalFileProcessor:

    def __init__(self, file_manager: LocalFileManager, embedding_manager: EmbeddingManager,
                 file_converter: FileToDocumentConverter ,vector_db: Chroma):
        self._file_manager = file_manager
        self._file_converter = file_converter
        self._embedding_manager = embedding_manager
        self._vector_db = vector_db
        self._embedding_generator: EmbeddingGenerator = ServiceLocator.get_service("embedding_generator")


    def _process_new_file(self, file: LocalFile):
        self._embedding_generator.generate_and_store_embeddings(file.path, LocalFile, file.id)

    def _process_deleted_file(self, file: LocalFile):
        if os.path.exists(file.path):
            # Datei existiert noch, wurde fälschlicherweise als deleted markiert, also als bearbeitet behandeln
            file.deleted = False
            self._process_edited_file(file)
            return
        self._embedding_generator.delete_file_embeddings(file)
        self._file_manager.remove_file(file)
        self._file_manager.save_updates()

    def _process_edited_file(self, file: LocalFile):
        self._embedding_generator.delete_file_embeddings(file)

        file.edited = False
        self._file_manager.save_updates()

    def process_changes(self):
        failed_files = []

        for file in self._file_manager.get_all_edited_files():
            try:
                self._process_edited_file(file)
            except RuntimeError:
                failed_files.append(file.path)

        for file in self._file_manager.get_all_deleted_files():
            try:
                self._process_deleted_file(file)
            except RuntimeError:
                failed_files.append(file.path)

        for file in self._file_manager.get_all_new_files():
            try:
                self._process_new_file(file)
            except RuntimeError:
                failed_files.append(file.path)

        if len(failed_files) > 0:
            msg = "\n".join([f"Konnte lokale Datei {x} nicht verarbeiten" for x in failed_files if len(x) > 0])
            raise RuntimeError(msg)
