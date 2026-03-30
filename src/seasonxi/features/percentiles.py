"""Compute within-role percentile rankings.

v1.2: Added pressures, ball_recoveries, pass_completion, aerial_duel_success,
      goals_minus_xg, clean_sheets, and GK-specific percentiles.
"""

import pandas as pd

# Per-90 stats to rank (source_col, output_col)
PERCENTILE_STATS = [
    # Attacking
    ("goals_p90", "goals_pct_role"),
    ("assists_p90", "assists_pct_role"),
    ("xg_p90", "xg_pct_role"),
    ("xa_p90", "xa_pct_role"),
    ("shots_p90", "shots_pct_role"),
    # Creation / Control
    ("key_passes_p90", "key_passes_pct_role"),
    ("prog_passes_p90", "prog_passes_pct_role"),
    ("prog_carries_p90", "prog_carries_pct_role"),
    ("dribbles_p90", "dribbles_pct_role"),
    # Defense
    ("tackles_p90", "tackles_pct_role"),
    ("interceptions_p90", "interceptions_pct_role"),
    ("clearances_p90", "clearances_pct_role"),
    ("aerials_won_p90", "aerials_pct_role"),
    # v1.2: New features
    ("pressures_p90", "pressures_pct_role"),
    ("ball_recoveries_p90", "ball_recoveries_pct_role"),
    ("goals_minus_xg_p90", "goals_minus_xg_pct_role"),
    # Rate-based (not per90, already 0-1 range but still rank within role)
    ("pressure_success_rate", "pressure_success_pct_role"),
    ("aerial_duel_success_rate", "aerial_duel_success_pct_role"),
    ("pass_completion_rate", "pass_completion_pct_role"),
    # Clean sheets (per90)
    ("clean_sheets_p90", "clean_sheets_pct_role"),
]

# GK-specific stats (only ranked among GKs)
GK_PERCENTILE_STATS = [
    ("gk_saves_p90", "gk_saves_pct_role"),
    ("gk_psxg_diff_p90", "gk_psxg_diff_pct_role"),
    ("gk_crosses_stopped_p90", "gk_crosses_stopped_pct_role"),
    ("gk_pass_completion_rate", "gk_pass_completion_pct_role"),
    ("gk_launch_rate", "gk_launch_pct_role"),
]


def compute_percentiles(
    df: pd.DataFrame,
    group_col: str = "primary_position",
) -> pd.DataFrame:
    """Rank each per-90 stat within position group as 0.0–1.0 percentile.

    If only one player exists in a group, they get percentile 0.5.
    With few players, percentile ranking is rough but still usable for MVP.
    """
    out = df.copy()

    # Standard percentiles (all positions)
    for p90_col, pct_col in PERCENTILE_STATS:
        if p90_col not in out.columns:
            out[pct_col] = 0.5
            continue

        out[pct_col] = out.groupby(group_col)[p90_col].rank(pct=True, method="average")
        out[pct_col] = out[pct_col].fillna(0.5)

    # GK-specific percentiles (only among GKs)
    for p90_col, pct_col in GK_PERCENTILE_STATS:
        if p90_col not in out.columns:
            out[pct_col] = 0.5
            continue

        # Only rank GKs, others get 0.5
        gk_mask = out[group_col] == "GK"
        out[pct_col] = 0.5
        if gk_mask.any():
            out.loc[gk_mask, pct_col] = (
                out.loc[gk_mask, p90_col].rank(pct=True, method="average").fillna(0.5)
            )

    return out
