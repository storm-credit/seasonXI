"""HANESIS Full Pipeline — Real FBref Data

H: Load 5 league CSVs
A: Position classification
N: Per90 + Percentile
E: v2.0 Engine rating (ATT/DEF/PACE/AURA/STA/MEN)
S: Validate known players
I: Anomaly detection
S: Export cards
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np

# ── H: HARVEST ────────────────────────────────────────────────
print("=" * 65)
print("  HANESIS PIPELINE — REAL DATA")
print("=" * 65)

print("\n[H] HARVEST: Loading FBref data...")
raw_dir = Path("data/raw/fbref")
dfs = []
for csv in sorted(raw_dir.glob("*_players.csv")):
    df = pd.read_csv(csv)
    league = csv.stem.split("_")[0]
    df["league_id"] = league
    dfs.append(df)
    print(f"  {league}: {len(df)} players")

all_players = pd.concat(dfs, ignore_index=True)
print(f"  TOTAL: {len(all_players)} players loaded")

# ── A: ALIGN ──────────────────────────────────────────────────
print("\n[A] ALIGN: Position classification...")

def classify_position(pos, goals):
    if pd.isna(pos): return "MF"
    pos = str(pos).upper()
    if "GK" in pos: return "GK"
    if "FW" in pos: return "FW"
    if "DF" in pos:
        if "MF" in pos and goals >= 3: return "MF"
        return "DF"
    if "MF" in pos:
        if "FW" in pos and goals >= 5: return "FW"
        return "MF"
    return "MF"

all_players["role_bucket"] = all_players.apply(
    lambda r: classify_position(r.get("primary_position"), r.get("goals", 0)), axis=1
)

pos_counts = all_players["role_bucket"].value_counts()
for pos, cnt in pos_counts.items():
    print(f"  {pos}: {cnt}")

# ── N: NORMALIZE ──────────────────────────────────────────────
print("\n[N] NORMALIZE: Per90 + Percentile...")

# Filter min minutes
MIN_MINUTES = 450
filtered = all_players[all_players["minutes_played"] >= MIN_MINUTES].copy()
print(f"  After {MIN_MINUTES}min filter: {len(filtered)} players")

# Per90
counting_stats = [
    "goals", "assists", "shots", "shots_on_target", "key_passes",
    "progressive_passes", "progressive_carries", "successful_dribbles",
    "tackles", "interceptions", "clearances", "aerial_duels_won",
    "xg", "xa", "clean_sheets",
]

for stat in counting_stats:
    if stat in filtered.columns:
        filtered[f"{stat}_p90"] = filtered[stat].fillna(0) / (filtered["minutes_played"] / 90)

# Derived features
filtered["goals_minus_xg_p90"] = filtered["goals_p90"] - filtered.get("xg_p90", filtered["goals_p90"])
filtered["team_goal_contribution"] = (
    (filtered["goals"].fillna(0) + filtered["assists"].fillna(0))
    / filtered["team_goals_scored"].clip(lower=1)
).clip(0, 1)

# Team success
league_games = {"epl": 38, "laliga": 38, "seriea": 38, "bundesliga": 34, "ligue1": 38}
filtered["max_points"] = filtered["league_id"].map(lambda x: league_games.get(x, 38) * 3)
filtered["team_success_pct"] = (filtered["team_points"] / filtered["max_points"]).clip(0, 1)
filtered["minutes_share"] = filtered["minutes_played"] / (
    filtered["league_id"].map(lambda x: league_games.get(x, 38)) * 90
).clip(lower=1)

# Percentile within role
pct_stats = [
    ("goals_p90", "goals_pct_role"),
    ("xg_p90", "xg_pct_role"),
    ("shots_p90", "shots_pct_role"),
    ("goals_minus_xg_p90", "goals_minus_xg_pct_role"),
    ("assists_p90", "assists_pct_role"),
    ("xa_p90", "xa_pct_role"),
    ("key_passes_p90", "key_passes_pct_role"),
    ("progressive_passes_p90", "prog_passes_pct_role"),
    ("progressive_carries_p90", "prog_carries_pct_role"),
    ("successful_dribbles_p90", "dribbles_pct_role"),
    ("tackles_p90", "tackles_pct_role"),
    ("interceptions_p90", "interceptions_pct_role"),
    ("clearances_p90", "clearances_pct_role"),
    ("aerial_duels_won_p90", "aerials_pct_role"),
    ("clean_sheets_p90", "clean_sheets_pct_role"),
]

for src, dst in pct_stats:
    if src in filtered.columns:
        filtered[dst] = filtered.groupby("role_bucket")[src].rank(pct=True)
    else:
        filtered[dst] = 0.5

# Proxy missing features from available data
# pressures ~ tackles + interceptions (defensive work rate)
if "pressures_pct_role" not in filtered.columns:
    if "tackles_pct_role" in filtered.columns:
        filtered["pressures_pct_role"] = (
            filtered["tackles_pct_role"] * 0.6 + filtered["interceptions_pct_role"] * 0.4
        )
    else:
        filtered["pressures_pct_role"] = 0.5

# pressure_success ~ tackles success proxy
if "pressure_success_pct_role" not in filtered.columns:
    filtered["pressure_success_pct_role"] = filtered.get("tackles_pct_role", pd.Series(0.5, index=filtered.index))

# ball_recoveries ~ interceptions + tackles
if "ball_recoveries_pct_role" not in filtered.columns:
    filtered["ball_recoveries_pct_role"] = (
        filtered.get("interceptions_pct_role", pd.Series(0.5, index=filtered.index)) * 0.5
        + filtered.get("tackles_pct_role", pd.Series(0.5, index=filtered.index)) * 0.5
    )

# aerial_duel_success ~ aerials won rank (proxy)
if "aerial_duel_success_pct_role" not in filtered.columns:
    filtered["aerial_duel_success_pct_role"] = filtered.get("aerials_pct_role", pd.Series(0.5, index=filtered.index))

# pass_completion ~ progressive_passes rank (good passers pass accurately)
if "pass_completion_pct_role" not in filtered.columns:
    filtered["pass_completion_pct_role"] = filtered.get("prog_passes_pct_role", pd.Series(0.5, index=filtered.index))

# GK features
for col in ["gk_saves_pct_role", "gk_psxg_diff_pct_role",
            "gk_crosses_stopped_pct_role", "gk_pass_completion_pct_role",
            "gk_launch_pct_role"]:
    if col not in filtered.columns:
        # For GK: use clean_sheets as proxy for defensive ability
        if "clean_sheets_pct_role" in filtered.columns:
            filtered[col] = filtered["clean_sheets_pct_role"]
        else:
            filtered[col] = 0.5

print(f"  Proxy features generated for missing data")

print(f"  Percentile columns: {len([c for c in filtered.columns if c.endswith('_pct_role')])}")

# ── E: EVALUATE ───────────────────────────────────────────────
print("\n[E] EVALUATE: Running v2.0 engine...")

from seasonxi.ratings.formula_v1 import ROLE_RATERS, STAT_NAMES
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import score_to_tier

results = []
for _, row in filtered.iterrows():
    role = row["role_bucket"]
    rater = ROLE_RATERS.get(role)
    if not rater: continue

    conf = compute_confidence(int(row["minutes_played"]))
    scores = rater(row, conf)
    tier = score_to_tier(scores["overall"]).value

    results.append({
        "player_name": row["player_name"],
        "club": row["club_name"],
        "league": row["league_id"],
        "season": row["season_label"],
        "position": row["role_bucket"],
        "minutes": int(row["minutes_played"]),
        "goals": int(row.get("goals", 0)),
        "assists": int(row.get("assists", 0)),
        "att": round(scores["att"], 1),
        "def": round(scores["def"], 1),
        "pace": round(scores["pace"], 1),
        "aura": round(scores["aura"], 1),
        "stamina": round(scores["stamina"], 1),
        "mental": round(scores["mental"], 1),
        "overall": round(scores["overall"], 1),
        "confidence": round(conf, 3),
        "tier": tier,
    })

ratings_df = pd.DataFrame(results)
print(f"  Rated: {len(ratings_df)} players")

# ── S: SYNERGIZE (Validate Known Players) ─────────────────────
print("\n[S] SYNERGIZE: Validating known players...")

known = [
    ("Mohamed Salah", "FW", 88, "Elite+"),
    ("Son Heung-min", "FW", 85, "Elite"),
    ("Karim Benzema", "FW", 88, "Elite+"),
    ("Robert Lewandowski", "FW", 88, "Elite+"),
    ("Kevin De Bruyne", "MF", 88, "Elite+"),
    ("Virgil van Dijk", "DF", 85, "Elite"),
    ("Trent Alexander-Arnold", "DF", 80, "Gold+"),
]

for name, exp_pos, min_ovr, exp_tier in known:
    match = ratings_df[ratings_df["player_name"].str.contains(name.split()[-1], case=False, na=False)]
    if len(match) == 0:
        print(f"  NOT FOUND: {name}")
        continue
    p = match.iloc[0]
    status = "PASS" if p["overall"] >= min_ovr else "LOW"
    print(f"  {status:4s} {p['player_name']:25s} {p['position']:3s} ATT:{p['att']:3.0f} DEF:{p['def']:3.0f} PAC:{p['pace']:3.0f} AUR:{p['aura']:3.0f} STA:{p['stamina']:3.0f} MEN:{p['mental']:3.0f} | OVR:{p['overall']:3.0f} {p['tier']}")

# ── I: INFER (Anomaly Detection) ──────────────────────────────
print("\n[I] INFER: Anomaly detection...")

# Top 20 overall
print("\n  TOP 20 OVERALL:")
top20 = ratings_df.nlargest(20, "overall")
for i, (_, p) in enumerate(top20.iterrows()):
    print(f"  {i+1:2d}. {p['player_name']:25s} {p['club']:20s} {p['position']:3s} OVR:{p['overall']:5.1f} {p['tier']}")

# Tier distribution
print("\n  TIER DISTRIBUTION:")
tier_dist = ratings_df["tier"].value_counts()
total = len(ratings_df)
for tier in ["Mythic", "Legendary", "Elite", "Gold", "Silver", "Bronze"]:
    cnt = tier_dist.get(tier, 0)
    pct = cnt / total * 100
    bar = "#" * int(pct)
    print(f"    {tier:10s} {cnt:4d} ({pct:5.1f}%) {bar}")

# Position distribution in top 50
print("\n  TOP 50 BY POSITION:")
top50 = ratings_df.nlargest(50, "overall")
pos_dist = top50["position"].value_counts()
for pos in ["FW", "MF", "DF", "GK"]:
    print(f"    {pos}: {pos_dist.get(pos, 0)}")

# Suspiciously high ratings for unknowns
print("\n  ANOMALY: High OVR but low goals+assists (FW):")
fw_high = ratings_df[(ratings_df["position"] == "FW") & (ratings_df["overall"] > 85)]
for _, p in fw_high.iterrows():
    if p["goals"] + p["assists"] < 10:
        print(f"    SUSPECT: {p['player_name']} OVR:{p['overall']:.0f} but only {p['goals']}G {p['assists']}A")

# ── S: STORYFRAME (Export) ────────────────────────────────────
print("\n[S] STORYFRAME: Exporting cards...")

out_dir = Path("outputs/cards")
out_dir.mkdir(parents=True, exist_ok=True)

# Save all cards
all_cards_path = out_dir / "_all_cards_v2.json"
ratings_df.to_json(all_cards_path, orient="records", indent=2, force_ascii=False)
print(f"  All cards: {all_cards_path} ({len(ratings_df)} cards)")

# Save top 50
top50_path = out_dir / "_top50_v2.json"
top50.to_json(top50_path, orient="records", indent=2, force_ascii=False)
print(f"  Top 50: {top50_path}")

print("\n" + "=" * 65)
print(f"  PIPELINE COMPLETE: {len(ratings_df)} players rated")
print(f"  Mythic: {tier_dist.get('Mythic', 0)}, Legendary: {tier_dist.get('Legendary', 0)}, Elite: {tier_dist.get('Elite', 0)}")
print("=" * 65)
