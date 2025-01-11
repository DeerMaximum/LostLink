import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lost_link.settings import Settings


class FileToDocumentConverter:

    def __init__(self, settings: Settings):
        overlap = settings.get(Settings.KEY_TEXT_SPLITTING_OVERLAP, 150)
        chunk_size = 500

        if overlap > chunk_size:
            overlap = chunk_size

        self._splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

    @staticmethod
    def _get_loader(path: str) -> BaseLoader | None:
        extension = os.path.splitext(path)[1]

        if extension in [".pdf"]:
            return PyPDFLoader(path)
        elif extension in [".docx", ".doc"]:
            return Docx2txtLoader(path)
        elif extension in [".pptx"]:
            return UnstructuredPowerPointLoader(path)
        elif extension in [".txt"]:
            return TextLoader(path, autodetect_encoding=True)

        return None

    def convert(self, file_path: str) -> list[Document]:
        loader = self._get_loader(file_path)

        if not loader:
            return []

        content = ""
        last_metadata = {}

        try:
            for page in loader.load():
                content += page.page_content.lower()
                content += "\n\n"
                last_metadata = page.metadata

            document = Document(content, metadata={
                "source": last_metadata["source"],
            })

            return self._splitter.split_documents([document])
        
        except Exception as e:
            raise RuntimeError(f"Konnte keine Embeddings für {file_path} generieren") from e
