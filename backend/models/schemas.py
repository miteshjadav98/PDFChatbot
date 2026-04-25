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