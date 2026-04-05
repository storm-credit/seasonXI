"""ElevenLabs TTS for SeasonXI narration generation.

Usage:
    import asyncio
    from seasonxi.content.tts_elevenlabs import generate_elevenlabs_tts

    path = asyncio.run(generate_elevenlabs_tts(script, output_path))
"""

from __future__ import annotations

import asyncio
import os
import random
import tempfile
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")
import time
from pathlib import Path

import requests

MAX_RETRIES = 3
DEFAULT_VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"  # Josh (다큐/스포츠 나레이션)
MODEL_ID = "eleven_multilingual_v2"
API_BASE = "https://api.elevenlabs.io/v1"


def _backoff_delay(attempt: int) -> float:
    """지수 백오프 + 지터."""
    base = min(2 ** (attempt + 1), 16)  # 2, 4, 8, 16 cap
    return base + random.uniform(0, base * 0.5)


async def generate_elevenlabs_tts(
    script: str,
    output_path: Path,
    voice_id: str = DEFAULT_VOICE_ID,
    speed: float = 0.95,
) -> Path:
    """ElevenLabs TTS로 나레이션 MP3 생성.

    Args:
        script: 나레이션 텍스트
        output_path: 저장 경로 (MP3)
        voice_id: ElevenLabs Voice ID (기본: Adam)
        speed: 말하기 속도 (0.7~1.2, 기본: 0.95)

    Returns:
        생성된 MP3 파일 경로

    Raises:
        RuntimeError: API 키 없음 또는 최대 재시도 초과
    """
    # Run blocking I/O in thread pool so caller stays async-friendly
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _generate_blocking,
        script,
        output_path,
        voice_id,
        speed,
    )
    return result


def _generate_blocking(
    script: str,
    output_path: Path,
    voice_id: str,
    speed: float,
) -> Path:
    """실제 HTTP 요청 처리 (동기 블로킹)."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "[ElevenLabs] ELEVENLABS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요."
        )

    url = f"{API_BASE}/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": script,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.75,
            "style": 0.48,
            "use_speaker_boost": True,
        },
        "speed": speed,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(MAX_RETRIES):
        label = f" (시도 {attempt + 1}/{MAX_RETRIES})" if attempt > 0 else ""
        print(f"[ElevenLabs] 나레이션 생성 중...{label}")

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30, stream=True)

            if response.status_code == 200:
                tmp_path = None
                try:
                    fd, tmp_str = tempfile.mkstemp(dir=str(output_path.parent), suffix=".tmp")
                    tmp_path = Path(tmp_str)
                    os.close(fd)

                    with open(tmp_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=4096):
                            if chunk:
                                f.write(chunk)

                    if tmp_path.stat().st_size == 0:
                        tmp_path.unlink(missing_ok=True)
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(_backoff_delay(attempt))
                            continue
                        raise RuntimeError("[ElevenLabs] 빈 오디오 파일 반환됨.")

                    tmp_path.replace(output_path)
                    print(f"[ElevenLabs] 완료: {output_path} ({output_path.stat().st_size:,} bytes)")
                    return output_path

                except RuntimeError:
                    raise
                except Exception as write_exc:
                    response.close()
                    if tmp_path:
                        tmp_path.unlink(missing_ok=True)
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(_backoff_delay(attempt))
                        continue
                    raise RuntimeError(f"[ElevenLabs] 파일 쓰기 실패: {write_exc}") from write_exc

            elif response.status_code == 401:
                response.close()
                raise RuntimeError("[ElevenLabs] API Key가 유효하지 않습니다.")

            elif response.status_code == 429:
                response.close()
                wait = _backoff_delay(attempt)
                print(f"[ElevenLabs] 할당량 초과, {wait:.1f}초 후 재시도...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(wait)
                    continue
                raise RuntimeError("[ElevenLabs] 할당량 초과 — 최대 재시도 횟수 도달.")

            else:
                err_body = response.text[:200]
                response.close()
                print(f"[ElevenLabs] HTTP {response.status_code}: {err_body}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(_backoff_delay(attempt))
                    continue
                raise RuntimeError(f"[ElevenLabs] 요청 실패 ({response.status_code})")

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as net_err:
            print(f"[ElevenLabs] 네트워크 오류: {net_err} ({attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(_backoff_delay(attempt))
                continue
            raise RuntimeError(f"[ElevenLabs] 네트워크 오류로 실패: {net_err}") from net_err

    raise RuntimeError("[ElevenLabs] 알 수 없는 오류로 생성 실패.")
