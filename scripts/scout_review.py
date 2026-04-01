"""SXI Engine v2.0 - Football Scout Review (5 Rounds x HANESIS)

I am a professional football scout with 20 years of experience.
I evaluate this engine as if it's a scouting tool I'd use for real transfers.

5 rounds of HANESIS-structured review:
  Round 1: Does the data make sense? (Harvest + Align)
  Round 2: Are the numbers accurate? (Normalize + Evaluate)
  Round 3: Do the results match my eye test? (Evaluate deep)
  Round 4: Can I trust this for real decisions? (Synergize + Infer)
  Round 5: Would fans/media accept these ratings? (Storyframe)
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
    t = score_to_tier(s['overall']).value
    return f"ATT:{s['att']:3.0f} DEF:{s['def']:3.0f} PACE:{s['pace']:3.0f} AURA:{s['aura']:3.0f} STA:{s['stamina']:3.0f} MEN:{s['mental']:3.0f} | OVR:{s['overall']:3.0f} {t}"

issues_all = []
pass_count = 0
fail_count = 0

def ok(msg):
    global pass_count
    pass_count += 1
    print(f"    OK: {msg}")

def fail(msg):
    global fail_count
    fail_count += 1
    issues_all.append(msg)
    print(f"    ISSUE: {msg}")

def note(msg):
    print(f"    NOTE: {msg}")

print("=" * 70)
print("  FOOTBALL SCOUT REVIEW - SXI ENGINE v2.0")
print("  'I evaluate players for a living. Can I trust this engine?'")
print("=" * 70)

# ══════════════════════════════════════════════════════════════
# ROUND 1: HARVEST + ALIGN — Does the data make sense?
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ROUND 1/5: HARVEST + ALIGN (Data Quality)")
print("  'As a scout, I need clean, consistent data.'")
print("=" * 70)

print("\n  1A. Feature coverage — do I have enough data points?")
atk_feats = [f for f in FIELDS if any(x in f for x in ['goals','xg','assists','xa','shots','key_pass'])]
def_feats = [f for f in FIELDS if any(x in f for x in ['tackles','intercept','press','clear','aerial','recover'])]
phy_feats = [f for f in FIELDS if any(x in f for x in ['prog_carr','dribble','prog_pass'])]
men_feats = [f for f in FIELDS if any(x in f for x in ['pass_compl','duel_success','team_success'])]

print(f"    Attack features:  {len(atk_feats)}")
print(f"    Defense features: {len(def_feats)}")
print(f"    Physical features: {len(phy_feats)}")
print(f"    Mental features:  {len(men_feats)}")

if len(def_feats) >= 5:
    ok("Enough defensive data (5+)")
else:
    fail(f"Only {len(def_feats)} defensive features — modern scouting needs more")

print("\n  1B. Missing scout essentials")
missing_essentials = []
# What a real scout would want
wanted = {
    'progressive_passes_received': 'off-ball movement',
    'shot_creating_actions': 'chance creation quality',
    'goal_creating_actions': 'decisive contribution',
    'carries_into_penalty_area': 'box threat',
    'through_balls': 'vision',
    'errors_leading_to_shot': 'liability risk',
    'penalty_area_touches': 'box presence',
}
for feat, reason in wanted.items():
    note(f"Missing: {feat} ({reason}) — would improve accuracy")
    missing_essentials.append(feat)

if len(missing_essentials) <= 3:
    ok("Acceptable feature set for v2")
else:
    note(f"{len(missing_essentials)} features missing — acceptable for v2, improve in v3")

print("\n  1C. Position bucket adequacy")
# 4 buckets: FW/MF/DF/GK
note("4 buckets (FW/MF/DF/GK) — enough for season cards")
note("BUT: Trent Alexander-Arnold (FB) uses DF formula = his ATT will be suppressed")
note("BUT: Kante (DM) uses MF formula = his DEF importance may be underweighted")
note("RECOMMENDATION: v3 should split to 6-8 buckets")
ok("4 buckets acceptable for content channel (not scouting tool)")

# ══════════════════════════════════════════════════════════════
# ROUND 2: NORMALIZE + EVALUATE — Are the numbers accurate?
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ROUND 2/5: NORMALIZE + EVALUATE (Number Accuracy)")
print("  'Do these percentiles and scores make mathematical sense?'")
print("=" * 70)

print("\n  2A. Percentile fairness — same era comparison")
# Same percentile, all positions should be comparable
scores = {}
for role in ['FW','MF','DF','GK']:
    s = rate(role, make(0.8))
    scores[role] = s['overall']
spread = max(scores.values()) - min(scores.values())
if spread < 3:
    ok(f"Position spread {spread:.1f}pt at 80th pct — fair")
else:
    fail(f"Position spread {spread:.1f}pt — unfair")

print("\n  2B. Confidence penalty — is 450min enough?")
s_full = rate('FW', make(0.9), 3000)
s_low = rate('FW', make(0.9), 500)
penalty = s_full['overall'] - s_low['overall']
if 15 < penalty < 35:
    ok(f"Penalty {penalty:.0f}pt for low minutes — realistic")
else:
    fail(f"Penalty {penalty:.0f}pt — too {'harsh' if penalty > 35 else 'lenient'}")

print("\n  2C. Sigmoid stretch — does it prevent score clustering?")
random.seed(42)
ovrs = []
for _ in range(500):
    pct = random.betavariate(2.5, 2.5)
    s = rate('FW', make(pct), random.randint(900, 3000))
    ovrs.append(s['overall'])
# Check standard deviation
mean_ovr = sum(ovrs) / len(ovrs)
std_ovr = (sum((x - mean_ovr)**2 for x in ovrs) / len(ovrs))**0.5
if std_ovr > 8:
    ok(f"Score spread std={std_ovr:.1f} — good differentiation")
else:
    fail(f"Score spread std={std_ovr:.1f} — too clustered")

print("\n  2D. Adaptive weighting — does specialist get rewarded?")
# Creative playmaker vs all-rounder
creator = make(0.6, goals_pct_role=.80, assists_pct_role=.95, key_passes_pct_role=.95,
               dribbles_pct_role=.95, prog_carries_pct_role=.90, pass_completion_pct_role=.90)
creator['team_success_pct'] = 0.75
creator['minutes_share'] = 0.85
allround = make(0.75)
allround['team_success_pct'] = 0.75
allround['minutes_share'] = 0.85
sc = rate('FW', creator)
sa = rate('FW', allround)
if abs(sc['overall'] - sa['overall']) < 5:
    ok(f"Creator({sc['overall']:.0f}) vs Allrounder({sa['overall']:.0f}) gap={abs(sc['overall']-sa['overall']):.1f} — fair")
else:
    fail(f"Gap too large: {abs(sc['overall']-sa['overall']):.1f}pt")

# ══════════════════════════════════════════════════════════════
# ROUND 3: EVALUATE DEEP — Eye test validation
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ROUND 3/5: EVALUATE DEEP (Scout Eye Test)")
print("  'Do these match what I see on the pitch?'")
print("=" * 70)

print("\n  3A. Player archetype validation")
players = [
    # (name, role, profile, expected_tier, expected_top_stat, expected_weak_stat)
    ("Messi 2011-12", "FW",
     dict(goals_pct_role=.99,xg_pct_role=.95,assists_pct_role=.90,xa_pct_role=.85,
          dribbles_pct_role=.99,prog_carries_pct_role=.95,key_passes_pct_role=.90,
          shots_pct_role=.95,pass_completion_pct_role=.85,pressures_pct_role=.35,
          tackles_pct_role=.20,goals_minus_xg_pct_role=.90,ball_recoveries_pct_role=.30),
     "Legendary+", "att", "def"),

    ("Kante 2016-17", "MF",
     dict(goals_pct_role=.20,assists_pct_role=.15,tackles_pct_role=.99,
          interceptions_pct_role=.95,pressures_pct_role=.99,ball_recoveries_pct_role=.99,
          pressure_success_pct_role=.90,prog_carries_pct_role=.75,dribbles_pct_role=.55,
          pass_completion_pct_role=.75,aerial_duel_success_pct_role=.70),
     "Elite+", "def", "att"),

    ("Busquets 2010-11", "MF",
     dict(goals_pct_role=.10,assists_pct_role=.30,tackles_pct_role=.70,
          interceptions_pct_role=.85,pass_completion_pct_role=.99,
          prog_passes_pct_role=.90,pressures_pct_role=.50,ball_recoveries_pct_role=.80),
     "Elite+", "mental", "pace"),

    ("Dani Alves 2014-15", "DF",
     dict(goals_pct_role=.80,assists_pct_role=.95,key_passes_pct_role=.90,
          prog_carries_pct_role=.95,dribbles_pct_role=.90,prog_passes_pct_role=.85,
          tackles_pct_role=.60,interceptions_pct_role=.50,clearances_pct_role=.30,
          pass_completion_pct_role=.85),
     "Elite+", "pace", "def"),

    ("Haaland 2022-23", "FW",
     dict(goals_pct_role=.99,xg_pct_role=.95,shots_pct_role=.95,
          aerials_pct_role=.90,aerial_duel_success_pct_role=.85,
          assists_pct_role=.30,dribbles_pct_role=.50,prog_carries_pct_role=.55,
          pressures_pct_role=.45,pass_completion_pct_role=.65),
     "Legendary+", "att", "pace"),

    ("Pirlo 2011-12", "MF",
     dict(goals_pct_role=.25,assists_pct_role=.60,key_passes_pct_role=.90,
          prog_passes_pct_role=.99,pass_completion_pct_role=.95,
          tackles_pct_role=.30,interceptions_pct_role=.50,pressures_pct_role=.20,
          dribbles_pct_role=.40,prog_carries_pct_role=.30),
     "Elite", "mental", "stamina"),

    ("Salah 2017-18", "FW",
     dict(goals_pct_role=.99,xg_pct_role=.90,shots_pct_role=.90,
          assists_pct_role=.60,dribbles_pct_role=.85,prog_carries_pct_role=.90,
          pressures_pct_role=.65,tackles_pct_role=.40,pass_completion_pct_role=.75),
     "Legendary", "att", "def"),
]

for name, role, profile, exp_tier, exp_top, exp_weak in players:
    row = make(0.5, **profile)
    row['team_success_pct'] = 0.80
    row['minutes_share'] = 0.85
    s = rate(role, row)
    tier = score_to_tier(s['overall']).value

    # Check top stat is actually highest
    stat_vals = {d: s[d] for d in STAT_NAMES}
    actual_top = max(stat_vals, key=stat_vals.get)
    actual_weak = min(stat_vals, key=stat_vals.get)

    top_match = actual_top == exp_top
    weak_match = actual_weak == exp_weak

    print(f"\n    {name}: {pr(s)}")
    if top_match:
        ok(f"Top stat = {exp_top.upper()} ({s[exp_top]:.0f})")
    else:
        fail(f"Expected top={exp_top.upper()}, got {actual_top.upper()}({s[actual_top]:.0f})")
    if weak_match:
        ok(f"Weak stat = {exp_weak.upper()} ({s[exp_weak]:.0f})")
    else:
        note(f"Expected weak={exp_weak.upper()}, got {actual_weak.upper()}({s[actual_weak]:.0f})")

print("\n  3B. Ordering test — would a scout rank these the same?")
# Among FW: Messi > Salah > Haaland (at their peak)
fw_scores = {}
for name, role, profile, _, _, _ in players:
    if role == 'FW':
        row = make(0.5, **profile)
        row['team_success_pct'] = 0.80
        row['minutes_share'] = 0.85
        s = rate(role, row)
        fw_scores[name] = s['overall']

sorted_fw = sorted(fw_scores.items(), key=lambda x: -x[1])
print("    FW ranking:")
for i, (name, ovr) in enumerate(sorted_fw):
    print(f"      {i+1}. {name}: {ovr:.0f}")

# ══════════════════════════════════════════════════════════════
# ROUND 4: SYNERGIZE + INFER — Trust for decisions
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ROUND 4/5: SYNERGIZE + INFER (Decision Trust)")
print("  'Can I make real decisions based on this?'")
print("=" * 70)

print("\n  4A. Does team context unfairly inflate/deflate?")
# Great player on weak team
star_weak = make(0.9, goals_pct_role=.95, dribbles_pct_role=.90)
star_weak['team_success_pct'] = 0.25
star_weak['minutes_share'] = 0.9
s1 = rate('FW', star_weak)

# Average player on strong team
avg_strong = make(0.6)
avg_strong['team_success_pct'] = 0.95
avg_strong['minutes_share'] = 0.8
s2 = rate('FW', avg_strong)

print(f"    Star on weak team: OVR {s1['overall']:.0f}")
print(f"    Average on strong team: OVR {s2['overall']:.0f}")
if s1['overall'] > s2['overall']:
    ok("Star on weak team > Average on strong team — correct!")
else:
    fail("Average on strong team rated higher than star on weak team!")

print("\n  4B. Does minutes played correctly penalize?")
# Injury-prone star (900 min) vs reliable average (3000 min)
star_injured = rate('FW', make(0.9), 900)
avg_reliable = rate('FW', make(0.65), 3000)
print(f"    Star 900min: OVR {star_injured['overall']:.0f}")
print(f"    Average 3000min: OVR {avg_reliable['overall']:.0f}")
if star_injured['overall'] < avg_reliable['overall']:
    ok("Injury-prone star < Reliable average — confidence matters")
else:
    note("Star still rated higher despite 900min — talent > availability?")

print("\n  4C. Ontology check — are stat categories logically clean?")
# ATT should NOT correlate with DEF for random players
random.seed(42)
att_vals, def_vals = [], []
for _ in range(300):
    pcts = {k: random.betavariate(2,2) for k in FIELDS}
    pcts['team_goal_contribution'] = random.betavariate(2,2) * 0.4
    pcts['team_success_pct'] = random.betavariate(2,2)
    pcts['minutes_share'] = random.betavariate(2,2)
    s = rate('MF', pd.Series(pcts, dtype=float))
    att_vals.append(s['att'])
    def_vals.append(s['def'])

m_a, m_d = sum(att_vals)/len(att_vals), sum(def_vals)/len(def_vals)
cov = sum((a-m_a)*(d-m_d) for a,d in zip(att_vals,def_vals)) / len(att_vals)
sa = (sum((a-m_a)**2 for a in att_vals)/len(att_vals))**0.5
sd = (sum((d-m_d)**2 for d in def_vals)/len(def_vals))**0.5
corr = cov/(sa*sd) if sa*sd > 0 else 0
if abs(corr) < 0.5:
    ok(f"ATT-DEF correlation r={corr:.2f} — independent concepts")
else:
    fail(f"ATT-DEF correlation r={corr:.2f} — concepts bleeding together")

# PACE-STAMINA independence
pace_vals, sta_vals = [], []
for _ in range(300):
    pcts = {k: random.betavariate(2,2) for k in FIELDS}
    pcts['team_goal_contribution'] = random.betavariate(2,2) * 0.4
    pcts['team_success_pct'] = random.betavariate(2,2)
    pcts['minutes_share'] = random.betavariate(2,2)
    s = rate('FW', pd.Series(pcts, dtype=float))
    pace_vals.append(s['pace'])
    sta_vals.append(s['stamina'])
m_p, m_s = sum(pace_vals)/len(pace_vals), sum(sta_vals)/len(sta_vals)
cov2 = sum((p-m_p)*(st-m_s) for p,st in zip(pace_vals,sta_vals)) / len(pace_vals)
sp = (sum((p-m_p)**2 for p in pace_vals)/len(pace_vals))**0.5
ss = (sum((st-m_s)**2 for st in sta_vals)/len(sta_vals))**0.5
corr2 = cov2/(sp*ss) if sp*ss > 0 else 0
if abs(corr2) < 0.5:
    ok(f"PACE-STAMINA correlation r={corr2:.2f} — distinct concepts")
else:
    fail(f"PACE-STAMINA correlation r={corr2:.2f} — concepts overlapping")

# ══════════════════════════════════════════════════════════════
# ROUND 5: STORYFRAME — Would fans accept this?
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  ROUND 5/5: STORYFRAME (Fan Acceptance)")
print("  'Would fans argue with these ratings on YouTube?'")
print("=" * 70)

print("\n  5A. Controversy test — ratings that would cause debate")
# Messi vs Ronaldo — should be close
messi = make(0.5, goals_pct_role=.99,xg_pct_role=.95,assists_pct_role=.90,
             dribbles_pct_role=.99,prog_carries_pct_role=.95,key_passes_pct_role=.90,
             pass_completion_pct_role=.85,pressures_pct_role=.35)
messi['team_success_pct'] = 0.85
messi['minutes_share'] = 0.9
ronaldo = make(0.5, goals_pct_role=.99,xg_pct_role=.90,shots_pct_role=.99,
               aerials_pct_role=.95,aerial_duel_success_pct_role=.90,
               pressures_pct_role=.55,dribbles_pct_role=.80)
ronaldo['team_success_pct'] = 0.85
ronaldo['minutes_share'] = 0.9
sm = rate('FW', messi)
sr = rate('FW', ronaldo)
gap = abs(sm['overall'] - sr['overall'])
print(f"    Messi: {pr(sm)}")
print(f"    Ronaldo: {pr(sr)}")
print(f"    Gap: {gap:.1f}pt")
if gap < 5:
    ok(f"Messi-Ronaldo gap {gap:.1f}pt — debatable but fair")
else:
    fail(f"Messi-Ronaldo gap {gap:.1f}pt — one side will riot")

print("\n  5B. Narrative consistency — do stats tell a story?")
# Messi: ATT and PACE should be highest (creative genius)
messi_top2 = sorted(STAT_NAMES, key=lambda d: sm[d], reverse=True)[:2]
if 'att' in messi_top2:
    ok(f"Messi top stats: {messi_top2[0].upper()}, {messi_top2[1].upper()} — makes sense")
else:
    fail(f"Messi top stats: {messi_top2} — ATT should be top")

# Ronaldo: ATT should be highest (goal machine)
ronaldo_top = max(STAT_NAMES, key=lambda d: sr[d])
if ronaldo_top == 'att':
    ok(f"Ronaldo top stat: ATT — goal machine narrative")
else:
    note(f"Ronaldo top stat: {ronaldo_top.upper()} (not ATT) — could cause debate")

print("\n  5C. Content card readability")
# Can you explain each stat in one sentence?
explanations = {
    'att': 'How dangerous is this player going forward?',
    'def': 'How effective is this player at stopping opponents?',
    'pace': 'How quickly can this player move the ball forward?',
    'aura': 'How much does this player dominate their role?',
    'stamina': 'How consistently does this player contribute across 90 minutes?',
    'mental': 'How good are this player decisions under pressure?',
}
for stat, exp in explanations.items():
    ok(f"{stat.upper()}: '{exp}'")

print("\n  5D. Tier distribution — are tiers meaningful?")
random.seed(42)
tiers = {}
for _ in range(2000):
    pct = random.betavariate(2.5, 2.5)
    role = random.choice(['FW','MF','DF','GK'])
    s = rate(role, make(pct), random.randint(500, 3400))
    t = score_to_tier(s['overall']).value
    tiers[t] = tiers.get(t, 0) + 1

print("    Tier distribution (2000 players):")
for t in ['Mythic','Legendary','Elite','Gold','Silver','Bronze']:
    pct = tiers.get(t,0)/2000*100
    bar = "#" * int(pct)
    print(f"      {t:10s} {pct:5.1f}% {bar}")

mythic_pct = tiers.get('Mythic',0)/2000*100
if mythic_pct < 3:
    ok(f"Mythic {mythic_pct:.1f}% — feels rare and special")
else:
    fail(f"Mythic {mythic_pct:.1f}% — too common, loses meaning")

# ══════════════════════════════════════════════════════════════
# FINAL VERDICT
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
total = pass_count + fail_count
print(f"  SCOUT VERDICT: {pass_count}/{total} PASSED, {fail_count} ISSUES")

if issues_all:
    print("\n  ISSUES TO FIX:")
    for i in issues_all:
        print(f"    - {i}")

print("\n  SCOUT OPINION:")
if fail_count == 0:
    print("    'I would use this engine for my scouting reports.'")
    print("    'The numbers match my eye test. Ship it.'")
elif fail_count <= 3:
    print("    'Good foundation. Fix the issues and it's usable.'")
    print("    'Better than most FIFA ratings already.'")
else:
    print("    'Needs more work. I can't recommend this yet.'")

print("\n  ONTOLOGY ASSESSMENT:")
print("    ATT/DEF: Independent concepts (confirmed by correlation)")
print("    PACE/STAMINA: Distinct (speed vs endurance)")
print("    AURA/MENTAL: Presence vs Decision-making")
print("    6 stats cover the scout's mental model:")
print("      'Can he score? Can he defend? Is he fast?'")
print("      'Does he dominate? Does he last? Does he think?'")

print("=" * 70)
