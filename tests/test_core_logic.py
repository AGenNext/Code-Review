from codereviewer.core.logic import recommendation_for_severity, summarize_findings
from codereviewer.core.models import Finding, RecommendationType, Severity


def test_recommendation_mapping() -> None:
    assert recommendation_for_severity(Severity.critical) == RecommendationType.must_fix
    assert recommendation_for_severity(Severity.medium) == RecommendationType.should_fix
    assert recommendation_for_severity(Severity.low) == RecommendationType.consider


def test_summary_scoring() -> None:
    findings = [
        Finding(title="a", description="a", severity=Severity.high, recommendation=RecommendationType.must_fix, file_path="a.py"),
        Finding(title="b", description="b", severity=Severity.low, recommendation=RecommendationType.consider, file_path="b.py"),
    ]
    summary = summarize_findings(findings)
    assert summary.total_findings == 2
    assert summary.risk_score == 25
