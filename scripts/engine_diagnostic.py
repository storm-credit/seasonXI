"""SXI Engine Full Diagnostic - 엔진 객관성 점검"""
import random
import inspect
import re
import pandas as pd

from seasonxi.ratings.formula_v1 import ROLE_RATERS
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

def make_row(pct: float) -> pd.Series:
    row = pd.Series({k: pct for k in FIELDS}, dtype=float)
    row['team_goal_contribution'] = pct * 0.4
    return row

print("=" * 70)
print("  SXI ENGINE v1.3 - FULL DIAGNOSTIC")
print("=" * 70)

# 1. Raw value range check
print("\n[1] RAW VALUE RANGE CHECK (all raws must be 0.0-1.0)")
for role in ['FW', 'MF', 'DF', 'GK']:
    s = ROLE_RATERS[role](make_row(1.0), 1.0)
    issues = []
    for d, v in s['_raws'].items():
        if d == 'overall':
            continue
        if v < -0.01 or v > 1.01:
            issues.append(f"{d}={v:.3f}")
    print(f"  {role}: {'PASS' if not issues else 'FAIL ' + str(issues)}")

# 2. Score range per position
print("\n[2] SCORE RANGE (min → max with confidence=1.0)")
print(f"  {'':4s}  {'Finish':>8s} {'Create':>8s} {'Ctrl':>8s} {'Defense':>8s} {'Clutch':>8s} {'Aura':>8s} {'OVR':>8s}")
for role in ['FW', 'MF', 'DF', 'GK']:
    lo = ROLE_RATERS[role](make_row(0.0), 1.0)
    hi = ROLE_RATERS[role](make_row(1.0), 1.0)
    parts = []
    for d in ['finishing', 'creation', 'control', 'defense', 'clutch', 'aura', 'overall']:
        parts.append(f"{lo[d]:.0f}-{hi[d]:.0f}")
    print(f"  {role:4s}  {'  '.join(f'{p:>8s}' for p in parts)}")

# 3. 80th percentile comparison
print("\n[3] 80TH PERCENTILE PLAYER (same stats, different positions)")
print(f"  {'':4s}  {'Fin':>5s} {'Cre':>5s} {'Ctl':>5s} {'Def':>5s} {'Clu':>5s} {'Aur':>5s} | {'OVR':>5s} {'Tier':<10s}")
for role in ['FW', 'MF', 'DF', 'GK']:
    s = ROLE_RATERS[role](make_row(0.8), 1.0)
    tier = score_to_tier(s['overall']).value
    vals = [f"{s[d]:5.0f}" for d in ['finishing','creation','control','defense','clutch','aura']]
    print(f"  {role:4s}  {' '.join(vals)} | {s['overall']:5.0f} {tier}")

# 4. Overall weight distribution (공격 vs 수비 비율)
print("\n[4] OVERALL WEIGHT DISTRIBUTION (attack vs defense)")
weights = {
    'FW': {'attack': 0.30+0.20+0.18, 'defense': 0.08, 'other': 0.12+0.12},
    'MF': {'attack': 0.16+0.24+0.24, 'defense': 0.14, 'other': 0.10+0.12},
    'DF': {'attack': 0.05+0.12+0.18, 'defense': 0.35, 'other': 0.15+0.15},
    'GK': {'attack': 0.00+0.05+0.15, 'defense': 0.45, 'other': 0.20+0.15},
}
for role, w in weights.items():
    bar_a = "█" * int(w['attack'] * 30)
    bar_d = "█" * int(w['defense'] * 30)
    bar_o = "░" * int(w['other'] * 30)
    print(f"  {role}: ATK {w['attack']:.0%} {bar_a}  DEF {w['defense']:.0%} {bar_d}  OTH {w['other']:.0%} {bar_o}")

# 5. Confidence curve
print("\n[5] CONFIDENCE CURVE (non-linear: (min/1800)^0.7)")
for mins in [450, 900, 1200, 1500, 1800, 2700, 3400]:
    c = compute_confidence(mins)
    bar = "█" * int(c * 30)
    print(f"  {mins:5d} min → {c:.3f} {bar}")

