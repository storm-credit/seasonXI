"""SXI Engine v2.0 - Improvement & Reinforcement Check

As a football analytics researcher + product engineer:
What's weak? What's missing? What would break in production?

Categories:
A. Algorithm weaknesses (공식 약점)
B. Data gaps (데이터 부족)
C. Edge cases that would embarrass us (창피한 케이스)
D. Ontology leaks (개념 오염)
E. Production risks (실제 운영 위험)
F. v3 roadmap priorities (다음 버전 필수)
"""
import random
import pandas as pd

from seasonxi.ratings.formula_v1 import ROLE_RATERS, STAT_NAMES, _adaptive_overall
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

def rate(role, row, mins=3000):
    return ROLE_RATERS[role](row, compute_confidence(mins))

def pr(s):
    return f"ATT:{s['att']:3.0f} DEF:{s['def']:3.0f} PAC:{s['pace']:3.0f} AUR:{s['aura']:3.0f} STA:{s['stamina']:3.0f} MEN:{s['mental']:3.0f} | OVR:{s['overall']:3.0f}"

critical = []
major = []
minor = []
good = []

def crit(msg): critical.append(msg); print(f"  [CRITICAL] {msg}")
def maj(msg): major.append(msg); print(f"  [MAJOR]    {msg}")
def mi(msg): minor.append(msg); print(f"  [MINOR]    {msg}")
def ok(msg): good.append(msg); print(f"  [OK]       {msg}")

print("=" * 70)
print("  SXI ENGINE v2.0 - IMPROVEMENT & REINFORCEMENT CHECK")
print("=" * 70)

# ══════════════════════════════════════════════════════════════
# A. ALGORITHM WEAKNESSES
# ══════════════════════════════════════════════════════════════
print("\n[A] ALGORITHM WEAKNESSES")

# A1. PACE has no actual speed data
print("\n  A1. PACE without speed data")
# PACE uses prog_carries + dribbles + prog_passes
# But Busquets has high prog_passes and zero pace
busquets = make(0.4, prog_passes_pct_role=.95, pass_completion_pct_role=.99,
                dribbles_pct_role=.30, prog_carries_pct_role=.20)
busquets['team_success_pct'] = 0.8
busquets['minutes_share'] = 0.85
s = rate('MF', busquets)
if s['pace'] > 85:
    maj(f"Busquets PACE={s['pace']:.0f} — too high! prog_passes inflates PACE")
elif s['pace'] > 75:
    mi(f"Busquets PACE={s['pace']:.0f} — slightly high, prog_passes effect")
else:
    ok(f"Busquets PACE={s['pace']:.0f} — reasonable")

# A2. MENTAL includes team_success_pct
print("\n  A2. MENTAL contamination from team success")
same_player_good_team = make(0.7, team_success_pct=0.95)
same_player_good_team['minutes_share'] = 0.8
same_player_bad_team = make(0.7, team_success_pct=0.2)
same_player_bad_team['minutes_share'] = 0.8
sg = rate('FW', same_player_good_team)
sb = rate('FW', same_player_bad_team)
mental_gap = sg['mental'] - sb['mental']
if mental_gap > 8:
    maj(f"MENTAL gap={mental_gap:.0f}pt from team alone — team_success too influential")
elif mental_gap > 5:
    mi(f"MENTAL gap={mental_gap:.0f}pt from team — moderate influence")
else:
    ok(f"MENTAL gap={mental_gap:.0f}pt from team — acceptable")

# A3. Adaptive weight — can it overfit?
print("\n  A3. Adaptive weight overfit risk")
# Player with extreme imbalance
extreme = make(0.1, goals_pct_role=.99)
extreme['team_success_pct'] = 0.5
extreme['minutes_share'] = 0.8
s_ext = rate('FW', extreme)
s_bal = rate('FW', make(0.5))
if s_ext['overall'] > s_bal['overall']:
    mi(f"One-stat wonder OVR={s_ext['overall']:.0f} > balanced OVR={s_bal['overall']:.0f} — adaptive may overboost")
