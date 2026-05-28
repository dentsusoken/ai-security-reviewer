"""Security compliance agent using Azure OpenAI."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.services.github_service import CodeFile, RepoInfo
from app.services.openai_service import get_openai_service


@dataclass
class ReviewResult:
    """Result of a security review."""

    id: str
    repo_info: RepoInfo
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    # Score summary
    overall_score: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Perspective scores
    perspective_scores: list[dict] = field(default_factory=list)

    # Findings
    findings: list[dict] = field(default_factory=list)

    # Error info
    error: Optional[str] = None


class SpecComplianceAgent:
    """Agent for OWASP ASVS compliance checking using AI."""

    def __init__(self):
        """Initialize the agent."""
        self.openai_service = get_openai_service()

    async def review(
        self,
        repo_info: RepoInfo,
        code_files: list[CodeFile],
        progress_callback=None,
    ) -> ReviewResult:
        """Perform security review on code files.

        Args:
            repo_info: Repository metadata
            code_files: List of code files to review
            progress_callback: Optional async callback for progress updates

        Returns:
            ReviewResult with findings and scores
        """
        review_id = str(uuid.uuid4())
        started_at = datetime.now()

        result = ReviewResult(
            id=review_id,
            repo_info=repo_info,
            status="analyzing",
            started_at=started_at,
        )

        try:
            # Prepare code for analysis
            code_for_analysis = [
                {"path": f.path, "content": f.content}
                for f in code_files
            ]

            if progress_callback:
                await progress_callback("analyzing_code", {
                    "message": f"SpecComplianceAgent: {len(code_files)} ファイルを解析中...",
                })

            # Call AI for analysis
            ai_result = await self.openai_service.analyze_code_security(
                code_for_analysis,
                progress_callback=progress_callback,
            )

            # Process results
            result = self._process_ai_result(result, ai_result)
            result.status = "completed"

        except Exception as e:
            result.status = "error"
            result.error = str(e)

        # Calculate duration
        result.completed_at = datetime.now()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )

        return result

    def _process_ai_result(
        self,
        result: ReviewResult,
        ai_result: dict[str, Any],
    ) -> ReviewResult:
        """Process AI analysis result into ReviewResult."""
        # Extract summary
        summary = ai_result.get("summary", {})
        result.overall_score = summary.get("overall_score", 70)
        result.critical_count = summary.get("critical_count", 0)
        result.high_count = summary.get("high_count", 0)
        result.medium_count = summary.get("medium_count", 0)
        result.low_count = summary.get("low_count", 0)

        # Extract perspective scores
        result.perspective_scores = ai_result.get("perspective_scores", [])

        # Process findings
        raw_findings = ai_result.get("findings", [])
        processed_findings = []

        for i, finding in enumerate(raw_findings):
            processed_findings.append({
                "id": finding.get("id", f"f{i+1}"),
                "severity": finding.get("severity", "medium"),
                "title": finding.get("title", "セキュリティの問題"),
                "description": finding.get("description", ""),
                "file_path": finding.get("file_path", "unknown"),
                "line_start": finding.get("line_start"),
                "line_end": finding.get("line_end"),
                "code_snippet": finding.get("code_snippet", ""),
                "asvs_requirements": finding.get("asvs_requirements", []),
                "cwe_ids": finding.get("cwe_ids", []),
                "remediation": finding.get("remediation", ""),
                "fixed_code": finding.get("fixed_code", ""),
            })

        result.findings = processed_findings

        return result


# Singleton instance
_agent: Optional[SpecComplianceAgent] = None


def get_spec_compliance_agent() -> SpecComplianceAgent:
    """Get or create SpecComplianceAgent singleton."""
    global _agent
    if _agent is None:
        _agent = SpecComplianceAgent()
    return _agent
