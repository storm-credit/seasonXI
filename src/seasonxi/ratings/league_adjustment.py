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
    # Standard IDs
    "ENG1": 1.04, "ESP1": 1.02, "GER1": 1.00, "ITA1": 1.01, "FRA1": 0.92,
    # Alternative names (from FBref/merge pipeline)
    "epl": 1.04, "laliga": 1.02, "bundesliga": 1.00, "seriea": 1.01, "ligue1": 0.92,
    # Full names
    "Premier League": 1.04, "La Liga": 1.02, "Bundesliga": 1.00, "Serie A": 1.01, "Ligue 1": 0.92,
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
