"""Review depth configuration registry.

Defines the behavior characteristics for each (perspective × depth) combination.
This is the single source of truth for review scope, time, and cost estimates.
"""

from dataclasses import dataclass

from app.api.schemas.common import Perspective, ReviewDepth


@dataclass(frozen=True)
class DepthConfig:
    """Configuration for a specific (perspective, depth) combination.

    Attributes:
        max_files: Maximum files to analyze (for ASVS/SAST)
        max_urls: Maximum URLs to scan (for DAST only, None for others)
        ruleset: Rule identifier(s) - ASVS categories, Semgrep rules, or ZAP mode
        use_llm_filter: Whether to use LLM for false-positive filtering (SAST detailed)
        scan_mode: DAST scan mode (passive/baseline/full, None for ASVS/SAST)
        prompt_style: LLM prompt complexity (concise/detailed/expert)
        estimated_time_sec: Estimated execution time in seconds
        estimated_cost_jpy: Estimated cost in JPY
        description: Human-readable description
    """

    max_files: int
    max_urls: int | None
    ruleset: str | list[str]
    use_llm_filter: bool
    scan_mode: str | None
    prompt_style: str
    estimated_time_sec: int
    estimated_cost_jpy: int
    description: str


# ============================================================================
# ASVS Configurations (LLM-based via Azure OpenAI GPT-4o)
# ============================================================================

_ASVS_QUICK = DepthConfig(
    max_files=10,
    max_urls=None,
    ruleset=["V1", "V2", "V5"],  # Top 3 critical categories
    use_llm_filter=False,
    scan_mode=None,
    prompt_style="concise",
    estimated_time_sec=60,
    estimated_cost_jpy=10,
    description="OWASP Top 10 focus on architecture, authentication, and input validation",
)

_ASVS_STANDARD = DepthConfig(
    max_files=30,
    max_urls=None,
    ruleset=["V1", "V2", "V3", "V4", "V5", "V6", "V7"],  # Common requirements
    use_llm_filter=False,
    scan_mode=None,
    prompt_style="detailed",
    estimated_time_sec=180,
    estimated_cost_jpy=30,
    description="ASVS V1-V7: balanced coverage of common security requirements",
)

_ASVS_DETAILED = DepthConfig(
    max_files=100,
    max_urls=None,
    ruleset=[
        "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
    ],  # Complete ASVS Level 1+2
    use_llm_filter=False,
    scan_mode=None,
    prompt_style="expert",
    estimated_time_sec=600,
    estimated_cost_jpy=150,
    description="ASVS V1-V14: complete coverage with attack scenarios and remediation",
)


# ============================================================================
# SAST Configurations (Semgrep-based)
# ============================================================================

_SAST_QUICK = DepthConfig(
    max_files=10,
    max_urls=None,
    ruleset="p/security-audit",
    use_llm_filter=False,
    scan_mode=None,
    prompt_style="concise",
    estimated_time_sec=30,
    estimated_cost_jpy=3,
    description="Quick security audit rules for fastest detection",
)

_SAST_STANDARD = DepthConfig(
    max_files=30,
    max_urls=None,
    ruleset=["p/owasp-top-ten", "p/security-audit"],
    use_llm_filter=False,
    scan_mode=None,
    prompt_style="detailed",
    estimated_time_sec=120,
    estimated_cost_jpy=10,
    description="OWASP Top 10 + security audit rulesets",
)

_SAST_DETAILED = DepthConfig(
    max_files=200,
    max_urls=None,
    ruleset="auto",  # All available Semgrep rules
    use_llm_filter=True,  # LLM filters false positives
    scan_mode=None,
    prompt_style="expert",
    estimated_time_sec=600,
    estimated_cost_jpy=80,
    description="Full Semgrep ruleset with LLM-based false positive filtering",
)


# ============================================================================
# DAST Configurations (OWASP ZAP-based)
# ============================================================================

_DAST_QUICK = DepthConfig(
    max_files=0,
    max_urls=5,
    ruleset="passive-only",
    use_llm_filter=False,
    scan_mode="passive",
    prompt_style="concise",
    estimated_time_sec=120,
    estimated_cost_jpy=15,
    description="Passive scan only: observation without attacks (safe)",
)

