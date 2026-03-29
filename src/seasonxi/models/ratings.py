"""Rating output model — Layer C."""

from datetime import datetime

from pydantic import BaseModel, Field


class SeasonXIRating(BaseModel):
    player_season_id: str
    player_id: str
    club_id: str
    season_id: str

    role_bucket: str
    role_subtype: str = ""

    finishing_score: float = Field(ge=0, le=99)
    creation_score: float = Field(ge=0, le=99)
    control_score: float = Field(ge=0, le=99)
    defense_score: float = Field(ge=0, le=99)
    clutch_score: float = Field(ge=0, le=99)
    aura_score: float = Field(ge=0, le=99)
    overall_score: float = Field(ge=0, le=99)

    confidence_score: float = Field(ge=0, le=1)
    tier_label: str  # Mythic / Legendary / Elite / Gold / Silver / Bronze

    explanation_json: str = "{}"
    formula_version: str = "v1"
    generated_at: datetime = Field(default_factory=datetime.now)


class CardOutput(BaseModel):
    """Public-facing card JSON for content generation."""

    player: str
    season: str
    club: str
    role: str
    overall: int
    finishing: int
    creation: int
    control: int
    defense: int
    clutch: int
    aura: int
    tier: str
    confidence: float
    explanation: dict | None = None
