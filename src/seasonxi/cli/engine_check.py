"""SXI Engine Health Check - HANESIS 파이프라인 진단 도구.

Usage: uv run python -m seasonxi.cli.engine_check

HANESIS 7단계별 진단:
  H - Harvest   : 데이터 수집 상태 점검
  A - Align     : 선수/팀/시즌 식별자 일관성
  N - Normalize : per90 + percentile 피처 검증
  E - Evaluate  : 레이팅 공식 + 점수 분포 + 티어 밸런스
  S - Synergize : 조합 엔진 준비 상태 (Phase 4)
  I - Infer     : 최적 XI 탐색 준비 상태 (Phase 4)
  S - Storyframe: 콘텐츠 파이프라인 점검
"""

from __future__ import annotations

import importlib
import inspect
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd

from seasonxi.ratings.formula_v1 import ROLE_RATERS, _safe_get, _scale
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import SCORE_BASE, SCORE_RANGE, TIER_THRESHOLDS, Tier, score_to_tier


# ─── Test Data ────────────────────────────────────────────────

def _make_mock_row(percentile: float = 0.5) -> pd.Series:
    """Create a mock player row at given percentile level."""
    return pd.Series({
        "goals_pct_role": percentile, "xg_pct_role": percentile,
        "shots_pct_role": percentile, "goals_minus_xg_pct_role": percentile,
        "assists_pct_role": percentile, "xa_pct_role": percentile,
        "key_passes_pct_role": percentile,
        "prog_passes_pct_role": percentile, "prog_carries_pct_role": percentile,
        "dribbles_pct_role": percentile, "pass_completion_pct_role": percentile,
        "tackles_pct_role": percentile, "interceptions_pct_role": percentile,
        "clearances_pct_role": percentile, "aerials_pct_role": percentile,
        "pressures_pct_role": percentile, "aerial_duel_success_pct_role": percentile,
        "ball_recoveries_pct_role": percentile, "pressure_success_pct_role": percentile,
        "team_goal_contribution": percentile * 0.4, "team_success_pct": percentile,
        "minutes_share": percentile, "clean_sheets_pct_role": percentile,
        "gk_saves_pct_role": percentile, "gk_psxg_diff_pct_role": percentile,
        "gk_crosses_stopped_pct_role": percentile,
        "gk_pass_completion_pct_role": percentile, "gk_launch_pct_role": percentile,
    })


# ═══════════════════════════════════════════════════════════════
# H - HARVEST: 데이터 수집 상태
# ═══════════════════════════════════════════════════════════════

def check_harvest() -> list[str]:
    """Check raw data availability."""
    issues = []
    raw_dir = Path("data/raw/fbref")

    if not raw_dir.exists():
        issues.append("FAIL: data/raw/fbref/ directory not found")
        return issues

    csv_files = list(raw_dir.glob("*.csv"))
    txt_files = list(raw_dir.glob("*.txt"))
    total = len(csv_files) + len(txt_files)

    if total == 0:
        issues.append("FAIL: No raw data files found")
    else:
        issues.append(f"INFO: {total} raw files ({len(csv_files)} csv, {len(txt_files)} txt)")

    # Check league coverage
    leagues_found = set()
    for f in csv_files + txt_files:
        name = f.stem.lower()
        for league in ["epl", "laliga", "seriea", "bundesliga", "ligue1"]:
            if league in name:
                leagues_found.add(league)
    missing = {"epl", "laliga", "seriea", "bundesliga", "ligue1"} - leagues_found
    if missing:
        issues.append(f"WARN: Missing leagues: {missing}")
    else:
        issues.append("INFO: All 5 leagues covered")

    # Check seed files
    seed_players = Path("data/raw/seed_players.csv")
    seed_teams = Path("data/raw/seed_teams.csv")
    if not seed_players.exists():
        issues.append("WARN: seed_players.csv not found")
    if not seed_teams.exists():
        issues.append("WARN: seed_teams.csv not found")

    return issues


# ═══════════════════════════════════════════════════════════════
# A - ALIGN: 식별자 일관성
# ═══════════════════════════════════════════════════════════════