_DAST_STANDARD = DepthConfig(
    max_files=0,
    max_urls=30,
    ruleset="baseline",
    use_llm_filter=False,
    scan_mode="baseline",
    prompt_style="detailed",
    estimated_time_sec=900,
    estimated_cost_jpy=100,
    description="Baseline scan: passive + light active attacks",
)

_DAST_DETAILED = DepthConfig(
    max_files=0,
    max_urls=200,
    ruleset="full-active",
    use_llm_filter=True,  # LLM analyzes attack results
    scan_mode="full",
    prompt_style="expert",
    estimated_time_sec=3600,
    estimated_cost_jpy=500,
    description="Full active scan: all attack vectors (use only on owned sites)",
)


# ============================================================================
# Central Registry
# ============================================================================

DEPTH_CONFIGS: dict[tuple[Perspective, ReviewDepth], DepthConfig] = {
    # ASVS
    (Perspective.ASVS, ReviewDepth.QUICK): _ASVS_QUICK,
    (Perspective.ASVS, ReviewDepth.STANDARD): _ASVS_STANDARD,
    (Perspective.ASVS, ReviewDepth.DETAILED): _ASVS_DETAILED,
    # SAST
    (Perspective.SAST, ReviewDepth.QUICK): _SAST_QUICK,
    (Perspective.SAST, ReviewDepth.STANDARD): _SAST_STANDARD,
    (Perspective.SAST, ReviewDepth.DETAILED): _SAST_DETAILED,
    # DAST
    (Perspective.DAST, ReviewDepth.QUICK): _DAST_QUICK,
    (Perspective.DAST, ReviewDepth.STANDARD): _DAST_STANDARD,
    (Perspective.DAST, ReviewDepth.DETAILED): _DAST_DETAILED,
}


# ============================================================================
# Helper Functions
# ============================================================================


def get_depth_config(
    perspective: Perspective | str,
    depth: ReviewDepth | str,
) -> DepthConfig:
    """Get configuration for a (perspective, depth) combination.

    Args:
        perspective: Review perspective (ASVS/SAST/DAST)
        depth: Review depth (quick/standard/detailed)

    Returns:
        DepthConfig for the combination

    Raises:
        KeyError: If combination is invalid
    """
    # Normalize string inputs to enums
    if isinstance(perspective, str):
        perspective = Perspective(perspective)
    if isinstance(depth, str):
        depth = ReviewDepth(depth)

    config = DEPTH_CONFIGS.get((perspective, depth))
    if config is None:
        raise KeyError(
            f"No configuration for perspective={perspective}, depth={depth}"
        )
    return config


def get_max_files(perspective: Perspective | str, depth: ReviewDepth | str) -> int:
    """Get max files for a (perspective, depth) combination."""
    return get_depth_config(perspective, depth).max_files


def get_max_urls(
    perspective: Perspective | str, depth: ReviewDepth | str
) -> int | None:
    """Get max URLs for a (perspective, depth) combination."""
    return get_depth_config(perspective, depth).max_urls


def get_ruleset(
    perspective: Perspective | str, depth: ReviewDepth | str
) -> str | list[str]:
    """Get ruleset for a (perspective, depth) combination."""
    return get_depth_config(perspective, depth).ruleset


def estimate_total_time(
    perspectives: list[Perspective | str],
    depth: ReviewDepth | str,
) -> int:
    """Estimate total time for multiple perspectives at given depth.

    Note: Assumes sequential execution. Parallel execution would reduce this.
    """
    total = 0
    for p in perspectives:
        total += get_depth_config(p, depth).estimated_time_sec
    return total


def estimate_total_cost(
    perspectives: list[Perspective | str],
    depth: ReviewDepth | str,
) -> int:
    """Estimate total cost in JPY for multiple perspectives at given depth."""
    total = 0
    for p in perspectives:
        total += get_depth_config(p, depth).estimated_cost_jpy
    return total


def is_valid_combination(
    perspective: Perspective | str,
    input_type: str,
) -> bool:
    """Check if a (perspective, input_type) combination is valid.

    Rules:
        - ASVS works with: github, code
        - SAST works with: github, code
        - DAST works with: url only

    Args:
        perspective: Review perspective
        input_type: Review input type (github/code/url)

    Returns:
        True if combination is valid
    """
    if isinstance(perspective, str):
        perspective = Perspective(perspective)

    if perspective == Perspective.DAST:
        return input_type == "url"
    else:
        return input_type in ("github", "code")
