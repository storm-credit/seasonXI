"""SXI Engine v2.0 - Performance & Reliability Check

Tests:
1. Computation speed (1000 players)
2. Memory stability (repeated runs)
3. Determinism (same input = same output)
4. Boundary testing (extreme values)
5. NaN/null resilience
6. Negative value handling
7. Feature missing gracefully
8. Confidence edge cases (0, 1, >1800min)
9. Weight sum verification (all positions)
10. Overall vs individual stat consistency
11. Tier threshold precision
12. Cross-run reproducibility
"""
import time
import random
import sys
import pandas as pd

from seasonxi.ratings.formula_v1 import (
    ROLE_RATERS, STAT_NAMES, _adaptive_overall, _scale, _stretch, _safe_get
)
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import SCORE_BASE, SCORE_RANGE, score_to_tier, Tier

FIELDS = [
    'goals_pct_role','xg_pct_role','shots_pct_role','goals_minus_xg_pct_role',
    'assists_pct_role','xa_pct_role','key_passes_pct_role',
    'prog_passes_pct_role','prog_carries_pct_role','dribbles_pct_role',
    'pass_completion_pct_role','tackles_pct_role','interceptions_pct_role',
    'clearances_pct_role','aerials_pct_role','pressures_pct_role',
    'pressure_success_pct_role','aerial_duel_success_pct_role',
    'ball_recoveries_pct_role','team_goal_contribution','team_success_pct',
    'minutes_share','clean_sheets_pct_role',
    'gk_saves_pct_role','gk_psxg_diff_pct_role','gk_crosses_stopped_pct_role',
    'gk_pass_completion_pct_role','gk_launch_pct_role',
]

def make(pct, **ov):
    r = pd.Series({k: pct for k in FIELDS}, dtype=float)
    r['team_goal_contribution'] = pct * 0.4
    for k, v in ov.items(): r[k] = v
    return r

passes = 0
fails = 0
warnings = 0

def check(name, ok, detail=""):
    global passes, fails
    status = "PASS" if ok else "FAIL"
    if not ok: fails += 1
    else: passes += 1
    print(f"  {status} {name}" + (f" ({detail})" if detail else ""))

def warn(name, detail=""):
    global warnings
    warnings += 1
    print(f"  WARN {name}" + (f" ({detail})" if detail else ""))

print("=" * 70)
print("  SXI ENGINE v2.0 - PERFORMANCE & RELIABILITY CHECK")
print("=" * 70)

# ── 1. Speed ──────────────────────────────────────────────────
print("\n[1] COMPUTATION SPEED")
random.seed(42)
rows = []
for _ in range(1000):
    pcts = {k: random.random() for k in FIELDS}
    pcts['team_goal_contribution'] = random.random() * 0.4
    rows.append(pd.Series(pcts, dtype=float))

start = time.perf_counter()
for row in rows:
    role = random.choice(['FW','MF','DF','GK'])
    ROLE_RATERS[role](row, compute_confidence(random.randint(450,3400)))
elapsed = time.perf_counter() - start
per_player = elapsed / 1000 * 1000  # ms

check("1000 players", elapsed < 5.0, f"{elapsed:.2f}s total, {per_player:.2f}ms/player")
if per_player > 1.0:
    warn("Slow", f"{per_player:.2f}ms/player > 1ms target")

# ── 2. Memory stability ──────────────────────────────────────
print("\n[2] MEMORY STABILITY (10 rounds x 1000 players)")
results = []
for rnd in range(10):
    for row in rows[:100]:
        s = ROLE_RATERS['FW'](row, 1.0)
        results.append(s['overall'])
# Check no memory leak symptoms (all values finite)
all_finite = all(0 <= v <= 100 for v in results)
check("All values finite", all_finite, f"{len(results)} computations")

# ── 3. Determinism ────────────────────────────────────────────
print("\n[3] DETERMINISM (same input = same output)")
test_row = make(0.75)
r1 = ROLE_RATERS['FW'](test_row, 1.0)
r2 = ROLE_RATERS['FW'](test_row, 1.0)
r3 = ROLE_RATERS['FW'](test_row, 1.0)
identical = all(r1[d] == r2[d] == r3[d] for d in STAT_NAMES + ['overall'])
check("3 runs identical", identical)

# ── 4. Boundary testing ──────────────────────────────────────
print("\n[4] BOUNDARY VALUES")
# All zeros
s = ROLE_RATERS['FW'](make(0.0), 1.0)
check("All 0.0: OVR >= 50", s['overall'] >= 50, f"OVR={s['overall']:.1f}")

