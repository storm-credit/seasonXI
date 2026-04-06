"""Merge FBref + Understat and run HANESIS pipeline - multi-season.

Season discovery:
  - FBref league-split files  : {league}_{YYYY}_{YYYY}_players.csv  (HANESIS schema)
  - FBref all-leagues file    : all_leagues_{YYYY}_{YYYY}_players.csv (Kaggle schema)
  - FBref partial files       : {league}_{YYYY}_{YYYY}_players.csv with fewer columns
  - Understat                 : all_leagues_{YYYY}_{YYYY}.csv

Outputs:
  outputs/cards/_all_cards_v2_merged.json        (2021-22 only, backward-compat)
  outputs/cards/_all_cards_v3_multiseason.json   (all seasons combined)
"""
import io
import re
import glob
import json
import sys

# Force UTF-8 output so player names with accents print correctly on Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from pathlib import Path

import pandas as pd
from thefuzz import fuzz

from seasonxi.ratings.formula_v1 import ROLE_RATERS, STAT_NAMES
from seasonxi.ratings.confidence import compute_confidence
from seasonxi.constants import score_to_tier

# ── CONSTANTS ─────────────────────────────────────────────────
MIN_MINUTES = 900  # 10+ full games

LEAGUE_GAMES = {
    "epl": 38, "laliga": 38, "seriea": 38, "bundesliga": 34, "ligue1": 38,
}

# Understat league → internal league_id
US_LEAGUE_MAP = {
    "ENG-Premier League": "epl",
    "ESP-La Liga": "laliga",
    "ITA-Serie A": "seriea",
    "GER-Bundesliga": "bundesliga",
    "FRA-Ligue 1": "ligue1",
}

# Kaggle Comp column → internal league_id
COMP_TO_LEAGUE = {
    "eng Premier League": "epl",
    "es La Liga": "laliga",
    "it Serie A": "seriea",
    "de Bundesliga": "bundesliga",
    "fr Ligue 1": "ligue1",
}

# Internal league_id → file stem prefix (for per-league FBref files)
LEAGUE_STEMS = {"epl", "laliga", "seriea", "bundesliga", "ligue1"}

# ══════════════════════════════════════════════════════════════
#  SEASON DISCOVERY
# ══════════════════════════════════════════════════════════════

def _season_label(y1: str, y2: str) -> str:
    """Convert "2021", "2022" → "2021-22"."""
    return f"{y1}-{y2[-2:]}"


def discover_seasons(base: str = "data/raw") -> dict:
    """Scan data/raw/ and return a dict keyed by season label.

    Returns:
        {
          "2021-22": {
              "fbref_league_files": {"epl": Path, "laliga": Path, ...},
              "fbref_all_file": None | Path,          # Kaggle-style all-leagues
              "understat_file": None | Path,
          },
          ...
        }
    """
    seasons: dict = {}

    def _ensure(label):
        if label not in seasons:
            seasons[label] = {
                "fbref_league_files": {},
                "fbref_all_file": None,
                "understat_file": None,
            }

    # FBref per-league files  e.g. epl_2021_2022_players.csv
    for fpath in sorted(Path(base).glob("fbref/*_players.csv")):
        stem = fpath.stem  # e.g. "epl_2021_2022_players"
        # Must not start with "all_"
        if stem.startswith("all_"):
            continue
        parts = stem.split("_")
        # Expect: league_YYYY_YYYY_players  (parts[0]=league, [-2]=year1, [-1]="players")
        if len(parts) < 4:
            continue
        # Year tokens are the two consecutive 4-digit numbers before "players"
        m = re.search(r"_(\d{4})_(\d{4})_players$", stem)
        if not m:
            continue
        y1, y2 = m.group(1), m.group(2)
        league = stem[: stem.index(f"_{y1}")]
        if league not in LEAGUE_STEMS:
            continue
        label = _season_label(y1, y2)
        _ensure(label)
        seasons[label]["fbref_league_files"][league] = fpath

    # FBref all-leagues Kaggle files  e.g. all_leagues_2023_2024_players.csv
    for fpath in sorted(Path(base).glob("fbref/all_leagues_*_players.csv")):
        m = re.search(r"all_leagues_(\d{4})_(\d{4})_players", fpath.stem)
        if not m:
            continue
        label = _season_label(m.group(1), m.group(2))
        _ensure(label)
        seasons[label]["fbref_all_file"] = fpath

    # FBref Kaggle multi-season files  e.g. fbref_2017_18_all.csv
    for fpath in sorted(Path(base).glob("fbref/fbref_*_all.csv")):
        m = re.search(r"fbref_(\d{4})_(\d{2})_all", fpath.stem)
        if not m:
            continue
        y1 = m.group(1)
        y2_short = m.group(2)
        y2 = str(int(y1[:2] + y2_short))  # "2017" + "18" → "2018"
        label = _season_label(y1, y2)
        _ensure(label)
        if seasons[label]["fbref_all_file"] is None:
            seasons[label]["fbref_all_file"] = fpath

    # Understat  e.g. all_leagues_2021_2022.csv
    for fpath in sorted(Path(base).glob("understat/all_leagues_*.csv")):
        m = re.search(r"all_leagues_(\d{4})_(\d{4})", fpath.stem)
        if not m:
            continue
        label = _season_label(m.group(1), m.group(2))
        _ensure(label)
        seasons[label]["understat_file"] = fpath

    return seasons


