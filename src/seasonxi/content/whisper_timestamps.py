"""Whisper 기반 단어별 타임스탬프 추출."""
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
        text = " ".join(w["word"] for w in group_words)

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
