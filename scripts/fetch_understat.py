"""Fetch xG/xA from Understat via direct HTTP scraping."""
import json
import re
from pathlib import Path

import httpx
import pandas as pd

LEAGUES = {
    "epl": "https://understat.com/league/EPL/2021",
    "laliga": "https://understat.com/league/La_liga/2021",
    "seriea": "https://understat.com/league/Serie_A/2021",
    "bundesliga": "https://understat.com/league/Bundesliga/2021",
    "ligue1": "https://understat.com/league/Ligue_1/2021",
}
OUT_DIR = Path("data/raw/understat")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_league(league_key: str, url: str) -> list[dict]:
    """Scrape player data from Understat league page."""
    resp = httpx.get(url, follow_redirects=True, timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    # Extract playersData JSON from page
    match = re.search(r"var\s+playersData\s*=\s*JSON\.parse\('(.+?)'\)", resp.text)
    if not match:
        print(f"  {league_key}: playersData not found")
        return []

    raw = match.group(1).encode().decode('unicode_escape')
    players = json.loads(raw)
    print(f"  {league_key}: {len(players)} players")
    return players


def main():
    print("=" * 60)
    print("  UNDERSTAT DATA FETCH - 2021-22")
    print("=" * 60)

    all_rows = []
    for key, url in LEAGUES.items():
        try:
            players = fetch_league(key, url)
            for p in players:
                all_rows.append({
                    "player_name": p.get("player_name", ""),
                    "team": p.get("team_title", ""),
                    "games": int(p.get("games", 0)),
                    "minutes": int(p.get("time", 0)),
                    "goals": int(p.get("goals", 0)),
                    "assists": int(p.get("assists", 0)),
                    "xG": round(float(p.get("xG", 0)), 2),
                    "xA": round(float(p.get("xA", 0)), 2),
                    "shots": int(p.get("shots", 0)),
                    "key_passes": int(p.get("key_passes", 0)),
                    "xGChain": round(float(p.get("xGChain", 0)), 2),
                    "xGBuildup": round(float(p.get("xGBuildup", 0)), 2),
                    "npg": int(p.get("npg", 0)),
                    "npxG": round(float(p.get("npxG", 0)), 2),
                    "league": key,
                })
        except Exception as e:
            print(f"  ERROR {key}: {e}")

    df = pd.DataFrame(all_rows)
    csv_path = OUT_DIR / "all_leagues_2021_2022.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  Total: {len(df)} players -> {csv_path}")

    # Verify key players
    for name in ["Salah", "Son Heung", "Benzema", "Lewandowski", "Mbappe"]:
        match = df[df["player_name"].str.contains(name, case=False, na=False)]
        if len(match) > 0:
            s = match.iloc[0]
            print(f"  {s['player_name']:25s} xG={s['xG']:5.1f} xA={s['xA']:5.1f} KP={s['key_passes']:3d} shots={s['shots']:3d}")


if __name__ == "__main__":
    main()
