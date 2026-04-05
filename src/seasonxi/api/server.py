"""SeasonXI Production API Server.

Usage: uv run python -m seasonxi.api.server
Opens at: http://localhost:8800
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SeasonXI API", version="1.3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # seasonXI/
OBSIDIAN_VAULT = Path(os.getenv("OBSIDIAN_VAULT_PATH", r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI"))
PLAYERS_DIR = OBSIDIAN_VAULT / "01_Players"
CONFIGS_DIR = PROJECT_ROOT / "configs"
REMOTION_DIR = PROJECT_ROOT / "remotion"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
SETTINGS_FILE = PROJECT_ROOT / "configs" / "dashboard_settings.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


# ─── Settings ─────────────────────────────────────────────────
def _load_settings() -> dict:
    if SETTINGS_FILE.exists():
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    return {"gemini_api_key": "", "output_dir": str(OUTPUTS_DIR), "remotion_port": 3334}


def _save_settings(data: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ─── API: Settings ────────────────────────────────────────────
@app.get("/api/settings")
def get_settings():
    s = _load_settings()
    # Mask API key
    if s.get("gemini_api_key"):
        s["gemini_api_key_masked"] = s["gemini_api_key"][:8] + "..."
    else:
        s["gemini_api_key_masked"] = ""
    return s


@app.post("/api/settings")
def save_settings(data: dict):
    current = _load_settings()
    current.update(data)
    _save_settings(current)
    return {"status": "saved"}


# ─── API: Search Players ──────────────────────────────────────
@app.get("/api/search")
def search_players(q: str = ""):
    """Search season documents by player name or season."""
    results = []
    if not PLAYERS_DIR.exists():
        return results

    for md_file in PLAYERS_DIR.rglob("*.md"):
        if md_file.name == "index.md":
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
            match = FRONTMATTER_RE.match(text)
            if not match:
                continue
            fm = yaml.safe_load(match.group(1))
            if not fm or fm.get("type") != "player_season":
                continue

            # Search filter
            name = fm.get("display_name", "")
            season = fm.get("season", "")
            search_str = f"{name} {season} {fm.get('club', '')}".lower()
            if q and q.lower() not in search_str:
                continue

            results.append({
                "id": f"{fm.get('player_id', '')}_{season.replace('-', '_')}",
                "player_id": fm.get("player_id", ""),
                "display_name": name,
                "player_name": fm.get("player_name", ""),
                "season": season,
                "season_label": fm.get("season_label", season),
                "club": fm.get("club", ""),
                "position": fm.get("position", ""),
                "ovr": fm.get("ovr", 0),
                "tier": fm.get("tier", ""),
                "hook": fm.get("hook", ""),
                "stats": {
                    "att": fm.get("att", fm.get("finishing", 0)),
                    "def": fm.get("defense", 0),
                    "pace": fm.get("pace", fm.get("dribbling", 0)),
                    "aura": fm.get("aura", 0),
                    "stamina": fm.get("stamina", fm.get("clutch", 0)),
                    "mental": fm.get("mental", fm.get("clutch", 0)),
                },
                "goals": fm.get("goals", 0),
                "assists": fm.get("assists", 0),
                "commentary": fm.get("commentary", ""),
                "achievement": fm.get("achievement", ""),
                "verdict": fm.get("verdict", ""),
                "cta": fm.get("cta", ""),
                "player_block": fm.get("player_block", ""),
                "season_mood": fm.get("season_mood", ""),
                "suno_title": fm.get("suno_title", ""),
                "suno_style": fm.get("suno_style", ""),
                "status": fm.get("status", "draft"),
                "file_path": str(md_file),
            })
        except Exception:
            continue

    results.sort(key=lambda x: x.get("ovr", 0), reverse=True)
    return results


# ─── API: Load Season ─────────────────────────────────────────
@app.get("/api/season/{player_id}/{season}")
def load_season(player_id: str, season: str):
    """Load a specific season document."""
    results = search_players(f"{player_id} {season}")
    if not results:
        raise HTTPException(404, f"Season not found: {player_id} {season}")
    return results[0]


# ─── API: Prompt Assembly ─────────────────────────────────────
@app.get("/api/prompt/{player_id}/{season}")
def assemble_prompt(player_id: str, season: str, scene: str = "HOOK"):
    """Assemble full image generation prompt."""
    # Load season data
    results = search_players(f"{player_id} {season}")
    if not results:
        raise HTTPException(404, "Season not found")
    data = results[0]

    # Read prompt parts
    parts = {}
    for fname in ["base_prompt.txt", "player_blocks.txt", "season_moods.txt", "scene_blocks.txt", "modifiers.txt"]:
        fpath = CONFIGS_DIR / "image_prompts" / fname
        if fpath.exists():
            parts[fname] = fpath.read_text(encoding="utf-8")

    # Extract player block
    block_name = data.get("player_block", player_id.upper())
    player_block = _extract_block(parts.get("player_blocks.txt", ""), block_name)

    # Extract mood
    mood_name = data.get("season_mood", "PEAK_MONSTER")
    mood_block = _extract_block(parts.get("season_moods.txt", ""), mood_name)

    # Extract scene
    scene_block = _extract_block(parts.get("scene_blocks.txt", ""), scene)

    # Base prompt
    base = parts.get("base_prompt.txt", "").strip()

    full_prompt = f"{base}\n\n{player_block}\n\n{mood_block}\n\n{scene_block}"

    return {
        "full_prompt": full_prompt,
        "base": base,
        "player_block": player_block,
        "mood": mood_block,
        "scene": scene_block,
        "player_block_name": block_name,
        "mood_name": mood_name,
        "scene_name": scene,
    }


def _extract_block(text: str, block_name: str) -> str:
    """Extract a named block from a prompt file."""
    pattern = rf"## {re.escape(block_name)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"[Block '{block_name}' not found]"


# ─── API: Render Video ────────────────────────────────────────
@app.post("/api/render/{player_id}/{season}")
def render_video(player_id: str, season: str):
    """Trigger Remotion render with player-specific props."""
    import urllib.request
    video_id = f"{player_id}_{season.replace('-', '_')}"
    s = season.replace("-", "_")

    # Build player-specific StoryCardData props
    # 1. Try to find card data
    card_data = None
    cards_file = PROJECT_ROOT / "outputs" / "cards" / "_all_cards_v2_merged.json"
    if cards_file.exists():
        all_cards = json.loads(cards_file.read_text(encoding="utf-8"))
        for c in all_cards:
            name = c.get("display_name", c.get("player_name", ""))
            if player_id.lower() in name.lower():
                card_data = c
                break

    # 2. Build props
    display = player_id.upper()
    club = ""
    tier = "ELITE"
    ovr = 85
    att = def_v = pace = aura = stamina = mental = 80
    goals = assists = 0

    if card_data:
        display = card_data.get("display_name", card_data.get("player_name", player_id.upper()))
        club = card_data.get("club", "")
        tier = card_data.get("tier", "ELITE")
        ovr_val = card_data.get("ovr")
        if ovr_val:
            ovr = int(float(ovr_val))
        else:
            # Compute from stats average
            stats = [float(card_data.get(k, 0) or 0) for k in ["att", "def", "pace", "aura", "stamina", "mental"]]
            ovr = int(sum(stats) / len(stats)) if stats else 85
        att = int(float(card_data.get("att", 80) or 80))
        def_v = int(float(card_data.get("def", 40) or 40))
        pace = int(float(card_data.get("pace", 80) or 80))
        aura = int(float(card_data.get("aura", 80) or 80))
        stamina = int(float(card_data.get("stamina", 80) or 80))
        mental = int(float(card_data.get("mental", 80) or 80))
        goals = int(float(card_data.get("goals", 0) or 0))
        assists = int(float(card_data.get("assists", 0) or 0))

    # 3. Build narration script + auto-generate MP3 if missing
    position_val = card_data.get("position", "FW") if card_data else "FW"
    narration_script = _build_narration_script(
        player_name=display, club=club, season=season,
        goals=goals, assists=assists, tier=tier, position=position_val,
        att=att, def_v=def_v, pace=pace, aura=aura, stamina=stamina, mental=mental,
    )

    narration_path = REMOTION_DIR / "public" / f"{player_id}_{season}" / "narration.mp3"
    if not narration_path.exists():
        try:
            generate_narration(player_id, season)
        except Exception:
            pass

    # 4. Check for images & audio in player folder
    player_folder = f"{player_id}_{season}"
    props = {
        "data": {
            "player_name": display,
            "club": club,
            "season": season,
            "position": card_data.get("position", "FW") if card_data else "FW",
            "tier": tier,
            "ovr": ovr,
            "att": att,
            "def": def_v,
            "pace": pace,
            "aura": aura,
            "stamina": stamina,
            "mental": mental,
            "goals": goals,
            "assists": assists,
            "hookImage": f"{player_folder}/{player_id}_{s}_hook_v1.png",
            "cardImage": f"{player_folder}/{player_id}_{s}_card_v1.png",
            "closeupImage": f"{player_folder}/{player_id}_{s}_closeup_v1.png",
            "narrationSrc": f"{player_folder}/narration.mp3",
            "bgmSrc": f"{player_folder}/bgm.mp3",
            "hookStat": _build_hook_stat(position_val, goals, assists, def_v),
            "hookLine": f"{display} · {season}",
            "verdictText": f"{tier} Season",
            "storyText": narration_script[:200] if narration_script else "",
            "highlights": _build_highlights(position_val, goals, assists, def_v, pace),
            "subtitles": _build_subtitles(narration_script),
        }
    }

    # Send render request to Remotion render-server
    render_url = "http://seasonxi-remotion:3335/render"
    payload = json.dumps({
        "composition": "SeasonStory",
        "output": f"/app/outputs/{video_id}.mp4",
        "props": props,
    }).encode()

    try:
        req = urllib.request.Request(
            render_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return {"status": "rendering", "video_id": video_id, "player": display, **result}
    except Exception as e:
        raise HTTPException(500, f"Render server error: {e}")


# ─── API: Pipeline Cards (real data) ──────────────────────────
@app.get("/api/pipeline-cards")
def get_pipeline_cards(q: str = ""):
    """Get cards from pipeline results (2030 players)."""
    cards_file = PROJECT_ROOT / "outputs" / "cards" / "_all_cards_v2_merged.json"
    if not cards_file.exists():
        return []
    cards = json.loads(cards_file.read_text(encoding="utf-8"))
    if q:
        cards = [c for c in cards if q.lower() in c.get("player_name", "").lower()]
    return cards[:50]


@app.post("/api/pipeline-export/{player_name}")
def pipeline_export(player_name: str):
    """Export a player from pipeline results to Remotion JSON."""
    cards_file = PROJECT_ROOT / "outputs" / "cards" / "_all_cards_v2_merged.json"
    if not cards_file.exists():
        raise HTTPException(404, "Pipeline not run yet")

    cards = json.loads(cards_file.read_text(encoding="utf-8"))
    match = [c for c in cards if player_name.lower() in c.get("player_name", "").lower()]
    if not match:
        raise HTTPException(404, f"Player not found: {player_name}")

    card = match[0]
    remotion_data = {
        "player": card["player_name"].split()[-1].upper(),
        "season": "2021-22",
        "club": card["club"],
        "position": card["position"],
        "ovr": int(card["overall"]),
        "stats": {
            "att": int(card["att"]),
            "def": int(card["def"]),
            "pace": int(card["pace"]),
            "aura": int(card["aura"]),
            "stamina": int(card["stamina"]),
            "mental": int(card["mental"]),
        },
        "tier": card["tier"],
        "hook": f"THIS WAS {card['tier'].upper()}",
        "play_style": f"{card['goals']} GOALS {card['assists']} ASSISTS",
        "achievement": "GOALS",
        "achievement_number": str(card["goals"]),
        "verdict": f"{card['tier'].upper()} SEASON",
        "cta": "WHO WAS BETTER?",
        "closeup_text": "UNSTOPPABLE",
        "energy_text": card["tier"].upper(),
    }

    out_dir = REMOTION_DIR / "public" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    name_clean = card["player_name"].lower().replace(" ", "_")
    out_path = out_dir / f"{name_clean}_2021_22.json"
    out_path.write_text(json.dumps(remotion_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"status": "exported", "path": str(out_path), "player": card["player_name"], "ovr": card["overall"], "tier": card["tier"]}


# ─── API: Render Status ──────────────────────────────────────
@app.get("/api/render-status/{player_id}/{season}")
def render_status(player_id: str, season: str):
    """Check if a rendered video exists."""
    vid = f"{player_id}_{season.replace('-', '_')}"
    for d in [PROJECT_ROOT / "outputs", REMOTION_DIR / "outputs"]:
        for name in [f"{vid}.mp4", f"{vid}_FINAL.mp4", f"{vid}_7cut_12s.mp4"]:
            p = d / name
            if p.exists():
                return {"status": "done", "filename": name, "size": p.stat().st_size}
    return {"status": "pending"}


# ─── API: Export JSON ─────────────────────────────────────────
@app.post("/api/export/{player_id}/{season}")
def export_json(player_id: str, season: str):
    """Export season data to Remotion JSON."""
    results = search_players(f"{player_id} {season}")
    if not results:
        raise HTTPException(404, "Season not found")

    data = results[0]
    out_dir = REMOTION_DIR / "public" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{data['id']}.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"status": "exported", "path": str(out_path)}


# ─── API: Engine Check ────────────────────────────────────────
@app.get("/api/engine-check")
def engine_check():
    """Run HANESIS health check."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "seasonxi.cli.engine_check"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {"output": result.stdout, "errors": result.stderr}
    except Exception as e:
        raise HTTPException(500, str(e))