def check_align() -> list[str]:
    """Check ID consistency and module structure."""
    issues = []

    # Check for player_session_id typo in formula source
    import seasonxi.ratings.formula_v1 as formula_mod
    source = inspect.getsource(formula_mod)
    if "player_session_id" in source:
        issues.append("FAIL: 'player_session_id' typo found (should be player_season_id)")
    else:
        issues.append("INFO: No ID typos detected")

    # Check position mapper exists
    try:
        from seasonxi.features.feature_pipeline import _fix_position
        issues.append("INFO: Position mapper (_fix_position) available")
    except ImportError:
        issues.append("WARN: Position mapper not found")

    # Circular dependency check
    modules = [
        "seasonxi.ratings.formula_v1", "seasonxi.ratings.confidence",
        "seasonxi.ratings.league_adjustment", "seasonxi.ratings.team_debiasing",
        "seasonxi.features.per90", "seasonxi.features.percentiles",
        "seasonxi.features.feature_pipeline", "seasonxi.constants",
    ]
    graph: dict[str, set[str]] = defaultdict(set)
    for mod_name in modules:
        try:
            mod = importlib.import_module(mod_name)
            src = inspect.getsource(mod)
            for target in modules:
                parts = target.rsplit(".", 1)
                if len(parts) == 2 and f"from {parts[0]}" in src and parts[1] in src:
                    graph[mod_name].add(target)
        except Exception:
            pass

    def _find_cycle(node: str, visited: set, path: set) -> bool:
        visited.add(node)
        path.add(node)
        for nb in graph.get(node, set()):
            if nb in path:
                issues.append(f"FAIL: CYCLE {node} -> {nb}")
                return True
            if nb not in visited and _find_cycle(nb, visited, path):
                return True
        path.discard(node)
        return False

    vis: set[str] = set()
    cycle_found = False
    for m in modules:
        if m not in vis and _find_cycle(m, vis, set()):
            cycle_found = True
    if not cycle_found:
        issues.append("INFO: No circular dependencies")

    return issues


# ═══════════════════════════════════════════════════════════════
# N - NORMALIZE: 피처 파이프라인 검증
# ═══════════════════════════════════════════════════════════════

def check_normalize() -> list[str]:
    """Check feature pipeline: per90, percentiles, completeness."""
    issues = []

    # Count per90 stats
    from seasonxi.features.per90 import COUNTING_STATS, P90_MAP
    issues.append(f"INFO: {len(COUNTING_STATS)} counting stats -> {len(P90_MAP)} per90 columns")

    # Count percentile features
    from seasonxi.features.percentiles import PERCENTILE_STATS, GK_PERCENTILE_STATS
    issues.append(f"INFO: {len(PERCENTILE_STATS)} standard + {len(GK_PERCENTILE_STATS)} GK percentiles = {len(PERCENTILE_STATS) + len(GK_PERCENTILE_STATS)} total")

    # Feature usage audit: percentile defined vs formula used
    import seasonxi.ratings.formula_v1 as fmod
    formula_source = inspect.getsource(fmod)

    defined = {p for _, p in PERCENTILE_STATS} | {p for _, p in GK_PERCENTILE_STATS}
    used = {p for p in defined if p in formula_source}
    unused = defined - used

    if unused:
        for p in sorted(unused):
            issues.append(f"WARN: UNUSED feature: {p}")
    else:
        issues.append("INFO: All percentile features used in formula")

    # Check league adjustment isn't double-applied
    from seasonxi.features.feature_pipeline import build_features
    fp_source = inspect.getsource(build_features)
    if "league_factors" in fp_source and "league_strength_factor" in fp_source:
        # Check if it's actively applying or just metadata
        if "* league" in fp_source or "apply_league" in fp_source:
            issues.append("FAIL: League adjustment double-applied in feature_pipeline AND formula_v1")
        else:
            issues.append("INFO: League adjustment applied only in formula_v1")
    else:
        issues.append("INFO: League adjustment applied only in formula_v1")

    # Check league match counts
    from seasonxi.features.feature_pipeline import LEAGUE_MATCHES
    for league, matches in LEAGUE_MATCHES.items():
        if league == "GER1" and matches != 34:
            issues.append(f"WARN: {league} should be 34 matches, got {matches}")
        elif league != "GER1" and matches != 38:
            issues.append(f"WARN: {league} should be 38 matches, got {matches}")
    issues.append(f"INFO: League match counts: {LEAGUE_MATCHES}")

    return issues


