"""Scrape FBref via CDP connection to existing Chrome browser.

This connects to the user's running Chrome browser (which has already
passed Cloudflare) and extracts data from FBref pages.

Usage:
    1. Make sure Chrome is running with remote debugging:
       chrome.exe --remote-debugging-port=9222
    2. Run: uv run python scripts/scrape_via_cdp.py --season 2021
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright
from unidecode import unidecode

LEAGUES = [
    ("ENG1", 9, "Premier-League", "Premier League"),
    ("ESP1", 12, "La-Liga", "La Liga"),
    ("ITA1", 11, "Serie-A", "Serie A"),
    ("GER1", 20, "Bundesliga", "Bundesliga"),
    ("FRA1", 13, "Ligue-1", "Ligue 1"),
]

MIN_MINUTES = 450
DELAY = 6

JS_EXTRACT_TEAMS = """
() => {
    const table = document.querySelector('table[id*="results"][id*="overall"]');
    if (!table) return {};
    const teams = {};
    table.querySelectorAll('tbody tr').forEach(row => {
        const g = (s) => { const c = row.querySelector(`td[data-stat="${s}"], th[data-stat="${s}"]`); return c ? c.textContent.trim() : ''; };
        const team = g('team');
        if (team) teams[team] = {rank: g('rank'), gf: g('goals_for'), ga: g('goals_against'), pts: g('points'), w: g('wins'), d: g('ties'), l: g('losses'), mp: g('games')};
    });
    return teams;
}
"""

JS_EXTRACT_SHOOTING = """
() => {
    const table = document.querySelector('#stats_shooting');
    if (!table) return {};
    const data = {};
    table.querySelectorAll('tbody tr:not(.thead)').forEach(row => {
        if (row.classList.contains('partial_table')) return;
        const p = row.querySelector('td[data-stat="player"] a');
        if (!p) return;
        const g = (s) => { const c = row.querySelector(`td[data-stat="${s}"]`); return c ? c.textContent.trim() : '0'; };
        data[p.textContent.trim() + '|||' + g('team')] = {sh: +g('shots') || 0, sot: +g('shots_on_target') || 0};
    });
    return data;
}
"""

JS_EXTRACT_STANDARD = """
() => {
    const table = document.querySelector('#stats_standard');
    if (!table) return [];
    const rows = table.querySelectorAll('tbody tr:not(.thead)');
    const data = [];
    rows.forEach(row => {
        if (row.classList.contains('partial_table')) return;
        const p = row.querySelector('td[data-stat="player"] a');
        if (!p) return;
        const g = (s) => { const c = row.querySelector(`td[data-stat="${s}"]`); return c ? c.textContent.trim() : '0'; };
        data.push({n: p.textContent.trim(), t: g('team'), pos: g('position'), mp: g('games'), st: g('games_starts'), min: g('minutes').replace(/,/g, ''), g: g('goals'), a: g('assists'), yc: g('cards_yellow'), rc: g('cards_red')});
    });
    return data;
}
"""


def slugify(name):
    s = unidecode(str(name)).lower().replace(" ", "-").replace(".", "").replace("'", "")
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def scrape_league(page, comp_id, fbref_name, league_name, season):
    ss = f"{season}-{season+1}"
    sl = f"{season}/{str(season+1)[-2:]}"
    base = f"https://fbref.com/en/comps/{comp_id}/{ss}"

    print(f"\n  {league_name} {ss}")

    # 1. Standings
    page.goto(f"{base}/{ss}-{fbref_name}-Stats", timeout=60000)
    time.sleep(DELAY)
    teams = page.evaluate(JS_EXTRACT_TEAMS)
    print(f"    Teams: {len(teams)}")

    # 2. Shooting
    page.goto(f"{base}/shooting/{ss}-{fbref_name}-Stats", timeout=60000)
    time.sleep(DELAY)
    shooting = page.evaluate(JS_EXTRACT_SHOOTING)
    print(f"    Shooting: {len(shooting)}")

    # 3. Standard
    page.goto(f"{base}/stats/{ss}-{fbref_name}-Stats", timeout=60000)
    time.sleep(DELAY)
    raw_players = page.evaluate(JS_EXTRACT_STANDARD)
    print(f"    Raw players: {len(raw_players)}")

    # Build DataFrame
    seen = set()
    rows = []
    for p in raw_players:
        minutes = int(p["min"] or 0)
        if minutes < MIN_MINUTES:
            continue
        name, team = p["n"], p["t"]
        slug = slugify(name)
        ts = slugify(team)
        psid = f"{slug}-{ts}-{ss}"
        if psid in seen:
            continue
        seen.add(psid)

        pos = p["pos"].upper()
        bucket = "FW"
        if "GK" in pos: bucket = "GK"
        elif "DF" in pos: bucket = "DF"
        elif "MF" in pos: bucket = "MF"

        sh = shooting.get(f"{name}|||{team}", {"sh": 0, "sot": 0})
        tm = teams.get(team, {})

        rows.append({
            "player_season_id": psid, "player_id": slug, "player_name": name,
            "club_id": ts, "club_name": team, "season_id": ss, "season_label": sl,
            "primary_position": bucket,
            "appearances": int(p["mp"] or 0), "starts": int(p["st"] or 0),
            "minutes_played": minutes,
            "goals": int(p["g"] or 0), "assists": int(p["a"] or 0),
            "shots": sh["sh"], "shots_on_target": sh["sot"],
            "key_passes": 0, "progressive_passes": 0, "progressive_carries": 0,
            "successful_dribbles": 0, "xg": 0, "xa": 0,
            "tackles": 0, "interceptions": 0, "clearances": 0, "aerial_duels_won": 0,
            "yellow_cards": int(p["yc"] or 0), "red_cards": int(p["rc"] or 0),
            "clean_sheets": 0,
            "team_goals_scored": int(tm.get("gf", 0) or 0),
            "team_goals_conceded": int(tm.get("ga", 0) or 0),
            "league_name": league_name,
            "final_table_rank": int(tm.get("rank", 0) or 0),
            "team_points": int(tm.get("pts", 0) or 0),
            "team_wins": int(tm.get("w", 0) or 0),
            "team_draws": int(tm.get("d", 0) or 0),
            "team_losses": int(tm.get("l", 0) or 0),
        })

    print(f"    Final: {len(rows)} players (>={MIN_MINUTES} min)")

    # Team DataFrame
    team_rows = []
    for tname, t in teams.items():
        team_rows.append({
            "team_season_id": f"{slugify(tname)}-{ss}", "club_id": slugify(tname),
            "season_id": ss, "competition_scope": "league_only",
            "matches_played": int(t.get("mp", 0) or 0),
            "team_goals": int(t.get("gf", 0) or 0),
            "team_goals_conceded": int(t.get("ga", 0) or 0),
            "points": int(t.get("pts", 0) or 0),
            "final_table_rank": int(t.get("rank", 0) or 0),
            "wins": int(t.get("w", 0) or 0), "draws": int(t.get("d", 0) or 0),
            "losses": int(t.get("l", 0) or 0),
        })

    return pd.DataFrame(rows), pd.DataFrame(team_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--league", type=str, default=None)
    parser.add_argument("--cdp", type=str, default="http://localhost:9222")
    args = parser.parse_args()

    out_dir = Path("data/raw/fbref")
    out_dir.mkdir(parents=True, exist_ok=True)

    leagues = LEAGUES
    if args.league:
        leagues = [l for l in LEAGUES if l[0] == args.league]

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(args.cdp)
            print(f"Connected to Chrome via CDP at {args.cdp}")
            context = browser.contexts[0]
            page = context.new_page()
        except Exception as e:
            print(f"Could not connect to Chrome CDP: {e}")
            print("Falling back to new browser...")
            browser = pw.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

        all_p, all_t = [], []
        for lid, comp_id, fbref_name, league_name in leagues:
            pdf, tdf = scrape_league(page, comp_id, fbref_name, league_name, args.season)
            if not pdf.empty:
                s = f"{args.season}_{args.season+1}"
                pdf.to_csv(out_dir / f"{lid.lower()}_{s}_players.csv", index=False)
                tdf.to_csv(out_dir / f"{lid.lower()}_{s}_teams.csv", index=False)
                all_p.append(pdf)
                all_t.append(tdf)

        if all_p:
            cp = pd.concat(all_p, ignore_index=True)
            ct = pd.concat(all_t, ignore_index=True)
            s = f"{args.season}_{args.season+1}"
            cp.to_csv(out_dir / f"all_big5_{s}_players.csv", index=False)
            ct.to_csv(out_dir / f"all_big5_{s}_teams.csv", index=False)
            print(f"\nTOTAL: {len(cp)} players, {len(ct)} teams -> {out_dir}/all_big5_{s}_*.csv")

        page.close()


if __name__ == "__main__":
    main()
