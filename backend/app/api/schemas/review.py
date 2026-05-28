"""Review-related Pydantic models."""

from datetime import datetime

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
    repo_url: str | None = Field(default=None, alias="repoUrl")
    branch: str | None = None
    code: str | None = None
    filename: str | None = None
    language: str | None = None
    target_url: str | None = Field(default=None, alias="targetUrl")
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
    progress_percent: int | None = Field(default=None, alias="progressPercent")
    current_activity: str | None = Field(default=None, alias="currentActivity")
    details: list[str] | None = None

    model_config = {"populate_by_name": True, "use_enum_values": True}


class ReviewDetail(BaseModel):
    """Full review session details."""

    id: str
    status: ReviewStatus
    input_type: InputType = Field(alias="inputType")
    repo_url: str | None = Field(default=None, alias="repoUrl")
    branch: str | None = None
    perspectives: list[Perspective]
    depth: ReviewDepth
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    duration_ms: int | None = Field(default=None, alias="durationMs")
    score_summary: ScoreSummary | None = Field(default=None, alias="scoreSummary")
    perspective_scores: list[PerspectiveScore] | None = Field(
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