# 6. team_success_pct dependency
print("\n[6] TEAM_SUCCESS_PCT DEPENDENCY (이중 반영 체크)")
for role in ['FW', 'MF', 'DF', 'GK']:
    src = inspect.getsource(ROLE_RATERS[role])
    count = len(re.findall(r'team_success_pct', src))
    dims = []
    for dim in ['clutch', 'aura']:
        if dim in src and 'team_success_pct' in src.split(dim + '_raw')[1].split('\n\n')[0] if dim + '_raw' in src else False:
            dims.append(dim)
    print(f"  {role}: appears {count}x in formula code")

# 7. Tier distribution simulation
print("\n[7] TIER DISTRIBUTION (1000 random players per role)")
random.seed(42)
for role in ['FW', 'MF', 'DF', 'GK']:
    tiers = {}
    for _ in range(1000):
        pct = random.betavariate(2.5, 2.5)
        mins = random.randint(500, 3400)
        row = make_row(pct)
        c = compute_confidence(mins)
        scores = ROLE_RATERS[role](row, c)
        tier = score_to_tier(scores['overall']).value
        tiers[tier] = tiers.get(tier, 0) + 1
    dist = ' | '.join(f"{t}:{tiers.get(t,0)/10:.1f}%" for t in ['Mythic','Legendary','Elite','Gold','Silver','Bronze'])
    print(f"  {role}: {dist}")

# 8. 수비 지표 수 vs 공격 지표 수
print("\n[8] FEATURE COUNT BY CATEGORY")
atk_features = ['goals','xg','shots','goals_minus_xg','assists','xa','key_passes','prog_passes','prog_carries','dribbles']
def_features = ['tackles','interceptions','clearances','aerials','pressures','pressure_success','aerial_duel_success','ball_recoveries']
ctx_features = ['pass_completion','team_goal_contribution','team_success_pct','minutes_share','clean_sheets']
gk_features = ['gk_saves','gk_psxg_diff','gk_crosses_stopped','gk_pass_completion','gk_launch']
print(f"  Attack:  {len(atk_features)} features ({', '.join(atk_features[:5])}...)")
print(f"  Defense: {len(def_features)} features ({', '.join(def_features[:5])}...)")
print(f"  Context: {len(ctx_features)} features")
print(f"  GK-only: {len(gk_features)} features")
print(f"  Total:   {len(atk_features)+len(def_features)+len(ctx_features)+len(gk_features)}")

# 9. 핵심 질문: 공정한가?
print("\n[9] FAIRNESS CHECK")
# 같은 능력치 선수가 강팀 vs 약팀에서 차이나는지
strong_team = make_row(0.8)
strong_team['team_success_pct'] = 0.9
strong_team['team_goal_contribution'] = 0.3

weak_team = make_row(0.8)
weak_team['team_success_pct'] = 0.3
weak_team['team_goal_contribution'] = 0.3

s_strong = ROLE_RATERS['FW'](strong_team, 1.0)
s_weak = ROLE_RATERS['FW'](weak_team, 1.0)
diff = s_strong['overall'] - s_weak['overall']
print(f"  Same FW (80th pct), strong team vs weak team:")
print(f"    Strong team OVR: {s_strong['overall']:.1f}")
print(f"    Weak team OVR:   {s_weak['overall']:.1f}")
print(f"    Difference:      {diff:.1f} points")
if diff > 5:
    print(f"    ⚠ WARNING: {diff:.1f} point gap - team effect too strong")
elif diff > 3:
    print(f"    ⚡ MODERATE: {diff:.1f} point gap - acceptable but watch")
else:
    print(f"    ✅ FAIR: {diff:.1f} point gap - minimal team bias")

# 10. 수비수 과소평가 체크
print("\n[10] DEFENDER VALUATION CHECK")
elite_df = make_row(0.95)
elite_fw = make_row(0.95)
s_df = ROLE_RATERS['DF'](elite_df, 1.0)
s_fw = ROLE_RATERS['FW'](elite_fw, 1.0)
print(f"  Elite DF (95th pct) OVR: {s_df['overall']:.1f} ({score_to_tier(s_df['overall']).value})")
print(f"  Elite FW (95th pct) OVR: {s_fw['overall']:.1f} ({score_to_tier(s_fw['overall']).value})")
gap = abs(s_df['overall'] - s_fw['overall'])
if gap > 3:
    print(f"  ⚠ WARNING: {gap:.1f} point gap between elite DF and FW")
else:
    print(f"  ✅ BALANCED: {gap:.1f} point gap")

print("\n" + "=" * 70)
print("  DIAGNOSTIC COMPLETE")
print("=" * 70)
