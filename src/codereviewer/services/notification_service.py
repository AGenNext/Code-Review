from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from codereviewer.core.models import ReviewJob, ReviewJobStatus


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


class NotificationService:
    def __init__(self) -> None:
        self.enabled = _is_enabled(os.getenv("NOTIFICATIONS_ENABLED"))
        channels = os.getenv("NOTIFICATION_CHANNELS", "email")
        self.channels = {channel.strip().lower() for channel in channels.split(",") if channel.strip()}

        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "")
        self.smtp_to = [email.strip() for email in os.getenv("SMTP_TO", "").split(",") if email.strip()]
        self.smtp_use_tls = _is_enabled(os.getenv("SMTP_USE_TLS", "true"))
        self.smtp_use_ssl = _is_enabled(os.getenv("SMTP_USE_SSL", "false"))

    def notify_review_result(self, job: ReviewJob) -> None:
        if not self.enabled:
            return
        if "email" in self.channels:
            self._send_review_email(job)

    def send_test_notification(self) -> bool:
        if not self.enabled or "email" not in self.channels:
            return False
        if not self._smtp_ready():
            return False
        subject = "[CodeReviewer] SMTP test notification"
        body = "SMTP notification channel is configured and reachable."
        self._send_email(subject, body)
        return True

    def _send_review_email(self, job: ReviewJob) -> None:
        if not self._smtp_ready():
            return

        subject = f"[CodeReviewer] Review {job.status.value}: {job.repository.name} ({job.id})"
        summary_line = (
            f"Findings: {job.summary.total_findings}, Risk score: {job.summary.risk_score}"
            if job.summary
            else "No summary generated."
        )
        error_line = f"Error: {job.error}" if job.error else "Error: none"
        body = (
            f"Review job completed.\n\n"
            f"Job ID: {job.id}\n"
            f"Repository: {job.repository.name}\n"
            f"Branch: {job.repository.branch}\n"
            f"Status: {job.status.value}\n"
            f"{summary_line}\n"
            f"{error_line}\n"
        )
        self._send_email(subject, body)

    def _smtp_ready(self) -> bool:
        return bool(self.smtp_host and self.smtp_from and self.smtp_to)

    def _send_email(self, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.smtp_from
        message["To"] = ", ".join(self.smtp_to)
        message.set_content(body)

        try:
            if self.smtp_use_ssl:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.smtp_username:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
                return

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
        except Exception:
            # Notifications must never break review processing.
            return


def should_notify_for_status(status: ReviewJobStatus) -> bool:
    return status in {ReviewJobStatus.completed, ReviewJobStatus.failed}
