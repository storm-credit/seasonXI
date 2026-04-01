"""SXI Engine v2.0 - Deep Algorithm Review"""
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
    for k, v in ov.items():
        r[k] = v
    return r

def pr(s, role='FW'):
    tier = score_to_tier(s['overall']).value
    return f"ATT:{s['att']:3.0f} DEF:{s['def']:3.0f} PACE:{s['pace']:3.0f} AURA:{s['aura']:3.0f} STA:{s['stamina']:3.0f} MEN:{s['mental']:3.0f} | OVR:{s['overall']:3.0f} {tier}"

print("=" * 70)
print("  SXI ENGINE v2.0 - DEEP ALGORITHM REVIEW")
print("=" * 70)

# 1. Archetype validation
print("\n[1] ARCHETYPE VALIDATION")
archetypes = [
    ("Messi (FW)", "FW", dict(goals_pct_role=.99,xg_pct_role=.95,assists_pct_role=.90,xa_pct_role=.85,dribbles_pct_role=.99,prog_carries_pct_role=.95,key_passes_pct_role=.90,shots_pct_role=.95,pass_completion_pct_role=.85,pressures_pct_role=.30,tackles_pct_role=.15)),
    ("Kante (MF)", "MF", dict(goals_pct_role=.20,assists_pct_role=.15,tackles_pct_role=.99,interceptions_pct_role=.95,pressures_pct_role=.99,ball_recoveries_pct_role=.99,pressure_success_pct_role=.90,prog_carries_pct_role=.70,dribbles_pct_role=.50,pass_completion_pct_role=.75)),
    ("VVD (DF)", "DF", dict(goals_pct_role=.60,tackles_pct_role=.85,interceptions_pct_role=.90,clearances_pct_role=.95,aerials_pct_role=.99,pass_completion_pct_role=.90,prog_passes_pct_role=.80,aerial_duel_success_pct_role=.95,clean_sheets_pct_role=.85)),
    ("Neuer (GK)", "GK", dict(gk_psxg_diff_pct_role=.95,gk_saves_pct_role=.85,clean_sheets_pct_role=.80,gk_crosses_stopped_pct_role=.85,gk_pass_completion_pct_role=.90,prog_passes_pct_role=.80)),
    ("Mbappe (FW)", "FW", dict(goals_pct_role=.90,xg_pct_role=.85,prog_carries_pct_role=.99,dribbles_pct_role=.95,assists_pct_role=.60,shots_pct_role=.90,pressures_pct_role=.50,tackles_pct_role=.25)),
    ("Modric (MF)", "MF", dict(goals_pct_role=.30,assists_pct_role=.70,key_passes_pct_role=.85,prog_passes_pct_role=.90,pass_completion_pct_role=.95,dribbles_pct_role=.80,tackles_pct_role=.60,interceptions_pct_role=.55,pressures_pct_role=.75)),
]
for name, role, ov in archetypes:
    row = make(0.5, **ov)
    row['team_success_pct'] = 0.8
    row['minutes_share'] = 0.85
    s = ROLE_RATERS[role](row, 1.0)
    print(f"  {name:15s} {pr(s, role)}")

# 2. Sensitivity
print("\n[2] TOP FEATURES THAT MOVE FW OVR (0.5 -> 0.95)")
base = ROLE_RATERS['FW'](make(0.5), 1.0)['overall']
impacts = []
for f in FIELDS:
    if f in ['team_goal_contribution','team_success_pct','minutes_share']:
        continue
    hi = make(0.5, **{f: 0.95})
    hi['team_success_pct'] = 0.5
    hi['minutes_share'] = 0.5
    d = ROLE_RATERS['FW'](hi, 1.0)['overall'] - base
    if abs(d) > 0.05:
        impacts.append((f.replace('_pct_role',''), d))
impacts.sort(key=lambda x: -x[1])
for f, d in impacts[:8]:
    bar = "+" * int(d * 15)
    print(f"  {f:30s} {d:+.2f} {bar}")

