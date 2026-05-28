"""Common schema definitions."""

from enum import StrEnum


class InputType(StrEnum):
    """Review input type."""

    GITHUB = "github"
    CODE = "code"
    URL = "url"


class Perspective(StrEnum):
    """Review perspective type."""

    ASVS = "asvs"
    SAST = "sast"
    DAST = "dast"


class ReviewDepth(StrEnum):
    """Review depth level."""

    QUICK = "quick"
    STANDARD = "standard"
    DETAILED = "detailed"


class Severity(StrEnum):
    """Finding severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewStatus(StrEnum):
    """Review session status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ResolutionState(StrEnum):
    """Finding resolution state."""

    OPEN = "open"
    RESOLVED = "resolved"


class AgentName(StrEnum):
    """Agent name constants."""

    SPEC_COMPLIANCE = "SpecComplianceAgent"
    SAST_ANALYSIS = "SastAnalysisAgent"
    REPORT_SYNTHESIZER = "ReportSynthesizerAgent"


class AgentStatus(StrEnum):
    """Agent execution status."""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
