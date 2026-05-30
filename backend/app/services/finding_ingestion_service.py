"""Finding ingestion service.

Converts raw findings from different sources (Semgrep SAST, ASVS AI review)
into a unified finding schema and persists them via the findings repository.
"""

import uuid
from datetime import datetime
from typing import Any

from app.repositories.findings_repository import FindingsRepository


class FindingIngestionService:
    """Normalise and persist findings from multiple analysis sources."""

    def __init__(self) -> None:
        self.repo = FindingsRepository()

    async def ingest_sast_findings(
        self,
        session_id: str,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Ingest SAST (Semgrep) findings.

        Args:
            session_id: Review session this scan belongs to.
            findings: Normalised findings from the SastAnalysisAgent.

        Returns:
            List of persisted finding documents.
        """
        docs = []
        for f in findings:
            doc = {
                "id": str(uuid.uuid4()),
                "reviewSessionId": session_id,
                "source": "semgrep",
                "perspective": "SAST",
                "ruleId": f.get("rule_id", ""),
                "severity": f.get("adjusted_severity", f.get("severity", "medium")),
                "title": f.get("title", ""),
                "description": f.get("description", ""),
                "filePath": f.get("file_path", ""),
                "lineStart": f.get("line_start"),
                "lineEnd": f.get("line_end"),
                "codeSnippet": f.get("code_snippet", ""),
                "cweIds": f.get("cwe_ids", []),
                "owaspIds": f.get("owasp_ids", []),
                "confidence": f.get("confidence", "MEDIUM"),
                "isFalsePositive": f.get("is_false_positive", False),
                "triageRationale": f.get("rationale", ""),
                "references": f.get("references", []),
                "resolutionState": "open",
                "createdAt": datetime.utcnow().isoformat(),
            }
            docs.append(doc)

        return await self.repo.create_many(docs)

    async def ingest_asvs_findings(
        self,
        session_id: str,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Ingest ASVS AI review findings.

        Args:
            session_id: Review session.
            findings: Findings from the SpecComplianceAgent.

        Returns:
            List of persisted finding documents.
        """
        docs = []
        for f in findings:
            doc = {
                "id": str(uuid.uuid4()),
                "reviewSessionId": session_id,
                "source": "openai",
                "perspective": "ASVS",
                "ruleId": "",
                "severity": f.get("severity", "medium"),
                "title": f.get("title", ""),
                "description": f.get("description", ""),
                "filePath": f.get("file_path", ""),
                "lineStart": f.get("line_start"),
                "lineEnd": f.get("line_end"),
                "codeSnippet": f.get("code_snippet", ""),
                "cweIds": f.get("cwe_ids", []),
                "owaspIds": [],
                "asvsRequirements": f.get("asvs_requirements", []),
                "remediation": f.get("remediation", ""),
                "fixedCode": f.get("fixed_code", ""),
                "isFalsePositive": False,
                "resolutionState": "open",
                "createdAt": datetime.utcnow().isoformat(),
            }
            docs.append(doc)

        return await self.repo.create_many(docs)


_service: FindingIngestionService | None = None


def get_finding_ingestion_service() -> FindingIngestionService:
    """Get or create singleton."""
    global _service
    if _service is None:
        _service = FindingIngestionService()
    return _service
