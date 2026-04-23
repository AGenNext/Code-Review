from codereviewer.core.models import Finding, RecommendationType, ReviewSummary, Severity


SEVERITY_WEIGHTS = {
    Severity.critical: 30,
    Severity.high: 20,
    Severity.medium: 10,
    Severity.low: 5,
    Severity.info: 1,
}


def recommendation_for_severity(severity: Severity) -> RecommendationType:
    if severity in (Severity.critical, Severity.high):
        return RecommendationType.must_fix
    if severity == Severity.medium:
        return RecommendationType.should_fix
    return RecommendationType.consider


def summarize_findings(findings: list[Finding]) -> ReviewSummary:
    by_severity = {sev: 0 for sev in Severity}
    for finding in findings:
        by_severity[finding.severity] += 1

    risk_score = sum(SEVERITY_WEIGHTS[f.severity] for f in findings)
    return ReviewSummary(total_findings=len(findings), by_severity=by_severity, risk_score=risk_score)
