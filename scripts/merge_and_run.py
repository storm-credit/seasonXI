"""Merge FBref + Understat and run HANESIS pipeline.

FBref has: goals, assists, shots, appearances, minutes, position, team
Understat adds: xG, xA, key_passes, xGChain, xGBuildup
"""
import pandas as pd
from pathlib import Path
from thefuzz import fuzz

from seasonxi.ratings.formula_v1 import ROLE_RATERS, STAT_NAMES
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import score_to_tier

print("=" * 65)
print("  HANESIS PIPELINE — FBref + Understat MERGED")
print("=" * 65)

# ── H: HARVEST ────────────────────────────────────────────────
print("\n[H] HARVEST")

# Load FBref
fbref_dfs = []
for csv in sorted(Path("data/raw/fbref").glob("*_players.csv")):
    df = pd.read_csv(csv)
    league = csv.stem.split("_")[0]
    df["league_id"] = league
    fbref_dfs.append(df)
fbref = pd.concat(fbref_dfs, ignore_index=True)
print(f"  FBref: {len(fbref)} players")

# Load Understat
us = pd.read_csv("data/raw/understat/all_leagues_2021_2022.csv")
us_league_map = {
    "ENG-Premier League": "epl", "ESP-La Liga": "laliga",
    "ITA-Serie A": "seriea", "GER-Bundesliga": "bundesliga",
    "FRA-Ligue 1": "ligue1",
}
us["league_id"] = us["league_name"].map(us_league_map)
print(f"  Understat: {len(us)} players")

# ── A: ALIGN (Fuzzy match FBref <-> Understat) ────────────────
print("\n[A] ALIGN: Matching FBref <-> Understat...")

def normalize_name(name):
    if pd.isna(name): return ""
    return str(name).lower().strip()

matched = 0
for idx, fb_row in fbref.iterrows():
    fb_name = normalize_name(fb_row["player_name"])
    fb_league = fb_row["league_id"]

    # Find best match in Understat for same league
    us_league = us[us["league_id"] == fb_league]
    best_score = 0
    best_idx = None

    for us_idx, us_row in us_league.iterrows():
        us_name = normalize_name(us_row["player"])
        score = fuzz.ratio(fb_name, us_name)
        if score > best_score:
            best_score = score
            best_idx = us_idx

    if best_score >= 80 and best_idx is not None:
        us_row = us.loc[best_idx]
        fbref.loc[idx, "xg"] = us_row["xg"]
        fbref.loc[idx, "xa"] = us_row["xa"]
        fbref.loc[idx, "key_passes"] = us_row["key_passes"]
        matched += 1

print(f"  Understat matched: {matched}/{len(fbref)} ({matched/len(fbref)*100:.0f}%)")

# Merge defense data (tackles_won, interceptions)
print("  Loading defense data...")
defense_map = {"epl": "epl", "laliga": "laliga", "seriea": "seriea",
               "bundesliga": "bundesliga", "ligue1": "ligue1"}
def_matched = 0
for league_key in defense_map:
    def_path = Path(f"data/raw/fbref_extra/{league_key}_defense.csv")
    if not def_path.exists():
        print(f"    {league_key}: no defense file")
        continue
    def_df = pd.read_csv(def_path)
    print(f"    {league_key}: {len(def_df)} defense rows")

    for _, def_row in def_df.iterrows():
        def_name = normalize_name(def_row["player_name"])
        # Find match in fbref for this league
        league_mask = fbref["league_id"] == league_key
        for idx in fbref[league_mask].index:
            fb_name = normalize_name(fbref.loc[idx, "player_name"])
            if fuzz.ratio(fb_name, def_name) >= 85:
                fbref.loc[idx, "tackles"] = def_row.get("tackles_won", 0)
                fbref.loc[idx, "interceptions"] = def_row.get("interceptions", 0)
                def_matched += 1
                break

print(f"  Defense matched: {def_matched}")

