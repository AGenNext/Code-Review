from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from codereviewer.core.models import MemoryRecord, ReviewFeedbackEvent, ReviewJob, RuntimeProfile


class SQLiteRepository:
    def __init__(self, db_path: str = "./.codereviewer/codereviewer.db") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_profiles (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS review_jobs (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS review_feedback (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    id TEXT PRIMARY KEY,
                    repository_name TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )


class ReviewJobRepository:
    def __init__(self, storage: SQLiteRepository) -> None:
        self.storage = storage

    def save(self, job: ReviewJob) -> ReviewJob:
        with self.storage._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO review_jobs (id, data) VALUES (?, ?)",
                (job.id, job.model_dump_json()),
            )
        return job

    def get(self, job_id: str) -> ReviewJob | None:
        with self.storage._connect() as con:
            row = con.execute("SELECT data FROM review_jobs WHERE id = ?", (job_id,)).fetchone()
        return ReviewJob.model_validate(json.loads(row[0])) if row else None

    def list(self) -> Iterable[ReviewJob]:
        with self.storage._connect() as con:
            rows = con.execute("SELECT data FROM review_jobs ORDER BY rowid DESC").fetchall()
        return [ReviewJob.model_validate(json.loads(row[0])) for row in rows]


class RuntimeProfileRepository:
    def __init__(self, storage: SQLiteRepository) -> None:
        self.storage = storage

    def save(self, profile: RuntimeProfile) -> RuntimeProfile:
        with self.storage._connect() as con:
            if profile.is_default:
                rows = con.execute("SELECT id, data FROM runtime_profiles").fetchall()
                for profile_id, raw in rows:
                    loaded = RuntimeProfile.model_validate(json.loads(raw))
                    loaded.is_default = False
                    con.execute(
                        "INSERT OR REPLACE INTO runtime_profiles (id, data) VALUES (?, ?)",
                        (profile_id, loaded.model_dump_json()),
                    )
            con.execute(
                "INSERT OR REPLACE INTO runtime_profiles (id, data) VALUES (?, ?)",
                (profile.id, profile.model_dump_json()),
            )
        return profile

    def get(self, profile_id: str) -> RuntimeProfile | None:
        with self.storage._connect() as con:
            row = con.execute("SELECT data FROM runtime_profiles WHERE id = ?", (profile_id,)).fetchone()
        return RuntimeProfile.model_validate(json.loads(row[0])) if row else None

    def list(self) -> list[RuntimeProfile]:
        with self.storage._connect() as con:
            rows = con.execute("SELECT data FROM runtime_profiles ORDER BY rowid DESC").fetchall()
        return [RuntimeProfile.model_validate(json.loads(row[0])) for row in rows]


class ReviewFeedbackRepository:
    def __init__(self, storage: SQLiteRepository) -> None:
        self.storage = storage

    def save(self, event: ReviewFeedbackEvent) -> ReviewFeedbackEvent:
        with self.storage._connect() as con:
            con.execute("INSERT OR REPLACE INTO review_feedback (id, data) VALUES (?, ?)", (event.id, event.model_dump_json()))
        return event

    def list(self, review_job_id: str | None = None) -> list[ReviewFeedbackEvent]:
        with self.storage._connect() as con:
            rows = con.execute("SELECT data FROM review_feedback ORDER BY rowid DESC").fetchall()
        events = [ReviewFeedbackEvent.model_validate(json.loads(row[0])) for row in rows]
        if review_job_id:
            return [event for event in events if event.review_job_id == review_job_id]
        return events


class MemoryRepository:
    def __init__(self, storage: SQLiteRepository) -> None:
        self.storage = storage

    def save(self, record: MemoryRecord) -> MemoryRecord:
        with self.storage._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO memory_records (id, repository_name, memory_type, data) VALUES (?, ?, ?, ?)",
                (record.id, record.repository_name, record.memory_type, record.model_dump_json()),
            )
        return record

    def list(self, repository_name: str, memory_type: str | None = None) -> list[MemoryRecord]:
        with self.storage._connect() as con:
            rows = con.execute("SELECT data FROM memory_records WHERE repository_name = ? ORDER BY rowid DESC", (repository_name,)).fetchall()
        records = [MemoryRecord.model_validate(json.loads(row[0])) for row in rows]
        if memory_type:
            return [record for record in records if record.memory_type == memory_type]
        return records