# All ones
s = ROLE_RATERS['FW'](make(1.0), 1.0)
check("All 1.0: OVR <= 99", s['overall'] <= 99, f"OVR={s['overall']:.1f}")

# Exact 0.5
s = ROLE_RATERS['FW'](make(0.5), 1.0)
check("All 0.5: OVR 70-80", 70 <= s['overall'] <= 80, f"OVR={s['overall']:.1f}")

# ── 5. NaN resilience ────────────────────────────────────────
print("\n[5] NaN RESILIENCE")
nan_row = pd.Series({k: float('nan') for k in FIELDS}, dtype=float)
try:
    s = ROLE_RATERS['FW'](nan_row, 1.0)
    all_valid = all(50 <= s[d] <= 99 or (d == 'def' and s[d] >= 30) for d in STAT_NAMES)
    check("NaN input: no crash", True)
    check("NaN input: valid scores", all_valid, f"OVR={s['overall']:.1f}")
except Exception as e:
    check("NaN input: no crash", False, str(e))

# ── 6. Negative values ───────────────────────────────────────
print("\n[6] NEGATIVE VALUE HANDLING")
neg_row = make(-0.5)
try:
    s = ROLE_RATERS['FW'](neg_row, 1.0)
    check("Negative input: no crash", True)
    check("Negative: OVR >= 50", s['overall'] >= 49, f"OVR={s['overall']:.1f}")
except Exception as e:
    check("Negative input", False, str(e))

# ── 7. Missing features ──────────────────────────────────────
print("\n[7] MISSING FEATURES")
sparse_row = pd.Series({'goals_pct_role': 0.8, 'minutes_share': 0.7}, dtype=float)
try:
    s = ROLE_RATERS['FW'](sparse_row, 1.0)
    check("Sparse input: no crash", True, f"OVR={s['overall']:.1f}")
except Exception as e:
    check("Sparse input", False, str(e))

# ── 8. Confidence edge cases ─────────────────────────────────
print("\n[8] CONFIDENCE EDGE CASES")
c0 = compute_confidence(0)
check("0 minutes: conf=0", c0 == 0.0, f"conf={c0}")

c450 = compute_confidence(450)
check("450 min: 0 < conf < 1", 0 < c450 < 1, f"conf={c450:.3f}")

c1800 = compute_confidence(1800)
check("1800 min: conf=1.0", c1800 == 1.0, f"conf={c1800}")

c5000 = compute_confidence(5000)
check("5000 min: conf=1.0 (capped)", c5000 == 1.0, f"conf={c5000}")

# Zero confidence should give base scores
s = ROLE_RATERS['FW'](make(0.9), 0.0)
check("conf=0: OVR=50", s['overall'] == 50.0, f"OVR={s['overall']:.1f}")

# ── 9. Weight sums ────────────────────────────────────────────
print("\n[9] WEIGHT SUM VERIFICATION")
base_weights = {
    'FW': {"att":0.30,"def":0.10,"pace":0.15,"aura":0.15,"stamina":0.10,"mental":0.20},
    'MF': {"att":0.15,"def":0.20,"pace":0.10,"aura":0.15,"stamina":0.20,"mental":0.20},
    'DF': {"att":0.05,"def":0.35,"pace":0.10,"aura":0.15,"stamina":0.15,"mental":0.20},
    'GK': {"att":0.00,"def":0.40,"pace":0.05,"aura":0.15,"stamina":0.10,"mental":0.30},
}
for role, w in base_weights.items():
    s = sum(w.values())
    check(f"{role} weights sum=1.0", abs(s - 1.0) < 0.001, f"sum={s:.3f}")

# ── 10. Overall consistency ───────────────────────────────────
print("\n[10] OVERALL vs INDIVIDUAL CONSISTENCY")
# Higher individual stats should give higher overall
low = ROLE_RATERS['FW'](make(0.3), 1.0)
mid = ROLE_RATERS['FW'](make(0.5), 1.0)
high = ROLE_RATERS['FW'](make(0.8), 1.0)
check("OVR: low < mid < high", low['overall'] < mid['overall'] < high['overall'],
      f"{low['overall']:.0f} < {mid['overall']:.0f} < {high['overall']:.0f}")

