"""Tests for the import API endpoints (preview & execute)."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_gtm_client
from app.main import app

WORKSPACE_PATH = "accounts/1/containers/2/workspaces/3"


@pytest.fixture
def mock_gtm_client():
    client = MagicMock()
    client.list_tags.return_value = [
        {"name": "Existing Tag", "type": "html", "path": "tags/1"}
    ]
    client.list_triggers.return_value = []
    client.list_variables.return_value = []
    client.list_built_in_variables.return_value = [
        {"type": "pageUrl", "name": "Page URL"}
    ]
    return client


@pytest.fixture
def client(mock_gtm_client):
    app.dependency_overrides[get_gtm_client] = lambda: mock_gtm_client
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


SAMPLE_IMPORT_DATA = {
    "tags": [
        {"name": "New Tag", "type": "html"},
        {"name": "Existing Tag", "type": "html"},
    ],
    "triggers": [],
    "variables": [],
    "built_in_variables": [
        {"type": "pageUrl", "name": "Page URL"},
    ],
}


class TestImportPreview:
    def test_preview_shows_diffs(self, client):
        resp = client.post("/api/import/preview", json={
            "workspace_path": WORKSPACE_PATH,
            "data": SAMPLE_IMPORT_DATA,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "diffs" in data
        assert "summary" in data
        assert data["summary"]["create"] >= 1  # "New Tag" should be created

    def test_preview_existing_built_in_skipped(self, client):
        resp = client.post("/api/import/preview", json={
            "workspace_path": WORKSPACE_PATH,
            "data": SAMPLE_IMPORT_DATA,
        })
        data = resp.json()
        bv_diffs = [d for d in data["diffs"] if d["type"] == "built_in_variables"]
        assert all(d["action"] == "skip" for d in bv_diffs)

    def test_preview_missing_workspace_path(self, client):
        resp = client.post("/api/import/preview", json={
            "data": {"tags": [], "triggers": [], "variables": [], "built_in_variables": []},
        })
        assert resp.status_code == 422

    def test_preview_empty_data(self, client):
        resp = client.post("/api/import/preview", json={
            "workspace_path": WORKSPACE_PATH,
            "data": {"tags": [], "triggers": [], "variables": [], "built_in_variables": []},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["create"] == 0
        assert data["summary"]["update"] == 0


class TestImportExecute:
    def test_execute_returns_results(self, client, mock_gtm_client):
        mock_gtm_client.list_tags.return_value = []
        mock_gtm_client.list_triggers.return_value = []
        mock_gtm_client.list_variables.return_value = []
        mock_gtm_client.list_built_in_variables.return_value = []

        resp = client.post("/api/import/execute", json={
            "workspace_path": WORKSPACE_PATH,
            "data": {
                "tags": [],
                "triggers": [],
                "variables": [],
                "built_in_variables": [],
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "summary" in data

    def test_execute_missing_data(self, client):
        resp = client.post("/api/import/execute", json={
            "workspace_path": WORKSPACE_PATH,
        })
        assert resp.status_code == 422
