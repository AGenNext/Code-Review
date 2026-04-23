from __future__ import annotations

from codereviewer.core.models import RepositoryContext, ReviewJob, ReviewJobStatus
from codereviewer.services.notification_service import NotificationService, should_notify_for_status


def test_should_notify_for_terminal_statuses() -> None:
    assert should_notify_for_status(ReviewJobStatus.completed) is True
    assert should_notify_for_status(ReviewJobStatus.failed) is True
    assert should_notify_for_status(ReviewJobStatus.running) is False


def test_send_test_notification_disabled(monkeypatch) -> None:
    monkeypatch.setenv("NOTIFICATIONS_ENABLED", "false")
    service = NotificationService()
    assert service.send_test_notification() is False


def test_notify_review_result_handles_missing_smtp(monkeypatch) -> None:
    monkeypatch.setenv("NOTIFICATIONS_ENABLED", "true")
    monkeypatch.setenv("NOTIFICATION_CHANNELS", "email")
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    monkeypatch.delenv("SMTP_TO", raising=False)
    service = NotificationService()

    job = ReviewJob(
        repository=RepositoryContext(name="demo", branch="main"),
        runtime_profile_id="profile-1",
        changes=[],
        status=ReviewJobStatus.completed,
    )
    service.notify_review_result(job)


def test_notify_review_result_smtp_called(monkeypatch) -> None:
    monkeypatch.setenv("NOTIFICATIONS_ENABLED", "true")
    monkeypatch.setenv("NOTIFICATION_CHANNELS", "email")
    monkeypatch.setenv("SMTP_HOST", "localhost")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_FROM", "noreply@example.com")
    monkeypatch.setenv("SMTP_TO", "dev@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    monkeypatch.setenv("SMTP_USE_SSL", "false")
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    sent = {"count": 0}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            assert host == "localhost"
            assert port == 587
            assert timeout == 10

        def __enter__(self) -> "FakeSMTP":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def starttls(self) -> None:
            return None

        def login(self, username: str, password: str) -> None:
            return None

        def send_message(self, message) -> None:
            sent["count"] += 1
            assert message["From"] == "noreply@example.com"
            assert "dev@example.com" in message["To"]

    monkeypatch.setattr("smtplib.SMTP", FakeSMTP)
    service = NotificationService()
    job = ReviewJob(
        repository=RepositoryContext(name="demo", branch="main"),
        runtime_profile_id="profile-1",
        changes=[],
        status=ReviewJobStatus.completed,
    )
    service.notify_review_result(job)
    assert sent["count"] == 1
