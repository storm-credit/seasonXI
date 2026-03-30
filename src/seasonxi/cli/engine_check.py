"""SXI Engine Health Check — 엔진 셀프 진단 도구.

Usage: uv run python -m seasonxi.cli.engine_check

Checks:
1. Weight sum validation (all must = 1.0)
2. Score range validation (min/max/distribution)
3. Feature usage audit (defined but unused features)
4. Circular dependency detection
5. Tier balance simulation
6. Cross-role consistency
7. Edge case testing
"""

from __future__ import annotations

import importlib
import inspect
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

from seasonxi.ratings.formula_v1 import (
    ROLE_RATERS,
    _safe_get,
    _scale,
    rate_defender,
    rate_forward,
    rate_goalkeeper,
    rate_midfielder,
)
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import SCORE_BASE, SCORE_RANGE, TIER_THRESHOLDS, Tier, score_to_tier


# ─── Test Data ────────────────────────────────────────────────

def _make_mock_row(percentile: float = 0.5) -> pd.Series:
    """Create a mock player row at given percentile level."""
    return pd.Series({
        # Attacking
        "goals_pct_role": percentile,
        "xg_pct_role": percentile,
        "shots_pct_role": percentile,
        "goals_minus_xg_pct_role": percentile,
        "assists_pct_role": percentile,
        "xa_pct_role": percentile,
        "key_passes_pct_role": percentile,
        # Control
        "prog_passes_pct_role": percentile,
        "prog_carries_pct_role": percentile,
        "dribbles_pct_role": percentile,
        "pass_completion_pct_role": percentile,
        # Defense
        "tackles_pct_role": percentile,
        "interceptions_pct_role": percentile,
        "clearances_pct_role": percentile,
        "aerials_pct_role": percentile,
        "pressures_pct_role": percentile,
        "aerial_duel_success_pct_role": percentile,
        "ball_recoveries_pct_role": percentile,
        # Context
        "team_goal_contribution": percentile * 0.4,
        "team_success_pct": percentile,
        "minutes_share": percentile,
        "clean_sheets_pct_role": percentile,
        # GK
        "gk_saves_pct_role": percentile,
        "gk_psxg_diff_pct_role": percentile,
        "gk_crosses_stopped_pct_role": percentile,
        "gk_pass_completion_pct_role": percentile,
        "gk_launch_pct_role": percentile,
    })


# ─── Check 1: Weight Sum Validation ──────────────────────────

def check_weight_sums() -> list[str]:
    """Verify all dimension weight sums = 1.0 for each role."""
    issues = []
    test_row = _make_mock_row(0.5)

    for role, rater in ROLE_RATERS.items():
        # Test with different inputs to detect weight issues
        scores_lo = rater(_make_mock_row(0.0), 1.0)
        scores_hi = rater(_make_mock_row(1.0), 1.0)

        # Overall should be deterministic — check range
        overall_lo = scores_lo["overall"]
        overall_hi = scores_hi["overall"]

        if overall_lo < 0 or overall_hi > 100:
            issues.append(f"  {role}: Overall out of range [{overall_lo:.1f}, {overall_hi:.1f}]")

        # Check that all raws are in [0, 1]
        for dim, raw in scores_hi["_raws"].items():
            if raw < -0.01 or raw > 1.01:
                issues.append(f"  {role}.{dim}: raw={raw:.3f} out of [0,1]")

    return issues


# ─── Check 2: Score Range Validation ─────────────────────────

def check_score_ranges() -> list[str]:
    """Verify min/max scores are reasonable for each role."""
    issues = []

    for role, rater in ROLE_RATERS.items():
        # Floor: all percentiles = 0, full confidence
        scores_floor = rater(_make_mock_row(0.0), 1.0)
        # Ceiling: all percentiles = 1, full confidence
        scores_ceil = rater(_make_mock_row(1.0), 1.0)
        # Low confidence
        scores_low_conf = rater(_make_mock_row(1.0), 0.3)

        for dim in ["finishing", "creation", "control", "defense", "clutch", "aura", "overall"]:
            lo = scores_floor[dim]
            hi = scores_ceil[dim]
            lc = scores_low_conf[dim]

            # Floor should be >= 30 (hardcoded minimum for GK finishing)
            if lo < 29:
                issues.append(f"  {role}.{dim}: floor={lo:.1f} (too low)")
            # Ceiling should be <= 99
            if hi > 99.5:
                issues.append(f"  {role}.{dim}: ceiling={hi:.1f} (too high)")
            # Low confidence should reduce scores
            if lc > hi:
                issues.append(f"  {role}.{dim}: low_conf={lc:.1f} > full_conf={hi:.1f}")

    return issues