# 3. Edge cases
print("\n[3] EDGE CASES")
# Pure scorer
row = make(0.2, goals_pct_role=.99, xg_pct_role=.95, shots_pct_role=.95)
row['team_success_pct'] = 0.7
row['minutes_share'] = 0.8
s = ROLE_RATERS['FW'](row, 1.0)
print(f"  Pure scorer (99 goals, no def): OVR:{s['overall']:.0f} {score_to_tier(s['overall']).value}")

# Pure defender
row = make(0.2, tackles_pct_role=.99, interceptions_pct_role=.95, clearances_pct_role=.95, aerials_pct_role=.90)
row['team_success_pct'] = 0.7
row['minutes_share'] = 0.8
row['clean_sheets_pct_role'] = 0.85
s = ROLE_RATERS['DF'](row, 1.0)
print(f"  Pure defender (99 tackles, no goals): OVR:{s['overall']:.0f} {score_to_tier(s['overall']).value}")

# Low minutes
s = ROLE_RATERS['FW'](make(0.95), compute_confidence(500))
print(f"  High talent, 500min only: OVR:{s['overall']:.0f} (conf={compute_confidence(500):.2f})")

# 4. Team effect
print("\n[4] TEAM EFFECT (same player, different teams)")
for tp in [0.2, 0.5, 0.8, 0.95]:
    row = make(0.8, team_success_pct=tp)
    row['minutes_share'] = 0.8
    s = ROLE_RATERS['FW'](row, 1.0)
    print(f"  team={tp:.0%}: OVR={s['overall']:.1f} MEN={s['mental']:.0f} AURA={s['aura']:.0f}")

# 5. Stat independence
print("\n[5] STAT INDEPENDENCE (FW, 500 random players)")
random.seed(42)
stat_vals = defaultdict(list)
for _ in range(500):
    pcts = {k: random.betavariate(2, 2) for k in FIELDS}
    pcts['team_goal_contribution'] = random.betavariate(2, 2) * 0.4
    pcts['team_success_pct'] = random.betavariate(2, 2)
    pcts['minutes_share'] = random.betavariate(2, 2)
    row = pd.Series(pcts, dtype=float)
    s = ROLE_RATERS['FW'](row, 1.0)
    for d in STAT_NAMES:
        stat_vals[d].append(s[d])

high_corr = []
for i, s1 in enumerate(STAT_NAMES):
    for s2 in STAT_NAMES[i+1:]:
        v1, v2 = stat_vals[s1], stat_vals[s2]
        m1, m2 = sum(v1)/len(v1), sum(v2)/len(v2)
        cov = sum((a-m1)*(b-m2) for a,b in zip(v1,v2)) / len(v1)
        sd1 = (sum((a-m1)**2 for a in v1)/len(v1))**0.5
        sd2 = (sum((b-m2)**2 for b in v2)/len(v2))**0.5
        corr = cov/(sd1*sd2) if sd1*sd2 > 0 else 0
        if abs(corr) > 0.6:
            high_corr.append((s1, s2, corr))

if high_corr:
    for s1, s2, c in high_corr:
        label = "WARNING" if abs(c) > 0.8 else "MODERATE"
        print(f"  {label}: {s1} ~ {s2} r={c:.2f}")
else:
    print(f"  All stat pairs r < 0.6 (good independence)")

# 6. GK checks
print("\n[6] GK CHECKS")
row = make(0.9, gk_psxg_diff_pct_role=.95, gk_saves_pct_role=.90)
row['clean_sheets_pct_role'] = 0.85
row['team_success_pct'] = 0.8
row['minutes_share'] = 0.9
s = ROLE_RATERS['GK'](row, 1.0)
print(f"  Elite GK: {pr(s, 'GK')}")
print(f"  ATT fixed ~30: {'PASS' if 29 <= s['att'] <= 32 else 'FAIL'}")

print("\n" + "=" * 70)
print("  REVIEW COMPLETE")
print("=" * 70)