# Merge Sofascore data (clearances, dribbles, pass accuracy, duels, clean_sheets)
print("  Loading Sofascore data...")
sf_path = Path("data/raw/sofascore/sofascore_all_leagues_2021_2022.csv")
sf_matched = 0
if sf_path.exists():
    sf = pd.read_csv(sf_path, sep='~')
    sf_league_map = {"epl": "epl", "laliga": "laliga", "seriea": "seriea",
                     "bundesliga": "bundesliga", "ligue1": "ligue1"}
    print(f"    Sofascore: {len(sf)} players")

    # Pre-convert columns to float to avoid dtype warnings
    for col in ["clearances", "successful_dribbles", "clean_sheets", "duels_won", "pass_completion_pct"]:
        if col not in fbref.columns:
            fbref[col] = 0.0
        else:
            fbref[col] = fbref[col].astype(float)

    for _, sf_row in sf.iterrows():
        sf_name = normalize_name(str(sf_row.get("player_name", "")))
        sf_league = str(sf_row.get("league", ""))

        league_mask = fbref["league_id"] == sf_league
        for idx in fbref[league_mask].index:
            fb_name = normalize_name(fbref.loc[idx, "player_name"])
            if fuzz.ratio(fb_name, sf_name) >= 80:
                fbref.loc[idx, "clearances"] = float(sf_row.get("clearances", 0))
                fbref.loc[idx, "successful_dribbles"] = float(sf_row.get("dribbles", 0))
                fbref.loc[idx, "clean_sheets"] = float(sf_row.get("clean_sheets", 0))
                total_p = sf_row.get("total_passes", 0)
                if total_p and total_p > 0:
                    fbref.loc[idx, "pass_completion_pct"] = float(sf_row.get("accurate_passes", 0)) / total_p
                fbref.loc[idx, "duels_won"] = float(sf_row.get("duels_won", 0))
                sf_matched += 1
                break

    print(f"  Sofascore matched: {sf_matched}")
else:
    print("  Sofascore: file not found")

# ── N: NORMALIZE ──────────────────────────────────────────────
print("\n[N] NORMALIZE")

MIN_MINUTES = 900  # 10+ full games — filters out bench warmers for fairer percentiles
filtered = fbref[fbref["minutes_played"] >= MIN_MINUTES].copy()
print(f"  After {MIN_MINUTES}min filter: {len(filtered)}")

# Position classification
def classify_pos(row):
    """Multi-factor position classifier v3.

    Based on PlayeRank (2019) principle: use multiple indicators
    rather than single threshold for role assignment.

    Key changes from v2:
    - FW threshold lowered: goals >= 10 (was 15) OR xg >= 8 (was 12)
    - Multi-factor fw_score replaces single threshold for MF reclassification
    - LW/RW in position string -> always FW
    - shots_p90, dribbles_p90 add supporting evidence
    """
    pos = row.get("primary_position", "")
    if pd.isna(pos): pos = ""
    pos = str(pos).upper().replace(",", "").replace("-", "").replace("/", "")

    goals = row.get("goals", 0) or 0
    xg = row.get("xg", 0) or 0
    assists = row.get("assists", 0) or 0
    minutes = row.get("minutes_played", 0) or 1
    goals_p90 = goals / (minutes / 90) if minutes > 0 else 0

    # shots_p90 and dribbles_p90 may not exist yet (computed later) — use raw counts
    shots = row.get("shots", 0) or 0
    shots_p90 = shots / (minutes / 90) if minutes > 0 else 0
    dribbles = row.get("successful_dribbles", 0) or 0
    dribbles_p90 = dribbles / (minutes / 90) if minutes > 0 else 0

    if "GK" in pos:
        return "GK"

    # Any position containing FW -> FW (trust FBref primary position)
    if "FW" in pos:
        return "FW"

    # Pure DF positions
    if pos in ("DF", "CB", "LB", "RB", "WB"):
        return "DF"

    # DF-MF hybrids (attacking fullbacks/wingbacks)
    if "DF" in pos and "MF" in pos:
        if assists >= 5 or goals >= 3 or goals_p90 >= 0.15:
            return "MF"
        return "DF"

    if pos.startswith("DF") or ("DF" in pos and "MF" not in pos):
        return "DF"

    # MF -> FW reclassification (the key fix)
    # Covers: MF, MFFW (already caught above), LW, RW embedded in pos string
    if pos.startswith("MF") or pos in ("AM", "CM", "CAM", "CDM", "LM", "RM"):
        # Multi-factor FW score
        fw_score = 0
        if goals >= 10:      fw_score += 2
        if goals >= 15:      fw_score += 1
        if xg >= 8:          fw_score += 2
        if xg >= 12:         fw_score += 1
        if goals_p90 >= 0.3: fw_score += 2
        if goals_p90 >= 0.5: fw_score += 1
        if shots_p90 >= 2.0: fw_score += 1
        if dribbles_p90 >= 1.5: fw_score += 1

        # Threshold: 3+ points -> FW
        if fw_score >= 3:
            return "FW"
        return "MF"

    # Fallback
    return "MF"

