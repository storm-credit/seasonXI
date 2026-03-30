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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SeasonXI API", version="1.3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # seasonXI/
OBSIDIAN_VAULT = Path(r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI")
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
                    "finishing": fm.get("finishing", 0),
                    "playmaking": fm.get("playmaking", 0),
                    "dribbling": fm.get("dribbling", 0),
                    "defense": fm.get("defense", 0),
                    "clutch": fm.get("clutch", 0),
                    "aura": fm.get("aura", 0),
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
    """Trigger Remotion render for a season."""
    video_id = f"{player_id}_{season.replace('-', '_')}"
    script = PROJECT_ROOT / "scripts" / "render_video.py"

    if not script.exists():
        raise HTTPException(404, "render_video.py not found")

    try:
        result = subprocess.Popen(
            [sys.executable, str(script), video_id],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {"status": "rendering", "video_id": video_id, "pid": result.pid}
    except Exception as e:
        raise HTTPException(500, str(e))


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
