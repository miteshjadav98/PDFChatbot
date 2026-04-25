from fastapi import UploadFile, HTTPException
from backend.services.session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)

# Single session manager shared across all requests
session_manager = SessionManager()

class RAGController:
    @staticmethod
    async def upload_pdf(file: UploadFile, session_id: str):
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        try:
            service = session_manager.get_service(session_id)
            content = await file.read()
            result = service.upload_pdf(content, file.filename)
            logger.info(f"[{session_id}] Uploaded {file.filename}: {result}")
            return result
        except Exception as e:
            logger.error(f"[{session_id}] Error uploading {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize or process the PDF. Check model availability and configuration.",
            )

    @staticmethod
    async def ask_question(q: str, session_id: str):
        if not q:
            raise HTTPException(status_code=400, detail="Question parameter 'q' is required")
        
        try:
            service = session_manager.get_service(session_id)
            result = service.ask_question(q)
            logger.info(f"[{session_id}] Answered question: {q}")
            return result
        except Exception as e:
            logger.error(f"[{session_id}] Error answering question '{q}': {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to answer the question. Check model availability and configuration.",
            )

    @staticmethod
    async def clear_session(session_id: str):
        cleared = session_manager.clear_session(session_id)
        if cleared:
            logger.info(f"[{session_id}] Session cleared successfully")
            return {"message": "Session cleared successfully", "session_id": session_id}
        else:
            logger.info(f"[{session_id}] No active session found to clear")
            return {"message": "No active session found", "session_id": session_id}

    @staticmethod
    async def save_history(session_id: str, messages: list):
        session_manager.save_chat_history(session_id, messages)
        return {"message": "Chat history saved", "session_id": session_id}

    @staticmethod
    async def load_history(session_id: str):
        messages = session_manager.load_chat_history(session_id)
        return {"messages": messages, "session_id": session_id}
