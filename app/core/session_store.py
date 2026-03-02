import time
import threading
from typing import Dict, List, Any, Optional
from uuid import uuid4


class SessionStore:
    """
    Thread-safe in-memory session store.
    Suitable for hackathon / single-instance deployments.
    Replace with Redis for production scaling.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._ttl = ttl_seconds

    # =====================================================
    # INTERNAL CLEANUP
    # =====================================================

    def _is_expired(self, session_id: str) -> bool:
        session = self._store.get(session_id)
        if not session:
            return True

        return (time.time() - session["created_at"]) > self._ttl

    def cleanup_expired(self):
        with self._lock:
            expired_sessions = [
                sid for sid in self._store
                if self._is_expired(sid)
            ]
            for sid in expired_sessions:
                del self._store[sid]

    # =====================================================
    # PUBLIC METHODS
    # =====================================================

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        with self._lock:
            self.cleanup_expired()

            session_id = str(uuid4())
            self._store[session_id] = {
                "created_at": time.time(),
                "metadata": metadata or {},
                "history": []
            }
            return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if session_id not in self._store:
                return None

            if self._is_expired(session_id):
                del self._store[session_id]
                return None

            return self._store[session_id]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        role: 'user' | 'assistant' | 'system'
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return False

            session["history"].append({
                "role": role,
                "content": content,
                "timestamp": time.time()
            })
            return True

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                return []
            return session["history"]

    def clear_session(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                return True
            return False

# Singleton instance
session_store = SessionStore()