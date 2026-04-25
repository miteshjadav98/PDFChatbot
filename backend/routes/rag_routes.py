from fastapi import APIRouter, UploadFile, File, Header
from backend.controllers.rag_controller import RAGController
from backend.models.schemas import (
    UploadResponse, AskResponse, ClearResponse,
    SaveHistoryRequest, SaveHistoryResponse, LoadHistoryResponse,
)

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), x_session_id: str = Header(...)):
    return await RAGController.upload_pdf(file, x_session_id)

@router.get("/ask", response_model=AskResponse)
async def ask_question(q: str, x_session_id: str = Header(...)):
    return await RAGController.ask_question(q, x_session_id)

@router.post("/clear", response_model=ClearResponse)
async def clear_session(x_session_id: str = Header(...)):
    return await RAGController.clear_session(x_session_id)

@router.post("/history/save", response_model=SaveHistoryResponse)
async def save_history(body: SaveHistoryRequest, x_session_id: str = Header(...)):
    return await RAGController.save_history(x_session_id, body.messages)

@router.get("/history/load", response_model=LoadHistoryResponse)
async def load_history(x_session_id: str = Header(...)):
    return await RAGController.load_history(x_session_id)
