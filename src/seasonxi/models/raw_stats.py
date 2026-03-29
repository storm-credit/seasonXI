"""Raw season stats model — Layer A (never overwrite)."""

from datetime import datetime

from pydantic import BaseModel


class PlayerSeasonStatsRaw(BaseModel):
    player_season_id: str
    player_id: str
    club_id: str
    season_id: str
    competition_scope: str = "league_only"

    primary_position: str  # FW, MF, DF, GK
    secondary_position: str = ""

    appearances: int = 0
    starts: int = 0
    minutes_played: int = 0

    goals: int = 0
    assists: int = 0
    shots: int = 0
    shots_on_target: int = 0

    key_passes: int = 0
    progressive_passes: int = 0
    progressive_carries: int = 0
    successful_dribbles: int = 0

    xg: float = 0.0
    xa: float = 0.0

    tackles: int = 0
    interceptions: int = 0
    clearances: int = 0
    aerial_duels_won: int = 0

    yellow_cards: int = 0
    red_cards: int = 0

    clean_sheets: int = 0
    team_goals_scored: int = 0
    team_goals_conceded: int = 0

    source_name: str = "manual"
    source_player_key: str = ""
    source_updated_at: datetime | None = None


class TeamSeasonStatsRaw(BaseModel):
    team_season_id: str
    club_id: str
    season_id: str
    competition_scope: str = "league_only"

    matches_played: int = 0
    team_goals: int = 0
    team_goals_conceded: int = 0
    points: int = 0
    final_table_rank: int = 0

    wins: int = 0
    draws: int = 0
    losses: int = 0
