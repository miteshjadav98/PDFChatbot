from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.rag.config import Config
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vectorstore import VectorStoreManager
from backend.rag.pipeline import RAGPipeline
import tempfile
import os
from typing import List
from langchain_core.documents import Document

class RAGService:
    def __init__(self):
        self.config = Config()
        self.embedding_manager = None
        self.vectorstore_manager = None
        self.pipeline = None

    def _ensure_initialized(self):
        if self.pipeline is not None:
            return

        self.embedding_manager = EmbeddingManager(self.config.EMBEDDING_MODEL)
        self.vectorstore_manager = VectorStoreManager(
            self.embedding_manager,
            self.config.VECTOR_STORE_PATH,
        )
        self.pipeline = RAGPipeline(self.vectorstore_manager)

    def upload_pdf(self, file_content: bytes, filename: str) -> dict:
        self._ensure_initialized()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        try:
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            chunks = text_splitter.split_documents(documents)
            self.vectorstore_manager.add_documents(chunks)
            return {
                "message": f"Successfully processed {filename}",
                "documents_processed": len(chunks)
            }
        finally:
            os.unlink(tmp_path)

    def ask_question(self, question: str) -> dict:
        self._ensure_initialized()

        result = self.pipeline.ask(question)
        source_data = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["sources"]
        ]
        return {
            "answer": result["answer"],
            "sources": source_data
        }
