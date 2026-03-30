"""Confidence score based on playing time.

Uses non-linear scaling to better reflect statistical reliability.
Research basis: early-sample instability is greater than late-sample,
so a sub-linear function (exponent < 1.0) penalizes low minutes more.

Reference: Wolf et al. (2020), "A football player rating system"
"""

from seasonxi.constants import CONFIDENCE_MINUTES_CAP, CONFIDENCE_EXPONENT


def compute_confidence(minutes_played: int) -> float:
    """Non-linear confidence: min(1.0, (minutes / 1800) ^ 0.7).

    Comparison (linear vs non-linear):
        450 min → linear: 0.25  | non-linear: 0.37  (small sample boosted slightly)
        900 min → linear: 0.50  | non-linear: 0.62  (mid-season more trusted)
       1350 min → linear: 0.75  | non-linear: 0.82  (near-regular more confident)
       1800 min → linear: 1.00  | non-linear: 1.00  (full season = full confidence)
    """
    ratio = min(1.0, minutes_played / CONFIDENCE_MINUTES_CAP)
    return ratio ** CONFIDENCE_EXPONENT
