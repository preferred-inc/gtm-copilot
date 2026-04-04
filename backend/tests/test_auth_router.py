"""Tests for the auth API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.session import create_session, _store


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_sessions():
    yield
    _store.clear()


class TestAuthMe:
    def test_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
        assert resp.json()["logged_in"] is False

    def test_authenticated_with_session(self, client):
        session_id = create_session(
            refresh_token="rt_test",
            client_id="cid_test",
            client_secret="cs_test",
        )
        resp = client.get("/api/auth/me", cookies={"session_id": session_id})
        assert resp.status_code == 200
        assert resp.json()["logged_in"] is True

    def test_invalid_session(self, client):
        resp = client.get("/api/auth/me", cookies={"session_id": "bogus"})
        assert resp.status_code == 401


class TestAuthLogout:
    def test_logout_without_session(self, client):
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_logout_clears_session(self, client):
        session_id = create_session(
            refresh_token="rt_test",
            client_id="cid_test",
            client_secret="cs_test",
        )
        resp = client.post("/api/auth/logout", cookies={"session_id": session_id})
        assert resp.status_code == 200

        # Session should be gone
        me_resp = client.get("/api/auth/me", cookies={"session_id": session_id})
        assert me_resp.status_code == 401


class TestAuthLogin:
    def test_login_redirects_to_google(self, client):
        with patch("app.routers.auth.get_authorization_url", return_value="https://accounts.google.com/o/oauth2/auth?test=1"):
            resp = client.get("/api/auth/login", follow_redirects=False)
            assert resp.status_code == 307
            assert "accounts.google.com" in resp.headers["location"]

    def test_callback_creates_session(self, client):
        mock_tokens = {
            "refresh_token": "rt_new",
            "access_token": "at_new",
        }
        with patch("app.routers.auth.exchange_code_for_tokens", return_value=mock_tokens):
            resp = client.get("/api/auth/callback?code=authcode123", follow_redirects=False)
            assert resp.status_code == 307
            assert "session_id" in resp.cookies
