"""Export season cards as JSON files."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from seasonxi.db.connection import get_connection


def export_cards(
    output_dir: Path = Path("outputs/cards"),
    conn: duckdb.DuckDBPyConnection | None = None,
) -> list[dict]:
    """Export all rated players as individual card JSONs."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Join ratings with player/club names
    cards_df = conn.execute("""
        SELECT
            r.player_season_id,
            p.player_name,
            r.season_id,
            c.club_name,
            r.role_bucket,
            r.finishing_score,
            r.creation_score,
            r.control_score,
            r.defense_score,
            r.clutch_score,
            r.aura_score,
            r.overall_score,
            r.confidence_score,
            r.tier_label,
            r.explanation_json
        FROM season_xi_ratings r
        JOIN players p ON r.player_id = p.player_id
        JOIN clubs c ON r.club_id = c.club_id
        ORDER BY r.overall_score DESC
    """).fetchdf()

    cards = []
    for _, row in cards_df.iterrows():
        card = {
            "player": row["player_name"],
            "season": row["season_id"].replace("-", "/"),
            "club": row["club_name"],
            "role": row["role_bucket"],
            "overall": int(round(row["overall_score"])),
            "finishing": int(round(row["finishing_score"])),
            "creation": int(round(row["creation_score"])),
            "control": int(round(row["control_score"])),
            "defense": int(round(row["defense_score"])),
            "clutch": int(round(row["clutch_score"])),
            "aura": int(round(row["aura_score"])),
            "tier": row["tier_label"],
            "confidence": round(row["confidence_score"], 2),
            "explanation": json.loads(row["explanation_json"]) if row["explanation_json"] else None,
        }
        cards.append(card)

        # Write individual file
        filename = f"{row['player_season_id']}.json"
        filepath = output_dir / filename
        filepath.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also write a combined file
    combined = output_dir / "_all_cards.json"
    combined.write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")

    if own_conn:
        conn.close()

    return cards
