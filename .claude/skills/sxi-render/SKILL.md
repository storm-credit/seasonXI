---
name: sxi-render
description: "Render SeasonXI Shorts videos using Remotion. Use when the user wants to: create a video, render MP4, make a Shorts clip, preview a card video, or export a player's season card as video. Also trigger for 'render Messi', 'make Benzema video', etc."
---

# SXI Render — Video Generation

추천 모델: **haiku** (단순 실행)
에이전트 역할: **"너는 Remotion 비디오 렌더링 엔지니어야. SeasonStory 60초 컴포지션을 렌더하고 결과를 보고해."**

## 렌더 API (메인)
```bash
curl -X POST "http://localhost:8800/api/render/{player_id}/{season}"
# 예시: curl -X POST "http://localhost:8800/api/render/benzema/2021-22"
```

## 렌더 상태 확인
```bash
curl "http://localhost:8800/api/render-status/{player_id}/{season}"
```

## 컴포지션
- **SeasonStory** (60초, 1800 frames) — 메인 (나레이션 + 카드 리빌 + 스탯)
- SeasonCard (12초, 360 frames) — 레거시

## 에셋 필요 (렌더 전 확인)
```
remotion/public/{player_id}_{season}/
  {player_id}_{season_underscore}_hook_v1.png    ← sxi-prepare로 생성
  {player_id}_{season_underscore}_card_v1.png
  {player_id}_{season_underscore}_closeup_v1.png
  narration.mp3                                   ← sxi-prepare로 생성
  bgm.mp3                                         ← 수동 (Suno)
```

## 8씬 구조 (60초)
1. Hook (0-5s) — hookStat 큰 숫자 + 이미지 줌인
2. Story (5-15s) — Ken Burns + storyText + 자막
3. Highlights (15-25s) — 골 숫자 팝업
4. Emotion (25-30s) — 빌드업
5. Card Reveal (30-35s) — 플래시 + 셰이크 + 카드 등장
6. Stats (35-45s) — 스탯 바 카운트업 + 육각 그래프
7. Verdict (45-55s) — TierBadge + 클로즈업
8. Outro (55-60s) — SeasonXI 로고 + CTA + 다음 선수 티저

## Remotion Studio
```
http://localhost:3334
```

## 주요 파일
- `remotion/src/SeasonStory.tsx` — 60초 메인 컴포지션
- `remotion/src/Root.tsx` — 컴포지션 등록 + 기본 데이터
- `remotion/render-server.js` — 렌더 서버 (포트 3335)
- `src/seasonxi/api/server.py` — 렌더 API (line 201)
