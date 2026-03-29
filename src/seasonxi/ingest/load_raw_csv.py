"""Load raw CSV seed data into DuckDB."""

from pathlib import Path

import duckdb
import pandas as pd

from seasonxi.db.connection import get_connection, init_schema


def load_seed_data(
    players_csv: Path = Path("data/raw/seed_players.csv"),
    teams_csv: Path = Path("data/raw/seed_teams.csv"),
    conn: duckdb.DuckDBPyConnection | None = None,
) -> None:
    """Load seed CSVs into DuckDB raw tables."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    init_schema(conn)

    # Load players
    pdf = pd.read_csv(players_csv)
    _upsert_players(conn, pdf)
    _upsert_clubs(conn, pdf)
    _upsert_seasons(conn, pdf)
    _upsert_player_season_stats(conn, pdf)

    # Load teams
    tdf = pd.read_csv(teams_csv)
    _upsert_team_season_stats(conn, tdf)

    if own_conn:
        conn.close()


def _upsert_players(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    players = df[["player_id", "player_name"]].drop_duplicates()
    for _, row in players.iterrows():
        conn.execute(
            """INSERT OR REPLACE INTO players (player_id, player_name)
               VALUES (?, ?)""",
            [row["player_id"], row["player_name"]],
        )


def _upsert_clubs(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    clubs = df[["club_id", "club_name", "league_name"]].drop_duplicates(subset=["club_id"])
    for _, row in clubs.iterrows():
        conn.execute(
            """INSERT OR REPLACE INTO clubs (club_id, club_name, league_name)
               VALUES (?, ?, ?)""",
            [row["club_id"], row["club_name"], row["league_name"]],
        )


def _upsert_seasons(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    seasons = df[["season_id", "season_label"]].drop_duplicates()
    for _, row in seasons.iterrows():
        parts = row["season_id"].split("-")
        conn.execute(
            """INSERT OR REPLACE INTO seasons (season_id, season_label, start_year, end_year)
               VALUES (?, ?, ?, ?)""",
            [row["season_id"], row["season_label"], int(parts[0]), int(parts[1])],
        )


def _upsert_player_season_stats(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    cols = [
        "player_season_id", "player_id", "club_id", "season_id",
        "primary_position", "appearances", "starts", "minutes_played",
        "goals", "assists", "shots", "shots_on_target",
        "key_passes", "progressive_passes", "progressive_carries", "successful_dribbles",
        "xg", "xa", "tackles", "interceptions", "clearances", "aerial_duels_won",
        "yellow_cards", "red_cards", "clean_sheets",
        "team_goals_scored", "team_goals_conceded",
    ]
    for _, row in df.iterrows():
        values = [row.get(c, 0) for c in cols]
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        conn.execute(
            f"""INSERT OR REPLACE INTO player_season_stats_raw
                ({col_names}, competition_scope, source_name)
                VALUES ({placeholders}, 'league_only', 'manual')""",
            values,
        )


def _upsert_team_season_stats(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        conn.execute(
            """INSERT OR REPLACE INTO team_season_stats_raw
               (team_season_id, club_id, season_id, competition_scope,
                matches_played, team_goals, team_goals_conceded, points,
                final_table_rank, wins, draws, losses)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                row["team_season_id"], row["club_id"], row["season_id"],
                row["competition_scope"], row["matches_played"],
                row["team_goals"], row["team_goals_conceded"], row["points"],
                row["final_table_rank"], row["wins"], row["draws"], row["losses"],
            ],
        )


if __name__ == "__main__":
    load_seed_data()
    print("Seed data loaded successfully.")