# ══════════════════════════════════════════════════════════════
#  FBREF LOADING — handles three different schemas
# ══════════════════════════════════════════════════════════════

# Columns the pipeline requires downstream (filled with 0 if absent)
REQUIRED_COLS = [
    "player_name", "club_name", "primary_position", "league_id",
    "minutes_played", "goals", "assists", "shots", "key_passes",
    "progressive_passes", "progressive_carries", "successful_dribbles",
    "xg", "xa", "tackles", "interceptions", "clearances",
    "aerial_duels_won", "yellow_cards", "red_cards", "clean_sheets",
    "team_goals_scored", "team_goals_conceded", "team_points",
]


def _normalise_kaggle_row(df: pd.DataFrame) -> pd.DataFrame:
    """Map Kaggle / FBref all-leagues column names to HANESIS schema.

    Handles two variants:
      - Standard Kaggle CSV (comma-sep): Player, Squad, Min, Gls, Ast, xG, xAG, Comp
      - Rich FBref semicolon CSV (2022-23): Player, Squad, Goals, Assists, Min, Comp,
          Shots (via SoT columns), TklWon, Int, Clr, AerWon, CrdY, CrdR
    """
    col_map = {
        # Standard Kaggle
        "Player": "player_name",
        "Squad": "club_name",
        "Pos": "primary_position",
        "Min": "minutes_played",
        "Gls": "goals",
        "Ast": "assists",
        "xG": "xg",
        "xAG": "xa",
        "PrgP": "progressive_passes",
        "PrgC": "progressive_carries",
        "CrdY": "yellow_cards",
        "CrdR": "red_cards",
        # Rich FBref semicolon format (2022-23)
        "Goals": "goals",
        "Assists": "assists",
        "TklWon": "tackles",
        "Int": "interceptions",
        "Clr": "clearances",
        "AerWon": "aerial_duels_won",
        # Kaggle multi-season (2017-2024, akshankrithick)
        "player": "player_name",
        "squad": "club_name",
        "pos": "primary_position",
        "comp": "league_raw",
        "Matches Played": "appearances",
        "Avg Mins per Match": "avg_mins",
        "Expected Goals": "xg",
        "Progressive Passes": "progressive_passes",
        "Progressive Carries": "progressive_carries",
        "Tackles Won": "tackles",
        "Interceptions": "interceptions",
        "Clearances": "clearances",
        "Total Shots": "shots",
        "Key passes": "key_passes",
        "Goals & Assists": "goals_assists",
        "Non Penalty Goals": "npg",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # league_id from Comp column
    # Standard Kaggle: "eng Premier League" / Rich format: "Premier League"
    if "Comp" in df.columns:
        # Try standard map first, then strip prefix
        def _map_comp(val):
            if pd.isna(val):
                return None
            v = str(val).strip()
            if v in COMP_TO_LEAGUE:
                return COMP_TO_LEAGUE[v]
            # Rich format: may be just "Premier League", "La Liga" etc.
            for k, lid in COMP_TO_LEAGUE.items():
                # Match last word(s): "eng Premier League" -> "Premier League"
                if v in k or k.endswith(v):
                    return lid
            return None
        df["league_id"] = df["Comp"].apply(_map_comp)

    # league_id from league_raw (lowercase comp column from akshankrithick dataset)
    if "league_raw" in df.columns and "league_id" not in df.columns:
        def _map_league_raw(val):
            if pd.isna(val): return None
            v = str(val).strip()
            if v in COMP_TO_LEAGUE: return COMP_TO_LEAGUE[v]
            for k, lid in COMP_TO_LEAGUE.items():
                if v in k or k.endswith(v): return lid
            return None
        df["league_id"] = df["league_raw"].apply(_map_league_raw)

    # Fill stats the Kaggle file does not contain
    for col in ["shots", "key_passes", "successful_dribbles", "tackles",
                "interceptions", "clearances", "aerial_duels_won",
                "clean_sheets", "team_goals_scored", "team_goals_conceded", "team_points"]:
        if col not in df.columns:
            df[col] = 0.0

    # minutes_played: compute from avg_mins × appearances if missing
    if "minutes_played" not in df.columns or df["minutes_played"].isna().all():
        if "avg_mins" in df.columns and "appearances" in df.columns:
            df["avg_mins"] = pd.to_numeric(df["avg_mins"], errors="coerce").fillna(0)
            df["appearances"] = pd.to_numeric(df["appearances"], errors="coerce").fillna(0)
            df["minutes_played"] = (df["avg_mins"] * df["appearances"]).round(0)
            print(f"    [minutes] Computed from avg_mins × appearances")
        else:
            df["minutes_played"] = 0

    if "minutes_played" in df.columns:
        df["minutes_played"] = (
            df["minutes_played"].astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("N/A", "0", regex=False)
        )
        df["minutes_played"] = pd.to_numeric(df["minutes_played"], errors="coerce").fillna(0)

    return df


def _normalise_partial_row(df: pd.DataFrame) -> pd.DataFrame:
    """Handle minimal schema files (e.g. epl_2024_2025_players.csv)."""
    # Already close to HANESIS schema — just fill missing cols
    for col in ["shots", "key_passes", "successful_dribbles", "xg", "xa",
                "tackles", "interceptions", "clearances", "aerial_duels_won",
                "clean_sheets", "team_goals_scored", "team_goals_conceded", "team_points",
                "progressive_passes", "progressive_carries"]:
        if col not in df.columns:
            df[col] = 0.0
    return df


def load_fbref_season(info: dict, season_label: str) -> pd.DataFrame:
    """Load all FBref data for one season into a single normalised DataFrame."""
    dfs = []

    # --- per-league HANESIS files ---
    for league, fpath in info["fbref_league_files"].items():
        try:
            df = pd.read_csv(fpath)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(fpath, encoding="latin-1")
            except Exception as e:
                print(f"    SKIP {fpath.name}: {e}")
                continue
        except Exception as e:
            print(f"    SKIP {fpath.name}: {e}")
            continue

        # Detect if this is a TSV masquerading as CSV (epl_2023_2024 style)
        if len(df.columns) == 1 and "\t" in df.columns[0]:
            try:
                df = pd.read_csv(fpath, sep="\t")
            except Exception:
                pass

        # If it has Kaggle-style columns (some per-league files exported from Kaggle)
        if "Player" in df.columns and "Min" in df.columns:
            df = _normalise_kaggle_row(df)
        elif "player_name" not in df.columns:
            # Unknown / unusable format
            print(f"    SKIP {fpath.name}: unrecognised schema (cols={list(df.columns)[:5]})")
            continue
        else:
            df = _normalise_partial_row(df)

        if "league_id" not in df.columns:
            df["league_id"] = league

        df["season"] = season_label
        dfs.append(df)

    # --- Kaggle all-leagues file (only use for leagues not already loaded) ---
    if info["fbref_all_file"] is not None:
        already_loaded = set(info["fbref_league_files"].keys())
        try:
            # Try UTF-8 first, fall back to latin-1 for files with encoding issues
            try:
                kaggle = pd.read_csv(info["fbref_all_file"])
            except UnicodeDecodeError:
                kaggle = pd.read_csv(info["fbref_all_file"], encoding="latin-1")
            # Detect semicolon-separated files (one giant column header)
            if len(kaggle.columns) == 1 and ";" in kaggle.columns[0]:
                try:
                    kaggle = pd.read_csv(
                        info["fbref_all_file"], sep=";", encoding="latin-1"
                    )
                except Exception:
                    pass
            kaggle = _normalise_kaggle_row(kaggle)
            kaggle["season"] = season_label

            if already_loaded:
                # Only keep leagues not already covered by per-league files
                kaggle = kaggle[~kaggle["league_id"].isin(already_loaded)]
                if len(kaggle) > 0:
                    print(f"    Kaggle supplement for: {sorted(kaggle['league_id'].dropna().unique())}")
            else:
                print(f"    Using Kaggle all-leagues file exclusively")

            if len(kaggle) > 0:
                dfs.append(kaggle)

        except Exception as e:
            print(f"    WARN: Kaggle file {info['fbref_all_file'].name} failed: {e}")

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)

    # Ensure all required columns exist
    for col in REQUIRED_COLS:
        if col not in combined.columns:
            combined[col] = 0.0

    # Clean up numeric columns — cast to float64 to avoid dtype incompatibility later
    float_cols = ["minutes_played", "goals", "assists", "shots", "xg", "xa",
                  "key_passes", "tackles", "interceptions", "clearances",
                  "aerial_duels_won", "clean_sheets", "successful_dribbles",
                  "progressive_passes", "progressive_carries"]
    for col in float_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0).astype(float)

    # Drop rows with no name
    combined = combined[combined["player_name"].notna() & (combined["player_name"] != "")]
    # Drop duplicate header rows (Kaggle files sometimes embed them)
    combined = combined[combined["player_name"] != "Player"]

    return combined


