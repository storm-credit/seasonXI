"""SXI Engine v2.0 - Full Trust Audit

Can we trust this engine? 10 tests to find out.
"""
import random
from collections import defaultdict
import pandas as pd

from seasonxi.ratings.formula_v1 import ROLE_RATERS, STAT_NAMES
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import score_to_tier

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

issues = []
passes = []

print("=" * 70)
print("  SXI ENGINE v2.0 - FULL TRUST AUDIT")
print("  Can we ship this? 10 tests.")
print("=" * 70)

# ──────────────────────────────────────────────────────────────
# TEST 1: Do legendary players get Mythic/Legendary?
# ──────────────────────────────────────────────────────────────
print("\n[1] LEGENDARY PLAYER TEST")
legends = [
    ("Messi peak", "FW", dict(goals_pct_role=.99,xg_pct_role=.95,assists_pct_role=.90,
        xa_pct_role=.85,dribbles_pct_role=.99,prog_carries_pct_role=.95,
        key_passes_pct_role=.90,shots_pct_role=.95,pass_completion_pct_role=.85,
        pressures_pct_role=.30,tackles_pct_role=.15,goals_minus_xg_pct_role=.90),
        "Mythic", 93),
    ("Ronaldo peak", "FW", dict(goals_pct_role=.99,xg_pct_role=.90,shots_pct_role=.99,
        assists_pct_role=.50,dribbles_pct_role=.80,prog_carries_pct_role=.75,
        aerials_pct_role=.90,pressures_pct_role=.50,aerial_duel_success_pct_role=.85),
        "Mythic", 93),
    ("VVD peak", "DF", dict(tackles_pct_role=.85,interceptions_pct_role=.90,
        clearances_pct_role=.95,aerials_pct_role=.99,pass_completion_pct_role=.90,
        prog_passes_pct_role=.80,aerial_duel_success_pct_role=.95,
        clean_sheets_pct_role=.85,pressures_pct_role=.60),
        "Legendary", 90),
    ("Neuer peak", "GK", dict(gk_psxg_diff_pct_role=.95,gk_saves_pct_role=.90,
        clean_sheets_pct_role=.85,gk_crosses_stopped_pct_role=.85,
        gk_pass_completion_pct_role=.90,prog_passes_pct_role=.80),
        "Legendary", 90),
]
for name, role, ov, exp_tier, min_ovr in legends:
    row = make(0.5, **ov)
    row['team_success_pct'] = 0.85
    row['minutes_share'] = 0.9
    s = ROLE_RATERS[role](row, 1.0)
    tier = score_to_tier(s['overall']).value
    ok = s['overall'] >= min_ovr
    status = "PASS" if ok else "FAIL"
    if not ok:
        issues.append(f"{name}: OVR {s['overall']:.0f} < {min_ovr} (expected {exp_tier})")
    else:
        passes.append(f"{name}")
    print(f"  {status} {name:18s} OVR:{s['overall']:3.0f} {tier:12s} (expect >={min_ovr} {exp_tier})")

# ──────────────────────────────────────────────────────────────
# TEST 2: Average player should be Gold/Silver
# ──────────────────────────────────────────────────────────────
print("\n[2] AVERAGE PLAYER TEST (50th pct = Gold/Silver)")
for role in ['FW','MF','DF','GK']:
    s = ROLE_RATERS[role](make(0.5), 1.0)
    tier = score_to_tier(s['overall']).value
    ok = tier in ['Gold', 'Silver']
    status = "PASS" if ok else "FAIL"
    if not ok: issues.append(f"Average {role}: {tier} (expected Gold/Silver)")
    else: passes.append(f"Average {role}")
    print(f"  {status} {role} average: OVR:{s['overall']:.0f} {tier}")

# ──────────────────────────────────────────────────────────────
# TEST 3: Team bias < 3 points
# ──────────────────────────────────────────────────────────────
print("\n[3] TEAM BIAS TEST (<3pt difference)")
for role in ['FW','MF','DF']:
    strong = make(0.8, team_success_pct=0.95)
    strong['minutes_share'] = 0.8
    weak = make(0.8, team_success_pct=0.2)
    weak['minutes_share'] = 0.8
    ss = ROLE_RATERS[role](strong, 1.0)['overall']
    sw = ROLE_RATERS[role](weak, 1.0)['overall']
    diff = abs(ss - sw)
    ok = diff < 3.0
    status = "PASS" if ok else "FAIL"
    if not ok: issues.append(f"{role} team bias: {diff:.1f}pt")
    else: passes.append(f"{role} team bias")
    print(f"  {status} {role}: strong={ss:.1f} weak={sw:.1f} diff={diff:.1f}pt")

