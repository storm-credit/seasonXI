"""Normalized feature model — Layer B."""

from pydantic import BaseModel


class PlayerSeasonFeatures(BaseModel):
    player_season_id: str
    player_id: str
    club_id: str
    season_id: str

    role_bucket: str  # FW, MF, DF, GK
    role_subtype: str = ""

    minutes_played: int
    appearances: int = 0

    # Per-90 rates
    goals_p90: float = 0.0
    assists_p90: float = 0.0
    xg_p90: float = 0.0
    xa_p90: float = 0.0
    shots_p90: float = 0.0
    key_passes_p90: float = 0.0
    prog_passes_p90: float = 0.0
    prog_carries_p90: float = 0.0
    dribbles_p90: float = 0.0
    tackles_p90: float = 0.0
    interceptions_p90: float = 0.0
    clearances_p90: float = 0.0
    aerials_won_p90: float = 0.0

    # Derived
    goal_involvement_per90: float = 0.0
    team_goal_contribution: float = 0.0  # share of team goal involvement
    minutes_share: float = 0.0  # minutes / possible team minutes

    # Context
    league_strength_factor: float = 1.0
    season_era_factor: float = 1.0

    # Within-role percentiles (0.0 to 1.0)
    goals_pct_role: float = 0.0
    assists_pct_role: float = 0.0
    xg_pct_role: float = 0.0
    xa_pct_role: float = 0.0
    shots_pct_role: float = 0.0
    key_passes_pct_role: float = 0.0
    prog_passes_pct_role: float = 0.0
    prog_carries_pct_role: float = 0.0
    dribbles_pct_role: float = 0.0
    tackles_pct_role: float = 0.0
    interceptions_pct_role: float = 0.0
    clearances_pct_role: float = 0.0
    aerials_pct_role: float = 0.0
