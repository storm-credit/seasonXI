---
name: sxi-data
description: "Manage SeasonXI data collection and scraping. Use when the user wants to: scrape FBref, fetch Understat data, collect new season data, add a league, update raw data, check data quality, or mentions 'data collection', 'scraping', 'FBref', 'Understat'."
---

# SXI Data — Collection & Management

## Fetch Understat (xG/xA/key_passes)
```bash
cd C:\ProjectS\seasonXI
PYTHONIOENCODING=utf-8 uv run python scripts/fetch_understat.py
```

## Fetch FBref defense (tackles/interceptions via browser)
Use Chrome MCP to navigate to FBref defense tables and extract data.
Defense CSVs saved to: data/raw/fbref_extra/

## FBref URLs (2021-22)
- EPL: https://fbref.com/en/comps/9/2021-2022/defense/
- La Liga: https://fbref.com/en/comps/12/2021-2022/defense/
- Serie A: https://fbref.com/en/comps/11/2021-2022/defense/
- Bundesliga: https://fbref.com/en/comps/20/2021-2022/defense/
- Ligue 1: https://fbref.com/en/comps/13/2021-2022/defense/

## Data status check
```bash
ls data/raw/fbref/*.csv | wc -l        # FBref CSVs
ls data/raw/fbref_extra/*.csv | wc -l  # Defense CSVs
ls data/raw/understat/*.csv | wc -l    # Understat CSVs
```

## Current data
- FBref: goals, assists, shots, appearances, minutes (5 leagues)
- Understat: xG, xA, key_passes, xGChain, xGBuildup (5 leagues)
- FBref Extra: tackles_won, interceptions (5 leagues)
- Missing: progressive_carries, dribbles, pressures, pass_completion% (need FBref possession/passing tables)
