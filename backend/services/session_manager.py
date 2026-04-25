import threading
import shutil
import json
import os
import logging
from backend.services.rag_service import RAGService

logger = logging.getLogger(__name__)

CHAT_HISTORY_FILE = "chat_history.json"


class SessionManager:
    """
    Manages per-user RAGService instances keyed by session_id.
    Each session gets its own in-memory FAISS index and vector store
    directory so that multiple users never share document context.
    Chat history is also persisted to disk per session.
    """

    def __init__(self, base_store_dir: str = "session_stores"):
        self._sessions: dict[str, RAGService] = {}
        self._lock = threading.Lock()
        self._base_store_dir = base_store_dir
        os.makedirs(self._base_store_dir, exist_ok=True)

    def _store_path(self, session_id: str) -> str:
        return os.path.join(self._base_store_dir, session_id)

    def get_service(self, session_id: str) -> RAGService:
        """Return the RAGService for the given session, creating one if needed."""
        with self._lock:
            if session_id not in self._sessions:
                store_path = self._store_path(session_id)
                service = RAGService(vector_store_path=store_path)
                self._sessions[session_id] = service
                logger.info(f"Created new session: {session_id}")
            return self._sessions[session_id]

    def save_chat_history(self, session_id: str, messages: list) -> None:
        """Persist chat messages to a JSON file in the session directory."""
        store_path = self._store_path(session_id)
        os.makedirs(store_path, exist_ok=True)
        filepath = os.path.join(store_path, CHAT_HISTORY_FILE)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False)

    def load_chat_history(self, session_id: str) -> list:
        """Load chat messages from disk. Returns an empty list if none exist."""
        filepath = os.path.join(self._store_path(session_id), CHAT_HISTORY_FILE)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def clear_session(self, session_id: str) -> bool:
        """
        Destroy the RAGService for the given session and clean up its
        vector store directory from disk (including chat history).
        Returns True if a session was actually removed, False if it didn't exist.
        """
        with self._lock:
            service = self._sessions.pop(session_id, None)

        # Remove persisted vector store files and chat history
        store_path = self._store_path(session_id)
        dir_existed = os.path.exists(store_path)
        if dir_existed:
            shutil.rmtree(store_path, ignore_errors=True)

        cleared = service is not None or dir_existed
        if cleared:
            logger.info(f"Cleared session: {session_id}")
        return cleared

    def active_sessions(self) -> list[str]:
        """Return a list of currently active session IDs."""
        with self._lock:
            return list(self._sessions.keys())