# ═══════════════════════════════════════════════════════════════
# E - EVALUATE: 레이팅 공식 + 점수 분포 + 밸런스
# ═══════════════════════════════════════════════════════════════

def check_evaluate() -> list[str]:
    """Check rating formulas, score ranges, and tier balance."""
    issues = []

    # --- E1: Role coverage ---
    issues.append(f"INFO: Supported roles: {list(ROLE_RATERS.keys())}")
    if len(ROLE_RATERS) < 4:
        issues.append("WARN: Not all 4 positions covered")

    # --- E2: Weight sum validation ---
    for role, rater in ROLE_RATERS.items():
        scores_lo = rater(_make_mock_row(0.0), 1.0)
        scores_hi = rater(_make_mock_row(1.0), 1.0)
        for dim, raw in scores_hi["_raws"].items():
            if raw < -0.01 or raw > 1.01:
                issues.append(f"FAIL: {role}.{dim}: raw={raw:.3f} out of [0,1] (weight sum != 1.0)")

    # --- E3: Score range validation ---
    for role, rater in ROLE_RATERS.items():
        scores_floor = rater(_make_mock_row(0.0), 1.0)
        scores_ceil = rater(_make_mock_row(1.0), 1.0)
        for dim in ["att", "def", "pace", "aura", "stamina", "mental", "overall"]:
            lo, hi = scores_floor[dim], scores_ceil[dim]
            if lo < 29:
                issues.append(f"WARN: {role}.{dim}: floor={lo:.1f} (below 30)")
            if hi > 99.5:
                issues.append(f"FAIL: {role}.{dim}: ceiling={hi:.1f} (above 99)")

    # --- E4: Confidence function ---
    conf_tests = [(450, 0.3, 0.5), (900, 0.5, 0.75), (1800, 1.0, 1.0)]
    for minutes, low_ok, high_ok in conf_tests:
        c = compute_confidence(minutes)
        if c < low_ok or c > high_ok:
            issues.append(f"WARN: confidence({minutes}min)={c:.3f} outside [{low_ok},{high_ok}]")
    issues.append(f"INFO: confidence curve: 450m={compute_confidence(450):.2f}, 900m={compute_confidence(900):.2f}, 1800m={compute_confidence(1800):.2f}")

    # --- E5: Tier balance simulation ---
    random.seed(42)
    for role in ROLE_RATERS:
        counts = {t.value: 0 for t in Tier}
        rater = ROLE_RATERS[role]
        for _ in range(2000):
            # Realistic: each feature has independent percentile
            # with correlation (base + noise per feature)
            base_talent = random.betavariate(2.5, 2.5)
            row_data = {}
            for k in _make_mock_row(0.5).index:
                noise = random.gauss(0, 0.15)
                row_data[k] = max(0.0, min(1.0, base_talent + noise))
            row_data["team_goal_contribution"] = base_talent * 0.4
            row = pd.Series(row_data)
            # Most players play 1500+ minutes (realistic)
            minutes = random.randint(900, 3400)
            scores = rater(row, compute_confidence(minutes))
            counts[score_to_tier(scores["overall"]).value] += 1

        total = sum(counts.values())
        mythic = counts["Mythic"] / total * 100
        bronze = counts["Bronze"] / total * 100
        dist = " | ".join(f"{t}:{counts[t]/total*100:.0f}%" for t in
                          ["Mythic", "Legendary", "Elite", "Gold", "Silver", "Bronze"])

        if mythic == 0:
            issues.append(f"WARN: {role} Mythic=0% (unreachable)")
        if mythic > 5:
            issues.append(f"WARN: {role} Mythic={mythic:.1f}% (too common, should be <5%)")
        if bronze > 35:
            issues.append(f"WARN: {role} Bronze={bronze:.0f}% (over-concentrated)")
        issues.append(f"INFO: {role} tiers: {dist}")

    # --- E6: Cross-role consistency ---
    for pct, label in [(0.95, "Star"), (0.50, "Average"), (0.10, "Weak")]:
        overalls = {r: ROLE_RATERS[r](_make_mock_row(pct), 1.0)["overall"] for r in ROLE_RATERS}
        spread = max(overalls.values()) - min(overalls.values())
        if spread > 10:
            detail = ", ".join(f"{r}={v:.0f}" for r, v in overalls.items())
            issues.append(f"WARN: {label} cross-role spread={spread:.1f} ({detail})")

    # --- E7: Edge cases ---
    for role, rater in ROLE_RATERS.items():
        try:
            rater(_make_mock_row(0.5), 0.0)  # zero confidence
        except Exception as e:
            issues.append(f"FAIL: {role} crashes with confidence=0: {e}")
        try:
            nan_row = pd.Series({k: float("nan") for k in _make_mock_row(0.5).index})
            rater(nan_row, 1.0)  # NaN input
        except Exception as e:
            issues.append(f"FAIL: {role} crashes with NaN input: {e}")

    return issues


