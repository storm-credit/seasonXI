"""V1 Rule-Based Rating Engine (SXI Engine).

Score formula: score = 50 + 49 * raw * confidence
- raw is a weighted sum of percentile inputs (0.0–1.0)
- confidence = min(1.0, (minutes/1800)^0.7) — non-linear, penalizes low minutes
- Output range: 50–99 (with confidence=1.0)
- Defense for FW is slightly compressed: 40 + 40 * raw * confidence

Research basis:
- PlayeRank (Pappalardo 2019): role-aware multi-dimensional evaluation
- Wolf et al. (2020): percentile-based player rating system
- VAEP (Decroos 2019): xG/xA as indirect action-value proxies
"""

from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from seasonxi.constants import SCORE_BASE, SCORE_RANGE, score_to_tier
from seasonxi.ratings.confidence import compute_confidence


def _scale(raw: float, confidence: float, base: int = SCORE_BASE, rng: int = SCORE_RANGE) -> float:
    """Scale a 0–1 raw score to card score."""
    return base + rng * max(0.0, min(1.0, raw)) * confidence


def _safe_get(row: pd.Series, col: str, default: float = 0.0) -> float:
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return float(val)


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
    defense_raw = (
        0.40 * _safe_get(row, "tackles_pct_role")
        + 0.30 * _safe_get(row, "interceptions_pct_role")
        + 0.30 * _safe_get(row, "minutes_share")
    )
    clutch_raw = (
        0.45 * _safe_get(row, "team_goal_contribution")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
    )

    # Aura uses average of other raws as performance proxy
    perf_proxy = (finishing_raw + creation_raw + control_raw) / 3.0
    role_dominance = (
        _safe_get(row, "goals_pct_role")
        + _safe_get(row, "xg_pct_role")
        + _safe_get(row, "shots_pct_role")
        + _safe_get(row, "dribbles_pct_role")
    ) / 4.0
    aura_raw = (
        0.35 * perf_proxy
        + 0.25 * _safe_get(row, "team_success_pct", 0.5)
        + 0.20 * _safe_get(row, "minutes_share")
        + 0.20 * role_dominance
    )

    finishing = _scale(finishing_raw, confidence)
    creation = _scale(creation_raw, confidence)
    control = _scale(control_raw, confidence)
    defense = _scale(defense_raw, confidence, base=40, rng=40)  # compressed for FW
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
        "finishing": finishing,
        "creation": creation,
        "control": control,
        "defense": defense,
        "clutch": clutch,
        "aura": aura,
        "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


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
    defense_raw = (
        0.35 * _safe_get(row, "tackles_pct_role")
        + 0.30 * _safe_get(row, "interceptions_pct_role")
        + 0.15 * _safe_get(row, "clearances_pct_role")
        + 0.20 * _safe_get(row, "minutes_share")
    )
    clutch_raw = (
        0.35 * _safe_get(row, "team_goal_contribution")
        + 0.30 * _safe_get(row, "minutes_share")
        + 0.35 * _safe_get(row, "team_success_pct", 0.5)
    )

    perf_proxy = (finishing_raw + creation_raw + control_raw) / 3.0
    role_dominance = (
        _safe_get(row, "assists_pct_role")
        + _safe_get(row, "xa_pct_role")
        + _safe_get(row, "prog_passes_pct_role")
        + _safe_get(row, "key_passes_pct_role")
    ) / 4.0
    aura_raw = (
        0.30 * perf_proxy
        + 0.25 * control_raw
        + 0.20 * _safe_get(row, "team_success_pct", 0.5)
        + 0.25 * role_dominance
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
        "finishing": finishing,
        "creation": creation,
        "control": control,
        "defense": defense,
        "clutch": clutch,
        "aura": aura,
        "overall": overall,
        "_raws": {
            "finishing": finishing_raw, "creation": creation_raw,
            "control": control_raw, "defense": defense_raw,
            "clutch": clutch_raw, "aura": aura_raw, "overall": overall_raw,
        },
    }


ROLE_RATERS = {
    "FW": rate_forward,
    "MF": rate_midfielder,
}


def compute_ratings(features_df: pd.DataFrame) -> pd.DataFrame:
    """Compute ratings for all players in the features DataFrame."""
    results = []

    for _, row in features_df.iterrows():
        role = row.get("role_bucket", row.get("primary_position", "FW"))
        rater = ROLE_RATERS.get(role)
        if rater is None:
            continue  # DF/GK not supported in V1

        confidence = compute_confidence(int(row.get("minutes_played", 0)))
        scores = rater(row, confidence)

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
            "formula_version": "v1",
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
            drivers.append(f"interceptions/90 pct: {_safe_get(row, 'interceptions_pct_role'):.0%}")
        elif dim == "clutch":
            drivers.append(f"team goal contribution: {_safe_get(row, 'team_goal_contribution'):.0%}")
        elif dim == "aura":
            drivers.append(f"team success: {_safe_get(row, 'team_success_pct', 0.5):.0%}")

        explanation[dim] = {
            "score": round(scores[dim]),
            "raw": round(raw_val, 3),
            "drivers": drivers,
        }

    explanation["overall_summary"] = (
        f"{scores['overall']:.0f} overall, {score_to_tier(scores['overall']).value} tier"
    )
    return explanation
