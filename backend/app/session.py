import secrets
import threading
from datetime import datetime, timedelta
from typing import Optional

SESSION_TTL = timedelta(days=30)
MAX_SESSIONS = 1000

_store: dict[str, dict] = {}
_lock = threading.Lock()


def create_session(refresh_token: str, client_id: str, client_secret: str) -> str:
    session_id = secrets.token_urlsafe(32)
    with _lock:
        # Cleanup expired sessions if we're approaching the limit
        if len(_store) >= MAX_SESSIONS:
            _cleanup_expired()
        _store[session_id] = {
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "created_at": datetime.utcnow(),
        }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    with _lock:
        session = _store.get(session_id)
        if session is None:
            return None
        if datetime.utcnow() - session["created_at"] > SESSION_TTL:
            _store.pop(session_id, None)
            return None
        return session


def delete_session(session_id: str) -> None:
    with _lock:
        _store.pop(session_id, None)


def _cleanup_expired() -> int:
    """Remove expired sessions. Returns count of removed sessions."""
    now = datetime.utcnow()
    expired = [
        sid for sid, data in _store.items()
        if now - data["created_at"] > SESSION_TTL
    ]
    for sid in expired:
        del _store[sid]
    return len(expired)
