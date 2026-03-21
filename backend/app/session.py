import secrets
from datetime import datetime
from typing import Optional

_store: dict[str, dict] = {}


def create_session(refresh_token: str, client_id: str, client_secret: str) -> str:
    session_id = secrets.token_urlsafe(32)
    _store[session_id] = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "created_at": datetime.utcnow(),
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    return _store.get(session_id)


def delete_session(session_id: str) -> None:
    _store.pop(session_id, None)
