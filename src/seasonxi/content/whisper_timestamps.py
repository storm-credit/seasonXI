"""Whisper 기반 단어별 타임스탬프 추출."""
import re
from pathlib import Path


def extract_word_timestamps(audio_path: Path, language: str = "en") -> list[dict]:
    """faster-whisper로 단어 단위 타임스탬프 추출.

    Returns:
        [{"word": "They", "start": 0.0, "end": 0.3}, ...]
    """
    from faster_whisper import WhisperModel

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
    )

    words = []
    for segment in segments:
        for word in segment.words:
            words.append({
                "word": word.word.strip(),
                "start": round(word.start, 3),
                "end": round(word.end, 3),
            })

    return words


def words_to_subtitle_cues(
    words: list[dict],
    fps: int = 30,
    max_words_per_cue: int = 8,
    offset_frames: int = 3,
) -> list[dict]:
    """단어 타임스탬프를 Remotion SubtitleCue 배열로 변환.

    여러 단어를 묶어서 한 줄 자막으로. 카드 리빌 구간(900-1050 프레임)은 건너뜀.

    Returns:
        [{"startFrame": 10, "endFrame": 80, "text": "They said he was nothing", "highlight": "nothing"}, ...]
    """
    if not words:
        return []

    cues = []
    i = 0

    while i < len(words):
        # 현재 단어 그룹 시작
        group_words = []
        group_start = words[i]["start"]

        # max_words_per_cue개씩 묶기, 또는 문장 끝(마침표/물음표/느낌표)에서 자르기
        while i < len(words) and len(group_words) < max_words_per_cue:
            group_words.append(words[i])
            # 문장 끝이면 여기서 자르기
            if words[i]["word"].rstrip().endswith(('.', '!', '?', ',')):
                i += 1
                break
            i += 1

        if not group_words:
            continue

        group_end = group_words[-1]["end"]
        text = " ".join(w["word"] for w in group_words).replace(",", "").replace("  ", " ").strip()

        start_frame = int(group_start * fps) + offset_frames  # 자막이 말보다 살짝 늦게
        end_frame = int(group_end * fps) + offset_frames + 6

        # 카드 리빌 구간 (900-1050) 건너뛰기
        if start_frame >= 880 and start_frame < 1060:
            continue

        # 하이라이트: 숫자나 대문자 단어 찾기
        highlight = None
        for w in group_words:
            clean = w["word"].strip('.,!?;:')
            if clean.isdigit() and int(clean) > 1:
                highlight = clean
                break
            if (
                len(clean) > 3
                and clean[0].isupper()
                and clean not in (
                    "They", "This", "That", "When", "Some",
                    "And", "But", "The", "His", "Her", "One",
                )
            ):
                highlight = clean
                break

        cues.append({
            "startFrame": start_frame,
            "endFrame": end_frame,
            "text": text,
            "highlight": highlight,
        })

    return cues


# ─── Scene timing constants ───────────────────────────────────────────────────
_SCENE_MARKERS = ["HOOK", "STORY", "HIGHLIGHTS", "EMOTION", "VERDICT"]
_STATS_DURATION = 150   # 5s
_VERDICT_DURATION = 120  # 4s


def _normalise_word(w: str) -> str:
    """Strip punctuation and lowercase for loose matching."""
    return re.sub(r"[^\w]", "", w).lower()


def _find_marker_sections(script: str) -> dict[str, str]:
    """Return {marker: text_after_marker} for each [MARKER] found in script."""
    sections: dict[str, str] = {}
    pattern = re.compile(r"\[([A-Z]+)\](.*?)(?=\[[A-Z]+\]|$)", re.DOTALL)
    for m in pattern.finditer(script):
        sections[m.group(1)] = m.group(2).strip()
    return sections


def _first_words(text: str, n: int = 3) -> list[str]:
    """Return up to n normalised words from the start of text."""
    raw = re.split(r"\s+", text.strip())
    return [_normalise_word(w) for w in raw[:n] if w]


def _find_frame_for_words(
    target_words: list[str],
    whisper_words: list[dict],
    fps: int,
) -> float | None:
    """Search whisper_words for the sequence target_words and return start time (s) of first word.

    Uses a sliding window match so minor extra punctuation is tolerated.
    Returns None if not found.
    """
    if not target_words or not whisper_words:
        return None

    norm_whisper = [_normalise_word(w["word"]) for w in whisper_words]
    n = len(target_words)

    for i in range(len(norm_whisper) - n + 1):
        window = norm_whisper[i : i + n]
        if all(a == b for a, b in zip(target_words, window)):
            return whisper_words[i]["start"]
    return None