filtered["role_bucket"] = filtered.apply(classify_pos, axis=1)

# Per90
stats_p90 = ["goals","assists","shots","key_passes","xg","xa",
             "tackles","interceptions","clearances","aerial_duels_won","clean_sheets",
             "successful_dribbles","duels_won"]
for s in stats_p90:
    if s in filtered.columns:
        filtered[f"{s}_p90"] = filtered[s].fillna(0) / (filtered["minutes_played"] / 90)

# Derived
filtered["goals_minus_xg_p90"] = filtered.get("goals_p90", 0) - filtered.get("xg_p90", 0)

# Context
league_games = {"epl":38,"laliga":38,"seriea":38,"bundesliga":34,"ligue1":38}
filtered["team_goal_contribution"] = (
    (filtered["goals"].fillna(0) + filtered["assists"].fillna(0))
    / filtered["team_goals_scored"].clip(lower=1)
).clip(0,1)
filtered["max_pts"] = filtered["league_id"].map(lambda x: league_games.get(x,38)*3)
filtered["team_success_pct"] = (filtered["team_points"] / filtered["max_pts"]).clip(0,1)
filtered["minutes_share"] = filtered["minutes_played"] / (
    filtered["league_id"].map(lambda x: league_games.get(x,38)) * 90
)

# Percentile within role
# Split into FBref-only stats (rank() applied) vs Sofascore stats (override after, no re-rank)
FBREF_PCT_MAP = [
    ("goals_p90","goals_pct_role"), ("xg_p90","xg_pct_role"),
    ("shots_p90","shots_pct_role"), ("goals_minus_xg_p90","goals_minus_xg_pct_role"),
    ("assists_p90","assists_pct_role"), ("xa_p90","xa_pct_role"),
    ("key_passes_p90","key_passes_pct_role"),
    ("tackles_p90","tackles_pct_role"), ("interceptions_p90","interceptions_pct_role"),
    ("aerial_duels_won_p90","aerials_pct_role"),
]
# Sofascore-sourced: ranked separately, then overridden — NOT re-ranked in FBREF loop
SOFASCORE_PCT_MAP = [
    ("clearances_p90","clearances_pct_role"),
    ("successful_dribbles_p90","dribbles_pct_role"),
    ("duels_won_p90","aerial_duel_success_pct_role"),
    ("clean_sheets_p90","clean_sheets_pct_role"),
]

# Pass completion (not per90 — it's already a rate)
if "pass_completion_pct" in filtered.columns:
    filtered["pass_completion_pct_role"] = filtered.groupby("role_bucket")["pass_completion_pct"].rank(pct=True).fillna(0.5)

# FBref stats: rank within role
for src, dst in FBREF_PCT_MAP:
    if src in filtered.columns:
        filtered[dst] = filtered.groupby("role_bucket")[src].rank(pct=True).fillna(0.5)
    else:
        filtered[dst] = 0.5

# BUG 2 fix: DF/GK-only stats — FW/MF get 0.0 (these stats are meaningless for attackers)
DF_GK_ONLY = {"clearances_pct_role", "aerials_pct_role", "clean_sheets_pct_role"}
df_gk_mask = filtered["role_bucket"].isin(["DF", "GK"])

