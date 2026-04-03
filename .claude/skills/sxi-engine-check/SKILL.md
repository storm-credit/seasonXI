---
name: sxi-engine-check
description: "Run SXI Engine diagnostics and audits. Use whenever the user wants to: check engine health, verify formulas, test player archetypes, run trust audit, check tier distribution, test edge cases, validate algorithm changes, or asks 'is the engine working correctly?'"
---

# SXI Engine Check

Run comprehensive engine diagnostics. Multiple levels available:

## Quick check (default)
```bash
cd C:\ProjectS\seasonXI
PYTHONIOENCODING=utf-8 uv run python scripts/engine_diagnostic.py
```
8 tests: raw range, score range, position comparison, weights, confidence, tier distribution, team bias, position balance.

## Deep review (archetype validation)
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/deep_review.py
```
Tests known player profiles (Messi, Kante, VVD, etc.) against expected ratings.

## Full trust audit (21 tests)
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/full_audit.py
```
Legendary player test, average player test, team bias, position balance, stat independence, confidence penalty, tier distribution, compressed ranges, monotonicity, playstyle sensitivity.

## Performance check (43 tests)
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/engine_performance_check.py
```
Speed, memory, determinism, boundaries, NaN resilience, negative values, missing features, confidence edge cases, weight sums, consistency, tier thresholds, adaptive weights, sigmoid, GK special cases.

## Improvement check (production readiness)
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/improvement_check.py
```
Algorithm weaknesses, data gaps, embarrassing edge cases, ontology leaks, production risks, v3 roadmap.

## Scout review (5 HANESIS rounds)
```bash
PYTHONIOENCODING=utf-8 uv run python scripts/scout_review.py
```
Professional scout perspective: data quality, number accuracy, eye test, decision trust, fan acceptance.
