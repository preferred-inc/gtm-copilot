"""Tests for the template library API."""

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.template_library import service as template_service
from app.services.template_library.presets import PRESET_TEMPLATES


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_custom_templates():
    """Clean up custom templates after each test."""
    yield
    custom_dir = template_service.CUSTOM_TEMPLATES_DIR
    if custom_dir.exists():
        shutil.rmtree(custom_dir)


class TestListTemplates:
    def test_list_all(self, client: TestClient):
        res = client.get("/api/templates")
        assert res.status_code == 200
        data = res.json()
        assert "templates" in data
        assert len(data["templates"]) >= len(PRESET_TEMPLATES)

    def test_filter_by_category(self, client: TestClient):
        res = client.get("/api/templates?category=analytics")
        assert res.status_code == 200
        templates = res.json()["templates"]
        assert all(t["category"] == "analytics" for t in templates)

    def test_filter_by_site_type(self, client: TestClient):
        res = client.get("/api/templates?site_type=ec")
        assert res.status_code == 200
        templates = res.json()["templates"]
        assert all("ec" in t["site_types"] for t in templates)


class TestGetTemplate:
    def test_get_preset(self, client: TestClient):
        res = client.get("/api/templates/ga4-basic")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "ga4-basic"
        assert "config" in data
        assert len(data["config"]["tags"]) > 0

    def test_not_found(self, client: TestClient):
        res = client.get("/api/templates/nonexistent")
        assert res.status_code == 404


class TestSaveTemplate:
    def test_save_custom(self, client: TestClient):
        body = {
            "name": "テスト用テンプレート",
            "description": "テスト説明",
            "category": "custom",
            "config": {
                "tags": [{"name": "Test Tag", "type": "html"}],
                "triggers": [],
                "variables": [],
                "built_in_variables": [],
            },
            "explanations": [],
        }
        res = client.post("/api/templates", json=body)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "テスト用テンプレート"
        assert data["id"].startswith("custom-")
        assert data["is_preset"] is False
        assert data["tags_count"] == 1

    def test_saved_template_appears_in_list(self, client: TestClient):
        body = {
            "name": "リスト確認用",
            "description": "desc",
            "category": "analytics",
            "config": {"tags": [], "triggers": [], "variables": [], "built_in_variables": []},
        }
        save_res = client.post("/api/templates", json=body)
        template_id = save_res.json()["id"]

        list_res = client.get("/api/templates")
        ids = [t["id"] for t in list_res.json()["templates"]]
        assert template_id in ids


class TestDeleteTemplate:
    def test_delete_custom(self, client: TestClient):
        # First save
        body = {
            "name": "削除用",
            "description": "desc",
            "category": "custom",
            "config": {"tags": [], "triggers": [], "variables": [], "built_in_variables": []},
        }
        save_res = client.post("/api/templates", json=body)
        template_id = save_res.json()["id"]

        # Then delete
        del_res = client.delete(f"/api/templates/{template_id}")
        assert del_res.status_code == 200

        # Verify gone
        get_res = client.get(f"/api/templates/{template_id}")
        assert get_res.status_code == 404

    def test_cannot_delete_preset(self, client: TestClient):
        res = client.delete("/api/templates/ga4-basic")
        assert res.status_code == 400
