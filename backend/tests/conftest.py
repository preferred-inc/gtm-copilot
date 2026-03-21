import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.dependencies import get_gtm_client


@pytest.fixture
def mock_gtm_client():
    client = MagicMock()
    client.list_accounts.return_value = [
        {"accountId": "123", "name": "Test Account", "path": "accounts/123"}
    ]
    client.list_containers.return_value = [
        {"containerId": "456", "name": "Test Container", "path": "accounts/123/containers/456", "publicId": "GTM-TEST"}
    ]
    client.list_workspaces.return_value = [
        {"workspaceId": "789", "name": "Default Workspace", "path": "accounts/123/containers/456/workspaces/789"}
    ]
    return client


@pytest.fixture
def client(mock_gtm_client):
    app.dependency_overrides[get_gtm_client] = lambda: mock_gtm_client
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def unauth_client():
    with TestClient(app) as c:
        yield c