def compute_scene_timing(
    words: list[dict],
    script: str,
    fps: int = 30,
    card_reveal_duration: int = 150,  # 5s (줄임: 7s→5s)
    outro_duration: int = 90,         # 3s (줄임: 5s→3s)
) -> dict:
    """Whisper 단어 타임스탬프 + 스크립트 씬 마커로 동적 씬 타이밍 계산.

    스크립트에서 각 씬의 첫 단어를 찾고, Whisper에서 그 단어의 시작 시간을 매핑.

    Returns:
        {
            "hook": {"start": 0, "end": 150},
            "story": {"start": 150, "end": 420},
            ...
            "total_frames": 1950,
        }
    """
    # ── 1. Try marker-based extraction ──────────────────────────────────────
    sections = _find_marker_sections(script)
    marker_frames: dict[str, int] = {}

    if sections:
        for marker in _SCENE_MARKERS:
            text = sections.get(marker, "")
            first_ws = _first_words(text, 3)
            if not first_ws:
                continue
            t = _find_frame_for_words(first_ws, words, fps)
            if t is not None:
                marker_frames[marker.lower()] = int(t * fps)

    # ── 2. Narration end frame ───────────────────────────────────────────────
    narration_end_frame = int(words[-1]["end"] * fps) if words else 0

    # ── 3. Build timing ─────────────────────────────────────────────────────
    # Narration scenes: hook, story, highlights, emotion (always)
    # VERDICT is added if its marker was found in the narration
    base_narration_keys = ["hook", "story", "highlights", "emotion"]
    has_verdict_narration = "verdict" in marker_frames
    narration_scene_keys = base_narration_keys + (["verdict"] if has_verdict_narration else [])

    if len(marker_frames) >= 2:
        # Marker-based: use detected start times, infer ends from next scene start
        scene_starts: list[tuple[str, int]] = []
        for key in narration_scene_keys:
            if key in marker_frames:
                scene_starts.append((key, marker_frames[key]))

        # Sort by frame order (they should already be ordered but be safe)
        scene_starts.sort(key=lambda x: x[1])

        timing: dict[str, dict] = {}
        for idx, (key, start) in enumerate(scene_starts):
            if idx + 1 < len(scene_starts):
                end = scene_starts[idx + 1][1]
            else:
                end = narration_end_frame
            timing[key] = {"start": start, "end": end}

        # Fill any missing narration scenes with equal slices between neighbours
        all_filled_starts = [v["start"] for v in timing.values()]
        segment_start = 0
        segment_end = narration_end_frame
        missing = [k for k in narration_scene_keys if k not in timing]
        if missing:
            slice_size = (segment_end - segment_start) // (len(narration_scene_keys))
            for i, key in enumerate(narration_scene_keys):
                if key not in timing:
                    s = segment_start + i * slice_size
                    e = segment_start + (i + 1) * slice_size
                    timing[key] = {"start": s, "end": e}
            # Re-sort by scene order to make sure ends are contiguous
            for i, key in enumerate(narration_scene_keys):
                if i + 1 < len(narration_scene_keys):
                    next_key = narration_scene_keys[i + 1]
                    timing[key]["end"] = timing[next_key]["start"]
                else:
                    timing[key]["end"] = narration_end_frame

    else:
        # ── Fallback: divide narration evenly across base 4 scenes only ──────
        total_narration = narration_end_frame
        slice_size = total_narration // 4
        timing = {}
        for i, key in enumerate(base_narration_keys):
            timing[key] = {
                "start": i * slice_size,
                "end": (i + 1) * slice_size if i < 3 else total_narration,
            }

    # Hook always starts at 0
    if "hook" in timing:
        timing["hook"]["start"] = 0

    # ── 4. Post-narration scenes ─────────────────────────────────────────────
    # Card reveal goes after EMOTION (not after VERDICT) when VERDICT is in narration.
    # This lets VERDICT narration play on top of the stats/verdict visual scenes
    # without a silent gap — card reveal is the only true silence.
    if has_verdict_narration and "emotion" in timing:
        card_reveal_start = timing["emotion"]["end"]
    else:
        card_reveal_start = narration_end_frame

    card_reveal_end = card_reveal_start + card_reveal_duration

    stats_start = card_reveal_end
    stats_end = stats_start + _STATS_DURATION

    # VERDICT narration starts WITH stats (no silent gap)
    # Stats scene shows graph+bars while VERDICT narration plays
    if has_verdict_narration and "verdict" in timing:
        verdict_start = stats_start  # Same as stats — narration covers both
        verdict_end = max(stats_end + _VERDICT_DURATION, timing["verdict"]["end"])
    else:
        verdict_start = stats_end
        verdict_end = verdict_start + _VERDICT_DURATION

    outro_start = max(verdict_end, narration_end_frame)
    outro_end = outro_start + outro_duration

    timing["cardReveal"] = {"start": card_reveal_start, "end": card_reveal_end}
    timing["stats"] = {"start": stats_start, "end": stats_end}
    timing["verdict"] = {"start": verdict_start, "end": verdict_end}
    timing["outro"] = {"start": outro_start, "end": outro_end}
    timing["total_frames"] = outro_end

    return timing
