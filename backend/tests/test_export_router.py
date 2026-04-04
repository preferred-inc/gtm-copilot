"""Tests for the export API endpoint."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_gtm_client
from app.main import app


@pytest.fixture
def mock_gtm_client():
    client = MagicMock()
    client.list_tags.return_value = [
        {"name": "GA4 Config", "type": "gaawc", "path": "tags/1"}
    ]
    client.list_triggers.return_value = [
        {"name": "All Pages", "type": "pageview", "path": "triggers/1"}
    ]
    client.list_variables.return_value = [
        {"name": "Page URL", "type": "u", "path": "variables/1"}
    ]
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


class TestExportRouter:
    def test_export_workspace(self, client, mock_gtm_client):
        resp = client.post("/api/export", json={
            "workspace_path": "accounts/1/containers/2/workspaces/3",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "GA4 Config"
        assert len(data["triggers"]) == 1
        assert len(data["variables"]) == 1
        assert len(data["built_in_variables"]) == 1
        mock_gtm_client.list_tags.assert_called_once_with(
            "accounts/1/containers/2/workspaces/3"
        )

    def test_export_empty_workspace(self, client, mock_gtm_client):
        mock_gtm_client.list_tags.return_value = []
        mock_gtm_client.list_triggers.return_value = []
        mock_gtm_client.list_variables.return_value = []
        mock_gtm_client.list_built_in_variables.return_value = []

        resp = client.post("/api/export", json={
            "workspace_path": "accounts/1/containers/2/workspaces/3",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["tags"] == []
        assert data["triggers"] == []

    def test_export_missing_workspace_path(self, client):
        resp = client.post("/api/export", json={})
        assert resp.status_code == 422

    def test_export_gtm_api_error(self, client, mock_gtm_client):
        mock_gtm_client.list_tags.side_effect = Exception("GTM API error")
        resp = client.post("/api/export", json={
            "workspace_path": "accounts/1/containers/2/workspaces/3",
        })
        assert resp.status_code == 500
