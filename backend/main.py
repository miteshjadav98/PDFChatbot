from fastapi import FastAPI
import logging
from backend.routes.rag_routes import router as rag_router
from backend.models.schemas import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

app.include_router(rag_router)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")
