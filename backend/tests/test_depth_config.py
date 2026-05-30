"""Tests for depth configuration module."""

import pytest

from app.api.schemas.common import Perspective, ReviewDepth
from app.core.depth_config import (
    DEPTH_CONFIGS,
    DepthConfig,
    estimate_total_cost,
    estimate_total_time,
    get_depth_config,
    get_max_files,
    is_valid_combination,
)


class TestDepthConfigCompleteness:
    """Verify all 9 (perspective × depth) combinations are defined."""

    def test_all_9_combinations_exist(self):
        """All 3 perspectives × 3 depths = 9 combinations must exist."""
        assert len(DEPTH_CONFIGS) == 9

    @pytest.mark.parametrize("perspective", list(Perspective))
    @pytest.mark.parametrize("depth", list(ReviewDepth))
    def test_each_combination_exists(self, perspective, depth):
        """Each combination has a valid DepthConfig."""
        config = get_depth_config(perspective, depth)
        assert isinstance(config, DepthConfig)


class TestMonotonicity:
    """Verify that quick < standard < detailed for time and cost."""

    @pytest.mark.parametrize("perspective", list(Perspective))
    def test_time_monotonic(self, perspective):
        """Time estimates should increase: quick < standard < detailed."""
        quick = get_depth_config(perspective, ReviewDepth.QUICK)
        standard = get_depth_config(perspective, ReviewDepth.STANDARD)
        detailed = get_depth_config(perspective, ReviewDepth.DETAILED)

        assert quick.estimated_time_sec < standard.estimated_time_sec
        assert standard.estimated_time_sec < detailed.estimated_time_sec

    @pytest.mark.parametrize("perspective", list(Perspective))
    def test_cost_monotonic(self, perspective):
        """Cost estimates should increase: quick < standard < detailed."""
        quick = get_depth_config(perspective, ReviewDepth.QUICK)
        standard = get_depth_config(perspective, ReviewDepth.STANDARD)
        detailed = get_depth_config(perspective, ReviewDepth.DETAILED)

        assert quick.estimated_cost_jpy < standard.estimated_cost_jpy
        assert standard.estimated_cost_jpy < detailed.estimated_cost_jpy


class TestAsvsConfig:
    """ASVS-specific configuration tests."""

    def test_asvs_quick_has_3_categories(self):
        config = get_depth_config(Perspective.ASVS, ReviewDepth.QUICK)
        assert isinstance(config.ruleset, list)
        assert len(config.ruleset) == 3

    def test_asvs_standard_has_7_categories(self):
        config = get_depth_config(Perspective.ASVS, ReviewDepth.STANDARD)
        assert isinstance(config.ruleset, list)
        assert len(config.ruleset) == 7

    def test_asvs_detailed_has_14_categories(self):
        config = get_depth_config(Perspective.ASVS, ReviewDepth.DETAILED)
        assert isinstance(config.ruleset, list)
        assert len(config.ruleset) == 14


class TestSastConfig:
    """SAST-specific configuration tests."""

    def test_sast_quick_uses_security_audit(self):
        config = get_depth_config(Perspective.SAST, ReviewDepth.QUICK)
        assert config.ruleset == "p/security-audit"

    def test_sast_detailed_uses_llm_filter(self):
        config = get_depth_config(Perspective.SAST, ReviewDepth.DETAILED)
        assert config.use_llm_filter is True


class TestDastConfig:
    """DAST-specific configuration tests."""

    def test_dast_quick_is_passive(self):
        config = get_depth_config(Perspective.DAST, ReviewDepth.QUICK)
        assert config.scan_mode == "passive"

    def test_dast_detailed_is_full_active(self):
        config = get_depth_config(Perspective.DAST, ReviewDepth.DETAILED)
        assert config.scan_mode == "full"

    def test_dast_has_max_urls(self):
        for depth in ReviewDepth:
            config = get_depth_config(Perspective.DAST, depth)
            assert config.max_urls is not None
            assert config.max_urls > 0


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_max_files(self):
        assert get_max_files("asvs", "quick") == 10
        assert get_max_files("asvs", "standard") == 30
        assert get_max_files("asvs", "detailed") == 100

    def test_get_depth_config_with_strings(self):
        config = get_depth_config("asvs", "quick")
        assert isinstance(config, DepthConfig)

    def test_get_depth_config_with_enums(self):
        config = get_depth_config(Perspective.ASVS, ReviewDepth.QUICK)
        assert isinstance(config, DepthConfig)

    def test_estimate_total_time_single(self):
        time = estimate_total_time(["asvs"], "standard")
        assert time == 180

    def test_estimate_total_time_multiple(self):
        time = estimate_total_time(["asvs", "sast"], "standard")
        assert time == 180 + 120  # ASVS standard + SAST standard

    def test_estimate_total_cost(self):
        cost = estimate_total_cost(["asvs", "sast"], "standard")
        assert cost == 30 + 10  # ASVS standard + SAST standard


class TestValidCombinations:
    """Test perspective × input_type validity."""

    def test_asvs_with_github_valid(self):
        assert is_valid_combination("asvs", "github") is True

    def test_asvs_with_code_valid(self):
        assert is_valid_combination("asvs", "code") is True

    def test_asvs_with_url_invalid(self):
        assert is_valid_combination("asvs", "url") is False

    def test_sast_with_github_valid(self):
        assert is_valid_combination("sast", "github") is True

    def test_sast_with_url_invalid(self):
        assert is_valid_combination("sast", "url") is False

    def test_dast_with_url_valid(self):
        assert is_valid_combination("dast", "url") is True

    def test_dast_with_github_invalid(self):
        assert is_valid_combination("dast", "github") is False

    def test_dast_with_code_invalid(self):
        assert is_valid_combination("dast", "code") is False


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_invalid_perspective_raises(self):
        with pytest.raises((ValueError, KeyError)):
            get_depth_config("invalid", "quick")

    def test_invalid_depth_raises(self):
        with pytest.raises((ValueError, KeyError)):
            get_depth_config("asvs", "invalid")
