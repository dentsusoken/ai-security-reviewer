"""Finding-related Pydantic models."""

from typing import Optional

from pydantic import BaseModel, Field

from app.api.schemas.common import ResolutionState, Severity


class FindingSummary(BaseModel):
    """Finding summary for list view."""

    id: str
    severity: Severity
    title: str
    file_path: str = Field(alias="filePath")
    line_start: Optional[int] = Field(default=None, alias="lineStart")
    asvs_requirement_ids: list[str] = Field(alias="asvsRequirementIds")
    cwe_ids: list[str] = Field(alias="cweIds")

    model_config = {"populate_by_name": True, "use_enum_values": True}


class FindingsResponse(BaseModel):
    """Response for findings list endpoint."""

    findings: list[FindingSummary]


class Reference(BaseModel):
    """External reference link."""

    title: str
    url: str


class FindingDetail(BaseModel):
    """Full finding details."""

    id: str
    review_session_id: str = Field(alias="reviewSessionId")
    severity: Severity
    title: str
    description: str
    file_path: str = Field(alias="filePath")
    line_start: Optional[int] = Field(default=None, alias="lineStart")
    line_end: Optional[int] = Field(default=None, alias="lineEnd")
    detected_code: str = Field(alias="detectedCode")
    fix_suggestion: str = Field(alias="fixSuggestion")
    ai_explanation: str = Field(alias="aiExplanation")
    agent_source: str = Field(alias="agentSource")
    asvs_requirement_ids: list[str] = Field(alias="asvsRequirementIds")
    cwe_ids: list[str] = Field(alias="cweIds")
    resolution_state: ResolutionState = Field(alias="resolutionState")
    references: list[Reference]

    model_config = {"populate_by_name": True, "use_enum_values": True}


class Finding(BaseModel):
    """Finding model for internal use."""

    id: str
    review_session_id: str = Field(alias="reviewSessionId")
    severity: Severity
    title: str
    description: str
    file_path: str = Field(alias="filePath")
    line_start: Optional[int] = Field(default=None, alias="lineStart")
    line_end: Optional[int] = Field(default=None, alias="lineEnd")
    resolution_state: ResolutionState = Field(alias="resolutionState")

    model_config = {"populate_by_name": True, "use_enum_values": True}


class FindingStatusUpdate(BaseModel):
    """Request body for updating finding status."""

    resolution_state: ResolutionState = Field(alias="resolutionState")

    model_config = {"populate_by_name": True}
