"""ASVS evidence mapping formatter.

This module maps security findings to OWASP ASVS requirements
and provides standardized evidence formatting.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ASVSRequirement:
    """OWASP ASVS requirement definition."""

    id: str  # e.g., "V1.1.1"
    level: int  # 1, 2, or 3
    chapter: str  # e.g., "V1 Architecture"
    section: str  # e.g., "1.1 Secure Software Development Lifecycle"
    requirement: str  # Full requirement text
    cwe_ids: list[int]  # Related CWE IDs


@dataclass
class EvidenceRef:
    """Reference to evidence in source code."""

    file_path: str
    line_start: int
    line_end: int | None
    code_snippet: str
    context: str | None = None


@dataclass
class MappedFinding:
    """A finding mapped to ASVS requirements with evidence."""

    id: str
    severity: str
    title: str
    description: str
    asvs_requirements: list[ASVSRequirement]
    cwe_ids: list[int]
    evidence: list[EvidenceRef]
    remediation: str
    fixed_code: str | None = None


# ASVS Chapter definitions (subset for common security issues)
ASVS_CHAPTERS = {
    "V1": "Architecture, Design and Threat Modeling",
    "V2": "Authentication",
    "V3": "Session Management",
    "V4": "Access Control",
    "V5": "Validation, Sanitization and Encoding",
    "V6": "Stored Cryptography",
    "V7": "Error Handling and Logging",
    "V8": "Data Protection",
    "V9": "Communication",
    "V10": "Malicious Code",
    "V11": "Business Logic",
    "V12": "Files and Resources",
    "V13": "API and Web Service",
    "V14": "Configuration",
}

# Common ASVS requirements mapped to security patterns
ASVS_REQUIREMENTS_DB = {
    # Authentication
    "V2.1.1": ASVSRequirement(
        id="V2.1.1",
        level=1,
        chapter="V2 Authentication",
        section="2.1 Password Security",
        requirement="Verify that user set passwords are at least 12 characters in length.",
        cwe_ids=[521],
    ),
    "V2.1.5": ASVSRequirement(
        id="V2.1.5",
        level=1,
        chapter="V2 Authentication",
        section="2.1 Password Security",
        requirement="Verify users can change their password.",
        cwe_ids=[620],
    ),
    "V2.2.1": ASVSRequirement(
        id="V2.2.1",
        level=1,
        chapter="V2 Authentication",
        section="2.2 General Authenticator Security",
        requirement="Verify anti-automation controls for credential stuffing, brute force.",
        cwe_ids=[307],
    ),
    # Session Management
    "V3.2.1": ASVSRequirement(
        id="V3.2.1",
        level=1,
        chapter="V3 Session Management",
        section="3.2 Session Binding",
        requirement="Verify session tokens use approved algorithms for cryptographic security.",
        cwe_ids=[331],
    ),
    "V3.3.1": ASVSRequirement(
        id="V3.3.1",
        level=1,
        chapter="V3 Session Management",
        section="3.3 Session Termination",
        requirement="Verify logout and expiration invalidate the session token.",
        cwe_ids=[613],
    ),
    # Access Control
    "V4.1.1": ASVSRequirement(
        id="V4.1.1",
        level=1,
        chapter="V4 Access Control",
        section="4.1 General Access Control Design",
        requirement="Verify trusted enforcement points like access control gateways.",
        cwe_ids=[602],
    ),
    "V4.2.1": ASVSRequirement(
        id="V4.2.1",
        level=1,
        chapter="V4 Access Control",
        section="4.2 Operation Level Access Control",
        requirement="Verify sensitive data and APIs are protected against direct object reference attacks.",
        cwe_ids=[639],
    ),
    # Input Validation
    "V5.1.1": ASVSRequirement(
        id="V5.1.1",
        level=1,
        chapter="V5 Validation",
        section="5.1 Input Validation",
        requirement="Verify HTTP parameter pollution attacks are protected.",
        cwe_ids=[235],
    ),
    "V5.2.1": ASVSRequirement(
        id="V5.2.1",
        level=1,
        chapter="V5 Validation",
        section="5.2 Sanitization and Sandboxing",
        requirement="Verify untrusted HTML input from WYSIWYG editors is sanitized.",
        cwe_ids=[116],
    ),
    "V5.3.1": ASVSRequirement(
        id="V5.3.1",
        level=1,
        chapter="V5 Validation",
        section="5.3 Output Encoding",
        requirement="Verify output encoding is relevant for the interpreter.",
        cwe_ids=[116],
    ),
    "V5.3.4": ASVSRequirement(
        id="V5.3.4",
        level=1,
        chapter="V5 Validation",
        section="5.3 Output Encoding",
        requirement="Verify data selection or database queries use parameterized queries.",
        cwe_ids=[89],
    ),
    # Cryptography
    "V6.2.1": ASVSRequirement(
        id="V6.2.1",
        level=1,
        chapter="V6 Stored Cryptography",
        section="6.2 Algorithms",
        requirement="Verify use of approved cryptographic algorithms.",
        cwe_ids=[327],
    ),
    "V6.3.1": ASVSRequirement(
        id="V6.3.1",
        level=2,
        chapter="V6 Stored Cryptography",
        section="6.3 Random Values",
        requirement="Verify cryptographic random number generators are secure.",
        cwe_ids=[338],
    ),
    # Error Handling
    "V7.1.1": ASVSRequirement(
        id="V7.1.1",
        level=1,
        chapter="V7 Error Handling",
        section="7.1 Log Content",
        requirement="Verify security relevant events are logged.",
        cwe_ids=[778],
    ),
    "V7.4.1": ASVSRequirement(
        id="V7.4.1",
        level=1,
        chapter="V7 Error Handling",
        section="7.4 Error Handling",
        requirement="Verify generic error messages are displayed without sensitive data.",
        cwe_ids=[209],
    ),
    # Data Protection
    "V8.3.1": ASVSRequirement(
        id="V8.3.1",
        level=1,
        chapter="V8 Data Protection",
        section="8.3 Sensitive Private Data",
        requirement="Verify sensitive data is sent in the HTTP body or headers.",
        cwe_ids=[319],
    ),
    # Communication
    "V9.1.1": ASVSRequirement(
        id="V9.1.1",
        level=1,
        chapter="V9 Communication",
        section="9.1 Client Communication Security",
        requirement="Verify TLS is used for all client connectivity.",
        cwe_ids=[319],
    ),
    # API Security
    "V13.1.1": ASVSRequirement(
        id="V13.1.1",
        level=1,
        chapter="V13 API",
        section="13.1 Generic Web Service Security",
        requirement="Verify all application components use the same encoding.",
        cwe_ids=[116],
    ),
    "V13.2.1": ASVSRequirement(
        id="V13.2.1",
        level=1,
        chapter="V13 API",
        section="13.2 RESTful Web Service",
        requirement="Verify enabled RESTful HTTP methods are valid for the action.",
        cwe_ids=[650],
    ),
    # Configuration
    "V14.2.1": ASVSRequirement(
        id="V14.2.1",
        level=1,
        chapter="V14 Configuration",
        section="14.2 Dependency",
        requirement="Verify all components are up to date.",
        cwe_ids=[1104],
    ),
    "V14.3.2": ASVSRequirement(
        id="V14.3.2",
        level=1,
        chapter="V14 Configuration",
        section="14.3 Unintended Security Disclosure",
        requirement="Verify debug modes are disabled in production.",
        cwe_ids=[215],
    ),
}

# CWE to ASVS mapping for automatic requirement lookup
CWE_TO_ASVS = {
    79: ["V5.3.1"],  # XSS
    89: ["V5.3.4"],  # SQL Injection
    94: ["V5.2.1"],  # Code Injection
    116: ["V5.3.1", "V13.1.1"],  # Improper Encoding
    200: ["V7.4.1"],  # Information Exposure
    209: ["V7.4.1"],  # Error Message Information Exposure
    215: ["V14.3.2"],  # Debug Information Exposure
    235: ["V5.1.1"],  # HTTP Parameter Pollution
    307: ["V2.2.1"],  # Brute Force
    319: ["V8.3.1", "V9.1.1"],  # Cleartext Transmission
    327: ["V6.2.1"],  # Broken Crypto
    331: ["V3.2.1"],  # Insufficient Entropy
    338: ["V6.3.1"],  # Weak PRNG
    521: ["V2.1.1"],  # Weak Password
    602: ["V4.1.1"],  # Client-Side Enforcement
    613: ["V3.3.1"],  # Insufficient Session Expiration
    620: ["V2.1.5"],  # Unverified Password Change
    639: ["V4.2.1"],  # Insecure Direct Object Reference
    650: ["V13.2.1"],  # HTTP Method Abuse
    778: ["V7.1.1"],  # Insufficient Logging
    1104: ["V14.2.1"],  # Vulnerable Components
}


class EvidenceMapper:
    """Maps security findings to ASVS requirements with evidence."""

    def __init__(self):
        """Initialize the evidence mapper."""
        self.asvs_db = ASVS_REQUIREMENTS_DB
        self.cwe_to_asvs = CWE_TO_ASVS

    def get_asvs_for_cwe(self, cwe_id: int) -> list[ASVSRequirement]:
        """Get ASVS requirements related to a CWE ID.

        Args:
            cwe_id: CWE identifier

        Returns:
            List of related ASVS requirements
        """
        asvs_ids = self.cwe_to_asvs.get(cwe_id, [])
        return [self.asvs_db[aid] for aid in asvs_ids if aid in self.asvs_db]

    def get_asvs_by_id(self, asvs_id: str) -> ASVSRequirement | None:
        """Get ASVS requirement by ID.

        Args:
            asvs_id: ASVS requirement ID (e.g., "V5.3.4")

        Returns:
            ASVS requirement or None
        """
        return self.asvs_db.get(asvs_id)

    def create_evidence_ref(
        self,
        file_path: str,
        line_start: int,
        line_end: int | None = None,
        code_snippet: str = "",
        context: str | None = None,
    ) -> EvidenceRef:
        """Create an evidence reference.

        Args:
            file_path: Path to the source file
            line_start: Starting line number
            line_end: Ending line number (optional)
            code_snippet: Relevant code snippet
            context: Additional context

        Returns:
            EvidenceRef instance
        """
        return EvidenceRef(
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            code_snippet=code_snippet,
            context=context,
        )

    def map_finding(self, raw_finding: dict[str, Any]) -> MappedFinding:
        """Map a raw finding to ASVS requirements with evidence.

        Args:
            raw_finding: Raw finding dict from AI analysis

        Returns:
            MappedFinding with ASVS mapping and evidence
        """
        # Extract CWE IDs
        cwe_ids = raw_finding.get("cwe_ids", [])
        if isinstance(cwe_ids, str):
            # Parse CWE string like "CWE-89"
            import re

            cwe_ids = [int(m) for m in re.findall(r"CWE-?(\d+)", cwe_ids)]

        # Get ASVS requirements from CWE mapping
        asvs_requirements = []
        seen_asvs = set()

        for cwe_id in cwe_ids:
            for req in self.get_asvs_for_cwe(cwe_id):
                if req.id not in seen_asvs:
                    asvs_requirements.append(req)
                    seen_asvs.add(req.id)

        # Add explicit ASVS requirements from finding
        explicit_asvs = raw_finding.get("asvs_requirements", [])
        for asvs_id in explicit_asvs:
            if asvs_id not in seen_asvs:
                req = self.get_asvs_by_id(asvs_id)
                if req:
                    asvs_requirements.append(req)
                    seen_asvs.add(asvs_id)

        # Create evidence references
        evidence = []
        if raw_finding.get("file_path"):
            evidence.append(
                self.create_evidence_ref(
                    file_path=raw_finding.get("file_path", ""),
                    line_start=raw_finding.get("line_start", 1),
                    line_end=raw_finding.get("line_end"),
                    code_snippet=raw_finding.get("code_snippet", ""),
                    context=raw_finding.get("context"),
                )
            )

        return MappedFinding(
            id=raw_finding.get("id", ""),
            severity=raw_finding.get("severity", "medium"),
            title=raw_finding.get("title", ""),
            description=raw_finding.get("description", ""),
            asvs_requirements=asvs_requirements,
            cwe_ids=cwe_ids,
            evidence=evidence,
            remediation=raw_finding.get("remediation", ""),
            fixed_code=raw_finding.get("fixed_code"),
        )

    def map_findings(
        self, raw_findings: list[dict[str, Any]]
    ) -> list[MappedFinding]:
        """Map multiple raw findings to ASVS requirements.

        Args:
            raw_findings: List of raw finding dicts

        Returns:
            List of mapped findings
        """
        return [self.map_finding(f) for f in raw_findings]

    def to_dict(self, mapped_finding: MappedFinding) -> dict[str, Any]:
        """Convert MappedFinding to dictionary for API response.

        Args:
            mapped_finding: MappedFinding instance

        Returns:
            Dictionary representation
        """
        return {
            "id": mapped_finding.id,
            "severity": mapped_finding.severity,
            "title": mapped_finding.title,
            "description": mapped_finding.description,
            "asvsRequirements": [
                {
                    "id": req.id,
                    "level": req.level,
                    "chapter": req.chapter,
                    "section": req.section,
                    "requirement": req.requirement,
                    "cweIds": req.cwe_ids,
                }
                for req in mapped_finding.asvs_requirements
            ],
            "cweIds": mapped_finding.cwe_ids,
            "evidence": [
                {
                    "filePath": ev.file_path,
                    "lineStart": ev.line_start,
                    "lineEnd": ev.line_end,
                    "codeSnippet": ev.code_snippet,
                    "context": ev.context,
                }
                for ev in mapped_finding.evidence
            ],
            "remediation": mapped_finding.remediation,
            "fixedCode": mapped_finding.fixed_code,
        }


# Singleton instance
_mapper: EvidenceMapper | None = None


def get_evidence_mapper() -> EvidenceMapper:
    """Get or create EvidenceMapper singleton."""
    global _mapper
    if _mapper is None:
        _mapper = EvidenceMapper()
    return _mapper
