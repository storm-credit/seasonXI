"""Generate 15-second Shorts edit scripts from SeasonCard data.

Structure (fixed for all videos):
  Scene 1 [0.0-1.8s]: Hook — player image + impact text
  Scene 2 [1.8-3.5s]: Card reveal — name, season, position
  Scene 3 [3.5-5.0s]: OVR pop — rating badge
  Scene 4 [5.0-9.2s]: Stat reveal — 6 stats one by one
  Scene 5 [9.2-12.5s]: Verdict — killer line + tier
  Scene 6 [12.5-15.0s]: End tag — SEASONXI + CTA
"""

from __future__ import annotations

import json
from pathlib import Path

# Hook templates by tier
HOOKS = {
    "Mythic": [
        "THIS VERSION WAS BROKEN",
        "THIS SEASON WAS ILLEGAL",
        "NOT HUMAN",
    ],
    "Legendary": [
        "PRIME VERSION UNLOCKED",
        "THIS WAS DIFFERENT",
        "LEGENDARY FORM",
    ],
    "Elite": [
        "ELITE SEASON INCOMING",
        "THIS VERSION HITS DIFFERENT",
        "UNDERRATED PEAK",
    ],
    "Gold": [
        "SOLID SEASON CARD",
        "BETTER THAN YOU REMEMBER",
        "QUALITY SEASON",
    ],
}

# CTA options
CTAS = [
    "WHO TOPS THIS?",
    "AGREE OR DISAGREE?",
    "DROP YOUR RATING BELOW",
    "BETTER VERSION EXISTS?",
]

STAT_DISPLAY_NAMES = {
    "finishing": "Finishing",
    "creation": "Playmaking",
    "control": "Dribbling",
    "defense": "Defense",
    "clutch": "Clutch",
    "aura": "Aura",
}

STAT_ORDER = ["finishing", "creation", "control", "defense", "clutch", "aura"]


def generate_script(card: dict, verdict_line: str | None = None) -> dict:
    """Generate a 15-second Shorts script from a card JSON.

    Args:
        card: CardOutput dict with player, season, club, overall, stats, tier
        verdict_line: Optional custom final verdict. Auto-generated if None.

    Returns:
        Script dict with scenes, timing, and text.
    """
    player = card["player"]
    season = card["season"]
    club = card["club"]
    role = card["role"]
    overall = card["overall"]
    tier = card["tier"]

    # Auto-generate verdict if not provided
    if not verdict_line:
        verdict_line = _auto_verdict(card)

    # Pick hook
    tier_hooks = HOOKS.get(tier, HOOKS["Gold"])
    hook = tier_hooks[0]  # Use first option by default

    # Build stat reveal sequence
    stat_reveals = []
    stat_start = 5.0
    for i, key in enumerate(STAT_ORDER):
        stat_reveals.append({
            "time": round(stat_start + i * 0.7, 1),
            "label": STAT_DISPLAY_NAMES[key],
            "value": card.get(key, card.get(f"{key}_score", 0)),
        })

    script = {
        "player": player,
        "season": season,
        "club": club,
        "total_duration": 15.0,
        "scenes": [
            {
                "id": "hook",
                "start": 0.0,
                "end": 1.8,
                "visual": f"Full-screen {player} image, push-in zoom, rain/particles",
                "text": hook,
                "audio": "Strong cinematic hit at 0.2s",
            },
            {
                "id": "card_reveal",
                "start": 1.8,
                "end": 3.5,
                "visual": "SeasonXI card frame slides in, player locks into frame",
                "text": f"{player.upper()}\n{season}\n{role}",
                "text_position": "top-left",
                "audio": "Short metallic reveal sound",
            },
            {
                "id": "ovr_reveal",
                "start": 3.5,
                "end": 5.0,
                "visual": "OVR badge lights up top-right, glow pulse",
                "text": f"OVR {overall}",
                "text_position": "top-right",
                "audio": "Heavy impact + gold flicker",
                "subtitle": f"{overall} overall. {tier} level.",
            },
            {
                "id": "stat_reveal",
                "start": 5.0,
                "end": 9.2,
                "visual": "Stats appear one by one with pop animation",
                "stats": stat_reveals,
                "audio": "Six rhythmic ticks on BGM beat",
            },
            {
                "id": "verdict",
                "start": 9.2,
                "end": 12.5,
                "visual": "Slight zoom toward player, background darkens",
                "text": f"{verdict_line}\n{tier.upper()} SEASON",
                "text_position": "center",
                "audio": "Strong rise then controlled drop",
            },
            {
                "id": "end_tag",
                "start": 12.5,
                "end": 15.0,
                "visual": "Card stays on screen, soft fade",
                "text": "SEASONXI",
                "cta": CTAS[0],
                "audio": "Short branded ending sting",
            },
        ],
        "subtitle_script": _build_subtitle(player, season, overall, stat_reveals, verdict_line, tier),
    }

    return script


def _auto_verdict(card: dict) -> str:
    """Generate a verdict line based on stats."""
    player = card["player"]
    goals = card.get("goals", 0)
    assists = card.get("assists", 0)
    overall = card["overall"]

    if overall >= 95:
        if goals >= 40:
            return f"{goals} LEAGUE GOALS"
        elif goals >= 25:
            return f"{goals} GOALS. PURE DOMINANCE."
        else:
            return "ABSOLUTE PEAK"
    elif overall >= 90:
        if goals >= 20:
            return f"{goals}G {assists}A. LEGENDARY."
        return "LEGENDARY FORM"
    elif overall >= 84:
        return f"{goals}G {assists}A. ELITE LEVEL."
    else:
        return f"{goals}G {assists}A. SOLID GOLD."


def _build_subtitle(player, season, overall, stats, verdict, tier):
    """Build the full subtitle text for the video."""
    lines = []
    lines.append(f"This version was different.")
    lines.append(f"{player}. {season}.")
    lines.append(f"{overall} overall.")
    for s in stats:
        lines.append(f"{s['label']} {s['value']}.")
    lines.append(f"{verdict}.")
    lines.append(f"{tier} season.")
    return " ".join(lines)


def export_script(card: dict, output_dir: Path = Path("outputs/scripts")) -> Path:
    """Generate and save a Shorts script."""
    output_dir.mkdir(parents=True, exist_ok=True)
    script = generate_script(card)

    slug = card["player"].lower().replace(" ", "-")
    season_slug = card["season"].replace("/", "-")
    filename = f"{slug}_{season_slug}_script.json"
    filepath = output_dir / filename

    filepath.write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    return filepath


if __name__ == "__main__":
    # Test with sample Messi card
    sample = {
        "player": "Lionel Messi",
        "season": "2011/12",
        "club": "FC Barcelona",
        "role": "RW",
        "overall": 97,
        "finishing": 97,
        "creation": 95,
        "control": 99,
        "defense": 55,
        "clutch": 98,
        "aura": 99,
        "tier": "Mythic",
        "goals": 50,
        "assists": 16,
    }
    script = generate_script(sample, verdict_line="50 LEAGUE GOALS")
    print(json.dumps(script, indent=2))
