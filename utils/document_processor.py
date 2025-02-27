# utils/document_processor.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import config

class DocumentProcessor:
    """Utility class for processing and chunking documents."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

    def process_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)