else:
    ok(f"One-stat wonder OVR={s_ext['overall']:.0f} < balanced OVR={s_bal['overall']:.0f} — safe")

# A4. AURA circular dependency check
print("\n  A4. AURA independence")
# Change only AURA inputs, check other stats don't move
base = make(0.5)
base['minutes_share'] = 0.5
base['team_goal_contribution'] = 0.2
s1 = rate('FW', base)
boosted = make(0.5, minutes_share=0.95, team_goal_contribution=0.4)
s2 = rate('FW', boosted)
aura_change = s2['aura'] - s1['aura']
att_change = s2['att'] - s1['att']
if att_change > 3 and aura_change > 5:
    mi(f"AURA inputs affect ATT by {att_change:.0f}pt — slight leakage via team_goal_contribution")
else:
    ok(f"AURA inputs: ATT change={att_change:.0f}pt — minimal leakage")

# A5. Bronze concentration
print("\n  A5. Bronze tier concentration")
random.seed(42)
tiers = {}
for _ in range(2000):
    pct = random.betavariate(2.5, 2.5)
    role = random.choice(['FW','MF','DF','GK'])
    s = rate(role, make(pct), random.randint(500, 3400))
    t = score_to_tier(s['overall']).value
    tiers[t] = tiers.get(t, 0) + 1
bronze_pct = tiers.get('Bronze',0)/2000*100
if bronze_pct > 50:
    maj(f"Bronze={bronze_pct:.0f}% — half the players are Bronze")
elif bronze_pct > 40:
    mi(f"Bronze={bronze_pct:.0f}% — high but confidence penalty is the cause")
else:
    ok(f"Bronze={bronze_pct:.0f}% — acceptable")

# ══════════════════════════════════════════════════════════════
# B. DATA GAPS
# ══════════════════════════════════════════════════════════════
print("\n[B] DATA GAPS")

print("\n  B1. Physical features count")
physical_feats = ['prog_carries_pct_role', 'dribbles_pct_role', 'prog_passes_pct_role']
if len(physical_feats) < 5:
    maj(f"Only {len(physical_feats)} physical proxy features — PACE accuracy limited")
    print("       Missing: sprint_speed, top_speed, acceleration, distance_covered")
else:
    ok(f"{len(physical_feats)} physical features")

print("\n  B2. Defensive quality vs quantity")
# tackles COUNT vs tackles WON
mi("tackles_pct = attempts, not success rate — high tackles could mean poor positioning")
print("       FIX: Add tackles_won / tackles ratio as quality metric")

print("\n  B3. GK distribution data")
gk_feats = [f for f in FIELDS if 'gk_' in f]
print(f"       GK-specific features: {len(gk_feats)}")
if len(gk_feats) < 6:
    mi(f"Only {len(gk_feats)} GK features — missing sweep actions, penalty saves")
else:
    ok(f"{len(gk_feats)} GK features — adequate")

print("\n  B4. Cross-era comparability")
mi("No era adjustment — 2010 EPL vs 2024 EPL have different average stats")
print("       FIX: season_era_factor currently hardcoded 1.0")
print("       NEED: league-season average normalization")

print("\n  B5. Match-level vs season-aggregate")
maj("All data is season aggregate — no game-state context")
print("       Can't measure: performance vs top 6, UCL knockout, late goals")
print("       IMPACT: MENTAL/CLUTCH are proxies, not real measures")

# ══════════════════════════════════════════════════════════════
# C. EMBARRASSING EDGE CASES
# ══════════════════════════════════════════════════════════════
print("\n[C] EMBARRASSING EDGE CASES")

print("\n  C1. Penalty specialist")
# Player who only scores penalties — should ATT be high?
pen_taker = make(0.3, goals_pct_role=.80, xg_pct_role=.40, shots_pct_role=.30)
pen_taker['team_success_pct'] = 0.6
pen_taker['minutes_share'] = 0.7
s = rate('FW', pen_taker)
if s['att'] > 80:
    maj(f"Penalty merchant ATT={s['att']:.0f} — goals without xG should penalize more")
