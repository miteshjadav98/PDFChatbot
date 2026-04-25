from fastapi import UploadFile, HTTPException
from backend.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

# Initialize a single service instance
rag_service = RAGService()

class RAGController:
    @staticmethod
    async def upload_pdf(file: UploadFile):
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        try:
            content = await file.read()
            result = rag_service.upload_pdf(content, file.filename)
            logger.info(f"Uploaded {file.filename}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize or process the PDF. Check model availability and configuration.",
            )

    @staticmethod
    async def ask_question(q: str):
        if not q:
            raise HTTPException(status_code=400, detail="Question parameter 'q' is required")
        
        try:
            result = rag_service.ask_question(q)
            logger.info(f"Answered question: {q}")
            return result
        except Exception as e:
            logger.error(f"Error answering question '{q}': {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to answer the question. Check model availability and configuration.",
            )
