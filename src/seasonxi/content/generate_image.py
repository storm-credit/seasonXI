"""SeasonXI — Gemini Image Generation

Usage:
  uv run python -m seasonxi.content.generate_image --player messi --season 2011-12 --scene HOOK
  uv run python -m seasonxi.content.generate_image --player ronaldo --season 2016-17 --scene HOOK --count 3
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

CONFIGS = Path(__file__).resolve().parents[3] / "configs" / "image_prompts"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "remotion" / "public"
COOLDOWN_FILE = Path(__file__).resolve().parents[3] / ".gemini_cooldowns.json"
COOLDOWN_HOURS = 24

# ── Prompt file readers ──────────────────────────────────────────────

def read_base() -> str:
    return (CONFIGS / "base_prompt.txt").read_text(encoding="utf-8").strip()

def read_block(filename: str, block_name: str) -> str:
    """Extract a ## BLOCK section from a blocks file."""
    text = (CONFIGS / filename).read_text(encoding="utf-8")
    pattern = rf"## {re.escape(block_name)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        raise ValueError(f"Block '{block_name}' not found in {filename}")
    return m.group(1).strip()

def read_player(player_block: str) -> str:
    return read_block("player_blocks.txt", player_block)

def read_mood(mood_name: str) -> str:
    return read_block("season_moods.txt", mood_name)

def read_scene(scene_name: str) -> str:
    return read_block("scene_blocks.txt", scene_name)

def read_modifiers(mod_names: list[str]) -> str:
    if not mod_names:
        return ""
    text = (CONFIGS / "modifiers.txt").read_text(encoding="utf-8")
    parts = []
    for name in mod_names:
        pattern = rf"## {re.escape(name)}\n(.*?)(?=\n## |\Z)"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            parts.append(m.group(1).strip())
    return "\n\n".join(parts)

# ── Prompt assembler ─────────────────────────────────────────────────

def assemble_prompt(
    player_block: str,
    mood: str,
    scene: str = "HOOK",
    modifiers: list[str] | None = None,
) -> str:
    parts = [
        read_base(),
        read_player(player_block),
        read_mood(mood),
        read_scene(scene),
    ]
    if modifiers:
        mod_text = read_modifiers(modifiers)
        if mod_text:
            parts.append(f"Additional instructions:\n{mod_text}")
    return "\n\n".join(parts)

# ── Season document reader ───────────────────────────────────────────

