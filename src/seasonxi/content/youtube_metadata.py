"""SeasonXI — YouTube Metadata Generator

Utility functions for generating YouTube Shorts titles, descriptions, and tags.
These are thin, composable helpers that can be called directly or via the API.

Usage:
    from seasonxi.content.youtube_metadata import generate_title, generate_description, generate_tags
"""
from __future__ import annotations


_TIER_EMOJI: dict[str, str] = {
    "MYTHIC": "👑",
    "LEGENDARY": "🔥",
    "ELITE": "⚡",
    "GOLD": "💛",
}


def generate_title(player_name: str, season: str, tier: str) -> str:
    """YouTube Shorts title generator.

    Args:
        player_name: Display name (e.g. "Karim Benzema")
        season: Season label (e.g. "2021-22")
        tier: Tier string (e.g. "LEGENDARY")

    Returns:
        Formatted YouTube title string.
    """
    emoji = _TIER_EMOJI.get(tier.upper(), "⚽")
    return f"{player_name} {season} was INSANE {emoji} | SeasonXI #{tier.upper()}"


def generate_description(
    player_name: str,
    season: str,
    goals: int,
    assists: int,
    tier: str,
) -> str:
    """YouTube Shorts description generator.

    Args:
        player_name: Display name (e.g. "Karim Benzema")
        season: Season label (e.g. "2021-22")
        goals: Goals scored that season
        assists: Assists that season
        tier: Tier string (e.g. "LEGENDARY")

    Returns:
        Multi-line description string with hashtags.
    """
    return (
        f"{player_name}'s {season} season rated by data. "
        f"{goals} goals, {assists} assists. Grade: {tier.upper()}.\n\n"
        f"#SeasonXI #Football #Shorts"
    )


def generate_tags(player_name: str, club: str, season: str) -> list[str]:
    """YouTube tags list generator.

    Args:
        player_name: Display name (e.g. "Karim Benzema")
        club: Club name (e.g. "Real Madrid")
        season: Season label (e.g. "2021-22")

    Returns:
        List of tag strings (no # prefix).
    """
    last = player_name.split()[-1].lower()
    slug = player_name.lower().replace(" ", "")
    club_slug = club.lower().replace(" ", "")
    return [
        "seasonxi",
        "football",
        "soccer",
        "shorts",
        last,
        slug,
        club_slug,
        f"{last} {season}",
        f"{last} season review",
        "football card",
        "player rating",
        "best season",
        "football highlights",
        "football analysis",
    ]
