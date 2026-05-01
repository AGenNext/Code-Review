import pytest

pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from codereviewer.api.app import app


def test_review_flow() -> None:
    client = TestClient(app)

    profile = client.post(
        "/api/runtime-profiles",
        json={
            "name": "default",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4",
            "auth_reference": "local-key",
            "is_default": True,
        },
    ).json()

    review = client.post(
        "/api/reviews",
        json={
            "repository": {"name": "demo", "branch": "main"},
            "runtime_profile_id": profile["id"],
            "changes": [{"path": "a.py", "change_type": "modified", "patch": "@@\n+# TODO remove hardcoded password"}],
        },
    ).json()

    assert review["status"] == "completed"
    assert review["summary"]["total_findings"] >= 1
    assert review["queued_at"] is not None
    assert review["started_at"] is not None
    assert review["completed_at"] is not None


def test_deleted_secret_not_reported() -> None:
    client = TestClient(app)
    profile = client.post(
        "/api/runtime-profiles",
        json={
            "name": "default-2",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4",
            "auth_reference": "local-key",
            "is_default": False,
        },
    ).json()
    review = client.post(
        "/api/reviews",
        json={
            "repository": {"name": "demo", "branch": "main"},
            "runtime_profile_id": profile["id"],
            "changes": [{"path": "a.py", "change_type": "modified", "patch": "@@\n-password='secret'"}],
        },
    ).json()
    assert review["summary"]["total_findings"] == 0


def test_feedback_roundtrip() -> None:
    client = TestClient(app)
    payload = {"review_job_id": "job-1", "feedback_type": "false_positive", "reason": "known test fixture"}
    created = client.post("/api/feedback", json=payload)
    assert created.status_code == 200
    items = client.get("/api/feedback").json()
    assert any(item["review_job_id"] == "job-1" for item in items)


def test_multitenant_review_isolation_by_header() -> None:
    client = TestClient(app)
    tenant_a = {"X-Tenant-ID": "tenant-a"}
    tenant_b = {"X-Tenant-ID": "tenant-b"}

    profile = client.post(
        "/api/runtime-profiles",
        headers=tenant_a,
        json={
            "name": "tenant-a-default",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4",
            "auth_reference": "local-key",
            "is_default": True,
        },
    ).json()

    review = client.post(
        "/api/reviews",
        headers=tenant_a,
        json={
            "repository": {"name": "demo-a", "branch": "main"},
            "runtime_profile_id": profile["id"],
            "changes": [{"path": "a.py", "change_type": "modified", "patch": "@@\n+# TODO tenant a"}],
        },
    ).json()

    assert client.get("/api/reviews", headers=tenant_a).status_code == 200
    assert any(item["id"] == review["id"] for item in client.get("/api/reviews", headers=tenant_a).json())
    assert all(item["id"] != review["id"] for item in client.get("/api/reviews", headers=tenant_b).json())
    assert client.get(f"/api/reviews/{review['id']}", headers=tenant_b).status_code == 404


def test_agent_identity_maps_to_tenant_namespace() -> None:
    client = TestClient(app)
    agent_headers = {"X-Agent-ID": "vscode-agent-1"}

    profile = client.post(
        "/api/runtime-profiles",
        headers=agent_headers,
        json={
            "name": "agent-default",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4",
            "auth_reference": "local-key",
            "is_default": False,
        },
    ).json()
    assert profile["tenant_id"] == "agent:vscode-agent-1"

    review = client.post(
        "/api/reviews",
        headers=agent_headers,
        json={
            "repository": {"name": "demo-agent", "branch": "main"},
            "runtime_profile_id": profile["id"],
            "changes": [{"path": "x.py", "change_type": "modified", "patch": "@@\n+# TODO agent path"}],
        },
    ).json()
    assert review["tenant_id"] == "agent:vscode-agent-1"
    assert review["agent_id"] == "vscode-agent-1"


def test_frontend_config_exposes_safe_runtime_config(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-ant-secret")
    monkeypatch.setenv("SSO_ENABLED", "true")
    monkeypatch.setenv("SSO_CLIENT_SECRET", "sso-secret")

    client = TestClient(app)
    headers = {"X-Tenant-ID": "frontend-config-test"}
    profile = client.post(
        "/api/runtime-profiles",
        headers=headers,
        json={
            "name": "frontend-default",
            "provider": "anthropic",
            "model_id": "claude-sonnet-4",
            "auth_reference": "local-key",
            "is_default": True,
        },
    ).json()

    response = client.get("/api/config", headers=headers)
    assert response.status_code == 200
    config = response.json()

    assert config["identity"]["tenant_id"] == "frontend-config-test"
    assert any(item["id"] == profile["id"] for item in config["runtime"]["profiles"])
    assert any(item["model_id"] == "claude-sonnet-4" for item in config["runtime"]["models"])
    assert config["integrations"]["claude_agent_sdk"]["api_key_configured"] is True
    assert config["integrations"]["sso"]["client_secret_configured"] is True
    assert "sk-ant-secret" not in response.text
    assert "sso-secret" not in response.text


def test_invalid_tenant_id_rejected() -> None:
    client = TestClient(app)
    response = client.get("/api/config", headers={"X-Tenant-ID": "bad tenant"})
    assert response.status_code == 400
    assert "X-Tenant-ID" in response.text


def test_security_headers_present_on_api_response() -> None:
    client = TestClient(app)
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_bearer_auth_guard_for_api(monkeypatch) -> None:
    monkeypatch.setenv("API_BEARER_AUTH_ENABLED", "true")
    monkeypatch.setenv("API_BEARER_TOKEN", "secret-token")
    client = TestClient(app)

    unauthorized = client.get("/api/config")
    assert unauthorized.status_code == 401

    authorized = client.get("/api/config", headers={"Authorization": "Bearer secret-token"})
    assert authorized.status_code == 200
