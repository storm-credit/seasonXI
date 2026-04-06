---
name: sxi-engine-check
description: "Run SXI Engine diagnostics and audits. Use whenever the user wants to: check engine health, verify formulas, test player archetypes, run trust audit, check tier distribution, test edge cases, validate algorithm changes, or asks 'is the engine working correctly?'"
---

# SXI Engine Check — v3 진단

추천 모델: **sonnet** (분석/해석 필요)
에이전트 역할: **"너는 축구 분석 시스템 QA 엔지니어야. SXI Engine v3의 공식 정확성, 아키타입 검증, 티어 분포를 진단하고 이상 징후를 보고해."**

## pytest (65개 테스트, 최우선)
```bash
cd C:/ProjectS/seasonXI
uv run pytest tests/ -v
```

## 진단 스크립트 (단계별)
```bash
# Quick (8 tests)
PYTHONIOENCODING=utf-8 uv run python scripts/engine_diagnostic.py

# Full audit (21 tests)
PYTHONIOENCODING=utf-8 uv run python scripts/full_audit.py

# Performance (43 tests)
PYTHONIOENCODING=utf-8 uv run python scripts/engine_performance_check.py

# Archetype (선수별 검증)
PYTHONIOENCODING=utf-8 uv run python scripts/deep_review.py
```

## v3 알려진 아키타입 레이팅

| 선수 | OVR | 티어 |
|------|-----|------|
| Vinicius | 92.8 | Legendary |
| Alisson | 94.1 | Legendary |
| Benzema | 91.2 | Legendary |
| Salah | 91.0 | Legendary |
| De Bruyne | 90.8 | Legendary |
| Kane | 86.5 | Elite |
| VVD | 86.0 | Elite |
| Lewandowski | 84.2 | Elite |

## v3 핵심 변경
- GK: clean_sheets DEF에만 (4중 오염 제거)
- DF: tackles 제거, interceptions 0.35 중심
- MENTAL: team_success_pct 완전 제거
- _adaptive_overall() 중앙화 (boost 5%)
- _stretch() k=4.5, 티어: Mythic≥95, Legendary≥90, Elite≥84

## 주요 파일
- `src/seasonxi/ratings/formula_v1.py` — v3 공식
- `src/seasonxi/constants.py` — 티어 임계값
- `tests/` — pytest 테스트 4개
- `scripts/` — 진단 스크립트 6개
