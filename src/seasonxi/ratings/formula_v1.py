"""V2.0 Rule-Based Rating Engine (SXI Engine).

New 6-stat system: ATT / DEF / PACE / AURA / STAMINA / MENTAL
- Position-neutral names, position-specific formulas
- All positions use same stat names → cross-position comparison possible
- No 8-bucket split needed — 4 buckets (FW/MF/DF/GK) with balanced weights

Score formula: score = 50 + 49 * stretch(raw) * confidence
- raw is a weighted sum of percentile inputs (0.0-1.0)
- stretch: sigmoid(k=4.0) to spread middle-heavy distributions
- confidence = min(1.0, (minutes/1800)^0.7)

Stats:
- ATT: Attack (goals, assists, xG, xA, shots, key passes)
- DEF: Defense (tackles, interceptions, pressures, blocks, recoveries)
- PACE: Speed/Mobility (progressive carries, dribbles, prog passes received)
- AURA: Presence/Influence (role dominance, minutes share, contribution)
- STAMINA: Endurance/Work Rate (pressures, minutes consistency, appearances)
- MENTAL: Decision/Clutch (pass accuracy, duel success, team success)

Research basis:
- PlayeRank (Pappalardo 2019): role-aware multi-dimensional evaluation
- Wolf et al. (2020): percentile-based player rating system
- VAEP (Decroos 2019): xG/xA as indirect action-value proxies
- xT (Singh 2018): progressive carries as pace proxy
- Pressing Intensity (arXiv 2025): stamina/work rate metrics
- Clutch Moments (Tandfonline 2025): mental/decision under pressure
"""

from __future__ import annotations

import json
import math
from datetime import datetime

import pandas as pd

from seasonxi.constants import SCORE_BASE, SCORE_RANGE, score_to_tier
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.ratings.league_adjustment import apply_league_adjustment
from seasonxi.ratings.team_debiasing import debias_team_feature


def _adaptive_overall(raws: dict[str, float], base_weights: dict[str, float], boost: float = 0.07) -> float:
    """Compute overall with adaptive weighting based on player's strengths.

    Identifies top 2 stats by raw value and shifts weight toward them.
    This ensures creative players aren't penalized for low stamina,
    and defensive players aren't penalized for low attack.

    boost=0.05 means top 2 stats get +5% each, bottom 2 lose -5% each.
    """
    # Rank stats by raw value (exclude overall)
    stat_items = [(k, v) for k, v in raws.items() if k != "overall"]
    stat_items.sort(key=lambda x: x[1], reverse=True)

    # Identify top 2 and bottom 2
    top_keys = {stat_items[0][0], stat_items[1][0]}
    bottom_keys = {stat_items[-1][0], stat_items[-2][0]}

    # Adjust weights
    adjusted = {}
    for stat, base_w in base_weights.items():
        if stat in top_keys:
            adjusted[stat] = base_w + boost
        elif stat in bottom_keys:
            adjusted[stat] = max(0.0, base_w - boost)
        else:
            adjusted[stat] = base_w

    # Normalize to sum=1.0
    total_w = sum(adjusted.values())
    if total_w > 0:
        adjusted = {k: v / total_w for k, v in adjusted.items()}

    return sum(raws.get(k, 0) * w for k, w in adjusted.items())


def _stretch(x: float, k: float = 5.0) -> float:
    """Sigmoid stretch to spread out middle-heavy distributions."""
    sig = lambda v: 1.0 / (1.0 + math.exp(-k * (v - 0.5)))
    raw = sig(x)
    lo, hi = sig(0.0), sig(1.0)
    return (raw - lo) / (hi - lo)


def _scale(raw: float, confidence: float, base: int = SCORE_BASE, rng: int = SCORE_RANGE) -> float:
    """Scale a 0-1 raw score to card score with sigmoid stretch."""
    clamped = max(0.0, min(1.0, raw))
    stretched = _stretch(clamped)
    return base + rng * stretched * confidence


def _safe_get(row: pd.Series, col: str, default: float = 0.0) -> float:
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return float(val)