# ──────────────────────────────────────────────────────────────
# TEST 4: Position balance (Elite 95th pct spread < 3)
# ──────────────────────────────────────────────────────────────
print("\n[4] POSITION BALANCE (95th pct spread < 3)")
scores_95 = {}
for role in ['FW','MF','DF','GK']:
    s = ROLE_RATERS[role](make(0.95), 1.0)
    scores_95[role] = s['overall']
spread = max(scores_95.values()) - min(scores_95.values())
ok = spread < 3.0
status = "PASS" if ok else "FAIL"
if not ok: issues.append(f"Position spread: {spread:.1f}pt")
else: passes.append("Position balance")
vals = ' '.join(f"{r}:{v:.0f}" for r,v in scores_95.items())
print(f"  {status} {vals} spread={spread:.1f}")

# ──────────────────────────────────────────────────────────────
# TEST 5: Stat independence (all pairs r < 0.7)
# ──────────────────────────────────────────────────────────────
print("\n[5] STAT INDEPENDENCE (r < 0.7 for all pairs)")
random.seed(42)
stat_vals = defaultdict(list)
for _ in range(500):
    pcts = {k: random.betavariate(2, 2) for k in FIELDS}
    pcts['team_goal_contribution'] = random.betavariate(2, 2) * 0.4
    pcts['team_success_pct'] = random.betavariate(2, 2)
    pcts['minutes_share'] = random.betavariate(2, 2)
    row = pd.Series(pcts, dtype=float)
    s = ROLE_RATERS['FW'](row, 1.0)
    for d in STAT_NAMES: stat_vals[d].append(s[d])

high_corrs = []
for i, s1 in enumerate(STAT_NAMES):
    for s2 in STAT_NAMES[i+1:]:
        v1, v2 = stat_vals[s1], stat_vals[s2]
        m1, m2 = sum(v1)/len(v1), sum(v2)/len(v2)
        cov = sum((a-m1)*(b-m2) for a,b in zip(v1,v2)) / len(v1)
        sd1 = (sum((a-m1)**2 for a in v1)/len(v1))**0.5
        sd2 = (sum((b-m2)**2 for b in v2)/len(v2))**0.5
        corr = cov/(sd1*sd2) if sd1*sd2 > 0 else 0
        if abs(corr) > 0.7:
            high_corrs.append((s1, s2, corr))

if high_corrs:
    for s1, s2, c in high_corrs:
        issues.append(f"High correlation: {s1}~{s2} r={c:.2f}")
        print(f"  FAIL {s1} ~ {s2} r={c:.2f}")
else:
    passes.append("Stat independence")
    print(f"  PASS All 15 pairs r < 0.7")

# ──────────────────────────────────────────────────────────────
# TEST 6: Confidence penalty works
# ──────────────────────────────────────────────────────────────
print("\n[6] CONFIDENCE PENALTY (low minutes = lower OVR)")
full = ROLE_RATERS['FW'](make(0.9), 1.0)['overall']
low = ROLE_RATERS['FW'](make(0.9), compute_confidence(500))['overall']
penalty = full - low
ok = penalty > 10
status = "PASS" if ok else "FAIL"
if not ok: issues.append(f"Confidence penalty too low: {penalty:.1f}")
else: passes.append("Confidence penalty")
print(f"  {status} 1800min:{full:.0f} vs 500min:{low:.0f} penalty={penalty:.1f}pt")

# ──────────────────────────────────────────────────────────────
# TEST 7: Tier distribution realistic
# ──────────────────────────────────────────────────────────────
print("\n[7] TIER DISTRIBUTION (Mythic < 5%, Bronze < 50%)")
random.seed(42)
tiers_all = {}
for _ in range(2000):
    pct = random.betavariate(2.5, 2.5)
    mins = random.randint(500, 3400)
    role = random.choice(['FW','MF','DF','GK'])
    row = make(pct)
    s = ROLE_RATERS[role](row, compute_confidence(mins))
    t = score_to_tier(s['overall']).value
    tiers_all[t] = tiers_all.get(t, 0) + 1

mythic_pct = tiers_all.get('Mythic', 0) / 2000 * 100
bronze_pct = tiers_all.get('Bronze', 0) / 2000 * 100
ok_mythic = mythic_pct < 5
ok_bronze = bronze_pct < 50
print(f"  {'PASS' if ok_mythic else 'FAIL'} Mythic: {mythic_pct:.1f}% (limit <5%)")
print(f"  {'PASS' if ok_bronze else 'FAIL'} Bronze: {bronze_pct:.1f}% (limit <50%)")
if not ok_mythic: issues.append(f"Too many Mythic: {mythic_pct:.1f}%")
else: passes.append("Mythic rarity")
if not ok_bronze: issues.append(f"Too many Bronze: {bronze_pct:.1f}%")
else: passes.append("Bronze limit")