# ══════════════════════════════════════════════════════════════
#  ALIGN (fuzzy match Understat → FBref)
# ══════════════════════════════════════════════════════════════

def normalize_name(name) -> str:
    if pd.isna(name):
        return ""
    return str(name).lower().strip()


def merge_understat(fbref: pd.DataFrame, us_path: Path) -> pd.DataFrame:
    """Fuzzy-match Understat xG/xA into fbref DataFrame in-place."""
    us = pd.read_csv(us_path)

    us_league_col = "league_name" if "league_name" in us.columns else "league"
    us["league_id"] = us[us_league_col].map(US_LEAGUE_MAP)

    matched = 0
    for idx, fb_row in fbref.iterrows():
        fb_name = normalize_name(fb_row["player_name"])
        fb_league = fb_row.get("league_id", "")

        us_league = us[us["league_id"] == fb_league]
        best_score = 0
        best_idx = None

        for us_idx, us_row in us_league.iterrows():
            score = fuzz.ratio(fb_name, normalize_name(us_row["player"]))
            if score > best_score:
                best_score = score
                best_idx = us_idx

        if best_score >= 80 and best_idx is not None:
            us_row = us.loc[best_idx]
            fbref.loc[idx, "xg"] = float(us_row["xg"])
            fbref.loc[idx, "xa"] = float(us_row["xa"])
            fbref.loc[idx, "key_passes"] = float(us_row["key_passes"])
            matched += 1

    print(f"    Understat matched: {matched}/{len(fbref)} ({matched/len(fbref)*100:.0f}%)")
    return fbref


