"""
SeasonXI: Obsidian → JSON Export

옵시디언 시즌 문서(frontmatter)를 읽어서
Remotion 렌더용 JSON으로 변환한다.

Usage:
    uv run python -m seasonxi.content.obsidian_export
    uv run python -m seasonxi.content.obsidian_export --player messi
    uv run python -m seasonxi.content.obsidian_export --status ready
"""

from pathlib import Path
import json
import re
import argparse

import yaml


# --- Paths ---
OBSIDIAN_VAULT = Path(r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI")
PLAYERS_DIR = OBSIDIAN_VAULT / "01_Players"
OBSIDIAN_EXPORT_DIR = OBSIDIAN_VAULT / "04_Exports" / "json"

# Also export to the Remotion project for direct rendering
REMOTION_EXPORT_DIR = Path(r"C:\ProjectS\seasonXI\remotion\public\data")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

REQUIRED_FIELDS = [
    "player_id", "player_name", "display_name",
    "season", "season_label", "club", "position",
    "ovr", "att", "defense", "pace",
    "aura", "stamina", "mental", "tier",
    "hook", "commentary", "achievement", "verdict",
]


def parse_frontmatter(md_text: str) -> dict:
    """YAML frontmatter를 파싱한다."""
    match = FRONTMATTER_RE.match(md_text)
    if not match:
        raise ValueError("frontmatter not found")
    return yaml.safe_load(match.group(1))


def validate(data: dict, path: Path) -> list[str]:
    """필수 필드 검증. 누락 필드 리스트 반환."""
    missing = [k for k in REQUIRED_FIELDS if k not in data or data[k] in ("", None)]
    return missing


def build_export(data: dict) -> dict:
    """frontmatter dict → Remotion 렌더용 JSON 구조."""
    return {
        "player_id": data["player_id"],
        "player_name": data["player_name"],
        "display_name": data["display_name"],
        "season": data["season"],
        "season_label": data["season_label"],
        "club": data["club"],
        "club_short": data.get("club_short", data["club"]),
        "position": data["position"],
        "role_bucket": data.get("role_bucket", ""),
        "ovr": data["ovr"],
        "stats": {
            "att": data["att"],
            "def": data["defense"],
            "pace": data["pace"],
            "aura": data["aura"],
            "stamina": data["stamina"],
            "mental": data["mental"],
        },
        "tier": data["tier"],
        "hook": data["hook"],
        "commentary": data["commentary"],
        "achievement": data["achievement"],
        "verdict": data["verdict"],
        "cta": data.get("cta", ""),
        "goals": data.get("goals", 0),
        "assists": data.get("assists", 0),
        "minutes": data.get("minutes", 0),
        "signature_stats": data.get("signature_stats", []),
        "music_theme": data.get("music_theme", ""),
        "season_mood": data.get("season_mood", ""),
        "player_block": data.get("player_block", ""),
        "assets": {
            "image_main": data.get("image_main", ""),
            "image_card": data.get("image_card", ""),
        },
        "backgrounds": {
            "hook": data.get("scene_hook_bg", "hook1.jpg"),
            "ovr": data.get("scene_ovr_bg", "ovr2.jpg"),
            "graph": data.get("scene_graph_bg", "graph1.jpg"),
            "stats": data.get("scene_stats_bg", "stats2.jpg"),
            "commentary": data.get("scene_commentary_bg", "commentary2.jpg"),
            "milestone": data.get("scene_milestone_bg", "milestone1.jpg"),
            "verdict": data.get("scene_verdict_bg", "verdict2.jpg"),
            "end": data.get("scene_end_bg", "end2.jpg"),
        },
        "status": data.get("status", "draft"),
    }


def export_all(player_filter: str | None = None, status_filter: str | None = None):
    """01_Players/ 아래 모든 시즌 문서를 JSON으로 내보낸다."""
    OBSIDIAN_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REMOTION_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    exported = []
    skipped = []
    errors = []

    for md_file in sorted(PLAYERS_DIR.rglob("*.md")):
        if md_file.name == "index.md":
            continue

        text = md_file.read_text(encoding="utf-8")

        try:
            data = parse_frontmatter(text)
        except ValueError:
            skipped.append((md_file.name, "no frontmatter"))
            continue

        if data.get("type") != "player_season":
            skipped.append((md_file.name, f"type={data.get('type')}"))
            continue

        # Filters
        if player_filter and data.get("player_id") != player_filter:
            continue
        if status_filter and data.get("status") != status_filter:
            continue

        missing = validate(data, md_file)
        if missing:
            errors.append((md_file.name, f"missing: {missing}"))
            continue

        output = build_export(data)
        out_name = f"{data['player_id']}_{data['season'].replace('-', '_')}.json"

        # Write to both locations
        for dest in [OBSIDIAN_EXPORT_DIR, REMOTION_EXPORT_DIR]:
            out_path = dest / out_name
            out_path.write_text(
                json.dumps(output, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        exported.append(out_name)
        print(f"  OK  {md_file.parent.name}/{md_file.name} → {out_name}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Exported: {len(exported)}")
    if skipped:
        print(f"Skipped:  {len(skipped)}")
        for name, reason in skipped:
            print(f"  SKIP  {name}: {reason}")
    if errors:
        print(f"Errors:   {len(errors)}")
        for name, reason in errors:
            print(f"  ERR   {name}: {reason}")

    return exported


def main():
    parser = argparse.ArgumentParser(description="SeasonXI Obsidian → JSON export")
    parser.add_argument("--player", help="Filter by player_id (e.g. messi)")
    parser.add_argument("--status", help="Filter by status (e.g. ready)")
    args = parser.parse_args()

    print("SeasonXI Obsidian → JSON Export")
    print(f"Vault: {OBSIDIAN_VAULT}")
    print(f"Players dir: {PLAYERS_DIR}")
    print()

    export_all(player_filter=args.player, status_filter=args.status)


if __name__ == "__main__":
    main()