# ═══════════════════════════════════════════════════════════════
# FORWARD
# ═══════════════════════════════════════════════════════════════

def rate_forward(row: pd.Series, confidence: float) -> dict:
    """FW: ATT dominant, DEF minimal, PACE important."""
    att_raw = (
        0.25 * _safe_get(row, "goals_pct_role")
        + 0.15 * _safe_get(row, "xg_pct_role")
        + 0.10 * _safe_get(row, "goals_minus_xg_pct_role")
        + 0.20 * _safe_get(row, "assists_pct_role")
        + 0.10 * _safe_get(row, "xa_pct_role")
        + 0.10 * _safe_get(row, "key_passes_pct_role")
        + 0.10 * _safe_get(row, "shots_pct_role")
    )
    def_raw = (
        0.25 * _safe_get(row, "tackles_pct_role")
        + 0.20 * _safe_get(row, "interceptions_pct_role")
        + 0.30 * _safe_get(row, "pressures_pct_role")
        + 0.15 * _safe_get(row, "pressure_success_pct_role")
        + 0.10 * _safe_get(row, "ball_recoveries_pct_role")
    )
    pace_raw = (
        0.35 * _safe_get(row, "prog_carries_pct_role")
        + 0.35 * _safe_get(row, "dribbles_pct_role")
        + 0.30 * _safe_get(row, "prog_passes_pct_role")
    )
    aura_raw = (
        0.40 * (
            (_safe_get(row, "goals_pct_role") + _safe_get(row, "xg_pct_role")
             + _safe_get(row, "dribbles_pct_role") + _safe_get(row, "shots_pct_role")) / 4.0
        )  # role_dominance
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "team_goal_contribution")
    )
    stamina_raw = (
        0.30 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "ball_recoveries_pct_role")
        + 0.25 * _safe_get(row, "pressure_success_pct_role")
        + 0.20 * _safe_get(row, "tackles_pct_role")
    )
    mental_raw = (
        0.30 * _safe_get(row, "pass_completion_pct_role")
        + 0.25 * _safe_get(row, "aerial_duel_success_pct_role")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
        + 0.20 * _safe_get(row, "minutes_share")
    )

    att = _scale(att_raw, confidence)
    defense = _scale(def_raw, confidence, base=30, rng=35)  # compressed for FW
    pace = _scale(pace_raw, confidence)
    aura = _scale(aura_raw, confidence)
    stamina = _scale(stamina_raw, confidence)
    mental = _scale(mental_raw, confidence)

    # FW base: ATT 30% DEF 10% PACE 15% AURA 15% STA 10% MEN 20%
    raws = {"att": att_raw, "def": def_raw, "pace": pace_raw,
            "aura": aura_raw, "stamina": stamina_raw, "mental": mental_raw}
    base_w = {"att": 0.30, "def": 0.10, "pace": 0.15,
              "aura": 0.15, "stamina": 0.10, "mental": 0.20}
    overall_raw = _adaptive_overall(raws, base_w)
    overall = _scale(overall_raw, confidence)

    return {
        "att": att, "def": defense, "pace": pace,
        "aura": aura, "stamina": stamina, "mental": mental,
        "overall": overall,
        "_raws": {**raws, "overall": overall_raw},
    }


# ═══════════════════════════════════════════════════════════════
# MIDFIELDER
# ═══════════════════════════════════════════════════════════════

