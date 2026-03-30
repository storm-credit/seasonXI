"""League strength adjustment for cross-league comparison.

Different leagues have different competitive depths. A top performer
in Ligue 1 might not be directly comparable to one in the Premier League.

Approach: UEFA coefficient-inspired multipliers applied as a small bonus/penalty
to raw scores before scaling. This is NOT a definitive ranking — it's a
context adjustment to reduce obvious distortions.

The multipliers are conservative (±5% max) to avoid over-correction.
"""

from __future__ import annotations

# League strength multipliers (relative to average = 1.0)
# Based on 5-year UEFA coefficient ratios, simplified
# Updated for ~2020-2024 window
LEAGUE_STRENGTH: dict[str, float] = {
    "ENG1": 1.05,   # Premier League — highest coefficient
    "ESP1": 1.03,   # La Liga — strong but slightly declined
    "GER1": 1.00,   # Bundesliga — baseline
    "ITA1": 1.02,   # Serie A — recovered strength
    "FRA1": 0.95,   # Ligue 1 — lower competitive depth
}

# Default if league unknown
DEFAULT_STRENGTH = 1.00


def get_league_multiplier(league_id: str) -> float:
    """Get the strength multiplier for a league."""
    return LEAGUE_STRENGTH.get(league_id, DEFAULT_STRENGTH)


def apply_league_adjustment(raw_score: float, league_id: str) -> float:
    """Apply league strength adjustment to a raw score.

    The adjustment is capped to prevent extreme distortion:
    - Max boost: +5% (EPL)
    - Max penalty: -5% (Ligue 1)
    - Result is clamped to [0.0, 1.0]
    """
    multiplier = get_league_multiplier(league_id)
    adjusted = raw_score * multiplier
    return max(0.0, min(1.0, adjusted))
