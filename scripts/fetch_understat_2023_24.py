"""Fetch xG/xA from Understat via soccerdata — 2023-24 season.

Uses soccerdata Understat reader (same as existing 2021-22 and 2024-25 files).
Season parameter: 2023 → season_id 2023 → 2023-24 in Understat's convention.
"""
from pathlib import Path
import pandas as pd
import soccerdata as sd

OUT_DIR = Path("data/raw/understat")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "all_leagues_2023_2024.csv"

LEAGUES = [
    "ENG-Premier League",
    "ESP-La Liga",
    "ITA-Serie A",
    "GER-Bundesliga",
    "FRA-Ligue 1",
]


def main():
    if OUT_FILE.exists():
        df_existing = pd.read_csv(OUT_FILE)
        print(f"ALREADY EXISTS: {OUT_FILE} ({len(df_existing)} rows) — skipping")
        return

    print("=" * 60)
    print("  UNDERSTAT 2023-24 via soccerdata")
    print("=" * 60)

    understat = sd.Understat(leagues=LEAGUES, seasons=[2023])

    print("  Fetching player season stats...")
    df = understat.read_player_season_stats()
    df = df.reset_index()

    print(f"  Raw rows: {len(df)}")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Leagues: {df['league'].unique().tolist() if 'league' in df.columns else 'N/A'}")
    print(f"  Seasons: {df['season'].unique().tolist() if 'season' in df.columns else 'N/A'}")

    df.to_csv(OUT_FILE, index=False)
    print(f"\n  Saved: {OUT_FILE} ({len(df)} rows)")

    # Spot-check key 2023-24 players
    print("\n  Key player spot-check:")
    name_col = "player" if "player" in df.columns else "player_name"
    for name in ["Mbappe", "Vinicius", "Haaland", "Kane", "Bellingham"]:
        hit = df[df[name_col].str.contains(name, case=False, na=False)]
        if len(hit) > 0:
            s = hit.iloc[0]
            xg_col = "xg" if "xg" in df.columns else "xG"
            xa_col = "xa" if "xa" in df.columns else "xA"
            league_col = "league" if "league" in df.columns else "league_name"
            print(f"    {str(s[name_col]):25s}  xG={s.get(xg_col, '?'):5.1f}  xA={s.get(xa_col, '?'):5.1f}  league={s.get(league_col, '?')}")
        else:
            print(f"    {name}: NOT FOUND")


if __name__ == "__main__":
    main()