# ══════════════════════════════════════════════════════════════
#  DEFENSE + SOFASCORE (optional supplementary data)
# ══════════════════════════════════════════════════════════════

def merge_defense(fbref: pd.DataFrame) -> pd.DataFrame:
    """Load fbref_extra defense files if present (2021-22 only typically)."""
    def_matched = 0
    for league_key in LEAGUE_STEMS:
        def_path = Path(f"data/raw/fbref_extra/{league_key}_defense.csv")
        if not def_path.exists():
            continue
        def_df = pd.read_csv(def_path)
        for _, def_row in def_df.iterrows():
            def_name = normalize_name(def_row["player_name"])
            league_mask = fbref["league_id"] == league_key
            for idx in fbref[league_mask].index:
                if fuzz.ratio(normalize_name(fbref.loc[idx, "player_name"]), def_name) >= 85:
                    fbref.loc[idx, "tackles"] = def_row.get("tackles_won", 0)
                    fbref.loc[idx, "interceptions"] = def_row.get("interceptions", 0)
                    def_matched += 1
                    break
    if def_matched:
        print(f"    Defense matched: {def_matched}")
    return fbref


def merge_sofascore(fbref: pd.DataFrame, season_label: str) -> pd.DataFrame:
    """Load Sofascore file matching this season if present."""
    # Try season-specific path first, then generic
    season_slug = season_label.replace("-", "_")
    candidates = [
        Path(f"data/raw/sofascore/sofascore_all_leagues_{season_slug}.csv"),
        Path("data/raw/sofascore/sofascore_all_leagues_2021_2022.csv"),
    ]
    sf_path = next((p for p in candidates if p.exists()), None)
    if sf_path is None:
        return fbref

    sf = pd.read_csv(sf_path, sep="~")
    print(f"    Sofascore: {len(sf)} rows from {sf_path.name}")

    for col in ["clearances", "successful_dribbles", "clean_sheets", "duels_won", "pass_completion_pct"]:
        if col not in fbref.columns:
            fbref[col] = 0.0
        else:
            fbref[col] = fbref[col].astype(float)

    sf_matched = 0
    for _, sf_row in sf.iterrows():
        sf_name = normalize_name(str(sf_row.get("player_name", "")))
        sf_league = str(sf_row.get("league", ""))
        league_mask = fbref["league_id"] == sf_league
        for idx in fbref[league_mask].index:
            if fuzz.ratio(normalize_name(fbref.loc[idx, "player_name"]), sf_name) >= 80:
                fbref.loc[idx, "clearances"] = float(sf_row.get("clearances", 0))
                fbref.loc[idx, "successful_dribbles"] = float(sf_row.get("dribbles", 0))
                fbref.loc[idx, "clean_sheets"] = float(sf_row.get("clean_sheets", 0))
                total_p = sf_row.get("total_passes", 0)
                if total_p and total_p > 0:
                    fbref.loc[idx, "pass_completion_pct"] = (
                        float(sf_row.get("accurate_passes", 0)) / total_p
                    )
                fbref.loc[idx, "duels_won"] = float(sf_row.get("duels_won", 0))
                sf_matched += 1
                break

    print(f"    Sofascore matched: {sf_matched}")
    return fbref


