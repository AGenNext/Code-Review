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