def rate_midfielder(row: pd.Series, confidence: float) -> dict:
    """MF: balanced, STAMINA/MENTAL high, DEF meaningful."""
    att_raw = (
        0.20 * _safe_get(row, "goals_pct_role")
        + 0.10 * _safe_get(row, "xg_pct_role")
        + 0.25 * _safe_get(row, "assists_pct_role")
        + 0.15 * _safe_get(row, "xa_pct_role")
        + 0.20 * _safe_get(row, "key_passes_pct_role")
        + 0.10 * _safe_get(row, "prog_passes_pct_role")
    )
    def_raw = (
        0.25 * _safe_get(row, "tackles_pct_role")
        + 0.20 * _safe_get(row, "interceptions_pct_role")
        + 0.25 * _safe_get(row, "pressures_pct_role")
        + 0.15 * _safe_get(row, "pressure_success_pct_role")
        + 0.15 * _safe_get(row, "ball_recoveries_pct_role")
    )
    pace_raw = (
        0.30 * _safe_get(row, "prog_carries_pct_role")
        + 0.30 * _safe_get(row, "prog_passes_pct_role")
        + 0.20 * _safe_get(row, "dribbles_pct_role")
        + 0.20 * _safe_get(row, "pass_completion_pct_role")
    )
    aura_raw = (
        0.40 * (
            (_safe_get(row, "assists_pct_role") + _safe_get(row, "xa_pct_role")
             + _safe_get(row, "prog_passes_pct_role") + _safe_get(row, "key_passes_pct_role")) / 4.0
        )
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "team_goal_contribution")
    )
    stamina_raw = (
        0.30 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "ball_recoveries_pct_role")
        + 0.25 * _safe_get(row, "prog_carries_pct_role")
        + 0.20 * _safe_get(row, "tackles_pct_role")
    )
    mental_raw = (
        0.30 * _safe_get(row, "pass_completion_pct_role")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
        + 0.25 * _safe_get(row, "aerial_duel_success_pct_role")
        + 0.20 * _safe_get(row, "pressure_success_pct_role")
    )

    att = _scale(att_raw, confidence)
    defense = _scale(def_raw, confidence)
    pace = _scale(pace_raw, confidence)
    aura = _scale(aura_raw, confidence)
    stamina = _scale(stamina_raw, confidence)
    mental = _scale(mental_raw, confidence)

    # MF base: ATT 15% DEF 20% PACE 10% AURA 15% STA 20% MEN 20%
    raws = {"att": att_raw, "def": def_raw, "pace": pace_raw,
            "aura": aura_raw, "stamina": stamina_raw, "mental": mental_raw}
    base_w = {"att": 0.15, "def": 0.20, "pace": 0.10,
              "aura": 0.15, "stamina": 0.20, "mental": 0.20}
    overall_raw = _adaptive_overall(raws, base_w)
    overall = _scale(overall_raw, confidence)

    return {
        "att": att, "def": defense, "pace": pace,
        "aura": aura, "stamina": stamina, "mental": mental,
        "overall": overall,
        "_raws": {**raws, "overall": overall_raw},
    }


# ═══════════════════════════════════════════════════════════════
# DEFENDER
# ═══════════════════════════════════════════════════════════════

def rate_defender(row: pd.Series, confidence: float) -> dict:
    """DF: DEF dominant, ATT compressed, MENTAL important."""
    att_raw = (
        0.30 * _safe_get(row, "goals_pct_role")
        + 0.20 * _safe_get(row, "assists_pct_role")
        + 0.25 * _safe_get(row, "key_passes_pct_role")
        + 0.25 * _safe_get(row, "prog_passes_pct_role")
    )
    def_raw = (
        0.25 * _safe_get(row, "tackles_pct_role")
        + 0.20 * _safe_get(row, "interceptions_pct_role")
        + 0.20 * _safe_get(row, "clearances_pct_role")
        + 0.15 * _safe_get(row, "aerials_pct_role")
        + 0.10 * _safe_get(row, "pressures_pct_role")
        + 0.10 * _safe_get(row, "ball_recoveries_pct_role")
    )
    pace_raw = (
        0.35 * _safe_get(row, "prog_carries_pct_role")
        + 0.30 * _safe_get(row, "prog_passes_pct_role")
        + 0.20 * _safe_get(row, "dribbles_pct_role")
        + 0.15 * _safe_get(row, "minutes_share")
    )
    aura_raw = (
        0.40 * (
            (_safe_get(row, "tackles_pct_role") + _safe_get(row, "interceptions_pct_role")
             + _safe_get(row, "clearances_pct_role") + _safe_get(row, "aerials_pct_role")) / 4.0
        )
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "clean_sheets_pct_role")
    )
    stamina_raw = (
        0.30 * _safe_get(row, "pressures_pct_role")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.20 * _safe_get(row, "ball_recoveries_pct_role")
        + 0.20 * _safe_get(row, "aerial_duel_success_pct_role")
    )
    mental_raw = (
        0.30 * _safe_get(row, "pass_completion_pct_role")
        + 0.25 * _safe_get(row, "aerial_duel_success_pct_role")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
        + 0.20 * _safe_get(row, "clean_sheets_pct_role")
    )

    att = _scale(att_raw, confidence, base=30, rng=35)  # compressed for DF
    defense = _scale(def_raw, confidence)
    pace = _scale(pace_raw, confidence)
    aura = _scale(aura_raw, confidence)
    stamina = _scale(stamina_raw, confidence)
    mental = _scale(mental_raw, confidence)

    # DF base: ATT 5% DEF 35% PACE 10% AURA 15% STA 15% MEN 20%
    raws = {"att": att_raw, "def": def_raw, "pace": pace_raw,
            "aura": aura_raw, "stamina": stamina_raw, "mental": mental_raw}
    base_w = {"att": 0.05, "def": 0.35, "pace": 0.10,
              "aura": 0.15, "stamina": 0.15, "mental": 0.20}
    overall_raw = _adaptive_overall(raws, base_w)
    overall = _scale(overall_raw, confidence)

    return {
        "att": att, "def": defense, "pace": pace,
        "aura": aura, "stamina": stamina, "mental": mental,
        "overall": overall,
        "_raws": {**raws, "overall": overall_raw},
    }