# ─── API: Generate Image (Imagen 4 + Nano Banana + Gemini fallback) ──
@app.post("/api/generate-image/{player_id}/{season}")
def generate_image_api(player_id: str, season: str, scene: str = "HOOK", count: int = 1):
    """Generate player image using full fallback chain: Imagen 4 → Nano Banana → Gemini.

    Runs as subprocess so the API returns immediately with a PID for status tracking.
    """
    try:
        # Check for ready-to-paste prompt file first
        s_clean = season.replace("-", "_")
        scene_lower = scene.lower()
        prompt_file = CONFIGS_DIR / "image_prompts" / "prompt_sets" / f"{player_id}_{s_clean}_{scene_lower}.txt"

        cmd = [
            sys.executable, "-m", "seasonxi.content.generate_image",
            "--player", player_id,
            "--season", season,
            "--scene", scene,
            "--count", str(count),
        ]
        if prompt_file.exists():
            cmd.extend(["--prompt-file", str(prompt_file)])

        result = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {
            "status": "generating",
            "engine": "imagen4+nano+gemini",
            "player_id": player_id,
            "season": season,
            "scene": scene,
            "count": count,
            "prompt_file": str(prompt_file) if prompt_file.exists() else None,
            "pid": result.pid,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# ─── Render helpers ────────────────────────────────────────────

def _build_hook_stat(position: str, goals: int, assists: int, def_v: int) -> str:
    """Position-aware hook stat for first frame."""
    if position in ("DF", "CB", "LB", "RB"):
        return f"DEF {def_v}" if def_v > 0 else "WALL"
    elif position == "GK":
        return "KEEPER"
    elif position in ("MF", "CM", "CAM", "CDM"):
        if goals >= 10:
            return f"{goals} GOALS"
        return f"{goals + assists} G+A"
    else:  # FW
        return f"{goals} GOALS"


def _build_highlights(position: str, goals: int, assists: int, def_v: int, pace: int) -> list:
    """Position-aware highlight stats."""
    if position in ("DF", "CB", "LB", "RB"):
        return [
            {"number": str(def_v), "label": "DEF Rating", "delay": 0},
            {"number": str(goals + assists), "label": "G+A", "delay": 35},
        ]
    elif position == "GK":
        return [
            {"number": str(def_v), "label": "DEF Rating", "delay": 0},
        ]
    else:
        highlights = [{"number": str(goals), "label": "Goals", "delay": 0}]
        if assists > 0:
            highlights.append({"number": str(assists), "label": "Assists", "delay": 35})
        return highlights


def _build_subtitles(script: str) -> list:
    """Auto-generate subtitle cues from narration script."""
    if not script:
        return []

    import re
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', script.strip())
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]

    if not sentences:
        return []

    # Distribute across 60 seconds (1800 frames), skip card reveal (900-1050)
    cues = []
    total_chars = sum(len(s) for s in sentences)
    current_frame = 10  # Start after first 10 frames

    for sentence in sentences:
        # Duration proportional to sentence length (~30fps reading speed)
        char_ratio = len(sentence) / max(total_chars, 1)
        duration = max(45, int(char_ratio * 1500))  # Min 1.5 sec, proportional to length

        # Skip card reveal zone (900-1050)
        if current_frame >= 880 and current_frame < 1060:
            current_frame = 1070

        end_frame = min(current_frame + duration, 1750)

        # Find a highlight word (first capitalized word, number, or key word)
        highlight = None
        words = sentence.split()
        for w in words:
            clean = w.strip('.,!?;:')
            if clean.isdigit() and int(clean) > 1:
                highlight = clean
                break
            if clean[0:1].isupper() and len(clean) > 3 and clean not in ("This", "That", "When", "Some", "They", "And", "But", "The", "His", "Her"):
                highlight = clean
                break

        cues.append({
            "startFrame": current_frame,
            "endFrame": end_frame,
            "text": sentence,
            "highlight": highlight,
        })

        current_frame = end_frame + 8  # 8 frame gap between cues

    return cues


