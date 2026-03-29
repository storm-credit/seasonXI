"""SeasonXI full pipeline: seed → features → ratings → export.

Usage:
    uv run python -m seasonxi.pipeline.run_pipeline
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from seasonxi.content.card_exporter import export_cards
from seasonxi.db.connection import get_connection, init_schema
from seasonxi.features.feature_pipeline import build_features
from seasonxi.ingest.load_raw_csv import load_seed_data
from seasonxi.ratings.formula_v1 import compute_ratings

console = Console()


def run() -> None:
    """Execute the full pipeline end-to-end."""
    conn = get_connection()

    # Step 1: Schema
    console.print("[bold blue]Step 1:[/] Initializing database schema...")
    init_schema(conn)

    # Step 2: Seed data
    console.print("[bold blue]Step 2:[/] Loading seed data...")
    load_seed_data(conn=conn)

    # Step 3: Features
    console.print("[bold blue]Step 3:[/] Building features (per90 + percentiles)...")
    features_df = build_features(conn=conn)
    console.print(f"  → {len(features_df)} player-seasons processed")

    # Step 4: Ratings
    console.print("[bold blue]Step 4:[/] Computing V1 ratings...")
    ratings_df = compute_ratings(features_df)
    console.print(f"  → {len(ratings_df)} ratings computed")

    # Store ratings in DB
    _store_ratings(conn, ratings_df)

    # Step 5: Export cards
    console.print("[bold blue]Step 5:[/] Exporting cards...")
    cards = export_cards(conn=conn)

    conn.close()

    # Print summary
    _print_summary(cards)


def _store_ratings(conn, ratings_df) -> None:
    """Insert ratings into season_xi_ratings table."""
    for _, row in ratings_df.iterrows():
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


def _print_summary(cards: list[dict]) -> None:
    """Pretty-print the results."""
    table = Table(title="SeasonXI Cards - V1")
    table.add_column("Player", style="bold")
    table.add_column("Season")
    table.add_column("Club")
    table.add_column("OVR", justify="right", style="bold yellow")
    table.add_column("FIN", justify="right")
    table.add_column("CRE", justify="right")
    table.add_column("CTR", justify="right")
    table.add_column("DEF", justify="right")
    table.add_column("CLU", justify="right")
    table.add_column("AUR", justify="right")
    table.add_column("Tier", style="bold cyan")

    for c in sorted(cards, key=lambda x: x["overall"], reverse=True):
        table.add_row(
            c["player"], c["season"], c["club"],
            str(c["overall"]),
            str(c["finishing"]), str(c["creation"]), str(c["control"]),
            str(c["defense"]), str(c["clutch"]), str(c["aura"]),
            c["tier"],
        )

    console.print()
    console.print(table)
    console.print(f"\n[green]Cards exported to outputs/cards/[/green]")


if __name__ == "__main__":
    run()