# Sofascore override: rank within role, then apply only where real data exists
# This runs AFTER FBref loop and is NOT overwritten again — bug 1 fix
for stat, pct_col in SOFASCORE_PCT_MAP:
    if stat in filtered.columns:
        real_pct = filtered.groupby("role_bucket")[stat].rank(pct=True)
        has_data = filtered[stat] > 0
        if pct_col in DF_GK_ONLY:
            # BUG 2 fix: zero out FW/MF first, then apply real data only for DF/GK
            filtered[pct_col] = 0.0
            override_mask = has_data & df_gk_mask
            filtered.loc[override_mask, pct_col] = real_pct[override_mask]
        else:
            filtered[pct_col] = 0.5  # default for rows without data
            filtered.loc[has_data, pct_col] = real_pct[has_data]
    else:
        if pct_col in DF_GK_ONLY:
            filtered[pct_col] = 0.0
        else:
            filtered[pct_col] = 0.5

# BUG 2 fix: aerials_pct_role (from FBref) also 0.0 for FW/MF
if "aerials_pct_role" in filtered.columns:
    filtered.loc[~df_gk_mask, "aerials_pct_role"] = 0.0

print(f"  Sofascore percentile overrides applied")

# Proxy missing features — smarter estimation from available data
# BUG 3 fix: use per-row has_data mask instead of checking if entire column is 0.5
# For DF: interceptions correlates with clearances/aerials
# For FW: key_passes correlates with progressive actions
# For MF: tackles correlates with pressures
for col in ["prog_passes_pct_role","prog_carries_pct_role","dribbles_pct_role",
            "pass_completion_pct_role","pressures_pct_role","pressure_success_pct_role",
            "aerial_duel_success_pct_role","ball_recoveries_pct_role",
            "gk_saves_pct_role","gk_psxg_diff_pct_role","gk_crosses_stopped_pct_role",
            "gk_pass_completion_pct_role","gk_launch_pct_role",
            "clearances_pct_role","aerials_pct_role"]:
    # BUG 3 fix: identify rows that are missing real data (NaN or never set / still at default)
    if col not in filtered.columns:
        filtered[col] = float("nan")
    # Per-row proxy mask: rows where value is NaN or 0.5 (default placeholder)
    needs_proxy = filtered[col].isna() | (filtered[col] == 0.5)
    if needs_proxy.any():
        if "prog" in col and "key_passes_pct_role" in filtered.columns:
            filtered.loc[needs_proxy, col] = filtered.loc[needs_proxy, "key_passes_pct_role"]
        elif "dribble" in col:
            # FW: goals proxy, DF: low, MF: assists proxy
            def _dribble_proxy(r):
                if r["role_bucket"] == "FW":
                    return r.get("goals_pct_role", 0.5) * 0.7 + r.get("assists_pct_role", 0.5) * 0.3
                elif r["role_bucket"] == "MF":
                    return r.get("assists_pct_role", 0.5) * 0.5 + r.get("tackles_pct_role", 0.5) * 0.5
                return 0.3
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_dribble_proxy, axis=1)
        elif "press" in col and "tackles_pct_role" in filtered.columns:
            icp = filtered.get("interceptions_pct_role", pd.Series(0.5, index=filtered.index))
            filtered.loc[needs_proxy, col] = (
                filtered.loc[needs_proxy, "tackles_pct_role"] * 0.8
                + icp[needs_proxy] * 0.2
            )
        elif "pass_comp" in col:
            def _pass_comp_proxy(r):
                if r["role_bucket"] == "DF":
                    return min(1.0, r.get("interceptions_pct_role", 0.5) * 0.6 + 0.3)
                return min(1.0, r.get("assists_pct_role", 0.5) * 0.7 + r.get("key_passes_pct_role", 0.5) * 0.3)
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_pass_comp_proxy, axis=1)
        elif "ball_rec" in col:
            icp = filtered.get("interceptions_pct_role", pd.Series(0.5, index=filtered.index))
            tck = filtered.get("tackles_pct_role", pd.Series(0.5, index=filtered.index))
            filtered.loc[needs_proxy, col] = icp[needs_proxy] * 0.6 + tck[needs_proxy] * 0.4
        elif "aerial" in col and "clearances" not in col:
            def _aerial_proxy(r):
                if r["role_bucket"] == "DF":
                    return min(1.0, r.get("interceptions_pct_role", 0.5) * 0.7 + r.get("tackles_pct_role", 0.5) * 0.3)
                return min(1.0, r.get("goals_pct_role", 0.5) * 0.3 + 0.3)
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_aerial_proxy, axis=1)
        elif "clearances" in col:
            def _clearances_proxy(r):
                if r["role_bucket"] in ["DF", "GK"]:
                    return r.get("interceptions_pct_role", 0.5) * 0.8 + r.get("tackles_pct_role", 0.5) * 0.2
                return 0.3
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_clearances_proxy, axis=1)
        elif "gk" in col and "clean_sheets_pct_role" in filtered.columns:
            filtered.loc[needs_proxy, col] = filtered.loc[needs_proxy, "clean_sheets_pct_role"]
        else:
            filtered.loc[needs_proxy, col] = 0.5

