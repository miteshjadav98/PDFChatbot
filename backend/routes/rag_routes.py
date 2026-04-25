from fastapi import APIRouter, UploadFile, File
from backend.controllers.rag_controller import RAGController
from backend.models.schemas import UploadResponse, AskResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    return await RAGController.upload_pdf(file)

@router.get("/ask", response_model=AskResponse)
async def ask_question(q: str):
    return await RAGController.ask_question(q)