# ══════════════════════════════════════════════════════════════
#  NORMALIZE (per90, percentile, proxy)
# ══════════════════════════════════════════════════════════════

def classify_pos(row) -> str:
    """Multi-factor position classifier v3."""
    pos = row.get("primary_position", "")
    if pd.isna(pos):
        pos = ""
    pos = str(pos).upper().replace(",", "").replace("-", "").replace("/", "")

    goals = row.get("goals", 0) or 0
    xg = row.get("xg", 0) or 0
    assists = row.get("assists", 0) or 0
    minutes = row.get("minutes_played", 0) or 1
    goals_p90 = goals / (minutes / 90) if minutes > 0 else 0
    shots = row.get("shots", 0) or 0
    shots_p90 = shots / (minutes / 90) if minutes > 0 else 0
    dribbles = row.get("successful_dribbles", 0) or 0
    dribbles_p90 = dribbles / (minutes / 90) if minutes > 0 else 0

    if "GK" in pos:
        return "GK"
    if "FW" in pos:
        return "FW"
    if pos in ("DF", "CB", "LB", "RB", "WB"):
        return "DF"
    if "DF" in pos and "MF" in pos:
        if assists >= 5 or goals >= 3 or goals_p90 >= 0.15:
            return "MF"
        return "DF"
    if pos.startswith("DF") or ("DF" in pos and "MF" not in pos):
        return "DF"
    if pos.startswith("MF") or pos in ("AM", "CM", "CAM", "CDM", "LM", "RM"):
        fw_score = 0
        if goals >= 10:       fw_score += 2
        if goals >= 15:       fw_score += 1
        if xg >= 8:           fw_score += 2
        if xg >= 12:          fw_score += 1
        if goals_p90 >= 0.3:  fw_score += 2
        if goals_p90 >= 0.5:  fw_score += 1
        if shots_p90 >= 2.0:  fw_score += 1
        if dribbles_p90 >= 1.5: fw_score += 1
        return "FW" if fw_score >= 3 else "MF"
    return "MF"


FBREF_PCT_MAP = [
    ("goals_p90", "goals_pct_role"), ("xg_p90", "xg_pct_role"),
    ("shots_p90", "shots_pct_role"), ("goals_minus_xg_p90", "goals_minus_xg_pct_role"),
    ("assists_p90", "assists_pct_role"), ("xa_p90", "xa_pct_role"),
    ("key_passes_p90", "key_passes_pct_role"),
    ("tackles_p90", "tackles_pct_role"), ("interceptions_p90", "interceptions_pct_role"),
    ("aerial_duels_won_p90", "aerials_pct_role"),
]
SOFASCORE_PCT_MAP = [
    ("clearances_p90", "clearances_pct_role"),
    ("successful_dribbles_p90", "dribbles_pct_role"),
    ("duels_won_p90", "aerial_duel_success_pct_role"),
    ("clean_sheets_p90", "clean_sheets_pct_role"),
]
DF_GK_ONLY = {"clearances_pct_role", "aerials_pct_role", "clean_sheets_pct_role"}

PROXY_COLS = [
    "prog_passes_pct_role", "prog_carries_pct_role", "dribbles_pct_role",
    "pass_completion_pct_role", "pressures_pct_role", "pressure_success_pct_role",
    "aerial_duel_success_pct_role", "ball_recoveries_pct_role",
    "gk_saves_pct_role", "gk_psxg_diff_pct_role", "gk_crosses_stopped_pct_role",
    "gk_pass_completion_pct_role", "gk_launch_pct_role",
    "clearances_pct_role", "aerials_pct_role",
]


