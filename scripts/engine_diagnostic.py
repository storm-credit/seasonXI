"""SXI Engine v2.0 Full Diagnostic"""
import random
import inspect
import re
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

DIMS = STAT_NAMES  # ['att', 'def', 'pace', 'aura', 'stamina', 'mental']

def make_row(pct: float) -> pd.Series:
    row = pd.Series({k: pct for k in FIELDS}, dtype=float)
    row['team_goal_contribution'] = pct * 0.4
    return row

print("=" * 65)
print("  SXI ENGINE v2.0 DIAGNOSTIC (ATT/DEF/PACE/AURA/STA/MEN)")
print("=" * 65)

# 1. Raw range
print("\n[1] RAW VALUE RANGE (must be 0.0-1.0)")
for role in ['FW','MF','DF','GK']:
    s = ROLE_RATERS[role](make_row(1.0), 1.0)
    bad = [f"{d}={s['_raws'][d]:.3f}" for d in DIMS if s['_raws'][d] < -0.01 or s['_raws'][d] > 1.01]
    print(f"  {role}: {'PASS' if not bad else 'FAIL ' + str(bad)}")

# 2. Score range
print("\n[2] SCORE RANGE (min-max, confidence=1.0)")
hdr = "  " + "".join(f"{d.upper():>8s}" for d in DIMS) + "     OVR"
print(hdr)
for role in ['FW','MF','DF','GK']:
    lo = ROLE_RATERS[role](make_row(0.0), 1.0)
    hi = ROLE_RATERS[role](make_row(1.0), 1.0)
    line = f"  {role} "
    for d in DIMS:
        line += f" {lo[d]:3.0f}-{hi[d]:2.0f}"
    line += f"   {lo['overall']:3.0f}-{hi['overall']:2.0f}"
    print(line)

# 3. 80th percentile comparison
print("\n[3] 80TH PERCENTILE (same stats, all positions)")
hdr = "  " + "".join(f"{d.upper():>6s}" for d in DIMS) + "  | OVR  Tier"
print(hdr)
for role in ['FW','MF','DF','GK']:
    s = ROLE_RATERS[role](make_row(0.8), 1.0)
    tier = score_to_tier(s['overall']).value
    vals = "".join(f"{s[d]:6.0f}" for d in DIMS)
    print(f"  {role} {vals}  | {s['overall']:4.0f}  {tier}")

# 4. Overall weight distribution
print("\n[4] OVERALL WEIGHTS")
weights = {
    'FW': {'ATT':30,'DEF':10,'PACE':15,'AURA':15,'STA':10,'MEN':20},
    'MF': {'ATT':15,'DEF':20,'PACE':10,'AURA':15,'STA':20,'MEN':20},
    'DF': {'ATT':5, 'DEF':35,'PACE':10,'AURA':15,'STA':15,'MEN':20},
    'GK': {'ATT':0, 'DEF':40,'PACE':5, 'AURA':15,'STA':10,'MEN':30},
}
for role, w in weights.items():
    atk = w['ATT']
    dfn = w['DEF']
    phy = w['PACE'] + w['STA']
    men = w['AURA'] + w['MEN']
    print(f"  {role}: ATK={atk:2d}% DEF={dfn:2d}% PHY={phy:2d}% MENTAL={men:2d}%")

# 5. Confidence curve
print("\n[5] CONFIDENCE CURVE")
for mins in [450, 900, 1200, 1500, 1800, 2700]:
    c = compute_confidence(mins)
    bar = "#" * int(c * 25)
    print(f"  {mins:5d}min -> {c:.3f} {bar}")

# 6. Tier distribution
print("\n[6] TIER DISTRIBUTION (1000 random per role)")
random.seed(42)
for role in ['FW','MF','DF','GK']:
    tiers = {}
    for _ in range(1000):
        pct = random.betavariate(2.5, 2.5)
        mins = random.randint(500, 3400)
        row = make_row(pct)
        c = compute_confidence(mins)
        s = ROLE_RATERS[role](row, c)
        t = score_to_tier(s['overall']).value
        tiers[t] = tiers.get(t, 0) + 1
    dist = ' '.join(f"{t[:3]}:{tiers.get(t,0)/10:.0f}%" for t in ['Mythic','Legendary','Elite','Gold','Silver','Bronze'])
    print(f"  {role}: {dist}")

# 7. Fairness: strong vs weak team
print("\n[7] TEAM BIAS CHECK")
strong = make_row(0.8); strong['team_success_pct'] = 0.9
weak = make_row(0.8); weak['team_success_pct'] = 0.3
ss = ROLE_RATERS['FW'](strong, 1.0)
sw = ROLE_RATERS['FW'](weak, 1.0)
diff = ss['overall'] - sw['overall']
status = "FAIR" if diff < 3 else "WARNING"
print(f"  FW strong({ss['overall']:.1f}) vs weak({sw['overall']:.1f}) = {diff:.1f}pt gap [{status}]")

# 8. DF vs FW balance
print("\n[8] POSITION BALANCE")
for pct, label in [(0.95, "Elite"), (0.5, "Average")]:
    scores = {}
    for role in ['FW','MF','DF','GK']:
        s = ROLE_RATERS[role](make_row(pct), 1.0)
        scores[role] = s['overall']
    spread = max(scores.values()) - min(scores.values())
    vals = ' '.join(f"{r}:{v:.0f}" for r,v in scores.items())
    status = "BALANCED" if spread < 5 else "IMBALANCED"
    print(f"  {label}({pct:.0%}): {vals} spread={spread:.1f} [{status}]")

print("\n" + "=" * 65)
print("  DIAGNOSTIC COMPLETE")
print("=" * 65)
