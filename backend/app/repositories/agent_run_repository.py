"""Agent run state repository.

This module manages the execution state of AI agents during security reviews.
Supports in-memory storage for MVP with planned Cosmos DB integration.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AgentRunStatus(str, Enum):
    """Status of an agent run."""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentRun:
    """Represents a single agent execution within a review."""

    id: str
    review_id: str
    agent_name: str
    status: AgentRunStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress_percent: int = 0
    current_activity: str | None = None
    error_message: str | None = None
    result_summary: dict[str, Any] | None = None
    logs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "reviewId": self.review_id,
            "agentName": self.agent_name,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "progressPercent": self.progress_percent,
            "currentActivity": self.current_activity,
            "errorMessage": self.error_message,
            "resultSummary": self.result_summary,
            "logs": self.logs,
        }


class AgentRunRepository:
    """Repository for managing agent run states.

    MVP implementation uses in-memory storage.
    Production should use Cosmos DB for persistence.
    """

    def __init__(self):
        """Initialize the repository."""
        self._runs: dict[str, AgentRun] = {}
        self._runs_by_review: dict[str, list[str]] = {}
        self._lock = asyncio.Lock()

    async def create(self, agent_run: AgentRun) -> AgentRun:
        """Create a new agent run record.

        Args:
            agent_run: AgentRun instance to store

        Returns:
            The stored AgentRun
        """
        async with self._lock:
            self._runs[agent_run.id] = agent_run

            # Index by review ID
            if agent_run.review_id not in self._runs_by_review:
                self._runs_by_review[agent_run.review_id] = []
            self._runs_by_review[agent_run.review_id].append(agent_run.id)

        return agent_run

    async def get(self, run_id: str) -> AgentRun | None:
        """Get an agent run by ID.

        Args:
            run_id: Agent run ID

        Returns:
            AgentRun or None if not found
        """
        return self._runs.get(run_id)

    async def get_by_review(self, review_id: str) -> list[AgentRun]:
        """Get all agent runs for a review.

        Args:
            review_id: Review session ID

        Returns:
            List of AgentRun instances
        """
        run_ids = self._runs_by_review.get(review_id, [])
        return [self._runs[rid] for rid in run_ids if rid in self._runs]

    async def update(
        self,
        run_id: str,
        *,
        status: AgentRunStatus | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        progress_percent: int | None = None,
        current_activity: str | None = None,
        error_message: str | None = None,
        result_summary: dict[str, Any] | None = None,
    ) -> AgentRun | None:
        """Update an agent run.

        Args:
            run_id: Agent run ID
            **kwargs: Fields to update

        Returns:
            Updated AgentRun or None if not found
        """
        async with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return None

            if status is not None:
                run.status = status
            if started_at is not None:
                run.started_at = started_at
            if completed_at is not None:
                run.completed_at = completed_at
            if progress_percent is not None:
                run.progress_percent = progress_percent
            if current_activity is not None:
                run.current_activity = current_activity
            if error_message is not None:
                run.error_message = error_message
            if result_summary is not None:
                run.result_summary = result_summary

            return run

    async def add_log(self, run_id: str, log_message: str) -> bool:
        """Add a log message to an agent run.

        Args:
            run_id: Agent run ID
            log_message: Log message to add

        Returns:
            True if log was added, False if run not found
        """
        async with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return False

            run.logs.append(f"[{datetime.now().isoformat()}] {log_message}")
            return True

    async def start_run(self, run_id: str) -> AgentRun | None:
        """Mark an agent run as started.

        Args:
            run_id: Agent run ID

        Returns:
            Updated AgentRun or None
        """
        return await self.update(
            run_id,
            status=AgentRunStatus.RUNNING,
            started_at=datetime.now(),
            current_activity="開始中...",
        )

    async def complete_run(
        self,
        run_id: str,
        result_summary: dict[str, Any] | None = None,
    ) -> AgentRun | None:
        """Mark an agent run as completed.

        Args:
            run_id: Agent run ID
            result_summary: Optional result summary

        Returns:
            Updated AgentRun or None
        """
        return await self.update(
            run_id,
            status=AgentRunStatus.COMPLETED,
            completed_at=datetime.now(),
            progress_percent=100,
            current_activity="完了",
            result_summary=result_summary,
        )

    async def fail_run(
        self,
        run_id: str,
        error_message: str,
    ) -> AgentRun | None:
        """Mark an agent run as failed.

        Args:
            run_id: Agent run ID
            error_message: Error description

        Returns:
            Updated AgentRun or None
        """
        return await self.update(
            run_id,
            status=AgentRunStatus.FAILED,
            completed_at=datetime.now(),
            error_message=error_message,
            current_activity="エラー発生",
        )

    async def cancel_run(self, run_id: str) -> AgentRun | None:
        """Cancel an agent run.

        Args:
            run_id: Agent run ID

        Returns:
            Updated AgentRun or None
        """
        return await self.update(
            run_id,
            status=AgentRunStatus.CANCELLED,
            completed_at=datetime.now(),
            current_activity="キャンセル済み",
        )

    async def get_active_runs(self) -> list[AgentRun]:
        """Get all currently running agent runs.

        Returns:
            List of running AgentRun instances
        """
        return [
            run for run in self._runs.values()
            if run.status in (AgentRunStatus.WAITING, AgentRunStatus.RUNNING)
        ]

    async def get_stats(self) -> dict[str, int]:
        """Get statistics about agent runs.

        Returns:
            Dictionary with status counts
        """
        stats = {status.value: 0 for status in AgentRunStatus}
        for run in self._runs.values():
            stats[run.status.value] += 1
        return stats

    async def delete_by_review(self, review_id: str) -> int:
        """Delete all agent runs for a review.

        Args:
            review_id: Review session ID

        Returns:
            Number of deleted runs
        """
        async with self._lock:
            run_ids = self._runs_by_review.get(review_id, [])
            for rid in run_ids:
                self._runs.pop(rid, None)

            if review_id in self._runs_by_review:
                del self._runs_by_review[review_id]

            return len(run_ids)


# Singleton instance
_repository: AgentRunRepository | None = None


def get_agent_run_repository() -> AgentRunRepository:
    """Get or create AgentRunRepository singleton."""
    global _repository
    if _repository is None:
        _repository = AgentRunRepository()
    return _repository