def load_season_doc(player_id: str, season: str) -> dict:
    """Read Obsidian season doc and return frontmatter."""
    import yaml
    obsidian_root = Path(r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI\01_Players")

    # Find player folder (case-insensitive)
    player_dir = None
    for d in obsidian_root.iterdir():
        if d.is_dir() and d.name.lower() == player_id.lower():
            player_dir = d
            break
        # Try capitalized
        if d.is_dir() and d.name.lower().replace("_", "").replace(" ", "") == player_id.lower().replace("_", ""):
            player_dir = d
            break

    if not player_dir:
        raise FileNotFoundError(f"Player folder not found: {player_id}")

    md_file = player_dir / f"{season}.md"
    if not md_file.exists():
        raise FileNotFoundError(f"Season file not found: {md_file}")

    text = md_file.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No frontmatter in {md_file}")

    return yaml.safe_load(fm_match.group(1))

# ── Gemini image generation ──────────────────────────────────────────

def _load_cooldowns() -> dict:
    """Load cooldown timestamps from disk."""
    if COOLDOWN_FILE.exists():
        import json
        return json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
    return {}

def _save_cooldowns(data: dict):
    """Save cooldown timestamps to disk."""
    import json
    COOLDOWN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _mark_rate_limited(api_key: str):
    """Mark a key as rate limited for COOLDOWN_HOURS."""
    cooldowns = _load_cooldowns()
    cooldowns[api_key[-8:]] = time.time()  # store last 8 chars as key id
    _save_cooldowns(cooldowns)

def _is_cooled_down(api_key: str) -> bool:
    """Check if a key is still in cooldown."""
    cooldowns = _load_cooldowns()
    key_id = api_key[-8:]
    if key_id not in cooldowns:
        return False
    elapsed = time.time() - cooldowns[key_id]
    return elapsed < COOLDOWN_HOURS * 3600

def get_api_keys() -> list[str]:
    """Get all available Gemini API keys for rotation."""
    keys = []
    primary = os.getenv("GEMINI_API_KEY")
    if primary:
        keys.append(primary)
    # Add backup keys
    for k, v in os.environ.items():
        if k.startswith("GEMINI_KEY_") and v not in keys:
            keys.append(v)
    return keys

def get_available_keys() -> list[tuple[int, str]]:
    """Get keys that are NOT in cooldown. Returns (index, key) pairs."""
    all_keys = get_api_keys()
    available = []
    for i, key in enumerate(all_keys):
        if not _is_cooled_down(key):
            available.append((i, key))
    return available

def generate_image(
    prompt: str,
    output_path: Path,
    key_index: int = 0,
) -> Path:
    """Generate image using Gemini API and save to output_path."""
    from google import genai
    from google.genai import types

    all_keys = get_api_keys()
    if not all_keys:
        raise RuntimeError("No GEMINI_API_KEY found in .env")

    available = get_available_keys()
    if not available:
        # Show when keys will be available again
        cooldowns = _load_cooldowns()
        earliest = min(cooldowns.values()) + COOLDOWN_HOURS * 3600
        remaining = earliest - time.time()
        hrs = int(remaining // 3600)
        mins = int((remaining % 3600) // 60)
        raise RuntimeError(
            f"All {len(all_keys)} keys are in 24h cooldown. "
            f"Next available in ~{hrs}h {mins}m. Use Nanobanana (Copy Prompt) instead."
        )

    print(f"  {len(available)}/{len(all_keys)} keys available (rest in cooldown)")

    image_models = [
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
        "gemini-2.5-flash-image",
    ]

    for model_name in image_models:
        print(f"\n  Model: {model_name}")
        for idx, api_key in available:
            client = genai.Client(api_key=api_key)
            print(f"    Key #{idx + 1}/{len(all_keys)}...")

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"],
                    ),
                )
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(part.inline_data.data)
                        print(f"    Saved: {output_path}")
                        return output_path

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    _mark_rate_limited(api_key)
                    print(f"    Rate limited → 24h cooldown. Next key...")
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    print(f"    Model not available, next model...")
                    break
                else:
                    print(f"    Error: {e}")
                    continue

    raise RuntimeError("All models/keys exhausted")

# ── Main CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SeasonXI Image Generator")
    parser.add_argument("--player", required=True, help="Player ID (e.g., messi)")
    parser.add_argument("--season", required=True, help="Season (e.g., 2011-12)")
    parser.add_argument("--scene", default="HOOK", help="Scene type (HOOK, CARD_BACKGROUND, etc.)")
    parser.add_argument("--count", type=int, default=1, help="Number of variants to generate")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--prompt-only", action="store_true", help="Print prompt without generating")
    args = parser.parse_args()

    # Load season data
    print(f"\n{'='*60}")
    print(f"  SeasonXI Image Generator")
    print(f"  {args.player.upper()} {args.season} / {args.scene}")
    print(f"{'='*60}\n")

    try:
        data = load_season_doc(args.player, args.season)
        player_block = data.get("player_block", args.player.upper())
        mood = data.get("season_mood", "PEAK_MONSTER")

        # Get modifiers from season doc
        mod_key = "hook_modifiers" if "HOOK" in args.scene.upper() else "card_modifiers"
        modifiers = data.get(mod_key, [])
        if isinstance(modifiers, list):
            modifiers = [m for m in modifiers if m]  # filter empty
        else:
            modifiers = []

    except FileNotFoundError:
        print(f"  Season doc not found, using defaults")
        player_block = args.player.upper()
        mood = "PEAK_MONSTER"
        modifiers = []

    # Assemble prompt
    prompt = assemble_prompt(player_block, mood, args.scene, modifiers)

    if args.prompt_only:
        print(prompt)
        return

    print(f"  Player block: {player_block}")
    print(f"  Mood: {mood}")
    print(f"  Scene: {args.scene}")
    print(f"  Modifiers: {modifiers or 'none'}")
    print(f"  Count: {args.count}")
    print()

    out_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    season_clean = args.season.replace("-", "_")
    scene_lower = args.scene.lower()

    for i in range(args.count):
        version = f"v{i+1}"
        filename = f"{args.player}_{season_clean}_{scene_lower}_{version}.png"
        output_path = out_dir / filename

        print(f"  [{i+1}/{args.count}] Generating {filename}...")
        try:
            generate_image(prompt, output_path, key_index=i)
        except Exception as e:
            print(f"  ERROR: {e}")
            # Try next key
            if args.count > 1:
                time.sleep(2)
                try:
                    generate_image(prompt, output_path, key_index=i+1)
                except Exception as e2:
                    print(f"  RETRY ERROR: {e2}")

        if i < args.count - 1:
            time.sleep(3)  # Rate limit spacing

    print(f"\n  Done! Check: {out_dir}")


if __name__ == "__main__":
    main()
