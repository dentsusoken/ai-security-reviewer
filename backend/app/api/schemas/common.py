"""Common schema definitions."""

from enum import Enum


class InputType(str, Enum):
    """Review input type."""

    GITHUB = "github"
    CODE = "code"
    URL = "url"


class Perspective(str, Enum):
    """Review perspective type."""

    ASVS = "asvs"
    SAST = "sast"
    DAST = "dast"


class ReviewDepth(str, Enum):
    """Review depth level."""

    QUICK = "quick"
    STANDARD = "standard"
    DETAILED = "detailed"


class Severity(str, Enum):
    """Finding severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewStatus(str, Enum):
    """Review session status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ResolutionState(str, Enum):
    """Finding resolution state."""

    OPEN = "open"
    RESOLVED = "resolved"


class AgentName(str, Enum):
    """Agent name constants."""

    SPEC_COMPLIANCE = "SpecComplianceAgent"
    SAST_ANALYSIS = "SastAnalysisAgent"
    REPORT_SYNTHESIZER = "ReportSynthesizerAgent"


class AgentStatus(str, Enum):
    """Agent execution status."""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
