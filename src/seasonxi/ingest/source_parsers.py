"""Auto-collect player stats from FBref and Understat."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import soccerdata as sd
from loguru import logger

# FBref stat types to collect
FBREF_STAT_TYPES = [
    "standard",
    "shooting",
    "passing",
    "defense",
    "possession",
    "misc",
]

# League mapping: our ID -> soccerdata ID
LEAGUE_MAP = {
    "ENG1": "ENG-Premier League",
    "ESP1": "ESP-La Liga",
    "GER1": "GER-Bundesliga",
    "ITA1": "ITA-Serie A",
    "FRA1": "FRA-Ligue 1",
}

# League name mapping
LEAGUE_NAMES = {
    "ENG1": "Premier League",
    "ESP1": "La Liga",
    "GER1": "Bundesliga",
    "ITA1": "Serie A",
    "FRA1": "Ligue 1",
}


def fetch_fbref_season(
    league_id: str,
    season: int,
    cache_dir: Path = Path("data/raw/fbref"),
) -> pd.DataFrame:
    """Fetch all player stats for a league-season from FBref.

    Args:
        league_id: Our league ID (e.g., "ENG1")
        season: The starting year (e.g., 2021 for 2021-22)
        cache_dir: Where to cache parquet files

    Returns:
        Merged DataFrame with all stat types combined
    """
    sd_league = LEAGUE_MAP.get(league_id)
    if not sd_league:
        raise ValueError(f"Unknown league: {league_id}")

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{league_id}_{season}_{season+1}_merged.parquet"

    if cache_file.exists():
        logger.info(f"Loading cached: {cache_file}")
        return pd.read_parquet(cache_file)

    logger.info(f"Fetching FBref: {sd_league} {season}")
    fbref = sd.FBref(leagues=sd_league, seasons=season)

    dfs = {}
    for stat_type in FBREF_STAT_TYPES:
        try:
            logger.info(f"  Fetching {stat_type}...")
            df = fbref.read_player_season_stats(stat_type=stat_type)
            if not df.empty:
                dfs[stat_type] = df
        except Exception as e:
            logger.warning(f"  Failed to fetch {stat_type}: {e}")

    if not dfs:
        logger.error("No data fetched!")
        return pd.DataFrame()

    # Merge all stat types
    merged = dfs["standard"].copy() if "standard" in dfs else pd.DataFrame()
    for stat_type, df in dfs.items():
        if stat_type == "standard":
            continue
        # Only add columns that don't already exist (except index cols)
        new_cols = [c for c in df.columns if c not in merged.columns]
        if new_cols:
            merged = merged.join(df[new_cols], how="left")

    # Save cache
    merged.to_parquet(cache_file)
    logger.info(f"Cached: {cache_file} ({len(merged)} players)")

    return merged


def fbref_to_raw_stats(
    df: pd.DataFrame,
    league_id: str,
    season: int,
) -> pd.DataFrame:
    """Convert FBref DataFrame to our raw stats format.

    FBref data has MultiIndex columns — this flattens and maps them.
    """
    # Reset index to get player info as columns
    flat = df.reset_index()

    # FBref column names vary — map common ones
    col_map = _build_column_map(flat.columns)

    out = pd.DataFrame()
    season_id = f"{season}-{season+1}"
    season_label = f"{season}/{str(season+1)[-2:]}"
    league_name = LEAGUE_NAMES.get(league_id, "Unknown")

    out["player_name"] = flat.get(col_map.get("player", "player"), "Unknown")
    out["player_id"] = out["player_name"].apply(_slugify)
    out["club_name"] = flat.get(col_map.get("team", "team"), "Unknown")
    out["club_id"] = out["club_name"].apply(_slugify)
    out["season_id"] = season_id
    out["season_label"] = season_label
    out["league_name"] = league_name
    out["player_season_id"] = out["player_id"] + "-" + out["club_id"] + "-" + season_id

    # Position
    pos_col = col_map.get("position", "Pos")
    if pos_col in flat.columns:
        out["primary_position"] = flat[pos_col].apply(_map_position)
    else:
        out["primary_position"] = "FW"

    # Stats mapping
    stat_mappings = {
        "appearances": ["MP", "Playing Time_MP", "matches_played"],
        "starts": ["Starts", "Playing Time_Starts"],
        "minutes_played": ["Min", "Playing Time_Min", "minutes"],
        "goals": ["Gls", "Performance_Gls"],
        "assists": ["Ast", "Performance_Ast"],
        "shots": ["Sh", "Standard_Sh"],
        "shots_on_target": ["SoT", "Standard_SoT"],
        "key_passes": ["KP", "KP_KP"],
        "progressive_passes": ["PrgP", "Progression_PrgP"],
        "progressive_carries": ["PrgC", "Progression_PrgC"],
        "successful_dribbles": ["Succ", "Take-Ons_Succ"],
        "xg": ["xG", "Expected_xG"],
        "xa": ["xAG", "Expected_xAG", "xA"],
        "tackles": ["Tkl", "Tackles_Tkl"],
        "interceptions": ["Int", "Int_Int"],
        "clearances": ["Clr", "Clr_Clr"],
        "aerial_duels_won": ["Won", "Aerial Duels_Won"],
        "yellow_cards": ["CrdY", "Performance_CrdY"],
        "red_cards": ["CrdR", "Performance_CrdR"],
    }

    for our_col, candidates in stat_mappings.items():
        out[our_col] = _find_col(flat, candidates, default=0)

    # Clean minutes (remove commas)
    if "minutes_played" in out.columns:
        out["minutes_played"] = (
            out["minutes_played"]
            .astype(str)
            .str.replace(",", "")
            .str.replace(".", "")
            .apply(lambda x: int(x) if x.isdigit() else 0)
        )

    out["source_name"] = "fbref"
    out["competition_scope"] = "league_only"

    return out


def _build_column_map(columns) -> dict:
    """Map FBref's multi-level or flat column names to standard names."""
    col_map = {}
    flat_cols = []
    for c in columns:
        if isinstance(c, tuple):
            flat_cols.append("_".join(str(x) for x in c))
        else:
            flat_cols.append(str(c))

    # Try to find player name column
    for candidate in ["player", "Player", "player_Player"]:
        if candidate in flat_cols or candidate in columns:
            col_map["player"] = candidate
            break

    for candidate in ["team", "squad", "Squad", "team_Squad"]:
        if candidate in flat_cols or candidate in columns:
            col_map["team"] = candidate
            break

    for candidate in ["Pos", "position", "pos"]:
        if candidate in flat_cols or candidate in columns:
            col_map["position"] = candidate
            break

    return col_map


def _find_col(df: pd.DataFrame, candidates: list[str], default=0):
    """Find the first matching column from candidates."""
    for col in candidates:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce").fillna(default)
        # Try flattened multi-index name
        for actual_col in df.columns:
            if isinstance(actual_col, tuple):
                joined = "_".join(str(x) for x in actual_col)
                if joined == col or col in joined:
                    return pd.to_numeric(df[actual_col], errors="coerce").fillna(default)
    return default


def _map_position(pos: str) -> str:
    """Map FBref position to our 4-bucket system."""
    if pd.isna(pos):
        return "FW"
    pos = str(pos).upper()
    if "GK" in pos:
        return "GK"
    if "DF" in pos or "CB" in pos or "FB" in pos:
        return "DF"
    if "MF" in pos or "DM" in pos or "CM" in pos or "AM" in pos:
        return "MF"
    return "FW"


def _slugify(name: str) -> str:
    """Create a URL-safe slug from a name."""
    if pd.isna(name):
        return "unknown"
    from unidecode import unidecode
    slug = unidecode(str(name)).lower()
    slug = slug.replace(" ", "-").replace(".", "").replace("'", "")
    # Remove consecutive hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")
