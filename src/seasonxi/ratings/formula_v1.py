"""V1.2 Rule-Based Rating Engine (SXI Engine).

Score formula: score = 50 + 49 * raw * confidence
- raw is a weighted sum of percentile inputs (0.0–1.0)
- confidence = min(1.0, (minutes/1800)^0.7) — non-linear
- Output range: 50–99 (with confidence=1.0)

v1.2 changes:
- Aura: removed perf_proxy circular dependency, uses role_dominance only
- team_success_pct: removed from Aura, kept only in Clutch
- FW/DF defense: base lowered from 40→30 (realistic range)
- Pressing: added pressures_pct_role to defense calculations
- GK: PSxG weight increased 20→35%, saves reduced 35→20%
- team_success_pct also debiased in compute_ratings()

Research basis:
- PlayeRank (Pappalardo 2019): role-aware multi-dimensional evaluation
- Wolf et al. (2020): percentile-based player rating system
- VAEP (Decroos 2019): xG/xA as indirect action-value proxies
- Springer 2025: pressing intensity as key defensive metric
- HAL 2025: PSxG as primary GK evaluation metric
"""

from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from seasonxi.constants import SCORE_BASE, SCORE_RANGE, score_to_tier
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.ratings.league_adjustment import apply_league_adjustment
from seasonxi.ratings.team_debiasing import debias_team_feature


def _scale(raw: float, confidence: float, base: int = SCORE_BASE, rng: int = SCORE_RANGE) -> float:
    """Scale a 0–1 raw score to card score."""
    return base + rng * max(0.0, min(1.0, raw)) * confidence


def _safe_get(row: pd.Series, col: str, default: float = 0.0) -> float:
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return float(val)


