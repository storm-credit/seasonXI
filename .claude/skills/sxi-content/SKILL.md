---
name: sxi-content
description: "Manage SeasonXI content production — images, narration, TTS, prompts, YouTube. Use when the user wants to: generate images, create narration, run TTS, manage prompts, prepare YouTube upload, or work on the content pipeline."
---

# SXI Content — Production Management

추천 모델: **haiku** (실행) / **sonnet** (스크립트 품질 검토)
에이전트 역할: **"너는 축구 쇼츠 콘텐츠 프로듀서야. 이미지 생성, 나레이션 TTS, YouTube 메타데이터를 관리해."**

## 이미지 생성 (Vertex AI + Nano Banana)
```bash
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=hook"
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=card"
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=closeup"
```
출력: `remotion/public/{player_id}_{season}/{player_id}_{season_underscore}_{scene}_v1.png`

## 나레이션 생성 (Gemini + Edge TTS)
```bash
curl -X POST "http://localhost:8800/api/generate-narration/{player_id}/{season}"
```
- Gemini 2.5 Flash → 45초 영어 나레이션
- Edge TTS en-US-AndrewNeural (rate=-5%, pitch=-2Hz)
- 출력: `remotion/public/{player_id}_{season}/narration.mp3`

## YouTube 메타데이터
```bash
curl "http://localhost:8800/api/youtube-metadata/{player_id}/{season}"
```

## 원클릭 준비 → sxi-prepare 스킬 사용

## 주요 파일
- `src/seasonxi/content/generate_image.py` — 이미지 (Nano Banana 폴백)
- `src/seasonxi/content/youtube_metadata.py` — 메타데이터
- `configs/image_prompts/prompt_sets/` — 선수별 프롬프트
- `configs/suno_prompts.txt` — 수노 BGM (60초 섹션 마커)