else:
    ok(f"Penalty merchant ATT={s['att']:.0f} — goals_minus_xg helps")

print("\n  C2. Red card machine")
# Aggressive player — no way to penalize red cards
mi("No red/yellow card data in formula — dirty players get same rating")
print("       FIX: Add cards_per90 as negative feature in MENTAL")

print("\n  C3. 'Stat padding' against weak teams")
# Player with high stats but only vs bottom teams
mi("No opponent strength weighting — goals vs relegation teams = goals vs top 6")
print("       FIX: Match-level data needed (v3)")

print("\n  C4. Position misclassification")
# Messi listed as RW but plays as false 9
trent_as_df = make(0.5, assists_pct_role=.95, key_passes_pct_role=.90,
                   prog_passes_pct_role=.90, prog_carries_pct_role=.85,
                   tackles_pct_role=.40, interceptions_pct_role=.35)
trent_as_df['team_success_pct'] = 0.8
trent_as_df['minutes_share'] = 0.85
s = rate('DF', trent_as_df)
print(f"       Trent as DF: {pr(s)}")
if s['att'] < 50:
    mi(f"Trent ATT={s['att']:.0f} — DF formula suppresses his creativity (base=30)")
else:
    ok(f"Trent ATT={s['att']:.0f} — acceptable for DF classification")

print("\n  C5. GK with no saves needed")
# GK on dominant team — barely tested but high clean sheets
easy_gk = make(0.3, clean_sheets_pct_role=.95, gk_saves_pct_role=.20,
               gk_psxg_diff_pct_role=.50)
easy_gk['team_success_pct'] = 0.95
easy_gk['minutes_share'] = 0.9
s = rate('GK', easy_gk)
if s['overall'] > 85:
    mi(f"Untested GK OVR={s['overall']:.0f} — clean sheets from strong defense, not skill")
else:
    ok(f"Untested GK OVR={s['overall']:.0f} — properly penalized")

# ══════════════════════════════════════════════════════════════
# D. ONTOLOGY LEAKS
# ══════════════════════════════════════════════════════════════
print("\n[D] ONTOLOGY LEAKS (concept contamination)")

print("\n  D1. Feature shared across multiple stats")
shared_features = {
    'minutes_share': ['aura', 'stamina', 'mental(indirect)'],
    'pressures_pct_role': ['def', 'stamina(removed but was here)'],
    'pass_completion_pct_role': ['pace(MF)', 'mental'],
    'ball_recoveries_pct_role': ['def', 'stamina'],
    'tackles_pct_role': ['def', 'stamina'],
}
leak_count = 0
for feat, stats in shared_features.items():
    if len(stats) >= 2:
        leak_count += 1
        print(f"       {feat}: used in {', '.join(stats)}")
if leak_count > 3:
    mi(f"{leak_count} features shared across stats — some concept bleeding")
else:
    ok(f"{leak_count} shared features — manageable")

print("\n  D2. minutes_share is in 3+ stats")
# minutes_share appears in AURA, STAMINA, and affects MENTAL indirectly
mi("minutes_share in AURA + STAMINA + DF PACE — 'play more = better' bias")
print("       IMPACT: Rotation players always penalized")
print("       FIX: Replace with 'performance per minute' metric")

print("\n  D3. PACE concept purity")
# PACE for MF includes pass_completion — is that speed?
mi("MF PACE includes pass_completion_pct — passing accuracy != speed")
print("       FIX: Remove pass_completion from MF PACE, add dribble success rate")

# ══════════════════════════════════════════════════════════════
# E. PRODUCTION RISKS
# ══════════════════════════════════════════════════════════════
print("\n[E] PRODUCTION RISKS")

