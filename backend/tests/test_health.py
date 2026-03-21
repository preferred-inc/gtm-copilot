def test_health(unauth_client):
    resp = unauth_client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
