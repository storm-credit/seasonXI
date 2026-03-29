"""Map overall score to tier label."""

from seasonxi.constants import Tier, score_to_tier


def assign_tier(overall_score: float) -> Tier:
    """Assign tier based on overall score."""
    return score_to_tier(overall_score)
