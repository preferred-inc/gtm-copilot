from datetime import datetime, timedelta
from unittest.mock import patch

from app.session import (
    SESSION_TTL,
    _cleanup_expired,
    _store,
    create_session,
    delete_session,
    get_session,
)


class TestSession:
    def setup_method(self):
        _store.clear()

    def test_create_and_get(self):
        sid = create_session("token", "client_id", "client_secret")
        session = get_session(sid)
        assert session is not None
        assert session["refresh_token"] == "token"
        assert session["client_id"] == "client_id"

    def test_get_nonexistent(self):
        assert get_session("nonexistent") is None

    def test_delete(self):
        sid = create_session("token", "cid", "csecret")
        delete_session(sid)
        assert get_session(sid) is None

    def test_delete_nonexistent(self):
        delete_session("nonexistent")  # should not raise

    def test_expired_session_returns_none(self):
        sid = create_session("token", "cid", "csecret")
        # Manually set created_at to past
        _store[sid]["created_at"] = datetime.utcnow() - SESSION_TTL - timedelta(seconds=1)
        assert get_session(sid) is None
        # Should also be removed from store
        assert sid not in _store

    def test_cleanup_expired(self):
        sid1 = create_session("t1", "c1", "s1")
        sid2 = create_session("t2", "c2", "s2")
        _store[sid1]["created_at"] = datetime.utcnow() - SESSION_TTL - timedelta(days=1)
        removed = _cleanup_expired()
        assert removed == 1
        assert sid1 not in _store
        assert sid2 in _store
