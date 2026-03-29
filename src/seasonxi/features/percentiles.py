"""Compute within-role percentile rankings."""

import pandas as pd

# Per-90 stats to rank
PERCENTILE_STATS = [
    ("goals_p90", "goals_pct_role"),
    ("assists_p90", "assists_pct_role"),
    ("xg_p90", "xg_pct_role"),
    ("xa_p90", "xa_pct_role"),
    ("shots_p90", "shots_pct_role"),
    ("key_passes_p90", "key_passes_pct_role"),
    ("prog_passes_p90", "prog_passes_pct_role"),
    ("prog_carries_p90", "prog_carries_pct_role"),
    ("dribbles_p90", "dribbles_pct_role"),
    ("tackles_p90", "tackles_pct_role"),
    ("interceptions_p90", "interceptions_pct_role"),
    ("clearances_p90", "clearances_pct_role"),
    ("aerials_won_p90", "aerials_pct_role"),
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

    for p90_col, pct_col in PERCENTILE_STATS:
        if p90_col not in out.columns:
            out[pct_col] = 0.5
            continue

        out[pct_col] = out.groupby(group_col)[p90_col].rank(pct=True, method="average")
        # Fill NaN (e.g., single player in group) with 0.5
        out[pct_col] = out[pct_col].fillna(0.5)

    return out
