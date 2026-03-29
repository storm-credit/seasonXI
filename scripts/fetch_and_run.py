"""Fetch real FBref data and run the full pipeline.

Usage:
    uv run python scripts/fetch_and_run.py --league ENG1 --season 2021
    uv run python scripts/fetch_and_run.py --all-big5 --season 2021
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console

from seasonxi.content.card_exporter import export_cards
from seasonxi.db.connection import get_connection, init_schema
from seasonxi.features.feature_pipeline import build_features
from seasonxi.ingest.source_parsers import LEAGUE_MAP, fetch_fbref_season, fbref_to_raw_stats
from seasonxi.ratings.formula_v1 import compute_ratings

console = Console()


def main():
    parser = argparse.ArgumentParser(description="SeasonXI: Fetch and Rate")
    parser.add_argument("--league", type=str, default="ENG1", help="League ID (ENG1, ESP1, etc.)")
    parser.add_argument("--season", type=int, required=True, help="Start year (e.g., 2021)")
    parser.add_argument("--all-big5", action="store_true", help="Fetch all 5 major leagues")
    args = parser.parse_args()

    conn = get_connection()
    init_schema(conn)

    leagues = list(LEAGUE_MAP.keys()) if args.all_big5 else [args.league]

    for league_id in leagues:
        console.print(f"\n[bold blue]Fetching {league_id} {args.season}-{args.season+1}...[/]")

        # Step 1: Fetch from FBref
        raw_df = fetch_fbref_season(league_id, args.season)
        if raw_df.empty:
            console.print(f"  [red]No data for {league_id}[/]")
            continue

        console.print(f"  -> {len(raw_df)} players fetched")

        # Step 2: Convert to our format
        stats_df = fbref_to_raw_stats(raw_df, league_id, args.season)
        console.print(f"  -> {len(stats_df)} player records converted")

        # Step 3: Load into DB
        _load_to_db(conn, stats_df, league_id, args.season)

    # Step 4: Build features
    console.print("\n[bold blue]Building features...[/]")
    features_df = build_features(conn=conn)
    console.print(f"  -> {len(features_df)} features computed")

    # Step 5: Compute ratings
    console.print("[bold blue]Computing ratings...[/]")
    ratings_df = compute_ratings(features_df)
    console.print(f"  -> {len(ratings_df)} ratings computed")

    # Step 6: Store ratings
    _store_ratings(conn, ratings_df)

    # Step 7: Export cards
    console.print("[bold blue]Exporting cards...[/]")
    cards = export_cards(conn=conn)
    console.print(f"  -> {len(cards)} cards exported to outputs/cards/")

    # Show top 20
    console.print("\n[bold yellow]Top 20 Players:[/]")
    for i, c in enumerate(sorted(cards, key=lambda x: x["overall"], reverse=True)[:20], 1):
        console.print(
            f"  {i:2d}. {c['player']:25s} | {c['season']:9s} | {c['club']:20s} | "
            f"OVR {c['overall']:2d} | {c['tier']}"
        )

    conn.close()


def _load_to_db(conn, stats_df, league_id, season):
    """Insert fetched data into DuckDB."""
    import pandas as pd

    season_id = f"{season}-{season+1}"

    # Upsert players
    players = stats_df[["player_id", "player_name"]].drop_duplicates(subset=["player_id"])
    for _, row in players.iterrows():
        conn.execute(
            "INSERT OR REPLACE INTO players (player_id, player_name) VALUES (?, ?)",
            [row["player_id"], row["player_name"]],
        )

    # Upsert clubs
    clubs = stats_df[["club_id", "club_name", "league_name"]].drop_duplicates(subset=["club_id"])
    for _, row in clubs.iterrows():
        conn.execute(
            "INSERT OR REPLACE INTO clubs (club_id, club_name, league_name) VALUES (?, ?, ?)",
            [row["club_id"], row["club_name"], row["league_name"]],
        )

    # Upsert season
    conn.execute(
        "INSERT OR REPLACE INTO seasons (season_id, season_label, start_year, end_year) VALUES (?, ?, ?, ?)",
        [season_id, f"{season}/{str(season+1)[-2:]}", season, season + 1],
    )

    # Upsert player stats
    stat_cols = [
        "player_season_id", "player_id", "club_id", "season_id",
        "primary_position", "appearances", "starts", "minutes_played",
        "goals", "assists", "shots", "shots_on_target",
        "key_passes", "progressive_passes", "progressive_carries", "successful_dribbles",
        "xg", "xa", "tackles", "interceptions", "clearances", "aerial_duels_won",
        "yellow_cards", "red_cards",
    ]

    for _, row in stats_df.iterrows():
        values = []
        for c in stat_cols:
            val = row.get(c, 0)
            if pd.isna(val):
                val = 0
            values.append(val)

        placeholders = ", ".join(["?"] * len(stat_cols))
        col_str = ", ".join(stat_cols)
        try:
            conn.execute(
                f"""INSERT OR REPLACE INTO player_season_stats_raw
                    ({col_str}, competition_scope, source_name)
                    VALUES ({placeholders}, 'league_only', 'fbref')""",
                values,
            )
        except Exception as e:
            pass  # Skip problematic rows silently


def _store_ratings(conn, ratings_df):
    """Store ratings in DB."""
    for _, row in ratings_df.iterrows():
        try:
            conn.execute(
                """INSERT OR REPLACE INTO season_xi_ratings
                   (player_season_id, player_id, club_id, season_id,
                    role_bucket, finishing_score, creation_score, control_score,
                    defense_score, clutch_score, aura_score, overall_score,
                    confidence_score, tier_label, explanation_json,
                    formula_version, generated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    row["player_season_id"], row["player_id"], row["club_id"],
                    row["season_id"], row["role_bucket"],
                    row["finishing_score"], row["creation_score"], row["control_score"],
                    row["defense_score"], row["clutch_score"], row["aura_score"],
                    row["overall_score"], row["confidence_score"], row["tier_label"],
                    row["explanation_json"], row["formula_version"], row["generated_at"],
                ],
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
