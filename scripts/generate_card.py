"""Generate SeasonXI card HTML + shorts script from a card JSON file.

Usage:
    uv run python scripts/generate_card.py data/cards/messi_2011-12.json
    uv run python scripts/generate_card.py data/cards/  (all cards in directory)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TEMPLATE = Path("src/seasonxi/content/card_template.html")
OUTPUT_DIR = Path("outputs/cards")


def load_card(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generate_card_html(card: dict) -> str:
    """Fill the HTML card template with card data."""
    html = TEMPLATE.read_text(encoding="utf-8")

    replacements = {
        "{{PLAYER_NAME}}": card["player"].upper(),
        "{{SEASON}}": card["season"],
        "{{POSITION}}": card["position"],
        "{{CLUB}}": card["club"],
        "{{OVR}}": str(card["ovr"]),
        "{{TIER}}": card["tier"].upper(),
        "{{TIER_CLASS}}": card["tier"].lower(),
        "{{TAGLINE}}": card.get("play_style", "")[:60],
        "{{FINISHING}}": str(card["stats"]["finishing"]),
        "{{CREATION}}": str(card["stats"]["playmaking"]),
        "{{CONTROL}}": str(card["stats"]["dribbling"]),
        "{{DEFENSE}}": str(card["stats"]["defense"]),
        "{{CLUTCH}}": str(card["stats"]["clutch"]),
        "{{AURA}}": str(card["stats"]["aura"]),
        "{{PLAYER_IMAGE}}": card.get("image", ""),
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    return html


def generate_shorts_script(card: dict) -> dict:
    """Generate 8-scene shorts script from card data."""
    s = card["stats"]
    # Find top 3 stats
    stat_pairs = sorted(s.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "player": card["player"],
        "season": card["season"],
        "club": card["club"],
        "total_duration": 15.0,
        "scenes": [
            {
                "id": "hook", "start": 0.0, "end": 1.5,
                "text": card["hook"],
                "sub": f"{card['player'].upper()} {card['season']}",
                "audio": "Strong cinematic hit",
            },
            {
                "id": "card_reveal", "start": 1.5, "end": 3.0,
                "text": f"{card['player'].upper()}\n{card['season']}\n{card['position']}",
                "club": card["club"],
                "audio": "Metallic reveal",
            },
            {
                "id": "ovr_shock", "start": 3.0, "end": 4.5,
                "text": f"OVR {card['ovr']}",
                "subtitle": f"{card['ovr']} overall. {card['tier']} level.",
                "audio": "Heavy impact + gold flicker",
            },
            {
                "id": "hex_graph", "start": 4.5, "end": 6.0,
                "stats": s,
                "audio": "Rising tension, electronic sweep",
            },
            {
                "id": "key_stats", "start": 6.0, "end": 8.0,
                "stats": [{"label": k.title(), "value": v} for k, v in stat_pairs],
                "audio": "Three rhythmic ticks",
            },
            {
                "id": "play_style", "start": 8.0, "end": 10.5,
                "text": card.get("play_style", ""),
                "audio": "BGM builds",
            },
            {
                "id": "achievement", "start": 10.5, "end": 12.5,
                "number": card.get("achievement_number", ""),
                "text": card["achievement"],
                "detail": card.get("achievement_detail", ""),
                "audio": "Strong rise + hit",
            },
            {
                "id": "verdict", "start": 12.5, "end": 15.0,
                "tier": card["tier"].upper(),
                "text": card["verdict"],
                "cta": card.get("cta", "AGREE OR DISAGREE?"),
                "audio": "Branded ending sting",
            },
        ],
    }


def generate_preview_html(card: dict) -> str:
    """Generate a standalone preview HTML for this card's shorts."""
    s = card["stats"]
    slug = card["player"].lower().replace(" ", "-")

    # Hex graph points calculation
    import math
    vals = [s["finishing"], s["playmaking"], s["defense"], s["clutch"], s["aura"], s["dribbling"]]
    cx, cy, r = 150, 150, 110
    angles = [-90, -30, 30, 90, 150, 210]
    pts = " ".join(
        f"{cx + r * (v/100) * math.cos(math.radians(a)):.1f},{cy + r * (v/100) * math.sin(math.radians(a)):.1f}"
        for v, a in zip(vals, angles)
    )

    # Find top 3
    stat_pairs = sorted(s.items(), key=lambda x: x[1], reverse=True)[:3]
    top3_html = "\n".join(
        f'          <div class="key-stat"><div class="val">{v}</div><div class="label">{k.title()}</div></div>'
        for k, v in stat_pairs
    )

    tier_class = card["tier"].lower()

    return f"""<!-- Auto-generated SeasonXI preview: {card['player']} {card['season']} -->
<!-- Open in browser to preview all 8 scenes -->
<!-- Data source: data/cards/{slug}_{card['season']}.json -->
<script>
window.CARD_DATA = {json.dumps(card, ensure_ascii=False)};
</script>
"""


def process_card(path: Path) -> None:
    """Process a single card JSON file."""
    card = load_card(path)
    slug = card["player"].lower().replace(" ", "-")
    season = card["season"].replace("/", "-")
    name = f"{slug}_{season}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Card HTML
    card_html = generate_card_html(card)
    html_path = OUTPUT_DIR / f"{name}_card.html"
    html_path.write_text(card_html, encoding="utf-8")

    # 2. Shorts script JSON
    script = generate_shorts_script(card)
    script_path = OUTPUT_DIR / f"{name}_script.json"
    script_path.write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")

    # 3. Card data JSON (copy for reference)
    data_path = OUTPUT_DIR / f"{name}.json"
    data_path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  {card['player']} {card['season']} ({card['tier']})")
    print(f"    -> {html_path}")
    print(f"    -> {script_path}")
    print(f"    OVR={card['ovr']} | Top: {', '.join(f'{k.title()} {v}' for k,v in sorted(card['stats'].items(), key=lambda x:x[1], reverse=True)[:3])}")


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/generate_card.py <card.json or directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_dir():
        files = sorted(target.glob("*.json"))
        print(f"Processing {len(files)} cards from {target}/\n")
        for f in files:
            process_card(f)
            print()
    else:
        process_card(target)


if __name__ == "__main__":
    main()
