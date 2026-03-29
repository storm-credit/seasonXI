"""Scrape FBref data for all 5 major leagues using Playwright.

Usage:
    uv run python scripts/scrape_fbref.py --season 2021
    uv run python scripts/scrape_fbref.py --season 2021 --league ENG1
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

# League configs: (our_id, fbref_comp_id, fbref_name, league_display_name, num_teams)
LEAGUES = [
    ("ENG1", 9, "Premier-League", "Premier League", 20),
    ("ESP1", 12, "La-Liga", "La Liga", 20),
    ("ITA1", 11, "Serie-A", "Serie A", 20),
    ("GER1", 20, "Bundesliga", "Bundesliga", 18),
    ("FRA1", 13, "Ligue-1", "Ligue 1", 20),
]

MIN_MINUTES = 450
DELAY_BETWEEN_PAGES = 4  # seconds


def scrape_league(page, league_id, comp_id, fbref_name, league_name, num_teams, season):
    season_str = f"{season}-{season+1}"
    season_label = f"{season}/{str(season+1)[-2:]}"

    print(f"\n{'='*60}")
    print(f"  {league_name} {season_str}")
    print(f"{'='*60}")

    # 1. Standings
    print("  [1/3] Standings...")
    url = f"https://fbref.com/en/comps/{comp_id}/{season_str}/{season_str}-{fbref_name}-Stats"
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(DELAY_BETWEEN_PAGES + 3)
    # Wait for Cloudflare challenge if any
    page.wait_for_selector("table", timeout=30000)

    teams = {}
    table = page.query_selector('table[id*="results"][id*="overall"]')
    if table:
        for row in table.query_selector_all("tbody tr"):
            cells = {}
            for stat in ["team", "rank", "games", "goals_for", "goals_against", "points", "wins", "ties", "losses"]:
                cell = row.query_selector(f'td[data-stat="{stat}"], th[data-stat="{stat}"]')
                cells[stat] = cell.inner_text().strip() if cell else ""
            if cells["team"]:
                teams[cells["team"]] = cells
    print(f"         {len(teams)} teams")

    # 2. Shooting
    print("  [2/3] Shooting...")
    url = f"https://fbref.com/en/comps/{comp_id}/{season_str}/shooting/{season_str}-{fbref_name}-Stats"
    page.goto(url, wait_until="domcontentloaded")
    time.sleep(DELAY_BETWEEN_PAGES)

    shooting = {}
    sh_table = page.query_selector("#stats_shooting")
    if sh_table:
        for row in sh_table.query_selector_all("tbody tr:not(.thead)"):
            if "partial_table" in (row.get_attribute("class") or ""):
                continue
            p_el = row.query_selector('td[data-stat="player"] a')
            if not p_el:
                continue
            name = p_el.inner_text().strip()
            team_el = row.query_selector('td[data-stat="team"]')
            team = team_el.inner_text().strip() if team_el else ""
            shots_el = row.query_selector('td[data-stat="shots"]')
            sot_el = row.query_selector('td[data-stat="shots_on_target"]')
            shooting[f"{name}|||{team}"] = {
                "shots": int(shots_el.inner_text().strip() or 0) if shots_el else 0,
                "sot": int(sot_el.inner_text().strip() or 0) if sot_el else 0,
            }
    print(f"         {len(shooting)} players")

    # 3. Standard stats
    print("  [3/3] Standard stats...")
    url = f"https://fbref.com/en/comps/{comp_id}/{season_str}/stats/{season_str}-{fbref_name}-Stats"
    page.goto(url, wait_until="domcontentloaded")
    time.sleep(DELAY_BETWEEN_PAGES)

    players = []
    std_table = page.query_selector("#stats_standard")
    if not std_table:
        print("         ERROR: No standard stats table found!")
        return pd.DataFrame(), pd.DataFrame()

    seen = set()
    for row in std_table.query_selector_all("tbody tr:not(.thead)"):
        if "partial_table" in (row.get_attribute("class") or ""):
            continue
        p_el = row.query_selector('td[data-stat="player"] a')
        if not p_el:
            continue

        def get(stat):
            cell = row.query_selector(f'td[data-stat="{stat}"]')
            return cell.inner_text().strip() if cell else "0"

        name = p_el.inner_text().strip()
        team = get("team")
        minutes = int(get("minutes").replace(",", "") or 0)
        if minutes < MIN_MINUTES:
            continue

        pos = get("position").upper()
        bucket = "FW"
        if "GK" in pos:
            bucket = "GK"
        elif "DF" in pos:
            bucket = "DF"
        elif "MF" in pos:
            bucket = "MF"

        from unidecode import unidecode
        slug = unidecode(name).lower().replace(" ", "-").replace(".", "").replace("'", "")
        while "--" in slug:
            slug = slug.replace("--", "-")
        slug = slug.strip("-")
        team_slug = unidecode(team).lower().replace(" ", "-").replace(".", "").replace("'", "")
        while "--" in team_slug:
            team_slug = team_slug.replace("--", "-")
        team_slug = team_slug.strip("-")

        psid = f"{slug}-{team_slug}-{season_str}"
        if psid in seen:
            continue
        seen.add(psid)

        sh = shooting.get(f"{name}|||{team}", {"shots": 0, "sot": 0})
        tm = teams.get(team, {})

        players.append({
            "player_season_id": psid,
            "player_id": slug,
            "player_name": name,
            "club_id": team_slug,
            "club_name": team,
            "season_id": season_str,
            "season_label": season_label,
            "primary_position": bucket,
            "appearances": int(get("games") or 0),
            "starts": int(get("games_starts") or 0),
            "minutes_played": minutes,
            "goals": int(get("goals") or 0),
            "assists": int(get("assists") or 0),
            "shots": sh["shots"],
            "shots_on_target": sh["sot"],
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
            "yellow_cards": int(get("cards_yellow") or 0),
            "red_cards": int(get("cards_red") or 0),
            "clean_sheets": 0,
            "team_goals_scored": int(tm.get("goals_for", 0) or 0),
            "team_goals_conceded": int(tm.get("goals_against", 0) or 0),
            "league_name": league_name,
            "final_table_rank": int(tm.get("rank", 0) or 0),
            "team_points": int(tm.get("points", 0) or 0),
            "team_wins": int(tm.get("wins", 0) or 0),
            "team_draws": int(tm.get("ties", 0) or 0),
            "team_losses": int(tm.get("losses", 0) or 0),
        })

    print(f"         {len(players)} players (>={MIN_MINUTES} min)")

    # Build team DataFrame
    team_rows = []
    for tname, t in teams.items():
        ts = unidecode(tname).lower().replace(" ", "-").replace(".", "").replace("'", "")
        while "--" in ts:
            ts = ts.replace("--", "-")
        team_rows.append({
            "team_season_id": f"{ts}-{season_str}",
            "club_id": ts,
            "season_id": season_str,
            "competition_scope": "league_only",
            "matches_played": int(t.get("games", 0) or 0),
            "team_goals": int(t.get("goals_for", 0) or 0),
            "team_goals_conceded": int(t.get("goals_against", 0) or 0),
            "points": int(t.get("points", 0) or 0),
            "final_table_rank": int(t.get("rank", 0) or 0),
            "wins": int(t.get("wins", 0) or 0),
            "draws": int(t.get("ties", 0) or 0),
            "losses": int(t.get("losses", 0) or 0),
        })

    return pd.DataFrame(players), pd.DataFrame(team_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--league", type=str, default=None, help="Single league ID (ENG1, ESP1, etc.)")
    args = parser.parse_args()

    out_dir = Path("data/raw/fbref")
    out_dir.mkdir(parents=True, exist_ok=True)

    leagues = LEAGUES
    if args.league:
        leagues = [l for l in LEAGUES if l[0] == args.league]
        if not leagues:
            print(f"Unknown league: {args.league}")
            sys.exit(1)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        all_players = []
        all_teams = []

        for lid, comp_id, fbref_name, league_name, num_teams in leagues:
            pdf, tdf = scrape_league(page, lid, comp_id, fbref_name, league_name, num_teams, args.season)
            if not pdf.empty:
                season_str = f"{args.season}_{args.season+1}"
                pdf.to_csv(out_dir / f"{lid.lower()}_{season_str}_players.csv", index=False)
                tdf.to_csv(out_dir / f"{lid.lower()}_{season_str}_teams.csv", index=False)
                all_players.append(pdf)
                all_teams.append(tdf)
                print(f"  -> Saved to {out_dir}/{lid.lower()}_{season_str}_*.csv")

        # Combine all leagues
        if all_players:
            combined_p = pd.concat(all_players, ignore_index=True)
            combined_t = pd.concat(all_teams, ignore_index=True)
            season_str = f"{args.season}_{args.season+1}"
            combined_p.to_csv(out_dir / f"all_big5_{season_str}_players.csv", index=False)
            combined_t.to_csv(out_dir / f"all_big5_{season_str}_teams.csv", index=False)
            print(f"\n{'='*60}")
            print(f"  TOTAL: {len(combined_p)} players, {len(combined_t)} teams")
            print(f"  Saved: {out_dir}/all_big5_{season_str}_*.csv")
            print(f"{'='*60}")

        browser.close()


if __name__ == "__main__":
    main()
