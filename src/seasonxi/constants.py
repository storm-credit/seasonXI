"""Core enumerations and constants for SeasonXI."""

from enum import Enum


class RoleBucket(str, Enum):
    FW = "FW"
    MF = "MF"
    DF = "DF"
    GK = "GK"


class LeagueId(str, Enum):
    ENG1 = "ENG1"
    ESP1 = "ESP1"
    GER1 = "GER1"
    ITA1 = "ITA1"
    FRA1 = "FRA1"


class Tier(str, Enum):
    MYTHIC = "Mythic"
    LEGENDARY = "Legendary"
    ELITE = "Elite"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"


# Tier thresholds (overall score >= threshold)
TIER_THRESHOLDS: list[tuple[int, Tier]] = [
    (95, Tier.MYTHIC),
    (90, Tier.LEGENDARY),
    (84, Tier.ELITE),
    (76, Tier.GOLD),
    (68, Tier.SILVER),
    (0, Tier.BRONZE),
]


def score_to_tier(overall: float) -> Tier:
    """Map an overall score to a tier label."""
    for threshold, tier in TIER_THRESHOLDS:
        if overall >= threshold:
            return tier
    return Tier.BRONZE


# Minimum minutes for full confidence
CONFIDENCE_MINUTES_CAP = 1800

# Score scaling constants
SCORE_BASE = 50
SCORE_RANGE = 49
