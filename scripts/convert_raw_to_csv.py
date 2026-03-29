"""Convert tilde-delimited raw text files to SeasonXI CSV format.

Usage:
    uv run python scripts/convert_raw_to_csv.py
"""

from pathlib import Path

import pandas as pd
from unidecode import unidecode

RAW_DIR = Path("data/raw/fbref")

# Map: (filename_prefix, league_name, season_id, season_label)
LEAGUE_FILES = [
    ("laliga", "La Liga", "2021-2022", "2021/22"),
    ("seriea", "Serie A", "2021-2022", "2021/22"),
    ("bundesliga", "Bundesliga", "2021-2022", "2021/22"),
    ("ligue1", "Ligue 1", "2021-2022", "2021/22"),
]

COLUMNS = [
    "player_name", "club_name", "primary_position",
    "appearances", "starts", "minutes_played",
    "goals", "assists", "shots", "shots_on_target",
    "yellow_cards", "red_cards",
    "team_goals_scored", "team_goals_conceded",
    "final_table_rank", "team_points", "team_wins", "team_draws", "team_losses",
]

CSV_HEADER = [
    "player_season_id", "player_id", "player_name", "club_id", "club_name",
    "season_id", "season_label", "primary_position",
    "appearances", "starts", "minutes_played", "goals", "assists",
    "shots", "shots_on_target",
    "key_passes", "progressive_passes", "progressive_carries", "successful_dribbles",
    "xg", "xa", "tackles", "interceptions", "clearances", "aerial_duels_won",
    "yellow_cards", "red_cards", "clean_sheets",
    "team_goals_scored", "team_goals_conceded",
    "league_name", "final_table_rank", "team_points", "team_wins", "team_draws", "team_losses",
]


def slugify(name: str) -> str:
    s = unidecode(str(name)).lower().replace(" ", "-").replace(".", "").replace("'", "")
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def convert_raw_file(prefix: str, league_name: str, season_id: str, season_label: str) -> int:
    raw_file = RAW_DIR / f"{prefix}_2021_2022_raw.txt"
    if not raw_file.exists():
        print(f"  SKIP: {raw_file} not found")
        return 0

    lines = raw_file.read_text(encoding="utf-8").strip().split("\n")
    rows = []

    for line in lines:
        parts = line.split("~")
        if len(parts) < 19:
            continue

        name = parts[0]
        team = parts[1]
        pos = parts[2].upper()

        # Position bucket
        bucket = "FW"
        if "GK" in pos:
            bucket = "GK"
        elif "DF" in pos:
            bucket = "DF"
        elif "MF" in pos:
            bucket = "MF"

        slug = slugify(name)
        team_slug = slugify(team)
        psid = f"{slug}-{team_slug}-{season_id}"

        rows.append({
            "player_season_id": psid,
            "player_id": slug,
            "player_name": name,
            "club_id": team_slug,
            "club_name": team,
            "season_id": season_id,
            "season_label": season_label,
            "primary_position": bucket,
            "appearances": int(parts[3] or 0),
            "starts": int(parts[4] or 0),
            "minutes_played": int(parts[5] or 0),
            "goals": int(parts[6] or 0),
            "assists": int(parts[7] or 0),
            "shots": int(parts[8] or 0),
            "shots_on_target": int(parts[9] or 0),
            "key_passes": 0,
            "progressive_passes": 0,
            "progressive_carries": 0,
            "successful_dribbles": 0,
            "xg": 0,
            "xa": 0,
            "tackles": 0,
            "interceptions": 0,
            "clearances": 0,
            "aerial_duels_won": 0,
            "yellow_cards": int(parts[10] or 0),
            "red_cards": int(parts[11] or 0),
            "clean_sheets": 0,
            "team_goals_scored": int(parts[12] or 0),
            "team_goals_conceded": int(parts[13] or 0),
            "league_name": league_name,
            "final_table_rank": int(parts[14] or 0),
            "team_points": int(parts[15] or 0),
            "team_wins": int(parts[16] or 0),
            "team_draws": int(parts[17] or 0),
            "team_losses": int(parts[18] or 0),
        })

    df = pd.DataFrame(rows, columns=CSV_HEADER)
    out_file = RAW_DIR / f"{prefix}_2021_2022_players.csv"
    df.to_csv(out_file, index=False)

    # Also generate teams CSV
    teams = df.groupby(["club_id", "club_name"]).agg({
        "team_goals_scored": "first",
        "team_goals_conceded": "first",
        "final_table_rank": "first",
        "team_points": "first",
        "team_wins": "first",
        "team_draws": "first",
        "team_losses": "first",
    }).reset_index()
    teams["team_season_id"] = teams["club_id"] + "-" + season_id
    teams["season_id"] = season_id
    teams["competition_scope"] = "league_only"
    teams["matches_played"] = 38
    teams = teams.rename(columns={
        "team_goals_scored": "team_goals",
        "team_goals_conceded": "team_goals_conceded",
        "team_points": "points",
        "team_wins": "wins",
        "team_draws": "draws",
        "team_losses": "losses",
    })
    team_cols = ["team_season_id", "club_id", "season_id", "competition_scope",
                 "matches_played", "team_goals", "team_goals_conceded", "points",
                 "final_table_rank", "wins", "draws", "losses"]
    teams[team_cols].to_csv(RAW_DIR / f"{prefix}_2021_2022_teams.csv", index=False)

    print(f"  {league_name}: {len(rows)} players -> {out_file}")
    return len(rows)


def main():
    total = 0
    for prefix, league_name, season_id, season_label in LEAGUE_FILES:
        total += convert_raw_file(prefix, league_name, season_id, season_label)
    print(f"\nTotal converted: {total} players")


if __name__ == "__main__":
    main()
