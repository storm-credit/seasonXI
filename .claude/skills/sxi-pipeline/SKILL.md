---
name: sxi-pipeline
description: "Run the SeasonXI HANESIS pipeline to rate football players. Use this skill whenever the user wants to: run the rating engine, generate player cards, check player ratings, update the database, re-run the pipeline after data changes, or see tier distributions. Also trigger when the user mentions 'pipeline', 'rate players', 'generate cards', 'HANESIS', 'engine run', or asks about specific player OVR/ratings from real data."
---

# SXI Pipeline — HANESIS Full Run

추천 모델: **haiku** (단순 실행)
에이전트 역할: **"너는 축구 데이터 파이프라인 오퍼레이터야. HANESIS 7단계를 순서대로 실행하고 결과를 보고해."**

SXI Engine **v3** 파이프라인. FBref + Understat + Sofascore 4소스 병합, v3 공식으로 ~2000명 레이팅, 카드 JSON 익스포트.
- Sofascore 버그 수정됨 (FBREF_PCT_MAP / SOFASCORE_PCT_MAP 분리)
- 포지션 분류 v3: 다중 지표 점수 기반 (FW 18%)
- 리그 보정: epl/laliga/bundesliga/seriea/ligue1 매핑

## When to use

- User says "run the pipeline", "rate the players", "generate cards"
- User wants to see real player ratings (not simulated)
- User changed engine formula and wants to see impact
- User added new data and wants to re-rate
- User asks "what's Salah's rating?" and needs pipeline results

## How to run

```bash
cd C:\ProjectS\seasonXI
PYTHONIOENCODING=utf-8 uv run python scripts/merge_and_run.py
```

## What it does (HANESIS 7 stages)

1. **H (Harvest):** Load 5-league FBref CSVs + Understat xG/xA
2. **A (Align):** Fuzzy-match FBref names to Understat (95% match rate), merge defense data
3. **N (Normalize):** Per90, percentile within position, proxy missing features
4. **E (Evaluate):** SXI Engine v3 — 6 stats, GK clean_sheets 오염 제거, MENTAL 팀 독립, adaptive overall 중앙화
5. **S (Synergize):** Validate known players (Salah, Son, Benzema, etc.)
6. **I (Infer):** Anomaly detection, Top 20 ranking, tier distribution
7. **S (Storyframe):** Export to outputs/cards/_all_cards_v2_merged.json

## Expected output

- ~2030 rated players
- Tier distribution: Mythic 0-2, Legendary 5-25, Elite 50-150
- Known players should be Elite+ (88+)
- JSON cards exported for Remotion rendering

## Key files

- `scripts/merge_and_run.py` — main pipeline script
- `data/raw/fbref/` — FBref player CSVs (5 leagues)
- `data/raw/understat/` — Understat xG/xA data
- `data/raw/fbref_extra/` — Defense data (tackles, interceptions)
- `src/seasonxi/ratings/formula_v1.py` — SXI Engine v3 (formula_version="v3")
- `src/seasonxi/ratings/league_adjustment.py` — 리그 보정 (epl/laliga/ligue1 등)
- `data/raw/sofascore/` — Sofascore 데이터
- `outputs/cards/` — exported card JSONs

## After running

Show the user:
1. Top 10 players with full stats
2. Tier distribution
3. Any anomalies or surprising results
4. Whether known players are rated correctly

## Troubleshooting

- If Mythic=0: Check if Understat data was loaded (xG/xA should not be 0)
- If all DEF=74: Defense CSV files missing from data/raw/fbref_extra/
- If FW STAMINA too low: Check FW stamina_raw formula doesn't include tackles
