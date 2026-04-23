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
            "changes": [{"path": "a.py", "change_type": "modified", "patch": "# TODO remove hardcoded password"}],
        },
    ).json()

    assert review["status"] == "completed"
    assert review["summary"]["total_findings"] >= 1