def normalize_season(filtered: pd.DataFrame) -> pd.DataFrame:
    """Apply per90, percentile ranking, and proxy filling to one season's data."""
    # Per90
    stats_p90 = ["goals", "assists", "shots", "key_passes", "xg", "xa",
                 "tackles", "interceptions", "clearances", "aerial_duels_won",
                 "clean_sheets", "successful_dribbles", "duels_won"]
    for s in stats_p90:
        if s in filtered.columns:
            filtered[f"{s}_p90"] = (
                filtered[s].fillna(0) / (filtered["minutes_played"] / 90)
            )

    filtered["goals_minus_xg_p90"] = (
        filtered.get("goals_p90", pd.Series(0, index=filtered.index))
        - filtered.get("xg_p90", pd.Series(0, index=filtered.index))
    )

    # Context
    filtered["team_goal_contribution"] = (
        (filtered["goals"].fillna(0) + filtered["assists"].fillna(0))
        / filtered["team_goals_scored"].clip(lower=1)
    ).clip(0, 1)
    filtered["max_pts"] = filtered["league_id"].map(
        lambda x: LEAGUE_GAMES.get(x, 38) * 3
    )
    filtered["team_success_pct"] = (
        filtered["team_points"] / filtered["max_pts"]
    ).clip(0, 1)
    filtered["minutes_share"] = filtered["minutes_played"] / (
        filtered["league_id"].map(lambda x: LEAGUE_GAMES.get(x, 38)) * 90
    )

    # Percentiles within role
    if "pass_completion_pct" in filtered.columns:
        filtered["pass_completion_pct_role"] = (
            filtered.groupby("role_bucket")["pass_completion_pct"]
            .rank(pct=True).fillna(0.5)
        )

    for src, dst in FBREF_PCT_MAP:
        if src in filtered.columns:
            filtered[dst] = (
                filtered.groupby("role_bucket")[src].rank(pct=True).fillna(0.5)
            )
        else:
            filtered[dst] = 0.5

    df_gk_mask = filtered["role_bucket"].isin(["DF", "GK"])
    # Zero out DF/GK-only stats for FW/MF first
    for pct_col in DF_GK_ONLY:
        if pct_col in filtered.columns:
            filtered.loc[~df_gk_mask, pct_col] = 0.0

    for stat, pct_col in SOFASCORE_PCT_MAP:
        if stat in filtered.columns:
            real_pct = filtered.groupby("role_bucket")[stat].rank(pct=True)
            has_data = filtered[stat] > 0
            if pct_col in DF_GK_ONLY:
                filtered[pct_col] = 0.0
                override_mask = has_data & df_gk_mask
                filtered.loc[override_mask, pct_col] = real_pct[override_mask]
            else:
                filtered[pct_col] = 0.5
                filtered.loc[has_data, pct_col] = real_pct[has_data]
        else:
            filtered[pct_col] = 0.0 if pct_col in DF_GK_ONLY else 0.5

    if "aerials_pct_role" in filtered.columns:
        filtered.loc[~df_gk_mask, "aerials_pct_role"] = 0.0

    # Proxy fill
    for col in PROXY_COLS:
        if col not in filtered.columns:
            filtered[col] = float("nan")
        needs_proxy = filtered[col].isna() | (filtered[col] == 0.5)
        if not needs_proxy.any():
            continue

        if "prog" in col and "key_passes_pct_role" in filtered.columns:
            filtered.loc[needs_proxy, col] = filtered.loc[needs_proxy, "key_passes_pct_role"]
        elif "dribble" in col:
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
                return min(1.0, r.get("assists_pct_role", 0.5) * 0.7
                           + r.get("key_passes_pct_role", 0.5) * 0.3)
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_pass_comp_proxy, axis=1)
        elif "ball_rec" in col:
            icp = filtered.get("interceptions_pct_role", pd.Series(0.5, index=filtered.index))
            tck = filtered.get("tackles_pct_role", pd.Series(0.5, index=filtered.index))
            filtered.loc[needs_proxy, col] = icp[needs_proxy] * 0.6 + tck[needs_proxy] * 0.4
        elif "aerial" in col and "clearances" not in col:
            def _aerial_proxy(r):
                if r["role_bucket"] == "DF":
                    return min(1.0, r.get("interceptions_pct_role", 0.5) * 0.7
                               + r.get("tackles_pct_role", 0.5) * 0.3)
                return min(1.0, r.get("goals_pct_role", 0.5) * 0.3 + 0.3)
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_aerial_proxy, axis=1)
        elif "clearances" in col:
            def _clearances_proxy(r):
                if r["role_bucket"] in ["DF", "GK"]:
                    return (r.get("interceptions_pct_role", 0.5) * 0.8
                            + r.get("tackles_pct_role", 0.5) * 0.2)
                return 0.3
            filtered.loc[needs_proxy, col] = filtered[needs_proxy].apply(_clearances_proxy, axis=1)
        elif "gk" in col and "clean_sheets_pct_role" in filtered.columns:
            filtered.loc[needs_proxy, col] = filtered.loc[needs_proxy, "clean_sheets_pct_role"]
        else:
            filtered.loc[needs_proxy, col] = 0.5

    return filtered


