"""Unit tests for formula_v1.py — _scale, confidence, rate_*, and tier constants.

Tests verify:
- _scale boundary and range behaviour
- confidence non-linear scaling
- rate_forward / rate_midfielder / rate_defender / rate_goalkeeper output shapes
- FW ATT > DEF structural guarantee
- Tier threshold constants
- Overall score always within plausible bounds (50–99)
"""

import math

import pytest

from seasonxi.ratings.confidence import compute_confidence
from seasonxi.ratings.formula_v1 import (
    _scale,
    _stretch,
    rate_defender,
    rate_forward,
    rate_goalkeeper,
    rate_midfielder,
)
from seasonxi.constants import TIER_THRESHOLDS, Tier


# ── _scale ──────────────────────────────────────────────────────────────────


class TestScale:
    def test_base_at_zero_raw(self):
        """_scale(0.0, confidence=1.0) must return exactly 50 (SCORE_BASE)."""
        assert _scale(0.0, 1.0) == pytest.approx(50.0, abs=0.01)

    def test_max_at_one_raw(self):
        """_scale(1.0, confidence=1.0) must return exactly 99 (BASE + RANGE)."""
        assert _scale(1.0, 1.0) == pytest.approx(99.0, abs=0.01)

    def test_midpoint_is_between_base_and_max(self):
        """_scale(0.5, 1.0) should land between 50 and 99."""
        result = _scale(0.5, 1.0)
        assert 50 < result < 99

    def test_zero_confidence_returns_base(self):
        """When confidence=0, the stretched contribution is zero → score == base (50)."""
        assert _scale(0.5, 0.0) == pytest.approx(50.0, abs=0.01)

    def test_monotone_with_raw(self):
        """Higher raw must produce a higher score (monotonicity)."""
        scores = [_scale(x / 10, 1.0) for x in range(0, 11)]
        assert scores == sorted(scores)

    def test_monotone_with_confidence(self):
        """Higher confidence must produce a higher score at the same raw."""
        scores = [_scale(0.7, c / 10) for c in range(0, 11)]
        assert scores == sorted(scores)

    def test_raw_clamped_above_one(self):
        """Raw values > 1.0 must be clamped to 1.0."""
        assert _scale(1.5, 1.0) == pytest.approx(_scale(1.0, 1.0), abs=0.01)

    def test_raw_clamped_below_zero(self):
        """Raw values < 0.0 must be clamped to 0.0."""
        assert _scale(-0.5, 1.0) == pytest.approx(_scale(0.0, 1.0), abs=0.01)


# ── _stretch ────────────────────────────────────────────────────────────────


class TestStretch:
    def test_stretch_range(self):
        """_stretch output must always be in [0, 1]."""
        for x in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            result = _stretch(x)
            assert 0.0 <= result <= 1.0, f"_stretch({x}) = {result} out of [0,1]"

    def test_stretch_midpoint_near_half(self):
        """_stretch(0.5) should be close to 0.5 (symmetric sigmoid)."""
        assert _stretch(0.5) == pytest.approx(0.5, abs=0.01)


# ── confidence ──────────────────────────────────────────────────────────────


class TestConfidence:
    def test_full_confidence_at_1800_minutes(self):
        """1800 minutes → confidence must be exactly 1.0."""
        assert compute_confidence(1800) == pytest.approx(1.0, abs=1e-9)

    def test_above_1800_capped_at_one(self):
        """More than 1800 minutes must not exceed confidence 1.0."""
        assert compute_confidence(3420) == pytest.approx(1.0, abs=1e-9)

    def test_zero_minutes_is_zero(self):
        """0 minutes → confidence is 0.0."""
        assert compute_confidence(0) == pytest.approx(0.0, abs=1e-9)

    def test_900_minutes_non_linear(self):
        """900 min is half the cap, but non-linear exponent 0.7 → > 0.5."""
        conf = compute_confidence(900)
        assert conf > 0.5, f"Expected >0.5 due to non-linear scaling, got {conf}"
        assert conf < 1.0

    def test_confidence_monotone(self):
        """Confidence must increase as minutes increase."""
        values = [compute_confidence(m) for m in range(0, 1801, 100)]
        assert values == sorted(values)


# ── rate_forward ─────────────────────────────────────────────────────────────


class TestRateForward:
    def test_returns_required_keys(self, sample_fw_row):
        result = rate_forward(sample_fw_row, confidence=1.0)
        for key in ("att", "def", "pace", "aura", "stamina", "mental", "overall", "_raws"):
            assert key in result, f"Missing key: {key}"

    def test_overall_in_valid_range(self, sample_fw_row):
        result = rate_forward(sample_fw_row, confidence=1.0)
        assert 50.0 <= result["overall"] <= 99.0, f"OVR={result['overall']} out of range"

    def test_elite_fw_scores_high_overall(self, sample_fw_row):
        """An elite-percentile FW row should produce an overall well above Gold (76)."""
        result = rate_forward(sample_fw_row, confidence=1.0)
        assert result["overall"] >= 80.0, (
            f"Elite FW overall {result['overall']} unexpectedly low"
        )

    def test_att_higher_than_def_for_fw(self, sample_fw_row):
        """FW ATT must be structurally above FW DEF.

        FW DEF is compressed (base=30, rng=35) while ATT uses full range.
        An elite FW should always have att > def.
        """
        result = rate_forward(sample_fw_row, confidence=1.0)
        assert result["att"] > result["def"], (
            f"FW ATT ({result['att']:.1f}) should be > DEF ({result['def']:.1f})"
        )

    def test_confidence_scaling(self, sample_fw_row):
        """Lower confidence must produce a lower overall score."""
        high_conf = rate_forward(sample_fw_row, confidence=1.0)["overall"]
        low_conf = rate_forward(sample_fw_row, confidence=0.3)["overall"]
        assert high_conf > low_conf


