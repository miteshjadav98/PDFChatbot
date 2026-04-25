from fastapi import FastAPI, UploadFile, File, HTTPException
import logging
from backend.services.rag_service import RAGService
from backend.models.schemas import UploadResponse, AskResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

rag_service = RAGService()

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        content = await file.read()
        result = rag_service.upload_pdf(content, file.filename)
        logger.info(f"Uploaded {file.filename}: {result}")
        return UploadResponse(**result)
    except Exception as e:
        logger.error(f"Error uploading {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize or process the PDF. Check model availability and configuration.",
        )

@app.get("/ask", response_model=AskResponse)
async def ask_question(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Question parameter 'q' is required")
    
    try:
        result = rag_service.ask_question(q)
        logger.info(f"Answered question: {q}")
        return AskResponse(**result)
    except Exception as e:
        logger.error(f"Error answering question '{q}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to answer the question. Check model availability and configuration.",
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")
