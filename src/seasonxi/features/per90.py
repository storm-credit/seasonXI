"""Convert counting stats to per-90-minute rates."""

import pandas as pd

# Stats to convert to per-90
COUNTING_STATS = [
    "goals", "assists", "shots", "shots_on_target",
    "key_passes", "progressive_passes", "progressive_carries", "successful_dribbles",
    "tackles", "interceptions", "clearances", "aerial_duels_won",
    # v1.2 additions
    "pressures", "successful_pressures", "ball_recoveries",
    "aerials_won", "aerials_lost",  # for duel success rate
]

# Mapping from raw column to per90 column
P90_MAP = {s: f"{s.replace('successful_', '').replace('_duels_won', 's_won')}_p90" for s in COUNTING_STATS}
# Fix names to match feature model
P90_MAP["goals"] = "goals_p90"
P90_MAP["assists"] = "assists_p90"
P90_MAP["shots"] = "shots_p90"
P90_MAP["shots_on_target"] = "shots_on_target_p90"
P90_MAP["key_passes"] = "key_passes_p90"
P90_MAP["progressive_passes"] = "prog_passes_p90"
P90_MAP["progressive_carries"] = "prog_carries_p90"
P90_MAP["successful_dribbles"] = "dribbles_p90"
P90_MAP["tackles"] = "tackles_p90"
P90_MAP["interceptions"] = "interceptions_p90"
P90_MAP["clearances"] = "clearances_p90"
P90_MAP["aerial_duels_won"] = "aerials_won_p90"
P90_MAP["pressures"] = "pressures_p90"
P90_MAP["successful_pressures"] = "successful_pressures_p90"
P90_MAP["ball_recoveries"] = "ball_recoveries_p90"
P90_MAP["aerials_won"] = "aerials_won_p90_v2"  # alternate source
P90_MAP["aerials_lost"] = "aerials_lost_p90"


def compute_per90(df: pd.DataFrame, min_minutes: int = 450) -> pd.DataFrame:
    """Add per-90 columns to a DataFrame of raw stats.

    Players with fewer than min_minutes are excluded.
    """
    out = df[df["minutes_played"] >= min_minutes].copy()
    nineties = out["minutes_played"] / 90.0

    for raw_col, p90_col in P90_MAP.items():
        if raw_col in out.columns:
            out[p90_col] = out[raw_col] / nineties

    # xG and xA are already rates but stored as totals — convert to per90
    if "xg" in out.columns:
        out["xg_p90"] = out["xg"] / nineties
    if "xa" in out.columns:
        out["xa_p90"] = out["xa"] / nineties

    # Derived: goal involvement per 90
    out["goal_involvement_per90"] = out["goals_p90"] + out["assists_p90"]

    # Team goal contribution: (goals + assists) / team_goals_scored
    if "team_goals_scored" in out.columns:
        out["team_goal_contribution"] = (
            (out["goals"] + out["assists"]) / out["team_goals_scored"].clip(lower=1)
        )
    else:
        out["team_goal_contribution"] = 0.0

    # Minutes share: minutes / (team matches * 90)
    # Approximate: assume 38-match league
    out["minutes_share"] = out["minutes_played"] / (38 * 90)

    # --- v1.2: New derived features ---

    # Goals - xG: finishing quality (positive = overperformer)
    if "xg" in out.columns and "goals" in out.columns:
        out["goals_minus_xg"] = out["goals"] - out["xg"]
        out["goals_minus_xg_p90"] = out["goals_minus_xg"] / nineties

    # Pressure success rate (0.0-1.0)
    if "pressures" in out.columns and "successful_pressures" in out.columns:
        out["pressure_success_rate"] = (
            out["successful_pressures"] / out["pressures"].clip(lower=1)
        )
        out["pressures_p90"] = out["pressures"] / nineties

    # Duel success rate (aerial)
    if "aerials_won" in out.columns and "aerials_lost" in out.columns:
        total_aerials = out["aerials_won"] + out["aerials_lost"]
        out["aerial_duel_success_rate"] = (
            out["aerials_won"] / total_aerials.clip(lower=1)
        )

    # Pass completion rate (if available)
    if "passes_completed" in out.columns and "passes_attempted" in out.columns:
        out["pass_completion_rate"] = (
            out["passes_completed"] / out["passes_attempted"].clip(lower=1)
        )

    return out