# ---------------------------------------------------------------------------
# FW — Forward
# ---------------------------------------------------------------------------
def rate_forward(row: pd.Series, confidence: float) -> dict:
    """Compute 6 scores + overall for a Forward."""
    finishing_raw = (
        0.35 * _safe_get(row, "goals_pct_role")
        + 0.25 * _safe_get(row, "xg_pct_role")
        + 0.20 * _safe_get(row, "shots_pct_role")
        + 0.20 * _safe_get(row, "team_goal_contribution")
    )
    creation_raw = (
        0.35 * _safe_get(row, "assists_pct_role")
        + 0.25 * _safe_get(row, "xa_pct_role")
        + 0.20 * _safe_get(row, "key_passes_pct_role")
        + 0.20 * _safe_get(row, "prog_passes_pct_role")
    )
    control_raw = (
        0.35 * _safe_get(row, "dribbles_pct_role")
        + 0.30 * _safe_get(row, "prog_carries_pct_role")
        + 0.20 * _safe_get(row, "prog_passes_pct_role")
        + 0.15 * _safe_get(row, "minutes_share")
    )
    # v1.2: added pressures, reduced minutes_share dependency
    defense_raw = (
        0.30 * _safe_get(row, "tackles_pct_role")
        + 0.25 * _safe_get(row, "interceptions_pct_role")
        + 0.30 * _safe_get(row, "pressures_pct_role")
        + 0.15 * _safe_get(row, "minutes_share")
    )
    clutch_raw = (
        0.45 * _safe_get(row, "team_goal_contribution")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
    )
    # v1.2: Aura — no perf_proxy, no team_success_pct
    role_dominance = (
        _safe_get(row, "goals_pct_role")
        + _safe_get(row, "xg_pct_role")
        + _safe_get(row, "shots_pct_role")
        + _safe_get(row, "dribbles_pct_role")
    ) / 4.0
    aura_raw = (
        0.45 * role_dominance
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "team_goal_contribution")
    )

    finishing = _scale(finishing_raw, confidence)
    creation = _scale(creation_raw, confidence)
    control = _scale(control_raw, confidence)
    defense = _scale(defense_raw, confidence, base=30, rng=35)  # v1.2: lowered
    clutch = _scale(clutch_raw, confidence)
    aura = _scale(aura_raw, confidence)

    overall_raw = (
        0.30 * finishing_raw
        + 0.20 * creation_raw
        + 0.18 * control_raw
        + 0.08 * defense_raw
        + 0.12 * clutch_raw
        + 0.12 * aura_raw
    )
    overall = _scale(overall_raw, confidence)

    return {
        "finishing": finishing, "creation": creation, "control": control,
        "defense": defense, "clutch": clutch, "aura": aura, "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


# ---------------------------------------------------------------------------
# MF — Midfielder
# ---------------------------------------------------------------------------
def rate_midfielder(row: pd.Series, confidence: float) -> dict:
    """Compute 6 scores + overall for a Midfielder."""
    finishing_raw = (
        0.30 * _safe_get(row, "goals_pct_role")
        + 0.20 * _safe_get(row, "xg_pct_role")
        + 0.20 * _safe_get(row, "shots_pct_role")
        + 0.30 * _safe_get(row, "team_goal_contribution")
    )
    creation_raw = (
        0.30 * _safe_get(row, "assists_pct_role")
        + 0.25 * _safe_get(row, "xa_pct_role")
        + 0.20 * _safe_get(row, "key_passes_pct_role")
        + 0.25 * _safe_get(row, "prog_passes_pct_role")
    )
    control_raw = (
        0.25 * _safe_get(row, "prog_carries_pct_role")
        + 0.25 * _safe_get(row, "prog_passes_pct_role")
        + 0.20 * _safe_get(row, "dribbles_pct_role")
        + 0.15 * _safe_get(row, "minutes_share")
        + 0.15 * _safe_get(row, "xa_pct_role")
    )
    # v1.2: added pressures, reduced minutes_share
    defense_raw = (
        0.30 * _safe_get(row, "tackles_pct_role")
        + 0.25 * _safe_get(row, "interceptions_pct_role")
        + 0.15 * _safe_get(row, "clearances_pct_role")
        + 0.20 * _safe_get(row, "pressures_pct_role")
        + 0.10 * _safe_get(row, "minutes_share")
    )
    clutch_raw = (
        0.35 * _safe_get(row, "team_goal_contribution")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.35 * _safe_get(row, "team_success_pct", 0.5)
    )
    # v1.2: Aura — no perf_proxy, no team_success_pct
    role_dominance = (
        _safe_get(row, "assists_pct_role")
        + _safe_get(row, "xa_pct_role")
        + _safe_get(row, "prog_passes_pct_role")
        + _safe_get(row, "key_passes_pct_role")
    ) / 4.0
    aura_raw = (
        0.40 * role_dominance
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "team_goal_contribution")
    )

    finishing = _scale(finishing_raw, confidence)
    creation = _scale(creation_raw, confidence)
    control = _scale(control_raw, confidence)
    defense = _scale(defense_raw, confidence)
    clutch = _scale(clutch_raw, confidence)
    aura = _scale(aura_raw, confidence)

    overall_raw = (
        0.16 * finishing_raw
        + 0.24 * creation_raw
        + 0.24 * control_raw
        + 0.14 * defense_raw
        + 0.10 * clutch_raw
        + 0.12 * aura_raw
    )
    overall = _scale(overall_raw, confidence)

    return {
        "finishing": finishing, "creation": creation, "control": control,
        "defense": defense, "clutch": clutch, "aura": aura, "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


# ---------------------------------------------------------------------------
# DF — Defender (CB / FB)
# ---------------------------------------------------------------------------
def rate_defender(row: pd.Series, confidence: float) -> dict:
    """Compute 6 scores + overall for a Defender."""
    finishing_raw = (
        0.40 * _safe_get(row, "goals_pct_role")
        + 0.30 * _safe_get(row, "xg_pct_role")
        + 0.30 * _safe_get(row, "shots_pct_role")
    )
    # v1.2: DF creation raised for modern build-up fullbacks
    creation_raw = (
        0.30 * _safe_get(row, "assists_pct_role")
        + 0.25 * _safe_get(row, "xa_pct_role")
        + 0.25 * _safe_get(row, "key_passes_pct_role")
        + 0.20 * _safe_get(row, "prog_passes_pct_role")
    )
    control_raw = (
        0.30 * _safe_get(row, "prog_passes_pct_role")
        + 0.25 * _safe_get(row, "prog_carries_pct_role")
        + 0.25 * _safe_get(row, "minutes_share")
        + 0.20 * _safe_get(row, "dribbles_pct_role")
    )
    # v1.2: added pressures for modern defensive evaluation
    defense_raw = (
        0.25 * _safe_get(row, "tackles_pct_role")
        + 0.20 * _safe_get(row, "interceptions_pct_role")
        + 0.20 * _safe_get(row, "clearances_pct_role")
        + 0.15 * _safe_get(row, "aerials_pct_role")
        + 0.20 * _safe_get(row, "pressures_pct_role")
    )
    clutch_raw = (
        0.30 * _safe_get(row, "clean_sheets_pct_role")
        + 0.30 * _safe_get(row, "team_success_pct", 0.5)
        + 0.20 * _safe_get(row, "minutes_share")
        + 0.20 * _safe_get(row, "team_goal_contribution")
    )
    # v1.2: Aura — no perf_proxy, no team_success_pct
    role_dominance = (
        _safe_get(row, "tackles_pct_role")
        + _safe_get(row, "interceptions_pct_role")
        + _safe_get(row, "clearances_pct_role")
        + _safe_get(row, "aerials_pct_role")
    ) / 4.0
    aura_raw = (
        0.40 * role_dominance
        + 0.35 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "clean_sheets_pct_role")
    )

    finishing = _scale(finishing_raw, confidence, base=30, rng=35)  # v1.2: lowered
    creation = _scale(creation_raw, confidence)
    control = _scale(control_raw, confidence)
    defense = _scale(defense_raw, confidence)
    clutch = _scale(clutch_raw, confidence)
    aura = _scale(aura_raw, confidence)

    # v1.2: DF creation weight raised 0.10→0.12 for modern fullbacks
    overall_raw = (
        0.05 * finishing_raw
        + 0.12 * creation_raw
        + 0.18 * control_raw
        + 0.35 * defense_raw
        + 0.15 * clutch_raw
        + 0.15 * aura_raw
    )
    overall = _scale(overall_raw, confidence)

    return {
        "finishing": finishing, "creation": creation, "control": control,
        "defense": defense, "clutch": clutch, "aura": aura, "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


# ---------------------------------------------------------------------------
# GK — Goalkeeper
# ---------------------------------------------------------------------------
def rate_goalkeeper(row: pd.Series, confidence: float) -> dict:
    """Compute 6 scores + overall for a Goalkeeper.

    v1.2: PSxG weight increased to 35% (primary GK metric per HAL 2025).
    """
    finishing_raw = 0.0
    creation_raw = (
        0.50 * _safe_get(row, "prog_passes_pct_role")
        + 0.50 * _safe_get(row, "key_passes_pct_role")
    )
    control_raw = (
        0.40 * _safe_get(row, "prog_passes_pct_role")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "gk_pass_completion_pct_role", 0.5)
    )
    # v1.2: PSxG raised to 35%, saves reduced to 20%
    defense_raw = (
        0.20 * _safe_get(row, "gk_saves_pct_role")
        + 0.20 * _safe_get(row, "clean_sheets_pct_role")
        + 0.35 * _safe_get(row, "gk_psxg_diff_pct_role")
        + 0.25 * _safe_get(row, "gk_crosses_stopped_pct_role")
    )
    clutch_raw = (
        0.35 * _safe_get(row, "clean_sheets_pct_role")
        + 0.35 * _safe_get(row, "team_success_pct", 0.5)
        + 0.30 * _safe_get(row, "minutes_share")
    )
    # v1.2: Aura — no perf_proxy, no team_success_pct
    aura_raw = (
        0.35 * _safe_get(row, "gk_psxg_diff_pct_role")
        + 0.30 * _safe_get(row, "clean_sheets_pct_role")
        + 0.35 * _safe_get(row, "minutes_share")
    )

    finishing = 30.0  # v1.2: hardcoded, GK has no finishing
    creation = _scale(creation_raw, confidence, base=35, rng=35)
    control = _scale(control_raw, confidence)
    defense = _scale(defense_raw, confidence)
    clutch = _scale(clutch_raw, confidence)
    aura = _scale(aura_raw, confidence)

    overall_raw = (
        0.00 * finishing_raw
        + 0.05 * creation_raw
        + 0.15 * control_raw
        + 0.45 * defense_raw
        + 0.20 * clutch_raw
        + 0.15 * aura_raw
    )
    overall = _scale(overall_raw, confidence)

    return {
        "finishing": finishing, "creation": creation, "control": control,
        "defense": defense, "clutch": clutch, "aura": aura, "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
ROLE_RATERS = {
    "FW": rate_forward,
    "MF": rate_midfielder,
    "DF": rate_defender,
    "GK": rate_goalkeeper,
}


def compute_ratings(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute ratings for all players in the features DataFrame.

    Pipeline: raw features → league adjustment → team debiasing → role rating → scaling
    """
    results = []

    for _, row in features_df.iterrows():
        role = row.get("role_bucket", row.get("primary_position", "FW"))
        rater = ROLE_RATERS.get(role)
        if rater is None:
            continue

        # Pre-processing: league adjustment on percentile features
        league_id = row.get("league_id", row.get("competition_id", ""))
        row_adj = row.copy()
        pct_cols = [c for c in row.index if c.endswith("_pct_role")]
        for col in pct_cols:
            if pd.notna(row_adj[col]):
                row_adj[col] = apply_league_adjustment(float(row_adj[col]), str(league_id))

        # Pre-processing: team debiasing on BOTH team-derived features
        team_success = float(row_adj.get("team_success_pct", 0.5))
        if pd.notna(row_adj.get("team_goal_contribution")):
            row_adj["team_goal_contribution"] = debias_team_feature(
                float(row_adj["team_goal_contribution"]), team_success
            )
        # v1.2: also debias team_success_pct itself
        row_adj["team_success_pct"] = debias_team_feature(team_success, team_success)

        confidence = compute_confidence(int(row_adj.get("minutes_played", 0)))
        scores = rater(row_adj, confidence)

        # Build explanation
        explanation = _build_explanation(row, scores, role)

        tier = score_to_tier(scores["overall"])

        results.append({
            "player_season_id": row["player_session_id"] if "player_session_id" in row.index else row.get("player_season_id", ""),
            "player_id": row.get("player_id", ""),
            "club_id": row.get("club_id", ""),
            "season_id": row.get("season_id", ""),
            "role_bucket": role,
            "finishing_score": round(scores["finishing"], 1),
            "creation_score": round(scores["creation"], 1),
            "control_score": round(scores["control"], 1),
            "defense_score": round(scores["defense"], 1),
            "clutch_score": round(scores["clutch"], 1),
            "aura_score": round(scores["aura"], 1),
            "overall_score": round(scores["overall"], 1),
            "confidence_score": confidence,
            "tier_label": tier.value,
            "explanation_json": json.dumps(explanation, ensure_ascii=False),
            "formula_version": "v1.2",
            "generated_at": datetime.now().isoformat(),
        })

    return pd.DataFrame(results)


def _build_explanation(row: pd.Series, scores: dict, role: str) -> dict:
    """Generate human-readable explanation."""
    raws = scores["_raws"]
    explanation: dict = {}

    for dim in ["finishing", "creation", "control", "defense", "clutch", "aura"]:
        drivers = []
        raw_val = raws.get(dim, 0)
        if dim == "finishing":
            drivers.append(f"goals/90 pct: {_safe_get(row, 'goals_pct_role'):.0%}")
            drivers.append(f"xG/90 pct: {_safe_get(row, 'xg_pct_role'):.0%}")
        elif dim == "creation":
            drivers.append(f"assists/90 pct: {_safe_get(row, 'assists_pct_role'):.0%}")
            drivers.append(f"xA/90 pct: {_safe_get(row, 'xa_pct_role'):.0%}")
        elif dim == "control":
            drivers.append(f"dribbles/90 pct: {_safe_get(row, 'dribbles_pct_role'):.0%}")
            drivers.append(f"prog carries/90 pct: {_safe_get(row, 'prog_carries_pct_role'):.0%}")
        elif dim == "defense":
            drivers.append(f"tackles/90 pct: {_safe_get(row, 'tackles_pct_role'):.0%}")
            drivers.append(f"pressures/90 pct: {_safe_get(row, 'pressures_pct_role'):.0%}")
        elif dim == "clutch":
            drivers.append(f"team goal contribution: {_safe_get(row, 'team_goal_contribution'):.0%}")
            drivers.append(f"team success: {_safe_get(row, 'team_success_pct', 0.5):.0%}")
        elif dim == "aura":
            drivers.append(f"role dominance: {raw_val:.3f}")

        explanation[dim] = {
            "score": round(scores[dim]),
            "raw": round(raw_val, 3),
            "drivers": drivers,
        }

    explanation["overall_summary"] = (
        f"{scores['overall']:.0f} overall, {score_to_tier(scores['overall']).value} tier"
    )
    return explanation
