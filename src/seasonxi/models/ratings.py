"""Rating output model — Layer C (v2.0: ATT/DEF/PACE/AURA/STAMINA/MENTAL)."""

from datetime import datetime

from pydantic import BaseModel, Field


class SeasonXIRating(BaseModel):
    player_season_id: str
    player_id: str
    club_id: str
    season_id: str

    role_bucket: str
    role_subtype: str = ""

    att_score: float = Field(ge=0, le=99)
    def_score: float = Field(ge=0, le=99)
    pace_score: float = Field(ge=0, le=99)
    aura_score: float = Field(ge=0, le=99)
    stamina_score: float = Field(ge=0, le=99)
    mental_score: float = Field(ge=0, le=99)
    overall_score: float = Field(ge=0, le=99)

    confidence_score: float = Field(ge=0, le=1)
    tier_label: str  # Mythic / Legendary / Elite / Gold / Silver / Bronze

    explanation_json: str = "{}"
    formula_version: str = "v2"
    generated_at: datetime = Field(default_factory=datetime.now)


class CardOutput(BaseModel):
    """Public-facing card JSON for content generation."""

    player: str
    season: str
    club: str
    role: str
    overall: int
    att: int
    defense: int
    pace: int
    aura: int
    stamina: int
    mental: int
    tier: str
    confidence: float
    explanation: dict | None = None