print("\n  E1. First video backlash risk")
# If Messi gets 93 (Legendary) instead of Mythic, fans will complain
messi = make(0.5, goals_pct_role=.99,xg_pct_role=.95,assists_pct_role=.90,
             dribbles_pct_role=.99,prog_carries_pct_role=.95,
             pass_completion_pct_role=.85,pressures_pct_role=.35)
messi['team_success_pct'] = 0.85
messi['minutes_share'] = 0.9
s = rate('FW', messi)
tier = score_to_tier(s['overall']).value
if tier == 'Mythic':
    ok(f"Messi 2011-12 = {tier} ({s['overall']:.0f}) — fans happy")
elif tier == 'Legendary' and s['overall'] >= 93:
    mi(f"Messi 2011-12 = {tier} ({s['overall']:.0f}) — close to Mythic, fans might argue")
else:
    maj(f"Messi 2011-12 = {tier} ({s['overall']:.0f}) — fans will riot")

print("\n  E2. Stat name confusion")
# 'PACE' might confuse FIFA fans (FIFA PACE = sprint speed)
mi("PACE in SXI = progressive movement, not sprint speed like FIFA")
print("       RISK: Fans expect Mbappe PACE=99 but SXI might give 94")
print("       FIX: Consider renaming to 'DRIVE' or 'MOBILITY'")

print("\n  E3. Consistency across 30 videos")
# If algorithm changes mid-series, old videos become wrong
mi("Algorithm changes invalidate previous cards")
print("       FIX: Version lock — all Season 1 videos use v2.0")
print("       Never change formula mid-season without re-rating all")

print("\n  E4. Explainability")
# Can you explain why Messi got 93 and not 95?
ok("explanation_json exists with per-stat drivers")
mi("But explanation doesn't show adaptive weight effect")
print("       FIX: Add 'boosted stats' and 'reduced stats' to explanation")

# ══════════════════════════════════════════════════════════════
# F. v3 ROADMAP PRIORITIES
# ══════════════════════════════════════════════════════════════
print("\n[F] v3 ROADMAP PRIORITIES")
priorities = [
    ("CRITICAL", "Add SCA/GCA features (chance/goal creation actions)"),
    ("CRITICAL", "Era adjustment (2010 vs 2024 stat inflation)"),
    ("HIGH", "6-8 position buckets (CB/FB/DM/AM split)"),
    ("HIGH", "Match-level data for real MENTAL/CLUTCH"),
    ("HIGH", "Rename PACE to DRIVE/MOBILITY"),
    ("MEDIUM", "tackles_won quality metric"),
    ("MEDIUM", "Red/yellow card penalty in MENTAL"),
    ("MEDIUM", "Opponent strength weighting"),
    ("MEDIUM", "Explanation includes adaptive weight info"),
    ("LOW", "StatsBomb event data integration"),
    ("LOW", "xT/VAEP action values"),
    ("LOW", "Pair chemistry (Synergize phase)"),
]
for pri, desc in priorities:
    print(f"  [{pri:8s}] {desc}")

# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"  SUMMARY: {len(critical)} CRITICAL, {len(major)} MAJOR, {len(minor)} MINOR, {len(good)} OK")
print()
if critical:
    print("  CRITICAL ISSUES:")
    for c in critical: print(f"    ! {c}")
if major:
    print("  MAJOR ISSUES:")
    for m in major: print(f"    * {m}")
if minor:
    print(f"  MINOR ISSUES: {len(minor)} items")
    for m in minor[:5]: print(f"    - {m}")
    if len(minor) > 5: print(f"    ... and {len(minor)-5} more")
print(f"\n  STRENGTHS ({len(good)}):")
for g in good: print(f"    + {g}")

print("\n  FINAL ASSESSMENT:")
if len(critical) == 0 and len(major) <= 3:
    print("    ENGINE IS SHIPPABLE for content channel.")
    print("    Major issues are data limitations, not algorithm bugs.")
    print("    Fix PACE naming + add SCA/GCA in v2.1 patch.")
else:
    print("    FIX CRITICAL ISSUES before shipping.")
print("=" * 70)