# ═══════════════════════════════════════════════════════════════
# S - SYNERGIZE: 조합 엔진 준비 (Phase 4)
# ═══════════════════════════════════════════════════════════════

def check_synergize() -> list[str]:
    """Check synergy engine readiness."""
    issues = []

    synergy_dir = Path("src/seasonxi/synergy")
    if synergy_dir.exists():
        py_files = list(synergy_dir.glob("*.py"))
        if len(py_files) > 1:  # more than __init__.py
            issues.append(f"INFO: Synergy module has {len(py_files)} files")
        else:
            issues.append("INFO: Synergy module exists but empty (Phase 4)")
    else:
        issues.append("INFO: Synergy module not created yet (Phase 4 - planned)")

    # Check DB schema for synergy tables
    schema_path = Path("src/seasonxi/db/schema.sql")
    if schema_path.exists():
        schema = schema_path.read_text(encoding="utf-8")
        if "pair_synergy_scores" in schema:
            issues.append("INFO: pair_synergy_scores table defined in schema")
        else:
            issues.append("WARN: pair_synergy_scores not in schema")
        if "best_xi_results" in schema:
            issues.append("INFO: best_xi_results table defined in schema")
    else:
        issues.append("WARN: schema.sql not found")

    return issues


# ═══════════════════════════════════════════════════════════════
# I - INFER: 최적 XI 탐색 준비 (Phase 4)
# ═══════════════════════════════════════════════════════════════

def check_infer() -> list[str]:
    """Check optimization engine readiness."""
    issues = []

    optimizer_dir = Path("src/seasonxi/optimizer")
    if optimizer_dir.exists():
        py_files = list(optimizer_dir.glob("*.py"))
        if len(py_files) > 1:
            issues.append(f"INFO: Optimizer module has {len(py_files)} files")
        else:
            issues.append("INFO: Optimizer module exists but empty (Phase 4)")
    else:
        issues.append("INFO: Optimizer module not created yet (Phase 4 - planned)")

    return issues


# ═══════════════════════════════════════════════════════════════
# S - STORYFRAME: 콘텐츠 파이프라인
# ═══════════════════════════════════════════════════════════════

