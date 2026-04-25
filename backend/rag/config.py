import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH = "faiss_index"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    K_RETRIEVE = 3