# ═══════════════════════════════════════════════════════════════
# GOALKEEPER
# ═══════════════════════════════════════════════════════════════

def rate_goalkeeper(row: pd.Series, confidence: float) -> dict:
    """GK: DEF/MENTAL dominant, ATT fixed 30, PACE minimal."""
    att_raw = 0.0  # GK has no attacking contribution

    def_raw = (
        0.30 * _safe_get(row, "gk_psxg_diff_pct_role")
        + 0.25 * _safe_get(row, "gk_saves_pct_role")
        + 0.20 * _safe_get(row, "clean_sheets_pct_role")
        + 0.15 * _safe_get(row, "gk_crosses_stopped_pct_role")
        + 0.10 * _safe_get(row, "aerials_pct_role")
    )
    pace_raw = (
        0.40 * _safe_get(row, "prog_passes_pct_role")
        + 0.30 * _safe_get(row, "gk_pass_completion_pct_role", 0.5)
        + 0.30 * _safe_get(row, "gk_launch_pct_role")
    )
    aura_raw = (
        0.35 * _safe_get(row, "clean_sheets_pct_role")
        + 0.35 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "gk_saves_pct_role")
    )
    stamina_raw = (
        0.40 * _safe_get(row, "minutes_share")
        + 0.30 * _safe_get(row, "clean_sheets_pct_role")
        + 0.30 * _safe_get(row, "gk_crosses_stopped_pct_role")
    )
    mental_raw = (
        0.30 * _safe_get(row, "gk_psxg_diff_pct_role")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
        + 0.25 * _safe_get(row, "clean_sheets_pct_role")
        + 0.20 * _safe_get(row, "gk_pass_completion_pct_role", 0.5)
    )

    att = _scale(att_raw, confidence, base=30, rng=20)  # fixed ~30
    defense = _scale(def_raw, confidence)
    pace = _scale(pace_raw, confidence)
    aura = _scale(aura_raw, confidence)
    stamina = _scale(stamina_raw, confidence)
    mental = _scale(mental_raw, confidence)

    # GK base: ATT 0% DEF 40% PACE 5% AURA 15% STA 10% MEN 30%
    raws = {"att": att_raw, "def": def_raw, "pace": pace_raw,
            "aura": aura_raw, "stamina": stamina_raw, "mental": mental_raw}
    base_w = {"att": 0.00, "def": 0.40, "pace": 0.05,
              "aura": 0.15, "stamina": 0.10, "mental": 0.30}
    overall_raw = _adaptive_overall(raws, base_w)
    overall = _scale(overall_raw, confidence)

    return {
        "att": att, "def": defense, "pace": pace,
        "aura": aura, "stamina": stamina, "mental": mental,
        "overall": overall,
        "_raws": {**raws, "overall": overall_raw},
    }


