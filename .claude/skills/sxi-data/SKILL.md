---
name: sxi-data
description: "Manage SeasonXI data collection and scraping. Use when the user wants to: scrape FBref, fetch Understat data, collect new season data, add a league, update raw data, check data quality, or mentions 'data collection', 'scraping', 'FBref', 'Understat'."
---

# SXI Data — Collection & Management

추천 모델: **sonnet** (데이터 검증/이상치 판단 필요)
에이전트 역할: **"너는 축구 데이터 엔지니어야. 4개 소스(FBref/Understat/Sofascore)에서 원시 데이터를 수집하고 품질을 검증해."**

## 현재 보유 데이터

| 시즌 | FBref | Understat | FBref Defense | Sofascore | 상태 |
|------|-------|-----------|---------------|-----------|------|
| 2021-22 | 5리그 ✅ | ✅ | 5리그 ✅ | ✅ | **완비** |
| 2024-25 | EPL만 ⚠️ | ✅ | ❌ | ❌ | **부분** |
| 2023-24 | ❌ | ❌ | ❌ | ❌ | **미수집** |
| 2011-12 | ❌ | ❌ | ❌ | ❌ | **미수집 (Mythic 검증용)** |

## 4개 데이터 소스

| 소스 | 경로 |
|------|------|
| FBref 메인 | `data/raw/fbref/*.csv` |
| FBref Defense | `data/raw/fbref_extra/*.csv` |
| Understat | `data/raw/understat/*.csv` |
| Sofascore | `data/raw/sofascore/*.csv` |

## 데이터 수집 방법 (rate limit 안전)

### 방법 1: Kaggle (가장 안전, 추천)
```
- FBref 역대 데이터가 CSV로 정리된 데이터셋
- rate limit 없음, 한번에 다운로드
- 키워드: "fbref football stats", "football player statistics"
```

### 방법 2: Understat 자동 수집
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/fetch_understat.py
```

### 방법 3: Chrome MCP 직접 스크래핑
```
- FBref 페이지를 Chrome으로 열고 테이블 복사
- rate limit 거의 없음 (브라우저 요청이라)
- 수동이지만 안전
```

### 방법 4: soccerdata 라이브러리 (rate limit 주의)
```bash
# 5-10초 딜레이 자동 적용
PYTHONIOENCODING=utf-8 uv run python scripts/fetch_fbref_slow.py
```

## 새 시즌 추가 절차

```
1. FBref 5리그 players CSV 수집 → data/raw/fbref/
2. FBref Defense CSV 수집 → data/raw/fbref_extra/
3. Understat xG/xA CSV 수집 → data/raw/understat/
4. Sofascore CSV 수집 → data/raw/sofascore/
5. merge_and_run.py에 시즌 경로 추가
6. sxi-pipeline 재실행
7. sxi-engine-check 검증
```

## 멀티시즌 목표

```
우선순위:
1. 2023-24 — 최근 완료 시즌 (비교 기준)
2. 2024-25 — 현재 시즌 (나머지 4리그)
3. 2011-12 — 메시 73골 (Mythic 검증)
4. 2013-14 — 호날두 61골 (Mythic 검증)
```

## v3 변경사항
- FBREF_PCT_MAP / SOFASCORE_PCT_MAP 분리 (override 버그 수정)
- 포지션별 percentile 범위 (clean_sheets는 DF/GK에만)
- 리그 보정 매핑: epl/laliga/bundesliga/seriea/ligue1

## 주의사항
- `data/raw/` 원시 데이터 절대 덮어쓰지 않기
- 새 시즌 추가 시 4소스 모두 수집 필요
- 수집 후 `sxi-pipeline` 스킬로 파이프라인 재실행
- FBref rate limit: 분당 20요청 이하

## 주요 파일
- `scripts/fetch_understat.py` — Understat 자동 수집
- `scripts/fetch_fbref_slow.py` — FBref 느린 수집 (rate limit 대응)
- `scripts/merge_and_run.py` — 4소스 병합 (N단계)
- `src/seasonxi/ratings/league_adjustment.py` — 리그 보정
