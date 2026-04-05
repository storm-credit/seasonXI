---
name: sxi-prepare
description: "Prepare all content assets for a SeasonXI player — 3 images + narration + TTS. Use when: 'prepare Benzema', 'get salah ready', 'generate all assets'."
---

# SXI Prepare — 선수 콘텐츠 원클릭 준비

역할: 이미지 3장 + 나레이션 MP3를 순서대로 한번에 생성
추천 모델: **haiku**

## 실행 순서

```bash
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=hook"
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=card"
curl -X POST "http://localhost:8800/api/generate-image/{player_id}/{season}?scene=closeup"
curl -X POST "http://localhost:8800/api/generate-narration/{player_id}/{season}"
```

## 출력 확인

```
remotion/public/{player_id}_{season}/
  {player_id}_{season_underscore}_hook_v1.png
  {player_id}_{season_underscore}_card_v1.png
  {player_id}_{season_underscore}_closeup_v1.png
  narration.mp3
  bgm.mp3  ← 수동 추가 (Suno)
```

## 완료 후

BGM 추가 → 대시보드 RENDER 클릭 → 영상 완성
