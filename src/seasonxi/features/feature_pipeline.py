"""End-to-end feature pipeline: raw stats → per90 → percentiles → features table."""

import duckdb
import pandas as pd

from seasonxi.db.connection import get_connection
from seasonxi.features.per90 import compute_per90
from seasonxi.features.percentiles import compute_percentiles


def build_features(conn: duckdb.DuckDBPyConnection | None = None) -> pd.DataFrame:
    """Load raw stats, compute per90 + percentiles, store in features table."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    # Read raw stats
    raw = conn.execute("SELECT * FROM player_season_stats_raw").fetchdf()
    if raw.empty:
        print("No raw stats found. Run seed first.")
        return raw

    # Step 0.5: Fix position mapping
    # FBref uses "MF,FW" etc. — map to primary bucket based on goals/role
    raw["primary_position"] = raw.apply(_fix_position, axis=1)

    # Step 1: per90
    features = compute_per90(raw, min_minutes=450)

    # Step 1.5: If xG is 0 for everyone, use goals as proxy
    if features["xg"].sum() == 0:
        features["xg"] = features["goals"]  # fallback
        features["xg_p90"] = features["goals_p90"]
    if features["xa"].sum() == 0:
        features["xa"] = features["assists"]  # fallback
        features["xa_p90"] = features["assists_p90"]

    # Step 2: league metadata (actual adjustment applied in formula_v1.py)
    # v1.2: removed league_factors here to avoid double-application
    clubs = conn.execute("SELECT club_id, league_name, league_id FROM clubs").fetchdf()
    features = features.merge(clubs[["club_id", "league_name", "league_id"]], on="club_id", how="left")
    features["league_strength_factor"] = 1.0  # Applied in ratings, not here
    features["season_era_factor"] = 1.0  # V1: neutral

    # Step 3: percentiles within role
    features = compute_percentiles(features, group_col="primary_position")

    # Step 4: team success proxy
    teams = conn.execute("SELECT * FROM team_season_stats_raw").fetchdf()
    if not teams.empty:
        team_map = teams.set_index(["club_id", "season_id"])
        features["team_success_pct"] = features.apply(
            lambda r: _team_success(r, team_map), axis=1
        )
    else:
        features["team_success_pct"] = 0.5

    # Store features
    _store_features(conn, features)

    if own_conn:
        conn.close()

    return features


def _fix_position(row: pd.Series) -> str:
    """Fix FBref multi-position labels to single bucket.

    Logic: If a player has many goals relative to their position group,
    they're likely an attacker even if FBref labels them MF,FW.
    """
    pos = str(row.get("primary_position", "FW")).upper().strip()
    goals = int(row.get("goals", 0))
    minutes = int(row.get("minutes_played", 0))

    if "GK" in pos:
        return "GK"

    # Multi-position: decide based on stats
    if "," in pos or "/" in pos:
        parts = [p.strip() for p in pos.replace("/", ",").split(",")]
        if "GK" in parts:
            return "GK"
        if "FW" in parts:
            # If they score goals, they're a FW
            if goals >= 3 or (minutes > 0 and goals / max(1, minutes) * 90 > 0.15):
                return "FW"
            # Low-scoring FW/MF -> MF
            if "MF" in parts:
                return "MF"
            return "FW"
        if "DF" in parts and "MF" in parts:
            return "DF"
        return parts[0]

    if "DF" in pos:
        return "DF"
    if "MF" in pos:
        return "MF"
    if "FW" in pos:
        return "FW"
    return "FW"


# League match counts (v1.2: no more hardcoded 38)
LEAGUE_MATCHES: dict[str, int] = {
    "ENG1": 38,  # Premier League
    "ESP1": 38,  # La Liga
    "ITA1": 38,  # Serie A
    "FRA1": 38,  # Ligue 1
    "GER1": 34,  # Bundesliga (18 teams)
}
DEFAULT_MATCHES = 38


def _team_success(row: pd.Series, team_map: pd.DataFrame) -> float:
    """Team success score: points / max_possible.

    v1.2: league-aware match count (Bundesliga=34, others=38).
    """
    key = (row["club_id"], row["season_id"])
    if key in team_map.index:
        team = team_map.loc[key]
        points = team["points"] if "points" in team.index else 0
        league_id = str(row.get("league_id", ""))
        matches = LEAGUE_MATCHES.get(league_id, DEFAULT_MATCHES)
        max_points = matches * 3
        return min(1.0, float(points) / max_points)
    return 0.5


def _store_features(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    """Insert features into player_season_features table."""
    feature_cols = [
        "player_season_id", "player_id", "club_id", "season_id",
        "minutes_played", "appearances",
        "goals_p90", "assists_p90", "xg_p90", "xa_p90", "shots_p90",
        "key_passes_p90", "prog_passes_p90", "prog_carries_p90", "dribbles_p90",
        "tackles_p90", "interceptions_p90", "clearances_p90", "aerials_won_p90",
        "goal_involvement_per90", "team_goal_contribution", "minutes_share",
        "league_strength_factor", "season_era_factor",
        "goals_pct_role", "assists_pct_role", "xg_pct_role", "xa_pct_role",
        "shots_pct_role", "key_passes_pct_role", "prog_passes_pct_role",
        "prog_carries_pct_role", "dribbles_pct_role",
        "tackles_pct_role", "interceptions_pct_role", "clearances_pct_role",
        "aerials_pct_role",
    ]

    for _, row in df.iterrows():
        role = row.get("primary_position", "FW")
        values = [row.get(c, 0) for c in feature_cols]
        placeholders = ", ".join(["?"] * (len(feature_cols) + 1))
        col_str = ", ".join(feature_cols + ["role_bucket"])
        conn.execute(
            f"INSERT OR REPLACE INTO player_season_features ({col_str}) VALUES ({placeholders})",
            values + [role],
        )
