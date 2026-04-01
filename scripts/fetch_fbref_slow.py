"""Fetch FBref additional tables with rate limiting.

Slowly fetches passing/defense/possession tables
with 10s delay between requests to avoid rate limiting.
"""
import time
import pandas as pd
from pathlib import Path
import soccerdata as sd

LEAGUES = [
    'ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A',
    'GER-Bundesliga', 'FRA-Ligue 1',
]
LEAGUE_SHORT = {
    'ENG-Premier League': 'epl', 'ESP-La Liga': 'laliga',
    'ITA-Serie A': 'seriea', 'GER-Bundesliga': 'bundesliga',
    'FRA-Ligue 1': 'ligue1',
}
SEASON = '2021-2022'
STAT_TYPES = ['shooting', 'passing', 'defense', 'possession']
OUT_DIR = Path("data/raw/fbref_extra")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DELAY = 12  # seconds between requests

print("=" * 60)
print(f"  FBref Extra Tables (delay={DELAY}s per request)")
print("=" * 60)

for league in LEAGUES:
    short = LEAGUE_SHORT[league]
    print(f"\n  {short}:")

    for stat_type in STAT_TYPES:
        out_path = OUT_DIR / f"{short}_2021_2022_{stat_type}.csv"

        if out_path.exists():
            print(f"    {stat_type}: CACHED ({out_path})")
            continue

        print(f"    {stat_type}: fetching...", end=" ", flush=True)
        try:
            fbref = sd.FBref(leagues=league, seasons=SEASON)
            df = fbref.read_player_season_stats(stat_type=stat_type)
            df = df.reset_index()
            df.to_csv(out_path, index=False)
            print(f"OK ({len(df)} rows)")
        except Exception as e:
            err = str(e)[:80]
            print(f"FAIL: {err}")

        print(f"    waiting {DELAY}s...", flush=True)
        time.sleep(DELAY)

print("\n" + "=" * 60)
print("  DONE")

# Show what we got
for f in sorted(OUT_DIR.glob("*.csv")):
    df = pd.read_csv(f)
    print(f"  {f.name}: {len(df)} rows, {df.shape[1]} cols")
print("=" * 60)
