"""Player, Club, Season entity models."""

from datetime import date

from pydantic import BaseModel


class Player(BaseModel):
    player_id: str
    player_name: str
    birth_date: date | None = None
    nationality: str = ""
    dominant_foot: str = ""


class Club(BaseModel):
    club_id: str
    club_name: str
    country: str = ""
    league_name: str = ""


class Season(BaseModel):
    season_id: str  # e.g. "2021-2022"
    season_label: str  # e.g. "2021/22"
    start_year: int
    end_year: int
