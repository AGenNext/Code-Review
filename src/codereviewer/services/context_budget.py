from __future__ import annotations

from dataclasses import dataclass

from codereviewer.core.models import FileChangeContext


@dataclass
class ContextChunk:
    path: str
    content: str
    priority: int


class ContextBudgetManager:
    """Budget-aware context selection for review prompts."""

    def __init__(self, max_chars: int = 12_000) -> None:
        self.max_chars = max_chars

    def select_chunks(self, changes: list[FileChangeContext]) -> list[ContextChunk]:
        chunks = [ContextChunk(path=change.path, content=change.patch, priority=self._priority(change.path)) for change in changes]
        chunks.sort(key=lambda item: item.priority, reverse=True)

        selected: list[ContextChunk] = []
        used = 0
        for chunk in chunks:
            part = chunk.content[: max(0, self.max_chars - used)]
            if not part:
                continue
            selected.append(ContextChunk(path=chunk.path, content=part, priority=chunk.priority))
            used += len(part)
            if used >= self.max_chars:
                break
        return selected

    def _priority(self, path: str) -> int:
        if any(token in path for token in ("auth", "security", "secret", "config")):
            return 5
        if path.endswith((".py", ".ts", ".js")):
            return 4
        return 2
