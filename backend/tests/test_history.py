"""Tests for the generation history API."""

import shutil

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import history_service


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_history():
    """Clean up history before and after each test."""
    if history_service.HISTORY_DIR.exists():
        shutil.rmtree(history_service.HISTORY_DIR)
    yield
    if history_service.HISTORY_DIR.exists():
        shutil.rmtree(history_service.HISTORY_DIR)


SAMPLE_ANALYSIS = {
    "url": "https://example.com",
    "title": "Example",
    "description": "Test site",
    "site_type": "corporate",
    "existing_tags": [],
    "forms": [],
    "cta_elements": [],
    "ecommerce": None,
    "technology": ["Google Analytics"],
    "pages_analyzed": [],
}

SAMPLE_CONFIG = {
    "tags": [{"name": "GA4 Config", "type": "gaawc"}],
    "triggers": [{"name": "All Pages", "type": "pageview"}],
    "variables": [],
    "built_in_variables": [],
}

SAMPLE_EXPLANATIONS = [
    {"name": "GA4 Config", "type": "tag", "reason": "基本的な計測", "priority": "required"},
]


def _save_sample():
    return history_service.save_generation(
        url="https://example.com",
        site_type="corporate",
        analysis=SAMPLE_ANALYSIS,
        config=SAMPLE_CONFIG,
        explanations=SAMPLE_EXPLANATIONS,
    )


class TestListHistory:
    def test_empty(self, client):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["entries"] == []
        assert data["total"] == 0

    def test_with_entries(self, client):
        _save_sample()
        _save_sample()
        resp = client.get("/api/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["entries"]) == 2
        assert data["total"] == 2

    def test_pagination(self, client):
        for _ in range(3):
            _save_sample()
        resp = client.get("/api/history?limit=2&offset=0")
        data = resp.json()
        assert len(data["entries"]) == 2
        assert data["total"] == 3


class TestGetHistory:
    def test_get_detail(self, client):
        entry = _save_sample()
        resp = client.get(f"/api/history/{entry.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == "https://example.com"
        assert "config" in data
        assert "analysis" in data
        assert len(data["config"]["tags"]) == 1

    def test_not_found(self, client):
        resp = client.get("/api/history/00000000")
        assert resp.status_code == 404

    def test_invalid_id(self, client):
        resp = client.get("/api/history/../../etc/passwd")
        assert resp.status_code == 404


class TestDeleteHistory:
    def test_delete(self, client):
        entry = _save_sample()
        resp = client.delete(f"/api/history/{entry.id}")
        assert resp.status_code == 200

        # Verify gone
        resp = client.get(f"/api/history/{entry.id}")
        assert resp.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/api/history/00000000")
        assert resp.status_code == 404