# ── rate_midfielder ───────────────────────────────────────────────────────────


class TestRateMidfielder:
    def test_returns_required_keys(self, sample_mf_row):
        result = rate_midfielder(sample_mf_row, confidence=1.0)
        for key in ("att", "def", "pace", "aura", "stamina", "mental", "overall"):
            assert key in result

    def test_overall_in_valid_range(self, sample_mf_row):
        result = rate_midfielder(sample_mf_row, confidence=1.0)
        assert 50.0 <= result["overall"] <= 99.0

    def test_elite_mf_scores_high_overall(self, sample_mf_row):
        result = rate_midfielder(sample_mf_row, confidence=1.0)
        assert result["overall"] >= 80.0, (
            f"Elite MF overall {result['overall']} unexpectedly low"
        )


# ── rate_defender ─────────────────────────────────────────────────────────────


class TestRateDefender:
    def test_returns_required_keys(self, sample_df_row):
        result = rate_defender(sample_df_row, confidence=1.0)
        for key in ("att", "def", "pace", "aura", "stamina", "mental", "overall"):
            assert key in result

    def test_overall_in_valid_range(self, sample_df_row):
        result = rate_defender(sample_df_row, confidence=1.0)
        assert 50.0 <= result["overall"] <= 99.0

    def test_def_higher_than_att_for_df(self, sample_df_row):
        """DF DEF must be above DF ATT — ATT is compressed (base=30, rng=35)."""
        result = rate_defender(sample_df_row, confidence=1.0)
        assert result["def"] > result["att"], (
            f"DF DEF ({result['def']:.1f}) should be > ATT ({result['att']:.1f})"
        )

    def test_elite_df_scores_high_def(self, sample_df_row):
        """An elite percentile DF should produce a DEF score above 80."""
        result = rate_defender(sample_df_row, confidence=1.0)
        assert result["def"] >= 80.0, (
            f"Elite DF def score {result['def']:.1f} unexpectedly low"
        )


# ── rate_goalkeeper ────────────────────────────────────────────────────────────


class TestRateGoalkeeper:
    def test_returns_required_keys(self, sample_gk_row):
        result = rate_goalkeeper(sample_gk_row, confidence=1.0)
        for key in ("att", "def", "pace", "aura", "stamina", "mental", "overall"):
            assert key in result

    def test_overall_in_valid_range(self, sample_gk_row):
        result = rate_goalkeeper(sample_gk_row, confidence=1.0)
        assert 50.0 <= result["overall"] <= 99.0

    def test_gk_att_is_always_low(self, sample_gk_row):
        """GK att_raw is forced to 0.0, so att should stay near the compressed base (~30)."""
        result = rate_goalkeeper(sample_gk_row, confidence=1.0)
        # att uses base=30, rng=20 with raw=0.0 → _scale(0, conf) ≈ 30
        assert result["att"] < 35.0, (
            f"GK ATT should be near 30 (compressed), got {result['att']:.1f}"
        )

    def test_gk_cannot_reach_mythic(self, sample_gk_row):
        """Even with perfect inputs, a GK cannot reach Mythic (95+) due to ATT cap."""
        result = rate_goalkeeper(sample_gk_row, confidence=1.0)
        assert result["overall"] < 95.0, (
            f"GK should not reach Mythic (95+); got {result['overall']:.1f}"
        )

    def test_gk_def_is_primary_driver(self, sample_gk_row):
        """GK DEF must be above GK ATT — DEF is the dominant stat for GK."""
        result = rate_goalkeeper(sample_gk_row, confidence=1.0)
        assert result["def"] > result["att"]


# ── tier constants ─────────────────────────────────────────────────────────────


class TestTierThresholds:
    def test_mythic_threshold_is_95_or_above(self):
        """MYTHIC tier must require at least 95."""
        mythic_threshold = next(
            thresh for thresh, tier in TIER_THRESHOLDS if tier == Tier.MYTHIC
        )
        assert mythic_threshold >= 95, (
            f"Mythic threshold {mythic_threshold} is below 95"
        )

    def test_legendary_threshold_is_90(self):
        legendary_threshold = next(
            thresh for thresh, tier in TIER_THRESHOLDS if tier == Tier.LEGENDARY
        )
        assert legendary_threshold == 90

    def test_elite_threshold_is_84(self):
        elite_threshold = next(
            thresh for thresh, tier in TIER_THRESHOLDS if tier == Tier.ELITE
        )
        assert elite_threshold == 84

    def test_thresholds_are_strictly_descending(self):
        """Tier thresholds must be in strictly descending order."""
        thresholds = [t for t, _ in TIER_THRESHOLDS]
        assert thresholds == sorted(thresholds, reverse=True), (
            f"Tier thresholds not in descending order: {thresholds}"
        )

    def test_bronze_has_zero_threshold(self):
        """BRONZE is the catch-all tier with threshold 0."""
        bronze_threshold = next(
            thresh for thresh, tier in TIER_THRESHOLDS if tier == Tier.BRONZE
        )
        assert bronze_threshold == 0
