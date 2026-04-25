from pydantic import BaseModel
from typing import List, Dict, Any

class UploadResponse(BaseModel):
    message: str
    documents_processed: int

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str

class ClearResponse(BaseModel):
    message: str
    session_id: str

class SaveHistoryRequest(BaseModel):
    messages: List[Dict[str, Any]]

class SaveHistoryResponse(BaseModel):
    message: str
    session_id: str

class LoadHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    session_id: str