# ══════════════════════════════════════════════════════════════
#  EVALUATE
# ══════════════════════════════════════════════════════════════

def evaluate_season(filtered: pd.DataFrame, season_label: str) -> pd.DataFrame:
    """Run HANESIS E-stage and return a ratings DataFrame."""
    from seasonxi.ratings.league_adjustment import get_league_multiplier

    results = []
    for _, row in filtered.iterrows():
        role = row["role_bucket"]
        rater = ROLE_RATERS.get(role)
        if not rater:
            continue
        conf = compute_confidence(int(row["minutes_played"]))
        scores = rater(row, conf)
        league_mult = get_league_multiplier(str(row.get("league_id", "")))
        ovr_raw = scores["overall"]
        scores["overall"] = max(50.0, min(99.0, 50 + (ovr_raw - 50) * league_mult))
        tier = score_to_tier(scores["overall"]).value

        results.append({
            "player_name": row["player_name"],
            "club": row["club_name"],
            "league": row["league_id"],
            "position": role,
            "season": season_label,
            "minutes": int(row["minutes_played"]),
            "goals": int(row.get("goals", 0)),
            "assists": int(row.get("assists", 0)),
            "xg": round(float(row.get("xg", 0)), 1),
            "xa": round(float(row.get("xa", 0)), 1),
            **{d: round(scores[d], 1) for d in STAT_NAMES},
            "overall": round(scores["overall"], 1),
            "confidence": round(conf, 3),
            "tier": tier,
        })

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════
#  VALIDATE / INFER helpers
# ══════════════════════════════════════════════════════════════

KNOWN_PLAYERS = [
    "Salah", "Son", "Benzema", "Lewandowski", "De Bruyne", "Van Dijk",
    "Mbappe", "Kane", "Modric", "Haaland",
]


def validate_known(ratings: pd.DataFrame, season: str) -> None:
    if ratings.empty or "player_name" not in ratings.columns:
        print("    (no players rated)")
        return
    for name in KNOWN_PLAYERS:
        m = ratings[ratings["player_name"].str.contains(name, case=False, na=False)]
        if len(m) == 0:
            continue  # Not every player appears in every season
        p = m.iloc[0]
        try:
            print(
                f"    {p['player_name']:25s} {p['position']:3s} "
                f"ATT:{p['att']:3.0f} DEF:{p['def']:3.0f} PAC:{p['pace']:3.0f} "
                f"AUR:{p['aura']:3.0f} STA:{p['stamina']:3.0f} MEN:{p['mental']:3.0f} "
                f"| OVR:{p['overall']:5.1f} {p['tier']}"
            )
        except (UnicodeEncodeError, KeyError):
            print(f"    {str(p['player_name'])[:24]} OVR:{p.get('overall', 0):5.1f} {p.get('tier', '?')}")


