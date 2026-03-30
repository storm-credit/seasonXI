"""Team debiasing for individual player ratings.

Problem: Players on dominant teams (e.g., Man City, Bayern) get inflated
scores because team_success_pct and team_goal_contribution are high
regardless of individual quality.

Solution: Apply a dampening factor to team-derived features so that
individual skill signals are not drowned by team environment.

Reference: Debiased ML approaches in sports analytics (ACM KDD 2023)
"""

from __future__ import annotations


# How much to dampen team-derived features (0.0 = ignore team, 1.0 = full team effect)
TEAM_DAMPENING_FACTOR = 0.7


def debias_team_feature(value: float, team_strength_pct: float) -> float:
    """Reduce the influence of team quality on individual features.

    For a player on a dominant team (team_strength_pct ~ 0.9+),
    their team-derived features get slightly reduced.

    For a player on a weak team (team_strength_pct ~ 0.2),
    their individual contribution is slightly boosted.

    Args:
        value: The raw feature value (0.0–1.0)
        team_strength_pct: Team's league position percentile (0.0=worst, 1.0=best)
    """
    # Team bias = how far from average (0.5) the team is
    team_bias = team_strength_pct - 0.5  # range: -0.5 to +0.5

    # Apply dampening: reduce the team effect
    adjustment = team_bias * (1.0 - TEAM_DAMPENING_FACTOR)

    # Strong team → slight reduction, weak team → slight boost
    debiased = value - adjustment

    return max(0.0, min(1.0, debiased))


def debias_row_features(
    team_goal_contribution: float,
    team_success_pct: float,
    minutes_share: float,
) -> dict:
    """Apply debiasing to all team-influenced features.

    Returns dict with debiased versions.
    """
    return {
        "team_goal_contribution": debias_team_feature(
            team_goal_contribution, team_success_pct
        ),
        "team_success_pct": debias_team_feature(
            team_success_pct, team_success_pct
        ),
        # minutes_share is less team-dependent, apply lighter debiasing
        "minutes_share": minutes_share,  # keep as-is
    }