# ─── Narration: Gemini-powered script builder ─────────────────
def _build_narration_script(
    player_name: str,
    club: str,
    season: str,
    goals: int,
    assists: int,
    tier: str,
    position: str,
    att: int = 0,
    def_v: int = 0,
    pace: int = 0,
    aura: int = 0,
    stamina: int = 0,
    mental: int = 0,
) -> str:
    """Generate a compelling 45-second narration script using Gemini.

    Falls back to a template if Gemini is unavailable.
    """
    # Try Gemini first
    try:
        from google import genai

        # Reuse the Vertex AI client from generate_image
        backend = os.getenv("GEMINI_BACKEND", "ai_studio").lower().strip()
        if backend == "vertex_ai":
            sa_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
            if sa_key and not os.path.isabs(sa_key):
                resolved = PROJECT_ROOT / sa_key
                if resolved.exists():
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(resolved)
            project = os.getenv("VERTEX_PROJECT", "")
            location = os.getenv("VERTEX_LOCATION", "us-central1")
            client = genai.Client(vertexai=True, project=project, location=location)
        else:
            api_key = os.getenv("GEMINI_API_KEY", "")
            client = genai.Client(api_key=api_key)

        prompt = f"""You are a football documentary narrator for YouTube Shorts. Write a compelling 45-second English narration script for this player's season.

PLAYER DATA:
- Name: {player_name}
- Club: {club}
- Season: {season}
- Position: {position}
- Goals: {goals}, Assists: {assists}
- Season Grade: {tier}
- Stats: ATT {att}, DEF {def_v}, PACE {pace}, AURA {aura}, STAMINA {stamina}, MENTAL {mental}

RULES:
- Write ONLY the narration text, no stage directions, no timestamps
- Start with a powerful hook line (1-2 sentences that make viewers stop scrolling)
- Tell the story of this season: what made it special, key moments, context
- End with the tier verdict: "{tier}. No debate." then "Season Eleven."
- Keep it under 150 words (45 seconds at normal speech pace)
- Use short punchy sentences. Create rhythm.
- Don't read stats like a spreadsheet. Make them FEEL meaningful.
- No emojis, no hashtags, no "subscribe"
- Write in a cinematic, authoritative tone

OUTPUT: Just the narration text, nothing else."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        script = (response.text or "").strip()
        if len(script) > 50:  # Valid response
            return script
    except Exception as e:
        print(f"  [Narration] Gemini failed ({e}), using template fallback")

    # Fallback template
    contributions = goals + assists
    return f"""{player_name}. {season}. {club}.