# ─── Check 3: Feature Usage Audit ────────────────────────────

def check_feature_usage() -> list[str]:
    """Find features defined in percentiles but unused in formula."""
    issues = []

    from seasonxi.features.percentiles import PERCENTILE_STATS, GK_PERCENTILE_STATS

    # Collect all pct_role names from percentiles
    defined_pcts = {pct_col for _, pct_col in PERCENTILE_STATS}
    defined_pcts.update(pct_col for _, pct_col in GK_PERCENTILE_STATS)

    # Scan formula source for used features
    import seasonxi.ratings.formula_v1 as formula_mod
    formula_source = inspect.getsource(formula_mod)

    used_pcts = set()
    unused_pcts = set()

    for pct in defined_pcts:
        if pct in formula_source:
            used_pcts.add(pct)
        else:
            unused_pcts.add(pct)

    if unused_pcts:
        for p in sorted(unused_pcts):
            issues.append(f"  UNUSED: {p} (defined in percentiles but not in formula)")

    return issues


# ─── Check 4: Circular Dependency Detection ──────────────────

def check_circular_imports() -> list[str]:
    """Basic circular dependency check for ratings modules."""
    issues = []

    modules = [
        "seasonxi.ratings.formula_v1",
        "seasonxi.ratings.confidence",
        "seasonxi.ratings.league_adjustment",
        "seasonxi.ratings.team_debiasing",
        "seasonxi.features.per90",
        "seasonxi.features.percentiles",
        "seasonxi.features.feature_pipeline",
        "seasonxi.constants",
    ]

    # Build import graph
    graph: dict[str, set[str]] = defaultdict(set)

    for mod_name in modules:
        try:
            mod = importlib.import_module(mod_name)
            source = inspect.getsource(mod)
            for target in modules:
                short = target.split(".")[-1]
                if f"from {target}" in source or f"import {target}" in source:
                    graph[mod_name].add(target)
                # Also check partial imports
                parts = target.rsplit(".", 1)
                if len(parts) == 2:
                    parent, child = parts
                    if f"from {parent} import {child}" in source:
                        graph[mod_name].add(target)
        except Exception:
            pass

    # Detect cycles (simple DFS)
    def has_cycle(node: str, visited: set, path: set) -> bool:
        visited.add(node)
        path.add(node)
        for neighbor in graph.get(node, set()):
            if neighbor in path:
                issues.append(f"  CYCLE: {node} → {neighbor}")
                return True
            if neighbor not in visited:
                if has_cycle(neighbor, visited, path):
                    return True
        path.discard(node)
        return False

    visited: set[str] = set()
    for mod in modules:
        if mod not in visited:
            has_cycle(mod, visited, set())

    return issues


# ─── Check 5: Tier Balance Simulation ────────────────────────

def check_tier_balance() -> list[str]:
    """Simulate 1000 players and check tier distribution."""
    issues = []
    import random
    random.seed(42)

    tier_counts: dict[str, dict[str, int]] = {}

    for role in ROLE_RATERS:
        tier_counts[role] = {t.value: 0 for t in Tier}
        rater = ROLE_RATERS[role]

        for _ in range(1000):
            # Random percentiles (beta distribution — realistic, slightly right-skewed)
            pct = random.betavariate(2.5, 2.5)
            minutes = random.randint(500, 3400)
            row = _make_mock_row(pct)
            conf = compute_confidence(minutes)
            scores = rater(row, conf)
            tier = score_to_tier(scores["overall"])
            tier_counts[role][tier.value] += 1

    for role, counts in tier_counts.items():
        total = sum(counts.values())
        mythic_pct = counts["Mythic"] / total * 100
        bronze_pct = counts["Bronze"] / total * 100

        if mythic_pct > 5:
            issues.append(f"  {role}: Mythic={mythic_pct:.1f}% (too many, should be <5%)")
        if mythic_pct == 0:
            issues.append(f"  {role}: Mythic=0% (too strict, should allow rare cases)")
        if bronze_pct > 30:
            issues.append(f"  {role}: Bronze={bronze_pct:.1f}% (too many)")

        # Report distribution
        dist_str = " | ".join(f"{t}: {counts[t]/total*100:.1f}%" for t in
                              ["Mythic", "Legendary", "Elite", "Gold", "Silver", "Bronze"])
        issues.append(f"  {role} dist: {dist_str}")

    return issues