def check_storyframe() -> list[str]:
    """Check content generation pipeline."""
    issues = []

    # Card exporter
    try:
        from seasonxi.content.card_exporter import export_cards
        issues.append("INFO: Card exporter available")
    except ImportError:
        issues.append("WARN: Card exporter not found")

    # Obsidian export
    try:
        from seasonxi.content.obsidian_export import export_all
        issues.append("INFO: Obsidian exporter available")
    except ImportError:
        issues.append("WARN: Obsidian exporter not found")

    # Shorts script writer
    try:
        from seasonxi.content.shorts_script_writer import generate_script
        issues.append("INFO: Shorts script writer available")
    except ImportError:
        issues.append("WARN: Shorts script writer not found")

    # Remotion project
    remotion_dir = Path("remotion")
    if remotion_dir.exists():
        tsx_files = list(remotion_dir.rglob("*.tsx"))
        issues.append(f"INFO: Remotion project found ({len(tsx_files)} .tsx files)")
    else:
        issues.append("WARN: Remotion project not found")

    # Image prompts
    prompts_dir = Path("configs/image_prompts")
    if prompts_dir.exists():
        prompt_files = list(prompts_dir.glob("*.txt"))
        issues.append(f"INFO: {len(prompt_files)} image prompt files")
    else:
        issues.append("WARN: Image prompt configs not found")

    # Suno prompts
    suno = Path("configs/suno_prompts.txt")
    if suno.exists():
        issues.append("INFO: Suno music prompts available")

    # Obsidian season documents
    obsidian_players = Path("C:/Users/Storm Credit/Desktop/shorts/seasonXI/01_Players")
    if not obsidian_players.exists():
        # Try alternate path
        obsidian_players = Path("../seasonXI/01_Players")
    if obsidian_players.exists():
        md_files = list(obsidian_players.rglob("*.md"))
        issues.append(f"INFO: {len(md_files)} Obsidian player/season documents")
    else:
        issues.append("INFO: Obsidian vault not detected (external path)")

    return issues


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

HANESIS_CHECKS = [
    ("H", "HARVEST", "Data Collection", check_harvest),
    ("A", "ALIGN", "Entity Matching & Dependencies", check_align),
    ("N", "NORMALIZE", "Feature Pipeline", check_normalize),
    ("E", "EVALUATE", "Ratings & Tier Balance", check_evaluate),
    ("S", "SYNERGIZE", "Pair Chemistry (Phase 4)", check_synergize),
    ("I", "INFER", "Best XI Search (Phase 4)", check_infer),
    ("S", "STORYFRAME", "Content Pipeline", check_storyframe),
]


def run_all_checks() -> None:
    """Run HANESIS pipeline health check."""
    print()
    print("=" * 64)
    print("  H.A.N.E.S.I.S  ENGINE HEALTH CHECK  v1.2")
    print("  SeasonXI - Football Season Card Engine")
    print("=" * 64)

    total_fail = 0
    total_warn = 0
    total_pass = 0
    stage_status: list[tuple[str, str, str]] = []

    for letter, stage, desc, check_fn in HANESIS_CHECKS:
        print(f"\n{'─' * 64}")
        print(f"  [{letter}] {stage} - {desc}")
        print(f"{'─' * 64}")

        results = check_fn()
        stage_fails = 0
        stage_warns = 0

        for r in results:
            if "FAIL" in r:
                print(f"    [FAIL] {r.replace('FAIL: ', '')}")
                total_fail += 1
                stage_fails += 1
            elif "WARN" in r:
                print(f"    [WARN] {r.replace('WARN: ', '')}")
                total_warn += 1
                stage_warns += 1
            elif "UNUSED" in r:
                print(f"    [WARN] {r}")
                total_warn += 1
                stage_warns += 1
            else:
                print(f"    [ OK ] {r.replace('INFO: ', '')}")
                total_pass += 1

        if stage_fails > 0:
            stage_status.append((letter, stage, "FAIL"))
        elif stage_warns > 0:
            stage_status.append((letter, stage, "WARN"))
        else:
            stage_status.append((letter, stage, "PASS"))

    # Summary
    print(f"\n{'=' * 64}")
    print("  HANESIS PIPELINE STATUS")
    print(f"{'=' * 64}")
    for letter, stage, status in stage_status:
        icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}[status]
        print(f"    [{icon}] {letter} - {stage}")

    print(f"\n    Totals: {total_fail} errors, {total_warn} warnings, {total_pass} passed")

    if total_fail == 0 and total_warn == 0:
        print("\n    ENGINE STATUS: ALL CLEAR")
    elif total_fail == 0:
        print(f"\n    ENGINE STATUS: HEALTHY ({total_warn} warnings)")
    else:
        print(f"\n    ENGINE STATUS: NEEDS FIX ({total_fail} errors)")
    print("=" * 64)


if __name__ == "__main__":
    run_all_checks()
