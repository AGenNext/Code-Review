from __future__ import annotations

from collections.abc import Iterable

from codereviewer.core.models import ReviewJob, RuntimeProfile


class InMemoryReviewJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, ReviewJob] = {}

    def save(self, job: ReviewJob) -> ReviewJob:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> ReviewJob | None:
        return self._jobs.get(job_id)

    def list(self) -> Iterable[ReviewJob]:
        return self._jobs.values()


class InMemoryRuntimeProfileRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, RuntimeProfile] = {}

    def save(self, profile: RuntimeProfile) -> RuntimeProfile:
        if profile.is_default:
            for existing in self._profiles.values():
                existing.is_default = False
        self._profiles[profile.id] = profile
        return profile

    def get(self, profile_id: str) -> RuntimeProfile | None:
        return self._profiles.get(profile_id)

    def list(self) -> list[RuntimeProfile]:
        return list(self._profiles.values())