print(f"  Features: {len([c for c in filtered.columns if c.endswith('_pct_role')])} percentiles")

# ── E: EVALUATE ───────────────────────────────────────────────
print("\n[E] EVALUATE")

from seasonxi.ratings.league_adjustment import get_league_multiplier

results = []
for _, row in filtered.iterrows():
    role = row["role_bucket"]
    rater = ROLE_RATERS.get(role)
    if not rater: continue
    conf = compute_confidence(int(row["minutes_played"]))
    scores = rater(row, conf)
    # Post-OVR league quality adjustment
    league_mult = get_league_multiplier(str(row.get("league_id", "")))
    ovr_raw = scores["overall"]
    scores["overall"] = max(50.0, min(99.0, 50 + (ovr_raw - 50) * league_mult))
    tier = score_to_tier(scores["overall"]).value
    results.append({
        "player_name": row["player_name"], "club": row["club_name"],
        "league": row["league_id"], "position": role,
        "minutes": int(row["minutes_played"]),
        "goals": int(row.get("goals",0)), "assists": int(row.get("assists",0)),
        "xg": round(float(row.get("xg",0)),1), "xa": round(float(row.get("xa",0)),1),
        **{d: round(scores[d],1) for d in STAT_NAMES},
        "overall": round(scores["overall"],1), "confidence": round(conf,3),
        "tier": tier,
    })

ratings = pd.DataFrame(results)
print(f"  Rated: {len(ratings)} players")

# ── S: VALIDATE ───────────────────────────────────────────────
print("\n[S] VALIDATE: Known players")

known = ["Salah","Son","Benzema","Lewandowski","De Bruyne","Van Dijk",
         "Mbappe","Kane","Modric","Haaland"]
for name in known:
    m = ratings[ratings["player_name"].str.contains(name, case=False, na=False)]
    if len(m) == 0:
        print(f"  NOT FOUND: {name}")
        continue
    p = m.iloc[0]
    print(f"  {p['player_name']:25s} {p['position']:3s} ATT:{p['att']:3.0f} DEF:{p['def']:3.0f} PAC:{p['pace']:3.0f} AUR:{p['aura']:3.0f} STA:{p['stamina']:3.0f} MEN:{p['mental']:3.0f} | OVR:{p['overall']:5.1f} {p['tier']}")

# ── I: INFER ──────────────────────────────────────────────────
print("\n[I] INFER: Top 20")
top20 = ratings.nlargest(20, "overall")
for i, (_, p) in enumerate(top20.iterrows()):
    print(f"  {i+1:2d}. {p['player_name']:25s} {p['club']:20s} {p['position']:3s} OVR:{p['overall']:5.1f} {p['tier']}")

print("\n  TIER DISTRIBUTION:")
td = ratings["tier"].value_counts()
total = len(ratings)
for t in ["Mythic","Legendary","Elite","Gold","Silver","Bronze"]:
    c = td.get(t,0)
    print(f"    {t:10s} {c:4d} ({c/total*100:5.1f}%)")

# ── S: STORYFRAME ─────────────────────────────────────────────
print("\n[S] STORYFRAME")
out = Path("outputs/cards")
out.mkdir(parents=True, exist_ok=True)
ratings.to_json(out / "_all_cards_v2_merged.json", orient="records", indent=2, force_ascii=False)
top20.to_json(out / "_top20_v2_merged.json", orient="records", indent=2, force_ascii=False)
print(f"  Exported: {len(ratings)} cards")

print("\n" + "=" * 65)
print(f"  DONE: {len(ratings)} players, Mythic={td.get('Mythic',0)}, Legendary={td.get('Legendary',0)}")
print("=" * 65)
