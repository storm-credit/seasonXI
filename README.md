# SeasonXI

**Football's greatest seasons — rated, ranked, revealed.**

SeasonXI turns iconic club seasons into original football cards powered by the **SXI Engine** — a data-driven season evaluation system.

*One season. One version. One legend.*

## 📊 SXI Engine v2.0

6 stats · 4 positions · 2,000+ players rated

| Stat | Measures |
|------|----------|
| **ATT** | Goals, assists, xG, xA, key passes |
| **DEF** | Tackles, interceptions, clearances |
| **PACE** | Progressive carries, dribbles |
| **AURA** | Role dominance, contribution |
| **STA** | Work rate, endurance |
| **MEN** | Pass accuracy, decision making |

**Tiers:** Mythic (95+) · Legendary (90-94) · Elite (84-89) · Gold (76-83)

### Data Sources
- FBref · Understat · Sofascore (4 sources merged)

### Validation
- 91/93 trust audit PASS · 43/43 performance PASS · 27/29 scout review PASS

## 🚀 Quick Start

```bash
uv sync
uv run python scripts/merge_and_run.py    # Rate 2000+ players
docker compose up -d                       # Dashboard + API + Remotion
```

**Dashboard:** http://localhost:3001
**API:** http://localhost:8800
**Remotion:** http://localhost:3334

## 🏗️ HANESIS Architecture

```
H — Harvest     → Data collection
A — Align       → Entity matching
N — Normalize   → Per90, percentile
E — Evaluate    → Rating engine
S — Synergize   → Team chemistry
I — Infer       → Best XI search
S — Storyframe  → Cards, video, YouTube
```

## 🎬 Video (7 scenes, 12 seconds)

Hook → Card Reveal → OVR → Hex Graph → Closeup → Achievement → Verdict

## 🛠️ Stack

Python 3.12 · DuckDB · Next.js 16 · Remotion · Docker · FastAPI

## 📺 Channel

[@season-xi](https://youtube.com/@season-xi)

---

*Built with the SXI Engine — data + context, not just vibes.*