dist = ' '.join(f"{t[:3]}:{tiers_all.get(t,0)/20:.0f}%" for t in
    ['Mythic','Legendary','Elite','Gold','Silver','Bronze'])
print(f"  Distribution: {dist}")

# ──────────────────────────────────────────────────────────────
# TEST 8: Compressed ranges correct
# ──────────────────────────────────────────────────────────────
print("\n[8] COMPRESSED RANGES (FW DEF, DF ATT, GK ATT)")
checks = [
    ("FW", "def", 30, 65),
    ("DF", "att", 30, 65),
    ("GK", "att", 30, 32),
]
for role, stat, exp_lo, exp_hi in checks:
    lo = ROLE_RATERS[role](make(0.0), 1.0)[stat]
    hi = ROLE_RATERS[role](make(1.0), 1.0)[stat]
    ok = lo >= exp_lo - 2 and hi <= exp_hi + 2
    status = "PASS" if ok else "FAIL"
    if not ok: issues.append(f"{role} {stat}: {lo:.0f}-{hi:.0f} (expected {exp_lo}-{exp_hi})")
    else: passes.append(f"{role} {stat} range")
    print(f"  {status} {role} {stat.upper()}: {lo:.0f}-{hi:.0f} (expected ~{exp_lo}-{exp_hi})")

# ──────────────────────────────────────────────────────────────
# TEST 9: Monotonicity (higher pct = higher OVR always)
# ──────────────────────────────────────────────────────────────
print("\n[9] MONOTONICITY (higher ability = higher OVR)")
mono_ok = True
for role in ['FW','MF','DF','GK']:
    prev = 0
    for pct in [0.1, 0.3, 0.5, 0.7, 0.9, 0.99]:
        s = ROLE_RATERS[role](make(pct), 1.0)['overall']
        if s < prev - 0.1:
            mono_ok = False
            issues.append(f"{role} monotonicity broken at pct={pct}")
        prev = s
if mono_ok:
    passes.append("Monotonicity")
    print(f"  PASS All 4 positions strictly monotonic")
else:
    print(f"  FAIL Monotonicity broken")

# ──────────────────────────────────────────────────────────────
# TEST 10: Playstyle sensitivity
# ──────────────────────────────────────────────────────────────
print("\n[10] PLAYSTYLE SENSITIVITY")
print("  (Same overall talent, different styles)")

# Creative FW vs Physical FW
creative = make(0.5, goals_pct_role=.80, assists_pct_role=.95,
    dribbles_pct_role=.95, key_passes_pct_role=.90, prog_carries_pct_role=.90,
    pass_completion_pct_role=.90, pressures_pct_role=.20)
creative['team_success_pct'] = 0.8
creative['minutes_share'] = 0.85

physical = make(0.5, goals_pct_role=.95, shots_pct_role=.95,
    aerials_pct_role=.90, aerial_duel_success_pct_role=.90,
    pressures_pct_role=.80, tackles_pct_role=.50)
physical['team_success_pct'] = 0.8
physical['minutes_share'] = 0.85

sc = ROLE_RATERS['FW'](creative, 1.0)
sp = ROLE_RATERS['FW'](physical, 1.0)
diff = abs(sc['overall'] - sp['overall'])
ok = diff < 5
status = "PASS" if ok else "WARN"
if diff >= 5: issues.append(f"Playstyle gap: creative={sc['overall']:.0f} vs physical={sp['overall']:.0f}")
else: passes.append("Playstyle fairness")
print(f"  {status} Creative FW: ATT:{sc['att']:.0f} PACE:{sc['pace']:.0f} OVR:{sc['overall']:.0f}")
print(f"  {status} Physical FW: ATT:{sp['att']:.0f} DEF:{sp['def']:.0f} OVR:{sp['overall']:.0f}")
print(f"  Gap: {diff:.1f}pt")

# ──────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
total = len(passes) + len(issues)
print(f"  RESULT: {len(passes)}/{total} PASSED, {len(issues)} ISSUES")
print()
if issues:
    print("  ISSUES:")
    for i in issues:
        print(f"    - {i}")
if passes:
    print(f"\n  PASSED: {', '.join(passes)}")
print()
if len(issues) == 0:
    print("  VERDICT: ENGINE READY TO SHIP")
elif len(issues) <= 2:
    print("  VERDICT: MINOR ISSUES - ACCEPTABLE FOR V2.0")
else:
    print("  VERDICT: NEEDS FIX BEFORE SHIPPING")
print("=" * 70)
