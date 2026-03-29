# SeasonXI — HANESIS Football Season Card Engine

## Project Overview
SeasonXI turns football's greatest club seasons into cards, rankings, and ultimate XIs.
- **Core**: Season evaluation engine (db → features → ratings → card export)
- **Stack**: Python 3.12, DuckDB, pandas, pydantic, uv
- **Philosophy**: Explainable model, not ground truth. Rules first, ML later.

## Commands
```bash
uv run python -m seasonxi.cli.build_features   # Build per90 + percentile features
uv run python -m seasonxi.cli.build_ratings     # Compute V1 ratings
uv run python -m seasonxi.cli.export_cards      # Export card JSONs
uv run pytest tests/ -v                          # Run tests
uv run ruff check src/                           # Lint
```

## Rules
- Never overwrite raw data in `data/raw/`
- Separate raw data (Layer A) from features (Layer B) from ratings (Layer C)
- Validate every stage output before moving to next stage
- Card stats are "analysis UI", not "truth numbers"
- Start with FW/MF; DF/GK in V1.1
- V1 scope: 5 major leagues, 2010–present, club seasons only

## Architecture (HANESIS)
- **H**arvest → `ingest/` (data collection)
- **A**lign → `ingest/id_resolution.py` (entity matching)
- **N**ormalize → `features/` (per90, percentile, adjustments)
- **E**valuate → `ratings/` (formula, confidence, tiering)
- **S**ynergize → `synergy/` (Phase 4)
- **I**nfer → `synergy/` (Phase 4)
- **S**toryframe → `content/` (card export, scripts)

## Rating System
- 6 scores: Finishing, Creation, Control, Defense, Clutch, Aura + Overall
- Scale: `score = 50 + 49 * raw * confidence`
- Confidence: `min(1.0, minutes / 1800)`
- Tiers: Mythic (95+), Legendary (90-94), Elite (84-89), Gold (76-83), Silver (68-75), Bronze (<68)
