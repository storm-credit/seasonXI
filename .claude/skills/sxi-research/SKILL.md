---
name: sxi-research
description: "Research better algorithms for SXI Engine. Use when: 'improve the engine', 'better formula', 'latest research', 'optimize ratings', 'why is GK too high', 'how to fix DF undervaluation', or any question about engine accuracy improvement."
---

# SXI Research — 엔진 알고리즘 연구

추천 모델: **opus** (깊은 분석 + 최신 연구 참조)
에이전트 역할: **"너는 축구 분석 알고리즘 연구원이야. 최신 논문(PlayeRank, VAEP, xT, Atomic-SPADL)과 업계 모델(FIFA EA, FiveThirtyEight, OPTA)을 참고해서 SXI Engine 성능 개선 방안을 제안해."**

## 연구 영역

### 1. 공식 정확도 개선
- 현재 v3 공식 vs 최신 연구 비교
- 피처 가중치 최적화 (아키타입 피팅, 그리드 서치)
- 포지션별 공식 세분화 (FW 내 CF/Winger/SS 구분)

### 2. 새 피처 후보
- xGChain / xGBuildup (팀 기여도)
- Progressive Actions (전진 패스/캐리/드리블 통합)
- VAEP (Valuing Actions by Estimating Probabilities)
- xT (Expected Threat) — 공간 점유 가치
- Pressing Intensity Index
- Defensive Action Expected Threat (xDEF)

### 3. 알려진 문제 연구
- GK Top 10 과다 — GK OVR 천장 로직 필요?
- DF 하위팀 과대평가 — 수비 부담 보정 방법?
- FW 분류 17.8% — 목표 22-26% 달성 방법?
- Mythic 0명 — 95+ 도달 불가능한 구조적 문제?
- confidence 비선형 커브 최적화

### 4. 참고 논문/모델
- PlayeRank (Pappalardo et al., 2019) — 멀티 역할 기반 선수 평가
- VAEP (Decroos et al., 2019) — 행동 기반 가치 평가
- xT (Karun Singh, 2018) — 공간 위협 모델
- Atomic-SPADL (Decroos, 2020) — 세분화된 행동 단위
- FIFA EA Rating System — 업계 표준 참조
- FiveThirtyEight SPI — 팀/선수 성과 예측

### 5. 연구 방법론
```
1. WebSearch로 최신 논문/블로그 검색
2. 현재 SXI 공식과 비교 분석
3. 개선안 설계 (공식 변경 제안)
4. 시뮬레이션: 특정 선수에 적용해서 영향도 확인
5. 보고서: 현재 vs 제안 비교표
```

## 현재 v3 공식 요약 (연구 기준선)

- 6스탯: ATT/DEF/PACE/AURA/STAMINA/MENTAL
- _stretch(k=4.5) sigmoid
- _adaptive_overall(boost=5%)
- confidence = min(1.0, (min/1800)^0.7)
- 리그 보정: epl 1.04, ligue1 0.92

## 주요 파일
- `src/seasonxi/ratings/formula_v1.py` — 현재 v3 공식
- `src/seasonxi/ratings/league_adjustment.py` — 리그 보정
- `src/seasonxi/ratings/team_debiasing.py` — 팀 편향 제거
- `src/seasonxi/ratings/confidence.py` — 출전 시간 신뢰도
- `scripts/merge_and_run.py` — 데이터 파이프라인
- `tests/` — 검증 테스트

## 보고 형식
1. 현재 문제점 진단
2. 참고한 논문/모델 (출처 포함)
3. 구체적 개선안 (공식 변경 코드 수준)
4. 예상 영향 (어떤 선수의 OVR이 어떻게 바뀌는지)
5. 위험도 (부작용 가능성)
