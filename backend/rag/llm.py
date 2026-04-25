from langchain_openai import ChatOpenAI
from backend.rag.config import Config

def get_llm():
    config = Config()
    # Ollama cloud uses an OpenAI-compatible API endpoint
    return ChatOpenAI(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        api_key=config.OLLAMA_API_KEY,
        temperature=0
    )