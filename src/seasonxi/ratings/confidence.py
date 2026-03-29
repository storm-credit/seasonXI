"""Confidence score based on playing time."""

from seasonxi.constants import CONFIDENCE_MINUTES_CAP


def compute_confidence(minutes_played: int) -> float:
    """Confidence = min(1.0, minutes / 1800).

    - 900 min → 0.50
    - 1800 min → 1.00 (cap)
    """
    return min(1.0, minutes_played / CONFIDENCE_MINUTES_CAP)
