---
name: sxi-data
description: "Manage SeasonXI data collection and scraping. Use when the user wants to: scrape FBref, fetch Understat data, collect new season data, add a league, update raw data, check data quality, or mentions 'data collection', 'scraping', 'FBref', 'Understat'."
---

# SXI Data — Collection & Management

추천 모델: **sonnet** (데이터 검증/이상치 판단 필요)
에이전트 역할: **"너는 축구 데이터 엔지니어야. 4개 소스(FBref/Understat/Sofascore)에서 원시 데이터를 수집하고 품질을 검증해."**

## 4개 데이터 소스

| 소스 | 경로 |
|------|------|
| FBref 메인 | `data/raw/fbref/*.csv` |
| FBref Defense | `data/raw/fbref_extra/*.csv` |
| Understat | `data/raw/understat/*.csv` |
| Sofascore | `data/raw/sofascore/*.csv` |

## Understat 수집
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/fetch_understat.py
```

## v3 변경사항
- FBREF_PCT_MAP / SOFASCORE_PCT_MAP 분리 (override 버그 수정)
- 포지션별 percentile 범위 (clean_sheets는 DF/GK에만)
- 리그 보정 매핑: epl/laliga/bundesliga/seriea/ligue1

## 주의사항
- `data/raw/` 원시 데이터 절대 덮어쓰지 않기
- 새 시즌 추가 시 4소스 모두 수집 필요
- 수집 후 `sxi-pipeline` 스킬로 파이프라인 재실행

## 주요 파일
- `scripts/fetch_understat.py` — Understat 자동 수집
- `scripts/merge_and_run.py` — 4소스 병합 (N단계)
- `src/seasonxi/ratings/league_adjustment.py` — 리그 보정
