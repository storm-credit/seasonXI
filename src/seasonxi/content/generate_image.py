"""SeasonXI — Image Generation Pipeline (Imagen 4 + Nano Banana + Gemini fallback)

Adapted from AskAnything's imagen.py for SeasonXI's use case.
Full fallback chain: Imagen 4 → Nano Banana → Gemini native image gen.
Features: key rotation, RPM management, vision verification, safety fallback.

Usage:
  uv run python -m seasonxi.content.generate_image --player messi --season 2011-12 --scene HOOK
  uv run python -m seasonxi.content.generate_image --player benzema --season 2021-22 --scene CARD --count 3
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# ── Paths ───────────────────────────────────────────────────────
CONFIGS = Path(__file__).resolve().parents[3] / "configs" / "image_prompts"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "remotion" / "public"
KEY_STATE_FILE = Path(__file__).resolve().parents[3] / ".image_key_state.json"

# ── Constants ───────────────────────────────────────────────────
MAX_KEY_RETRIES = 10       # 키 전환 최대 횟수 (per model)
MAX_VISION_RETRIES = 1     # 이미지-프롬프트 불일치 시 재생성
COOLDOWN_SECONDS = 3600    # 1시간 (기존 24시간에서 축소)
RPM_WINDOW = 60            # RPM 윈도우 (초)
RPM_LIMIT = 5              # 분당 최대 요청 수

# ── Model chains (priority order) ──
# SeasonXI uses Nano Banana (free tier) as primary.
# Imagen 4 requires paid plan — only used if IMAGEN_PAID=true in .env.

# Primary: Nano Banana (Gemini native image gen) — free tier
NANO_BANANA_MODELS = [
    {"id": "gemini-2.5-flash-image",         "tag": "nano_flash",     "label": "Nano Flash"},
    {"id": "gemini-3.1-flash-image-preview", "tag": "nano_3_1_flash", "label": "Nano 3.1 Flash"},
]

# Secondary: Gemini text+image fallback
GEMINI_FALLBACK_MODELS = [
    {"id": "gemini-3-pro-image-preview", "tag": "gemini_pro", "label": "Gemini 3 Pro"},
]

# Paid tier only: Imagen 4
IMAGEN_MODELS = [
    {"id": "imagen-4.0-generate-001", "tag": "imagen_standard", "label": "Imagen 4"},
]


# ══════════════════════════════════════════════════════════════════
#  KEY MANAGEMENT — Rotation, RPM, Cooldown
# ══════════════════════════════════════════════════════════════════

def _load_key_state() -> dict:
    if KEY_STATE_FILE.exists():
        try:
            return json.loads(KEY_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_key_state(state: dict):
    KEY_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _mask_key(key: str) -> str:
    """마스킹: AIza...XXXX"""
    if len(key) > 12:
        return f"{key[:4]}...{key[-4:]}"
    return "***"


def get_api_keys() -> list[str]:
    """Get all Gemini API keys from env."""
    keys = []
    primary = os.getenv("GEMINI_API_KEY")
    if primary:
        keys.append(primary)
    for k, v in sorted(os.environ.items()):
        if k.startswith("GEMINI_KEY_") and v not in keys:
            keys.append(v)
    return keys


def _get_available_key(service_tag: str, exclude: set[str] | None = None) -> str | None:
    """Get next available key for a service, excluding exhausted ones."""
    backend = os.getenv("GEMINI_BACKEND", "ai_studio").lower().strip()

    # Vertex AI: no API key needed, always return placeholder
    if backend == "vertex_ai":
        return "vertex_ai_service_account"

    state = _load_key_state()
    exclude = exclude or set()
    now = time.time()

    for key in get_api_keys():
        if key in exclude:
            continue
        key_id = key[-8:]
        key_state = state.get(key_id, {}).get(service_tag, {})

        # Check cooldown
        cooldown_until = key_state.get("cooldown_until", 0)
        if now < cooldown_until:
            continue

        return key

    return None


def _mark_key_exhausted(api_key: str, service_tag: str):
    """Mark key as exhausted for a service with cooldown."""
    state = _load_key_state()
    key_id = api_key[-8:]
    if key_id not in state:
        state[key_id] = {}
    state[key_id][service_tag] = {
        "cooldown_until": time.time() + COOLDOWN_SECONDS,
        "exhausted_at": time.time(),
    }
    _save_key_state(state)


def _record_rpm(api_key: str, service_tag: str):
    """Record an API call for RPM tracking."""
    state = _load_key_state()
    key_id = api_key[-8:]
    if key_id not in state:
        state[key_id] = {}
    if service_tag not in state[key_id]:
        state[key_id][service_tag] = {}
    calls = state[key_id][service_tag].get("rpm_calls", [])
    calls.append(time.time())
    # Keep only recent calls
    cutoff = time.time() - RPM_WINDOW
    calls = [t for t in calls if t > cutoff]
    state[key_id][service_tag]["rpm_calls"] = calls
    _save_key_state(state)


def _check_rpm(api_key: str, service_tag: str) -> bool:
    """Check if key has RPM budget remaining."""
    state = _load_key_state()
    key_id = api_key[-8:]
    calls = state.get(key_id, {}).get(service_tag, {}).get("rpm_calls", [])
    cutoff = time.time() - RPM_WINDOW
    recent = [t for t in calls if t > cutoff]
    return len(recent) < RPM_LIMIT


def _exponential_backoff(attempt: int, base: float = 2.0, max_wait: float = 30.0) -> float:
    """Calculate exponential backoff wait time."""
    return min(base ** attempt, max_wait)


# ══════════════════════════════════════════════════════════════════
#  ERROR CLASSIFICATION
# ══════════════════════════════════════════════════════════════════

def _is_key_rotation_error(error_msg: str) -> bool:
    """429/503/quota exhausted/invalid key → rotate key."""
    lower = error_msg.lower()
    return any(k in lower for k in [
        "429", "resource_exhausted", "503", "quota",
        "rate limit", "too many requests", "paid plan",
        "upgrade your account", "api key not found",
        "invalid_argument", "permission_denied", "api_key_invalid",
    ])


def _is_safety_error(error_msg: str) -> bool:
    """Safety policy violation → modify prompt."""
    lower = error_msg.lower()
    return any(k in lower for k in [
        "unsafe", "policy", "blocked", "safety",
        "harmful", "responsible ai", "image_generation_blocked",
    ])


def _get_safety_fallback_prompt(original: str, stage: int) -> str:
    """Progressively soften prompt for safety retries."""
    if stage == 0:
        # Stage 1: Remove specific player name references
        return re.sub(r"(?i)(karim benzema|lionel messi|cristiano ronaldo|[a-z]+ [a-z]+(?:inho|ovic|ez|son))",
                       "a football player", original)
    elif stage == 1:
        # Stage 2: More generic
        return ("Create a premium vertical 9:16 cinematic football portrait. "
                "Semi-realistic style, dark cinematic lighting, gold accents. "
                "Athletic male footballer in white kit, intense expression, "
                "dark stadium background. No text, no logos, no watermark.")
    else:
        # Stage 3: Ultra generic
        return ("Create a vertical 9:16 artistic football poster. "
                "Dark cinematic style with gold highlights. "
                "Athletic figure in sports attire, dramatic lighting. "
                "No text, no logos.")


# ══════════════════════════════════════════════════════════════════
#  GEMINI CLIENT FACTORY (AI Studio / Vertex AI)
# ══════════════════════════════════════════════════════════════════

def _create_client(api_key: str | None = None):
    """Create genai Client based on GEMINI_BACKEND env.

    Supports:
    - ai_studio: API Key (default)
    - vertex_ai: Service Account or ADC
    """
    from google import genai

    backend = os.getenv("GEMINI_BACKEND", "ai_studio").lower().strip()

    if backend == "vertex_ai":
        project = os.getenv("VERTEX_PROJECT", "")
        location = os.getenv("VERTEX_LOCATION", "us-central1")

        # Set GOOGLE_APPLICATION_CREDENTIALS for service account auth
        sa_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        if sa_key and not os.path.isabs(sa_key):
            # Relative path → resolve from project root
            resolved = Path(__file__).resolve().parents[3] / sa_key
            if resolved.exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(resolved)

        return genai.Client(vertexai=True, project=project, location=location)

    # AI Studio mode — need real API key
    if not api_key or api_key == "vertex_ai_service_account":
        raise RuntimeError("AI Studio mode requires a valid API key in .env")
    return genai.Client(api_key=api_key)


# ══════════════════════════════════════════════════════════════════
#  VISION VERIFICATION
# ══════════════════════════════════════════════════════════════════

def _verify_image(image_bytes: bytes, prompt: str, api_key: str) -> bool:
    """Gemini Vision으로 생성 이미지가 프롬프트와 일치하는지 검증."""
    try:
        from google.genai import types

        subject = prompt[:150]  # 프롬프트 핵심 부분
        client = _create_client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                f"Does this image show a football player matching: '{subject}'?\nAnswer ONLY 'yes' or 'no'.",
            ],
            config={"http_options": types.HttpOptions(timeout=15_000)},
        )
        answer = (response.text or "").strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        print(f"  [Vision] 검증 스킵 ({e})")
        return True  # 검증 실패 시 통과


# ══════════════════════════════════════════════════════════════════
#  PROMPT SYSTEM — Block-based assembly
# ══════════════════════════════════════════════════════════════════

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


def load_season_doc(player_id: str, season: str) -> dict:
    """Read Obsidian season doc and return frontmatter."""
    import yaml
    obsidian_root = Path(r"C:\Users\Storm Credit\Desktop\쇼츠\seasonXI\01_Players")

    player_dir = None
    for d in obsidian_root.iterdir():
        if d.is_dir() and d.name.lower() == player_id.lower():
            player_dir = d
            break
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


# ══════════════════════════════════════════════════════════════════
#  IMAGE GENERATION — Imagen 4
# ══════════════════════════════════════════════════════════════════

def _generate_imagen_raw(api_key: str, prompt: str, model_id: str) -> bytes:
    """Low-level Imagen 4 API call → returns raw image bytes."""
    from google.genai import types

    safety_level = os.getenv("IMAGEN_SAFETY_FILTER", "BLOCK_LOW_AND_ABOVE")
    client = _create_client(api_key=api_key)
    response = client.models.generate_images(
        model=model_id,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            safety_filter_level=safety_level,
            http_options=types.HttpOptions(timeout=120_000),
        ),
    )

    if not response.generated_images:
        raise ValueError("Imagen API: no images in response")

    gen_image = response.generated_images[0].image
    if hasattr(gen_image, "image_bytes") and gen_image.image_bytes:
        return gen_image.image_bytes
    raise ValueError("Imagen API: cannot extract image_bytes")


def _generate_nano_banana_raw(api_key: str, prompt: str, model_id: str) -> bytes:
    """Low-level Nano Banana (Gemini native image gen) call."""
    from google.genai import types

    client = _create_client(api_key=api_key)
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="9:16"),
        ),
    )

    for part in response.parts:
        if part.inline_data is not None:
            return part.inline_data.data

    raise ValueError(f"Nano Banana ({model_id}): no image in response")


def _save_image(image_bytes: bytes, output_path: Path) -> Path:
    """Resize to 1080x1920 and save as PNG (atomic write)."""
    from PIL import Image, ImageOps

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    fitted = ImageOps.fit(image, (1080, 1920), method=Image.LANCZOS, centering=(0.5, 0.5))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(output_path.parent), suffix=".tmp")
    os.close(fd)
    try:
        fitted.save(tmp, format="PNG")
        os.replace(tmp, str(output_path))
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise

    return output_path


# ══════════════════════════════════════════════════════════════════
#  MAIN GENERATION — Full fallback chain
# ══════════════════════════════════════════════════════════════════

def generate_image(
    prompt: str,
    output_path: Path,
    enable_vision: bool = True,
) -> Path:
    """Full image generation pipeline with fallback chain.

    Chain: Imagen 4 → Nano Banana → Gemini text+image
    Each level has key rotation + safety fallback.
    """
    backend = os.getenv("GEMINI_BACKEND", "ai_studio").lower().strip()
    all_keys = get_api_keys()

    if backend == "vertex_ai":
        # Vertex AI uses service account — no API key needed
        # Insert a placeholder so the key rotation loop works
        if not all_keys:
            all_keys = ["vertex_ai_service_account"]
        print(f"  Backend: Vertex AI (project={os.getenv('VERTEX_PROJECT', '?')})")
    else:
        if not all_keys:
            raise RuntimeError("No GEMINI_API_KEY found in .env — add keys to .env file")
        print(f"  Backend: AI Studio | Keys: {len(all_keys)}")

    use_imagen = os.getenv("IMAGEN_PAID", "").lower() in ("true", "1", "yes")

    # ── Stage 1: Imagen 4 (only if paid plan) ──
    if use_imagen:
        result = _try_model_chain(
            models=IMAGEN_MODELS,
            prompt=prompt,
            output_path=output_path,
            gen_fn=_generate_imagen_raw,
            engine_name="Imagen 4",
            enable_vision=enable_vision,
        )
        if result:
            return result
        print(f"\n  [Imagen → Nano Banana] Imagen 소진, Nano Banana로 전환...")

    # ── Stage 2: Nano Banana (primary for free tier) ──
    result = _try_model_chain(
        models=NANO_BANANA_MODELS,
        prompt=prompt,
        output_path=output_path,
        gen_fn=_generate_nano_banana_raw,
        engine_name="Nano Banana",
        enable_vision=enable_vision,
    )
    if result:
        return result

    # ── Stage 3: Gemini text+image (last resort) ──
    print(f"\n  [Nano Banana → Gemini] Nano Banana 소진, Gemini fallback...")
    result = _try_model_chain(
        models=GEMINI_FALLBACK_MODELS,
        prompt=prompt,
        output_path=output_path,
        gen_fn=_generate_nano_banana_raw,  # same API, different model
        engine_name="Gemini Fallback",
        enable_vision=False,
    )
    if result:
        return result

    raise RuntimeError("All image engines and keys exhausted")


def _try_model_chain(
    models: list[dict],
    prompt: str,
    output_path: Path,
    gen_fn,
    engine_name: str,
    enable_vision: bool = True,
) -> Path | None:
    """Try a chain of models with key rotation + safety fallback.

    Returns output_path on success, None if all exhausted.
    """
    for model_idx, model in enumerate(models):
        model_id = model["id"]
        model_label = model["label"]
        service_tag = model["tag"]

        # Reset prompt for each model (safety fallback may have changed it)
        current_prompt = prompt
        safety_stage = 0
        tried_keys: set[str] = set()
        key_attempt = 0

        while key_attempt < MAX_KEY_RETRIES:
            api_key = _get_available_key(service_tag, exclude=tried_keys)
            if not api_key:
                break  # No keys left for this model

            tried_keys.add(api_key)

            # RPM check
            if not _check_rpm(api_key, service_tag):
                wait = _exponential_backoff(key_attempt, base=1.5, max_wait=10)
                print(f"  [{model_label}] RPM 한도 근접, {wait:.1f}초 대기...")
                time.sleep(wait)

            if key_attempt == 0 and model_idx == 0:
                print(f"  [{engine_name}] {model_label} 렌더링 중...")
            elif key_attempt == 0:
                print(f"  [{engine_name}] {model_label}로 폴백...")
            else:
                print(f"  [{model_label}] 키 #{key_attempt+1} 재시도 ({_mask_key(api_key)})")

            try:
                image_bytes = gen_fn(api_key, current_prompt, model_id)

                if not image_bytes:
                    raise ValueError("Empty image response")

                # Vision verification
                if enable_vision:
                    verify_key = _get_available_key("gemini_vision", exclude=tried_keys) or api_key
                    if not _verify_image(image_bytes, current_prompt, verify_key):
                        vision_key = f"_vision_{model_id}"
                        if not hasattr(generate_image, vision_key):
                            setattr(generate_image, vision_key, 0)
                        retries = getattr(generate_image, vision_key)
                        if retries < MAX_VISION_RETRIES:
                            setattr(generate_image, vision_key, retries + 1)
                            print(f"  [Vision] 불일치 → 재생성...")
                            continue
                        else:
                            print(f"  [Vision] 재생성 후에도 불일치 — 결과 유지")

                # Save
                _save_image(image_bytes, output_path)
                _record_rpm(api_key, service_tag)
                print(f"  [{engine_name}] {model_label} 완료! → {output_path.name}")
                return output_path

            except Exception as e:
                error_msg = str(e)

                if _is_key_rotation_error(error_msg):
                    _mark_key_exhausted(api_key, service_tag)
                    backoff = _exponential_backoff(key_attempt, base=2.0, max_wait=30)
                    print(f"  [{model_label}] {_mask_key(api_key)} 차단 → {backoff:.1f}초 후 다른 키")
                    time.sleep(backoff)
                    key_attempt += 1
                    continue

                if _is_safety_error(error_msg) and safety_stage < 3:
                    current_prompt = _get_safety_fallback_prompt(prompt, safety_stage)
                    safety_stage += 1
                    tried_keys.discard(api_key)  # Same key OK for safety retry
                    print(f"  [{model_label}] 안전 정책 위반 → 프롬프트 수정 ({safety_stage}/3)")
                    continue

                print(f"  [{model_label}] 실패: {error_msg[:120]}")
                break  # Give up this model → next model

        # This model exhausted → next model in chain
        if model_idx < len(models) - 1:
            next_label = models[model_idx + 1]["label"]
            print(f"  [{model_label}] 전 키 소진 → {next_label}로 전환...")

    return None  # All models in this chain exhausted


# ══════════════════════════════════════════════════════════════════
#  READY-TO-USE PROMPT FILE GENERATION
# ══════════════════════════════════════════════════════════════════

def generate_from_prompt_file(prompt_file: Path, output_path: Path) -> Path:
    """Generate image directly from a ready-to-paste prompt file."""
    prompt = prompt_file.read_text(encoding="utf-8").strip()
    return generate_image(prompt, output_path)


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="SeasonXI Image Generator (Imagen 4 + Nano Banana)")
    parser.add_argument("--player", required=True, help="Player ID (e.g., messi)")
    parser.add_argument("--season", required=True, help="Season (e.g., 2011-12)")
    parser.add_argument("--scene", default="HOOK", help="Scene type (HOOK, CARD_BACKGROUND, EMOTION_CLOSEUP)")
    parser.add_argument("--count", type=int, default=1, help="Number of variants")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--prompt-only", action="store_true", help="Print prompt without generating")
    parser.add_argument("--prompt-file", type=str, default=None, help="Use ready-to-paste prompt file directly")
    parser.add_argument("--no-vision", action="store_true", help="Skip vision verification")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  SeasonXI Image Generator v2.0")
    print(f"  {args.player.upper()} {args.season} / {args.scene}")
    print(f"  Chain: Nano Banana → Gemini Fallback (Imagen 4 if paid)")
    print(f"{'='*60}\n")

    # ── Prompt from file (ready-to-paste) ──
    if args.prompt_file:
        pf = Path(args.prompt_file)
        if not pf.exists():
            print(f"  ERROR: Prompt file not found: {pf}")
            sys.exit(1)
        prompt = pf.read_text(encoding="utf-8").strip()
        if args.prompt_only:
            print(prompt)
            return
    else:
        # ── Prompt from blocks ──
        try:
            data = load_season_doc(args.player, args.season)
            player_block = data.get("player_block", args.player.upper())
            mood = data.get("season_mood", "PEAK_MONSTER")
            mod_key = "hook_modifiers" if "HOOK" in args.scene.upper() else "card_modifiers"
            modifiers = data.get(mod_key, [])
            if isinstance(modifiers, list):
                modifiers = [m for m in modifiers if m]
            else:
                modifiers = []
        except FileNotFoundError:
            print(f"  Season doc not found, using defaults")
            player_block = args.player.upper()
            mood = "PEAK_MONSTER"
            modifiers = []

        prompt = assemble_prompt(player_block, mood, args.scene, modifiers)

        if args.prompt_only:
            print(prompt)
            return

        print(f"  Player: {player_block} | Mood: {mood}")
        print(f"  Scene: {args.scene} | Modifiers: {modifiers or 'none'}")

    print(f"  Count: {args.count} | Vision: {'off' if args.no_vision else 'on'}")
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
            generate_image(prompt, output_path, enable_vision=not args.no_vision)
        except Exception as e:
            print(f"  ERROR: {e}")

        if i < args.count - 1:
            time.sleep(3)

    print(f"\n  Done! Check: {out_dir}")


if __name__ == "__main__":
    main()
