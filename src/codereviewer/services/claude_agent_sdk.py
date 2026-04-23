from codereviewer.core.logic import recommendation_for_severity
from codereviewer.core.models import FileChangeContext, Finding, Severity


class ClaudeAgentSDKReviewer:
    """Claude Agent SDK adapter boundary.

    Replace `_analyze_changes` internals with official SDK orchestration in deployment environments.
    """

    def analyze(self, changes: list[FileChangeContext]) -> list[Finding]:
        findings: list[Finding] = []
        for change in changes:
            findings.extend(self._analyze_changes(change))
        return findings

    def _analyze_changes(self, change: FileChangeContext) -> list[Finding]:
        patch_lower = change.patch.lower()
        result: list[Finding] = []
        if "todo" in patch_lower:
            severity = Severity.low
            result.append(
                Finding(
                    title="TODO left in code",
                    description="Detected TODO in submitted patch; convert to tracked ticket or complete before merge.",
                    severity=severity,
                    recommendation=recommendation_for_severity(severity),
                    file_path=change.path,
                )
            )
        if "password" in patch_lower or "secret" in patch_lower:
            severity = Severity.critical
            result.append(
                Finding(
                    title="Potential credential exposure",
                    description="Potential secret-like value found in changes.",
                    severity=severity,
                    recommendation=recommendation_for_severity(severity),
                    file_path=change.path,
                )
            )
        return result
