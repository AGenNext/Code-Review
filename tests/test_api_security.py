from fastapi.testclient import TestClient

from codereviewer.api.app import app


def test_healthz_is_public() -> None:
    response = TestClient(app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_requires_bearer_token_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("API_BEARER_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_BEARER_TOKEN", "secret-token")

    response = TestClient(app).get("/api/providers")

    assert response.status_code == 401


def test_api_accepts_valid_bearer_token_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("API_BEARER_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_BEARER_TOKEN", "secret-token")

    response = TestClient(app).get(
        "/api/providers",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert "anthropic" in response.json()


def test_security_headers_are_enabled_by_default() -> None:
    response = TestClient(app).get("/healthz")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_invalid_tenant_id_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("API_BEARER_AUTH_ENABLED", "false")

    response = TestClient(app).get("/api/config", headers={"X-Tenant-ID": "!"})

    assert response.status_code == 400


def test_agent_identity_can_define_tenant(monkeypatch) -> None:
    monkeypatch.setenv("API_BEARER_AUTH_ENABLED", "false")

    response = TestClient(app).get("/api/config", headers={"X-Agent-ID": "agent-1"})

    assert response.status_code == 200
    assert response.json()["identity"] == {
        "tenant_id": "agent:agent-1",
        "agent_id": "agent-1",
    }