{goals} goals, {assists} assists.
{"" if contributions <= goals else f"{contributions} goal contributions. "}

This is what {tier.lower()} looks like.
When talent meets consistency, numbers tell the story.
And the numbers say everything.

{tier}. No debate.

Season Eleven."""


async def _generate_tts(script: str, output_path: "Path") -> None:
    """Run Edge TTS and save MP3 to output_path."""
    import edge_tts  # type: ignore
    comm = edge_tts.Communicate(script, "en-US-AndrewNeural", rate="-5%", pitch="-2Hz")
    await comm.save(str(output_path))


# ─── API: Generate Narration ──────────────────────────────────
@app.post("/api/generate-narration/{player_id}/{season}")
def generate_narration(player_id: str, season: str):
    """Generate narration script + TTS MP3 for a player season.

    Saves to remotion/public/{player_id}_{season}/narration.mp3.
    """
    import asyncio

    # 1. Get card data — try search first, fallback to cards JSON
    results = search_players(f"{player_id} {season}")
    data = {}
    if results:
        data = results[0]
    else:
        # Fallback: search in _all_cards_v2_merged.json
        cards_file = PROJECT_ROOT / "outputs" / "cards" / "_all_cards_v2_merged.json"
        if cards_file.exists():
            all_cards = json.loads(cards_file.read_text(encoding="utf-8"))
            for c in all_cards:
                name = c.get("display_name", c.get("player_name", ""))
                if player_id.lower() in name.lower():
                    data = c
                    break

    player_name = data.get("display_name") or data.get("player_name") or player_id.upper()
    club = data.get("club") or ""
    tier = data.get("tier") or "ELITE"
    position = data.get("position") or "FW"
    goals = int(float(data.get("goals", 0) or 0))
    assists = int(float(data.get("assists", 0) or 0))

    # 2. Build script (with stats for Gemini)
    script = _build_narration_script(
        player_name=player_name,
        club=club,
        season=season,
        goals=goals,
        assists=assists,
        tier=tier,
        position=position,
        att=int(float(data.get("att", 0) or 0)),
        def_v=int(float(data.get("def", 0) or 0)),
        pace=int(float(data.get("pace", 0) or 0)),
        aura=int(float(data.get("aura", 0) or 0)),
        stamina=int(float(data.get("stamina", 0) or 0)),
        mental=int(float(data.get("mental", 0) or 0)),
    )

    # 3. Determine output path
    player_folder = REMOTION_DIR / "public" / f"{player_id}_{season}"
    player_folder.mkdir(parents=True, exist_ok=True)
    output_path = player_folder / "narration.mp3"

    # 4. Run Edge TTS
    try:
        asyncio.run(_generate_tts(script, output_path))
    except Exception as e:
        raise HTTPException(500, f"TTS generation failed: {e}")

    return {
        "status": "done",
        "player_id": player_id,
        "season": season,
        "script": script,
        "output": str(output_path),
        "size": output_path.stat().st_size if output_path.exists() else 0,
    }


@app.post("/api/assemble-prompt/{player_id}/{season}")
def assemble_prompt_api(player_id: str, season: str, scene: str = "HOOK"):
    """Assemble full prompt text for copy-paste to Nanobanana."""
    try:
        from seasonxi.content.generate_image import assemble_prompt, load_season_doc
        data = load_season_doc(player_id, season)
        player_block = data.get("player_block", player_id.upper())
        mood = data.get("season_mood", "PEAK_MONSTER")
        mod_key = "hook_modifiers" if "HOOK" in scene.upper() else "card_modifiers"
        modifiers = data.get(mod_key, [])
        if isinstance(modifiers, list):
            modifiers = [m for m in modifiers if m]
        else:
            modifiers = []

        prompt = assemble_prompt(player_block, mood, scene, modifiers)
        return {"prompt": prompt, "player_block": player_block, "mood": mood, "scene": scene}
    except Exception as e:
        raise HTTPException(500, str(e))


# ─── API: Check Existing Assets ───────────────────────────────
@app.get("/api/assets/{player_id}/{season}")
def check_assets(player_id: str, season: str):
    """Check which assets already exist for a player/season."""
    s = season.replace("-", "_")
    pub = REMOTION_DIR / "public"

    assets = {}
    # Player folder: e.g., benzema_2021-22/
    player_folder = pub / f"{player_id}_{season}"

    for asset_type in ["hook", "card", "closeup", "main", "bgm"]:
        found = False
        for ext in ["png", "jpg", "mp3", "wav", "m4a"]:
            # Pattern 1: In player subfolder (new structure)
            # e.g., benzema_2021-22/benzema_2021_22_hook_v1.png
            if player_folder.exists():
                folder_patterns = [
                    f"{player_id}_{s}_{asset_type}_v*.{ext}",
                    f"{player_id}_{s}_{asset_type}.{ext}",
                    f"*_{asset_type}_v*.{ext}",
                    f"*_{asset_type}.{ext}",
                ]
                for pattern in folder_patterns:
                    matches = list(player_folder.glob(pattern))
                    if matches:
                        path = matches[0]
                        rel = path.relative_to(pub)
                        assets[asset_type] = {
                            "exists": True,
                            "filename": path.name,
                            "size": path.stat().st_size,
                            "url": f"/remotion/public/{rel.as_posix()}",
                        }
                        found = True
                        break
                if found:
                    break

            # Pattern 2: Flat in public/ (legacy)
            flat_patterns = [
                f"{player_id}_{s}_{asset_type}.{ext}",
                f"{player_id}_{s}_{asset_type}_v*.{ext}",
                f"{player_id}_*_{s}_{asset_type}.{ext}",
                f"{player_id}_*_{s}_{asset_type}_v*.{ext}",
            ]
            for pattern in flat_patterns:
                if "*" in pattern:
                    matches = list(pub.glob(pattern))
                    if matches:
                        path = matches[0]
                        assets[asset_type] = {
                            "exists": True,
                            "filename": path.name,
                            "size": path.stat().st_size,
                            "url": f"/remotion/public/{path.name}",
                        }
                        found = True
                        break
                else:
                    path = pub / pattern
                    if path.exists():
                        assets[asset_type] = {
                            "exists": True,
                            "filename": path.name,
                            "size": path.stat().st_size,
                            "url": f"/remotion/public/{path.name}",
                        }
                        found = True
                        break
            if found:
                break
        if not found:
            assets[asset_type] = {"exists": False}

    return assets


@app.get("/api/asset-file/{filename:path}")
def serve_asset(filename: str):
    """Serve an asset file (image/audio/video) from remotion/public or outputs."""
    # Check remotion/public (supports subfolders like benzema_2021-22/hook_v1.png)
    path = REMOTION_DIR / "public" / filename
    if path.exists():
        return FileResponse(path)
    # Check outputs
    path = OUTPUTS_DIR / filename
    if path.exists():
        return FileResponse(path)
    # Check remotion outputs
    path = REMOTION_DIR / "outputs" / filename
    if path.exists():
        return FileResponse(path)
    raise HTTPException(404, f"File not found: {filename}")


# ─── API: Upload Image (Drag & Drop) ─────────────────────────
@app.post("/api/upload-image")
async def upload_image(file: UploadFile, filename: str = Form(...)):
    """Save uploaded image to remotion/public/."""
    out_path = REMOTION_DIR / "public" / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    out_path.write_bytes(content)
    return {"status": "saved", "filename": filename, "size": len(content), "path": str(out_path)}


# ─── API: YouTube Upload ─────────────────────────────────────
@app.post("/api/upload-youtube/{player_id}/{season}")
def upload_youtube(player_id: str, season: str, privacy: str = "unlisted"):
    """Upload rendered video to YouTube."""
    video_id = f"{player_id}_{season.replace('-', '_')}"
    video_path = PROJECT_ROOT / "outputs" / f"{video_id}.mp4"

    if not video_path.exists():
        # Try remotion outputs
        video_path = REMOTION_DIR / "outputs" / f"{video_id}.mp4"

    if not video_path.exists():
        raise HTTPException(404, f"Video not found: {video_id}.mp4")

    try:
        result = subprocess.Popen(
            [
                sys.executable, "-m", "seasonxi.content.youtube_upload",
                "--video", str(video_path),
                "--player", player_id,
                "--season", season,
                "--privacy", privacy,
            ],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {
            "status": "uploading",
            "video_id": video_id,
            "privacy": privacy,
            "pid": result.pid,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/youtube-metadata/{player_id}/{season}")
def youtube_metadata(player_id: str, season: str):
    """Preview YouTube upload metadata, enriched with SeasonXI metadata helpers."""
    from seasonxi.content.youtube_upload import build_upload_metadata
    from seasonxi.content.youtube_metadata import (
        generate_description,
        generate_tags,
        generate_title,
    )

    # Load season data for enrichment
    results = search_players(f"{player_id} {season}")
    season_data = results[0] if results else {}

    player_name = season_data.get("display_name") or player_id.upper()
    season_label = season_data.get("season_label") or season
    tier = season_data.get("tier") or ""
    club = season_data.get("club") or ""
    goals = season_data.get("goals") or 0
    assists = season_data.get("assists") or 0

    # Build enriched metadata using youtube_metadata helpers
    title = generate_title(player_name, season_label, tier) if tier else None
    description = generate_description(player_name, season_label, goals, assists, tier) if tier else None
    tags = generate_tags(player_name, club, season_label)

    # Also include the full upload-ready structure from youtube_upload
    metadata = build_upload_metadata(player_id=player_id, season=season)

    # Inject enriched fields
    if title:
        metadata["snippet"]["title"] = title
    if description:
        metadata["snippet"]["description"] = description
    metadata["snippet"]["tags"] = tags

    return {
        **metadata,
        "preview": {
            "title": metadata["snippet"]["title"],
            "description": metadata["snippet"]["description"],
            "tags": tags,
        },
    }


# ─── API: Prompts List ────────────────────────────────────────
@app.get("/api/prompts")
def list_prompts():
    """List available prompt files."""
    prompt_dir = CONFIGS_DIR / "image_prompts"
    if not prompt_dir.exists():
        return []
    return [f.name for f in prompt_dir.glob("*.txt")]


@app.get("/api/suno-prompts")
def get_suno_prompts():
    """Get Suno music prompts."""
    suno_file = CONFIGS_DIR / "suno_prompts.txt"
    if not suno_file.exists():
        return {"content": ""}
    return {"content": suno_file.read_text(encoding="utf-8")}


# ─── Static Files (Dashboard) ────────────────────────────────
CONTENT_DIR = Path(__file__).parent.parent / "content"
if CONTENT_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(CONTENT_DIR)), name="static")


@app.get("/")
def dashboard():
    html_path = CONTENT_DIR / "dashboard.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Dashboard not found</h1>")


# ─── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("SeasonXI API: http://localhost:8800")
    print("Dashboard:    http://localhost:8800/")
    print("API Docs:     http://localhost:8800/docs")
    uvicorn.run(app, host="0.0.0.0", port=8800)