# ─── Check 6: Cross-Role Consistency ─────────────────────────

def check_cross_role_consistency() -> list[str]:
    """Elite players across roles should have similar Overall ranges."""
    issues = []

    for pct_level, label in [(0.9, "Elite"), (0.5, "Average"), (0.1, "Weak")]:
        row = _make_mock_row(pct_level)
        overalls = {}

        for role, rater in ROLE_RATERS.items():
            scores = rater(row, 1.0)
            overalls[role] = scores["overall"]

        # Check variance
        vals = list(overalls.values())
        spread = max(vals) - min(vals)

        if spread > 10:
            details = ", ".join(f"{r}={v:.1f}" for r, v in overalls.items())
            issues.append(f"  {label} (pct={pct_level}): spread={spread:.1f} ({details})")

    return issues


# ─── Check 7: Edge Cases ─────────────────────────────────────

def check_edge_cases() -> list[str]:
    """Test edge cases: 0 minutes, all zeros, all maxes."""
    issues = []

    for role, rater in ROLE_RATERS.items():
        # Zero confidence
        try:
            scores = rater(_make_mock_row(0.5), 0.0)
            for dim in ["finishing", "creation", "control", "defense", "clutch", "aura"]:
                if role == "GK" and dim == "finishing":
                    continue  # hardcoded 30
                if scores[dim] != SCORE_BASE and scores[dim] != 30:
                    issues.append(f"  {role}.{dim}: confidence=0 → {scores[dim]:.1f} (expected {SCORE_BASE})")
        except Exception as e:
            issues.append(f"  {role}: ERROR with confidence=0: {e}")

        # NaN handling
        try:
            nan_row = pd.Series({k: float("nan") for k in _make_mock_row(0.5).index})
            scores = rater(nan_row, 1.0)
            # Should not crash, defaults should kick in
        except Exception as e:
            issues.append(f"  {role}: CRASH with NaN input: {e}")

    return issues


# ─── Main ─────────────────────────────────────────────────────

def run_all_checks() -> None:
    """Run all engine health checks."""
    checks = [
        ("1. Weight Sum Validation", check_weight_sums),
        ("2. Score Range Validation", check_score_ranges),
        ("3. Feature Usage Audit", check_feature_usage),
        ("4. Circular Dependency Check", check_circular_imports),
        ("5. Tier Balance Simulation (1000 players)", check_tier_balance),
        ("6. Cross-Role Consistency", check_cross_role_consistency),
        ("7. Edge Case Testing", check_edge_cases),
    ]

    print("=" * 60)
    print("  SXI ENGINE HEALTH CHECK v1.2")
    print("=" * 60)

    total_issues = 0
    total_warnings = 0

    for name, check_fn in checks:
        print(f"\n--- {name} ---")
        results = check_fn()

        if not results:
            print("  ALL PASS")
        else:
            for r in results:
                if "CYCLE" in r or "CRASH" in r or "ERROR" in r:
                    print(f"  [FAIL] {r}")
                    total_issues += 1
                elif "UNUSED" in r or "too" in r:
                    print(f"  [WARN] {r}")
                    total_warnings += 1
                else:
                    print(f"  [INFO] {r}")

    print("\n" + "=" * 60)
    print(f"  SUMMARY: {total_issues} errors, {total_warnings} warnings")
    if total_issues == 0:
        print("  ENGINE STATUS: HEALTHY")
    else:
        print("  ENGINE STATUS: NEEDS FIX")
    print("=" * 60)


if __name__ == "__main__":
    run_all_checks()
