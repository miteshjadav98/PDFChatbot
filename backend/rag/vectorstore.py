import faiss
import numpy as np
import os
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from backend.rag.embeddings import EmbeddingManager

class VectorStoreManager:
    def __init__(self, embedding_manager: EmbeddingManager, store_path: str):
        self.embedding_manager = embedding_manager
        self.store_path = store_path
        self.vectorstore = None
        self.load_or_create()

    def load_or_create(self):
        if os.path.exists(self.store_path) and os.listdir(self.store_path):
            self.vectorstore = FAISS.load_local(self.store_path, self.embedding_manager, allow_dangerous_deserialization=True)
        else:
            # Create empty FAISS index
            dimension = len(self.embedding_manager.embed_query("test"))
            index = faiss.IndexFlatL2(dimension)
            docstore = InMemoryDocstore({})
            index_to_docstore_id = {}
            self.vectorstore = FAISS(
                embedding_function=self.embedding_manager,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )

    def add_documents(self, documents: List[Document]):
        if self.vectorstore:
            self.vectorstore.add_documents(documents)
            self.save()

    def save(self):
        if self.vectorstore:
            self.vectorstore.save_local(self.store_path)

    def search(self, query: str, k: int = 3) -> List[Document]:
        if self.vectorstore:
            return self.vectorstore.similarity_search(query, k=k)
        return []