def print_tier_distribution(ratings: pd.DataFrame) -> None:
    td = ratings["tier"].value_counts()
    total = len(ratings)
    for t in ["Mythic", "Legendary", "Elite", "Gold", "Silver", "Bronze"]:
        c = td.get(t, 0)
        print(f"    {t:10s} {c:4d} ({c/total*100:5.1f}%)")


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  HANESIS PIPELINE - FBref + Understat MULTI-SEASON")
    print("=" * 65)

    seasons = discover_seasons()
    print(f"\nDiscovered seasons: {sorted(seasons.keys())}")

    all_ratings: list[pd.DataFrame] = []
    ratings_2122: pd.DataFrame | None = None

    for season_label in sorted(seasons.keys()):
        info = seasons[season_label]
        print(f"\n{'-'*65}")
        print(f"  SEASON: {season_label}")
        print(f"{'-'*65}")

        # ── H: HARVEST ──────────────────────────────────────────
        print("\n  [H] HARVEST")
        fbref = load_fbref_season(info, season_label)

        if fbref.empty:
            print(f"    No FBref data - skipping {season_label}")
            continue

        print(f"    FBref raw: {len(fbref)} rows | leagues: {sorted(fbref['league_id'].dropna().unique())}")

        # ── A: ALIGN ────────────────────────────────────────────
        print("\n  [A] ALIGN")
        if info["understat_file"] is not None:
            fbref = merge_understat(fbref, info["understat_file"])
        else:
            print("    Understat: no file - using FBref xG/xA as-is")

        # Optional supplementary data
        print("  [A] Loading supplementary data...")
        fbref = merge_defense(fbref)
        fbref = merge_sofascore(fbref, season_label)

        # ── N: NORMALIZE ────────────────────────────────────────
        print("\n  [N] NORMALIZE")
        filtered = fbref[fbref["minutes_played"] >= MIN_MINUTES].copy()
        print(f"    After {MIN_MINUTES}min filter: {len(filtered)}")

        filtered["role_bucket"] = filtered.apply(classify_pos, axis=1)
        role_counts = filtered["role_bucket"].value_counts().to_dict()
        print(f"    Roles: {role_counts}")

        filtered = normalize_season(filtered)
        pct_cols = [c for c in filtered.columns if c.endswith("_pct_role")]
        print(f"    Features: {len(pct_cols)} percentiles computed")

        # ── E: EVALUATE ─────────────────────────────────────────
        print("\n  [E] EVALUATE")
        ratings = evaluate_season(filtered, season_label)
        print(f"    Rated: {len(ratings)} players")

        # ── S: VALIDATE ─────────────────────────────────────────
        print("\n  [S] VALIDATE (known players):")
        validate_known(ratings, season_label)

        # ── I: INFER ────────────────────────────────────────────
        print(f"\n  [I] INFER: Top 10 for {season_label}")
        if not ratings.empty:
            top10 = ratings.nlargest(10, "overall")
            for i, (_, p) in enumerate(top10.iterrows()):
                try:
                    name_str = str(p['player_name'])
                    club_str = str(p['club'])
                    print(f"    {i+1:2d}. {name_str:25s} {club_str:20s} "
                          f"{p['position']:3s} OVR:{p['overall']:5.1f} {p['tier']}")
                except UnicodeEncodeError:
                    print(f"    {i+1:2d}. [encoding error] OVR:{p['overall']:5.1f} {p['tier']}")
        else:
            print("    (no players rated)")

        print(f"\n  TIER DISTRIBUTION ({season_label}):")
        print_tier_distribution(ratings)

        if not ratings.empty:
            all_ratings.append(ratings)
        if season_label == "2021-22" and not ratings.empty:
            ratings_2122 = ratings

    # ── S: STORYFRAME ─────────────────────────────────────────
    print(f"\n{'='*65}")
    print("  [S] STORYFRAME - export")

    out = Path("outputs/cards")
    out.mkdir(parents=True, exist_ok=True)

    # Backward-compat: 2021-22 only
    if ratings_2122 is not None and len(ratings_2122) > 0:
        td_2122 = ratings_2122["tier"].value_counts()
        ratings_2122.to_json(
            out / "_all_cards_v2_merged.json",
            orient="records", indent=2, force_ascii=False,
        )
        top20_2122 = ratings_2122.nlargest(20, "overall")
        top20_2122.to_json(
            out / "_top20_v2_merged.json",
            orient="records", indent=2, force_ascii=False,
        )
        print(f"  v2 (2021-22): {len(ratings_2122)} cards -> _all_cards_v2_merged.json")
    else:
        print("  v2 (2021-22): no data found - skipped")

    # Multi-season export
    if all_ratings:
        combined = pd.concat(all_ratings, ignore_index=True)
        combined.to_json(
            out / "_all_cards_v3_multiseason.json",
            orient="records", indent=2, force_ascii=False,
        )
        print(f"  v3 (all seasons): {len(combined)} cards -> _all_cards_v3_multiseason.json")

        print(f"\n  SEASON SUMMARY:")
        season_counts = combined.groupby("season").agg(
            players=("player_name", "count"),
            mythic=("tier", lambda x: (x == "Mythic").sum()),
            legendary=("tier", lambda x: (x == "Legendary").sum()),
            elite=("tier", lambda x: (x == "Elite").sum()),
        ).reset_index()
        for _, row in season_counts.iterrows():
            print(f"    {row['season']}: {row['players']:4d} players | "
                  f"Mythic={row['mythic']} Legendary={row['legendary']} Elite={row['elite']}")

        td_all = combined["tier"].value_counts()
        print(f"\n  GLOBAL TIER DISTRIBUTION ({len(combined)} players):")
        print_tier_distribution(combined)

        total_m = td_all.get("Mythic", 0)
        total_l = td_all.get("Legendary", 0)
        print(f"\n  DONE: {len(combined)} players across {len(all_ratings)} seasons, "
              f"Mythic={total_m}, Legendary={total_l}")
    else:
        print("  No ratings produced.")

    print("=" * 65)


if __name__ == "__main__":
    main()