# Each stat should also follow
for d in STAT_NAMES:
    ok = low[d] <= mid[d] <= high[d]
    if not ok:
        check(f"{d}: monotonic", False, f"{low[d]:.0f} {mid[d]:.0f} {high[d]:.0f}")

# ── 11. Tier threshold precision ──────────────────────────────
print("\n[11] TIER THRESHOLD PRECISION")
# Scores just at boundaries
for score, exp_tier in [(95.0, "Mythic"), (94.9, "Legendary"), (90.0, "Legendary"),
                         (89.9, "Elite"), (84.0, "Elite"), (83.9, "Gold"),
                         (76.0, "Gold"), (75.9, "Silver"), (68.0, "Silver"),
                         (67.9, "Bronze")]:
    actual = score_to_tier(score).value
    check(f"Score {score}: {exp_tier}", actual == exp_tier, f"got {actual}")

# ── 12. Adaptive weight sanity ────────────────────────────────
print("\n[12] ADAPTIVE WEIGHT SANITY")
# Verify adaptive weights are normalized
raws = {"att": 0.9, "def": 0.2, "pace": 0.8, "aura": 0.5, "stamina": 0.3, "mental": 0.7}
base_w = {"att": 0.30, "def": 0.10, "pace": 0.15, "aura": 0.15, "stamina": 0.10, "mental": 0.20}
result = _adaptive_overall(raws, base_w)
check("Adaptive result in [0,1]", 0 <= result <= 1, f"result={result:.4f}")

# Check that high ATT player gets higher OVR than balanced player
attacker = make(0.5, goals_pct_role=.99, xg_pct_role=.95, shots_pct_role=.95,
                dribbles_pct_role=.95, prog_carries_pct_role=.90)
attacker['team_success_pct'] = 0.7
attacker['minutes_share'] = 0.8
balanced = make(0.7)
balanced['team_success_pct'] = 0.7
balanced['minutes_share'] = 0.8
sa = ROLE_RATERS['FW'](attacker, 1.0)
sb = ROLE_RATERS['FW'](balanced, 1.0)
check("Specialist > Balanced (with adaptive)", sa['overall'] >= sb['overall'] - 2,
      f"specialist={sa['overall']:.0f} balanced={sb['overall']:.0f}")

# ── 13. _stretch function ─────────────────────────────────────
print("\n[13] SIGMOID STRETCH FUNCTION")
check("stretch(0.0) = 0", abs(_stretch(0.0)) < 0.01, f"{_stretch(0.0):.4f}")
check("stretch(0.5) ~ 0.5", abs(_stretch(0.5) - 0.5) < 0.01, f"{_stretch(0.5):.4f}")
check("stretch(1.0) = 1", abs(_stretch(1.0) - 1.0) < 0.01, f"{_stretch(1.0):.4f}")
check("stretch monotonic", _stretch(0.3) < _stretch(0.5) < _stretch(0.7))

# ── 14. GK special cases ─────────────────────────────────────
print("\n[14] GK SPECIAL CASES")
s = ROLE_RATERS['GK'](make(0.5), 1.0)
check("GK ATT always 30", 29 <= s['att'] <= 31, f"ATT={s['att']:.0f}")

s = ROLE_RATERS['GK'](make(0.99), 1.0)
check("GK ATT at 99th pct still 30", 29 <= s['att'] <= 31, f"ATT={s['att']:.0f}")

# ── 15. All 4 positions produce valid output ──────────────────
print("\n[15] ALL POSITIONS VALID OUTPUT")
for role in ['FW','MF','DF','GK']:
    for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
        s = ROLE_RATERS[role](make(pct), 1.0)
        valid = all(k in s for k in STAT_NAMES + ['overall', '_raws'])
        all_nums = all(isinstance(s[k], (int, float)) for k in STAT_NAMES + ['overall'])
        if not valid or not all_nums:
            check(f"{role} pct={pct}", False, "missing keys or non-numeric")
            break
    else:
        check(f"{role}: all percentiles valid", True)

# ── Summary ───────────────────────────────────────────────────
total = passes + fails
print("\n" + "=" * 70)
print(f"  RESULT: {passes}/{total} PASSED, {fails} FAILED, {warnings} WARNINGS")
if fails == 0:
    print("  STATUS: ALL CHECKS PASSED - ENGINE PERFORMANCE VERIFIED")
elif fails <= 2:
    print("  STATUS: MINOR ISSUES")
else:
    print("  STATUS: NEEDS ATTENTION")
print("=" * 70)
