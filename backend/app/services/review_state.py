"""In-memory review state management for MVP."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.agents.spec_compliance_agent import ReviewResult


@dataclass
class ReviewState:
    """State of a review session."""

    id: str
    status: str  # queued, running, completed, error
    repo_url: str
    branch: str | None = None
    input_type: str = "github"
    perspectives: list[str] = field(default_factory=lambda: ["spec_compliance"])
    depth: str = "standard"

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None

    # Progress
    progress_percent: int = 0
    progress_message: str = ""

    # Results
    result: ReviewResult | None = None
    error: str | None = None


class ReviewStateManager:
    """Manages review states in memory."""

    def __init__(self):
        self._reviews: dict[str, ReviewState] = {}
        self._sse_queues: dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def create_review(
        self,
        review_id: str,
        repo_url: str,
        branch: str | None = None,
        perspectives: list[str] | None = None,
        depth: str = "standard",
    ) -> ReviewState:
        """Create a new review state."""
        async with self._lock:
            state = ReviewState(
                id=review_id,
                status="queued",
                repo_url=repo_url,
                branch=branch,
                perspectives=perspectives or ["spec_compliance"],
                depth=depth,
            )
            self._reviews[review_id] = state
            self._sse_queues[review_id] = asyncio.Queue()
            return state

    async def get_review(self, review_id: str) -> ReviewState | None:
        """Get review state by ID."""
        return self._reviews.get(review_id)

    async def update_review(
        self,
        review_id: str,
        **updates: Any,
    ) -> ReviewState | None:
        """Update review state fields."""
        async with self._lock:
            state = self._reviews.get(review_id)
            if state:
                for key, value in updates.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
            return state

    async def set_result(
        self,
        review_id: str,
        result: ReviewResult,
    ) -> ReviewState | None:
        """Set review result and mark as completed."""
        async with self._lock:
            state = self._reviews.get(review_id)
            if state:
                state.result = result
                state.status = "completed"
                state.completed_at = datetime.now()
                if state.started_at:
                    state.duration_ms = int(
                        (state.completed_at - state.started_at).total_seconds() * 1000
                    )
                state.progress_percent = 100
                state.progress_message = "完了"
            return state

    async def set_error(
        self,
        review_id: str,
        error: str,
    ) -> ReviewState | None:
        """Set review error and mark as failed."""
        async with self._lock:
            state = self._reviews.get(review_id)
            if state:
                state.error = error
                state.status = "error"
                state.completed_at = datetime.now()
            return state

    def get_sse_queue(self, review_id: str) -> asyncio.Queue | None:
        """Get SSE event queue for a review."""
        return self._sse_queues.get(review_id)

    async def send_sse_event(
        self,
        review_id: str,
        event_type: str,
        data: dict,
    ) -> None:
        """Send an SSE event to the queue."""
        queue = self._sse_queues.get(review_id)
        if queue:
            await queue.put(
                {
                    "event": event_type,
                    "data": data,
                }
            )

    async def close_sse_queue(self, review_id: str) -> None:
        """Close SSE queue for a review."""
        queue = self._sse_queues.get(review_id)
        if queue:
            await queue.put(None)  # Signal end of stream

    def list_reviews(self) -> list[ReviewState]:
        """List all reviews."""
        return list(self._reviews.values())

    def get_completed_reviews(self) -> list[ReviewState]:
        """Get all completed reviews, sorted by completion time (newest first)."""
        completed = [
            r for r in self._reviews.values() if r.status == "completed" and r.result is not None
        ]
        # Sort by completed_at descending (newest first)
        return sorted(
            completed,
            key=lambda r: r.completed_at or r.created_at,
            reverse=True,
        )

    def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics from completed reviews."""
        completed = self.get_completed_reviews()

        if not completed:
            return {
                "total_reviews": 0,
                "total_findings": 0,
                "resolved_findings": 0,
                "average_score": 0,
            }

        total_findings = 0
        total_score = 0

        for review in completed:
            if review.result:
                total_findings += len(review.result.findings)
                total_score += review.result.overall_score

        return {
            "total_reviews": len(completed),
            "total_findings": total_findings,
            "resolved_findings": 0,  # MVP: no resolution tracking yet
            "average_score": total_score // len(completed) if completed else 0,
        }

    def review_to_history_format(self, state: ReviewState) -> dict:
        """Convert ReviewState to history response format."""
        result = state.result

        # Extract repo URL
        repo_url = state.repo_url

        # Calculate score summary
        if result:
            score_summary = {
                "overall": result.overall_score,
                "critical": result.critical_count,
                "high": result.high_count,
                "medium": result.medium_count,
                "low": result.low_count,
            }
        else:
            score_summary = {
                "overall": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            }

        return {
            "id": state.id,
            "repoUrl": repo_url,
            "branch": state.branch or "main",
            "inputType": state.input_type,
            "perspectives": state.perspectives,
            "startedAt": state.started_at.isoformat()
            if state.started_at
            else state.created_at.isoformat(),
            "durationMs": state.duration_ms or 0,
            "scoreSummary": score_summary,
        }


# Singleton instance
_manager: ReviewStateManager | None = None


def get_review_manager() -> ReviewStateManager:
    """Get or create ReviewStateManager singleton."""
    global _manager
    if _manager is None:
        _manager = ReviewStateManager()
    return _manager
