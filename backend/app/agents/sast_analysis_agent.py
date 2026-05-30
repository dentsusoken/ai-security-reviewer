"""SAST analysis agent – combines Semgrep static analysis with AI triage.

The agent:
1. Sends code to the Semgrep Azure Function for static scanning.
2. Uses Azure OpenAI to prioritise, de-duplicate, and flag likely
   false-positives among the Semgrep findings.
3. Returns a consolidated ``ReviewResult`` compatible with the spec
   compliance agent output.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.services.openai_service import get_openai_service
from app.services.semgrep_client import SemgrepClient, SemgrepScanError, get_semgrep_client


@dataclass
class SastReviewResult:
    """Result of a SAST review."""

    id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None

    # Score summary
    overall_score: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Findings
    findings: list[dict] = field(default_factory=list)
    semgrep_errors: list[dict] = field(default_factory=list)
    semgrep_version: str = "unknown"

    # Error info
    error: str | None = None


_TRIAGE_SYSTEM_PROMPT = """\
You are a security engineer performing triage on static analysis (Semgrep) findings.
For each finding you must decide:
- Is it a true positive, likely false-positive, or needs investigation?
- Assign an adjusted severity: critical / high / medium / low / info.
- Provide a short rationale (1-2 sentences).

Return a JSON array of objects, one per finding, with the keys:
  id, is_false_positive (bool), adjusted_severity, rationale
Only output valid JSON, no markdown fences.
"""


class SastAnalysisAgent:
    """Agent that runs Semgrep and triages results with AI."""

    def __init__(self) -> None:
        self.semgrep: SemgrepClient = get_semgrep_client()
        self.openai = get_openai_service()

    async def review(
        self,
        code_files: list[dict[str, str]],
        progress_callback=None,
    ) -> SastReviewResult:
        """Run SAST analysis on the provided code files.

        Args:
            code_files: List of ``{"path": "...", "content": "..."}`` dicts.
            progress_callback: Optional async callback for progress updates.

        Returns:
            SastReviewResult with triaged findings and scores.
        """
        review_id = str(uuid.uuid4())
        started_at = datetime.now()

        result = SastReviewResult(
            id=review_id,
            status="scanning",
            started_at=started_at,
        )

        try:
            # Step 1 – Semgrep scan
            if progress_callback:
                await progress_callback(
                    "sast_scanning",
                    {"message": f"Semgrep: {len(code_files)} ファイルをスキャン中..."},
                )

            scan_result = await self.semgrep.scan(code_files)
            raw_findings = scan_result.get("findings", [])
            result.semgrep_errors = scan_result.get("errors", [])
            result.semgrep_version = scan_result.get("version", "unknown")

            if progress_callback:
                await progress_callback(
                    "sast_triaging",
                    {"message": f"AI: {len(raw_findings)} 件の検出結果をトリアージ中..."},
                )

            # Step 2 – AI triage (only if there are findings)
            if raw_findings:
                triaged = await self._triage_findings(raw_findings)
            else:
                triaged = []

            result.findings = triaged
            result.status = "completed"

            # Score calculation
            self._compute_scores(result)

        except SemgrepScanError as exc:
            result.status = "error"
            result.error = str(exc)
        except Exception as exc:
            result.status = "error"
            result.error = f"SAST analysis failed: {exc}"

        result.completed_at = datetime.now()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _triage_findings(self, findings: list[dict]) -> list[dict]:
        """Use OpenAI to triage Semgrep findings."""
        # Build a concise summary for the LLM
        summary_items = []
        for f in findings:
            summary_items.append(
                {
                    "id": f["id"],
                    "rule_id": f.get("rule_id", ""),
                    "severity": f.get("severity", ""),
                    "title": f.get("title", ""),
                    "file_path": f.get("file_path", ""),
                    "line_start": f.get("line_start", 0),
                    "code_snippet": (f.get("code_snippet", ""))[:300],
                }
            )

        import json

        user_prompt = json.dumps(summary_items, ensure_ascii=False)

        try:
            triage_result = await self.openai.chat_json(
                system_prompt=_TRIAGE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
        except Exception:
            # If AI triage fails, return findings as-is
            for f in findings:
                f["is_false_positive"] = False
                f["adjusted_severity"] = f.get("severity", "medium")
                f["rationale"] = "AI triage unavailable"
            return findings

        # Merge triage into findings
        triage_map = {t["id"]: t for t in triage_result if isinstance(t, dict)}
        for f in findings:
            triage = triage_map.get(f["id"], {})
            f["is_false_positive"] = triage.get("is_false_positive", False)
            f["adjusted_severity"] = triage.get(
                "adjusted_severity", f.get("severity", "medium")
            )
            f["rationale"] = triage.get("rationale", "")

        return findings

    @staticmethod
    def _compute_scores(result: SastReviewResult) -> None:
        """Compute severity counts and an overall score."""
        true_positives = [f for f in result.findings if not f.get("is_false_positive")]

        for f in true_positives:
            s = f.get("adjusted_severity", f.get("severity", "medium"))
            if s == "critical":
                result.critical_count += 1
            elif s == "high":
                result.high_count += 1
            elif s == "medium":
                result.medium_count += 1
            elif s == "low":
                result.low_count += 1

        # Score: start at 100, deduct per severity
        score = 100
        score -= result.critical_count * 15
        score -= result.high_count * 10
        score -= result.medium_count * 5
        score -= result.low_count * 2
        result.overall_score = max(0, min(100, score))


# Singleton
_agent: SastAnalysisAgent | None = None


def get_sast_analysis_agent() -> SastAnalysisAgent:
    """Get or create SastAnalysisAgent singleton."""
    global _agent
    if _agent is None:
        _agent = SastAnalysisAgent()
    return _agent
