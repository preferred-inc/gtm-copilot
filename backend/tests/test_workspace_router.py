class TestWorkspaceRouter:
    def test_list_accounts(self, client):
        resp = client.get("/api/accounts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["accountId"] == "123"

    def test_list_containers(self, client):
        resp = client.get("/api/accounts/123/containers")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["containerId"] == "456"

    def test_list_workspaces(self, client):
        resp = client.get("/api/containers/123/456/workspaces")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["workspaceId"] == "789"

    def test_connect_workspace_with_ids(self, client, mock_gtm_client):
        mock_gtm_client.get_container.return_value = {"name": "Test", "containerId": "456"}
        mock_gtm_client.get_workspace.return_value = {"name": "Default", "workspaceId": "789"}

        resp = client.post("/api/workspace/connect", json={
            "account_id": "123",
            "container_id": "456",
            "workspace_id": "789",
        })
        assert resp.status_code == 200
        assert resp.json()["workspace_path"] == "accounts/123/containers/456/workspaces/789"

    def test_connect_workspace_missing_ids(self, client):
        resp = client.post("/api/workspace/connect", json={})
        assert resp.status_code == 400


class TestAuthRouter:
    def test_me_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/api/auth/me")
        assert resp.status_code == 401
        assert resp.json()["logged_in"] is False

    def test_logout(self, unauth_client):
        resp = unauth_client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
