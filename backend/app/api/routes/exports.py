"""Export endpoints for review reports."""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.data.mock_data import DEMO_REVIEW_ID, MOCK_REVIEWS, MOCK_FINDINGS_LIST
from app.services.excel_export_service import create_excel_report, format_duration, format_datetime
from app.services.review_state import get_review_manager

router = APIRouter()


def _prepare_review_data(review_state) -> dict:
    """Prepare review data for export from ReviewState."""
    result = review_state.result

    repo_name = "-"
    if result and result.repo_info:
        repo_name = f"{result.repo_info.owner}/{result.repo_info.repo}"
    elif review_state.repo_url:
        # Extract from URL
        parts = review_state.repo_url.rstrip("/").split("/")
        if len(parts) >= 2:
            repo_name = f"{parts[-2]}/{parts[-1]}"

    # Perspective scores
    perspective_scores = []
    if result and result.perspective_scores:
        perspective_scores = result.perspective_scores
    else:
        # Default perspective scores
        score = result.overall_score if result else 70
        perspective_scores = [
            {"name": "Spec Compliance (ASVS)", "score": score, "rating": "B" if score >= 60 else "C"},
        ]

    return {
        "repo_name": repo_name,
        "branch": review_state.branch or "main",
        "executed_at": format_datetime(review_state.completed_at or review_state.created_at),
        "duration": format_duration(review_state.duration_ms) if review_state.duration_ms else "-",
        "overall_score": result.overall_score if result else 0,
        "critical_count": result.critical_count if result else 0,
        "high_count": result.high_count if result else 0,
        "medium_count": result.medium_count if result else 0,
        "low_count": result.low_count if result else 0,
        "perspective_scores": perspective_scores,
    }


def _prepare_findings(review_state) -> list[dict]:
    """Prepare findings list for export from ReviewState."""
    if not review_state.result:
        return []

    findings = review_state.result.findings or []
    processed_findings = []

    for idx, finding in enumerate(findings, start=1):
        processed = {
            "id": finding.get("id", f"F{idx:03d}"),
            "title": finding.get("title", "Unknown Issue"),
            "severity": finding.get("severity", "medium"),
            "location": finding.get("location", {}),
            "asvs_id": finding.get("asvs_id", "-"),
            "cwe_id": finding.get("cwe_id", "-"),
            "source_agent": finding.get("source_agent", "SpecComplianceAgent"),
            "status": finding.get("status", "open"),
            "description": finding.get("description", ""),
            "explanation": finding.get("explanation", finding.get("description", "")),
            "vulnerable_code": finding.get("vulnerable_code", finding.get("code_snippet", "")),
            "ai_explanation": finding.get("ai_explanation", ""),
            "remediation": finding.get("remediation", finding.get("fix_suggestion", "")),
            "references": finding.get("references", []),
        }
        processed_findings.append(processed)

    return processed_findings


def _get_mock_review_data(review_id: str) -> tuple[dict, list[dict]]:
    """Get mock data for demo review."""
    mock_review = MOCK_REVIEWS.get(review_id, MOCK_REVIEWS.get(DEMO_REVIEW_ID, {}))

    # Extract repo name from mock data
    repo_url = mock_review.get("repoUrl", "https://github.com/example/my-bi-tool")
    parts = repo_url.rstrip("/").split("/")
    repo_name = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else "example/unknown"

    # Get score summary
    score_summary = mock_review.get("scoreSummary", {})

    review_data = {
        "repo_name": repo_name,
        "branch": mock_review.get("branch", "main"),
        "executed_at": mock_review.get("completedAt", "2026年5月27日 10:00:00"),
        "duration": f"{mock_review.get('durationMs', 0) // 60000}分{(mock_review.get('durationMs', 0) % 60000) // 1000}秒",
        "overall_score": score_summary.get("overall", 75),
        "critical_count": score_summary.get("critical", 1),
        "high_count": score_summary.get("high", 2),
        "medium_count": score_summary.get("medium", 2),
        "low_count": score_summary.get("low", 1),
        "perspective_scores": [
            {"name": ps.get("category", "Unknown"), "score": ps.get("percentage", 0), "rating": "A" if ps.get("percentage", 0) >= 80 else "B" if ps.get("percentage", 0) >= 60 else "C"}
            for ps in mock_review.get("perspectiveScores", [])
        ],
    }

    # Get findings from mock data - MOCK_FINDINGS_LIST is a list, not a dict
    findings = []

    for idx, f in enumerate(MOCK_FINDINGS_LIST, start=1):
        findings.append({
            "id": f.get("id", f"F{idx:03d}"),
            "title": f.get("title", "Unknown Issue"),
            "severity": f.get("severity", "medium"),
            "location": {"file": f.get("filePath", "-"), "line": f.get("lineStart", 0)},
            "asvs_id": ", ".join(f.get("asvsRequirementIds", [])) or "-",
            "cwe_id": ", ".join(f.get("cweIds", [])) or "-",
            "source_agent": "SpecComplianceAgent",
            "status": "open",
            "description": f"Security issue detected: {f.get('title', 'Unknown')}",
            "explanation": f"This finding relates to security best practices.",
            "vulnerable_code": "",
            "ai_explanation": f"This finding relates to OWASP ASVS requirements and CWE standards.",
            "remediation": "Apply secure coding practices and follow OWASP guidelines.",
            "references": [
                {"title": "OWASP ASVS", "url": "https://owasp.org/www-project-application-security-verification-standard/"},
            ],
        })

    return review_data, findings


@router.post("/reviews/{review_id}/export/excel")
async def export_review_to_excel(review_id: str) -> Response:
    """Export review results to Excel format.

    Returns an Excel file (.xlsx) with three sheets:
    - Summary: Basic info, overall score, severity counts, perspective scores
    - Findings List: Table of all findings
    - Details: Detailed information for each finding
    """
    manager = get_review_manager()
    review_state = await manager.get_review(review_id)

    # Check if it's a real review
    if review_state and review_state.result:
        review_data = _prepare_review_data(review_state)
        findings = _prepare_findings(review_state)
    elif review_id == DEMO_REVIEW_ID or review_id in MOCK_REVIEWS:
        # Use mock data for demo
        review_data, findings = _get_mock_review_data(review_id)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Review not found: {review_id}"
        )

    # Generate Excel file
    excel_bytes = create_excel_report(review_data, findings)

    # Create filename
    safe_repo_name = review_data.get("repo_name", "review").replace("/", "-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"security-review-{safe_repo_name}-{timestamp}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