# ═══════════════════════════════════════════════════════════════
# DISPATCH + PIPELINE
# ═══════════════════════════════════════════════════════════════

ROLE_RATERS = {
    "FW": rate_forward,
    "MF": rate_midfielder,
    "DF": rate_defender,
    "GK": rate_goalkeeper,
}

# Stat names (v2.0)
STAT_NAMES = ["att", "def", "pace", "aura", "stamina", "mental"]


def compute_ratings(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute ratings for all players in the features DataFrame."""
    results = []

    for _, row in features_df.iterrows():
        role = row.get("role_bucket", row.get("primary_position", "FW"))
        rater = ROLE_RATERS.get(role)
        if rater is None:
            continue

        league_id = row.get("league_id", row.get("competition_id", ""))
        row_adj = row.copy()
        pct_cols = [c for c in row.index if c.endswith("_pct_role")]
        for col in pct_cols:
            if pd.notna(row_adj[col]):
                row_adj[col] = apply_league_adjustment(float(row_adj[col]), str(league_id))

        team_success = float(row_adj.get("team_success_pct", 0.5))
        if pd.notna(row_adj.get("team_goal_contribution")):
            row_adj["team_goal_contribution"] = debias_team_feature(
                float(row_adj["team_goal_contribution"]), team_success
            )
        if pd.notna(row_adj.get("team_success_pct")):
            row_adj["team_success_pct"] = debias_team_feature(
                float(row_adj["team_success_pct"]), team_success
            )

        confidence = compute_confidence(int(row_adj.get("minutes_played", 0)))
        scores = rater(row_adj, confidence)
        explanation = _build_explanation(row, scores, role)
        tier = score_to_tier(scores["overall"])

        results.append({
            "player_season_id": row.get("player_season_id", ""),
            "player_id": row.get("player_id", ""),
            "club_id": row.get("club_id", ""),
            "season_id": row.get("season_id", ""),
            "role_bucket": role,
            "att_score": round(scores["att"], 1),
            "def_score": round(scores["def"], 1),
            "pace_score": round(scores["pace"], 1),
            "aura_score": round(scores["aura"], 1),
            "stamina_score": round(scores["stamina"], 1),
            "mental_score": round(scores["mental"], 1),
            "overall_score": round(scores["overall"], 1),
            "confidence_score": confidence,
            "tier_label": tier.value,
            "explanation_json": json.dumps(explanation, ensure_ascii=False),
            "formula_version": "v2",
            "generated_at": datetime.now().isoformat(),
        })

    return pd.DataFrame(results)


def _build_explanation(row: pd.Series, scores: dict, role: str) -> dict:
    """Generate human-readable explanation."""
    raws = scores["_raws"]
    explanation: dict = {}

    drivers_map = {
        "att": [("goals/90 pct", "goals_pct_role"), ("xG/90 pct", "xg_pct_role")],
        "def": [("tackles/90 pct", "tackles_pct_role"), ("pressures/90 pct", "pressures_pct_role")],
        "pace": [("prog carries pct", "prog_carries_pct_role"), ("dribbles pct", "dribbles_pct_role")],
        "aura": [("minutes share", "minutes_share"), ("contribution", "team_goal_contribution")],
        "stamina": [("pressures pct", "pressures_pct_role"), ("minutes share", "minutes_share")],
        "mental": [("pass completion pct", "pass_completion_pct_role"), ("team success", "team_success_pct")],
    }

    for dim in STAT_NAMES:
        drivers = []
        for label, col in drivers_map.get(dim, []):
            val = _safe_get(row, col)
            drivers.append(f"{label}: {val:.0%}")
        explanation[dim] = {
            "score": round(scores[dim]),
            "raw": round(raws.get(dim, 0), 3),
            "drivers": drivers,
        }

    explanation["overall_summary"] = (
        f"{scores['overall']:.0f} overall, {score_to_tier(scores['overall']).value} tier"
    )
    return explanation
