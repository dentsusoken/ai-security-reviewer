"""Review-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.api.schemas.common import (
    AgentName,
    AgentStatus,
    InputType,
    Perspective,
    ReviewDepth,
    ReviewStatus,
)


class ReviewCreateRequest(BaseModel):
    """Request body for creating a new review."""

    input_type: InputType = Field(alias="inputType")
    repo_url: Optional[str] = Field(default=None, alias="repoUrl")
    branch: Optional[str] = None
    code: Optional[str] = None
    filename: Optional[str] = None
    language: Optional[str] = None
    target_url: Optional[str] = Field(default=None, alias="targetUrl")
    perspectives: list[Perspective]
    depth: ReviewDepth

    model_config = {"populate_by_name": True}


class ReviewCreateResponse(BaseModel):
    """Response after creating a review."""

    review_session_id: str = Field(alias="reviewSessionId")
    status: ReviewStatus

    model_config = {"populate_by_name": True, "use_enum_values": True}


class ScoreSummary(BaseModel):
    """Score summary with severity counts."""

    overall: int
    critical: int
    high: int
    medium: int
    low: int


class PerspectiveScore(BaseModel):
    """Score for a specific ASVS category."""

    category: str
    percentage: int


class AgentState(BaseModel):
    """Agent execution state."""

    agent_name: AgentName = Field(alias="agentName")
    status: AgentStatus
    progress_percent: Optional[int] = Field(default=None, alias="progressPercent")
    current_activity: Optional[str] = Field(default=None, alias="currentActivity")
    details: Optional[list[str]] = None

    model_config = {"populate_by_name": True, "use_enum_values": True}


class ReviewDetail(BaseModel):
    """Full review session details."""

    id: str
    status: ReviewStatus
    input_type: InputType = Field(alias="inputType")
    repo_url: Optional[str] = Field(default=None, alias="repoUrl")
    branch: Optional[str] = None
    perspectives: list[Perspective]
    depth: ReviewDepth
    started_at: Optional[datetime] = Field(default=None, alias="startedAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    duration_ms: Optional[int] = Field(default=None, alias="durationMs")
    score_summary: Optional[ScoreSummary] = Field(default=None, alias="scoreSummary")
    perspective_scores: Optional[list[PerspectiveScore]] = Field(
        default=None, alias="perspectiveScores"
    )

    model_config = {"populate_by_name": True, "use_enum_values": True}


class HistoryReview(BaseModel):
    """Review item for history list."""

    id: str
    repo_url: str = Field(alias="repoUrl")
    branch: str
    input_type: InputType = Field(alias="inputType")
    perspectives: list[Perspective]
    started_at: datetime = Field(alias="startedAt")
    duration_ms: int = Field(alias="durationMs")
    score_summary: ScoreSummary = Field(alias="scoreSummary")

    model_config = {"populate_by_name": True, "use_enum_values": True}


class HistoryResponse(BaseModel):
    """Response for history endpoint."""

    reviews: list[HistoryReview]
    total_count: int = Field(alias="totalCount")

    model_config = {"populate_by_name": True}


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    total_reviews: int = Field(alias="totalReviews")
    total_findings: int = Field(alias="totalFindings")
    resolved_findings: int = Field(alias="resolvedFindings")
    average_score: int = Field(alias="averageScore")
    recent_reviews: list[HistoryReview] = Field(alias="recentReviews")

    model_config = {"populate_by_name": True}
