---
name: sxi-render
description: "Render SeasonXI Shorts videos using Remotion. Use when the user wants to: create a video, render MP4, make a Shorts clip, preview a card video, or export a player's season card as video. Also trigger for 'render Messi', 'make Benzema video', etc."
---

# SXI Render — Video Generation

## Render a specific player
```bash
cd C:\ProjectS\seasonXI/remotion
npx remotion render SeasonCard --output="../outputs/{player}_{season}.mp4"
```

## Pipeline: Export JSON then Render
1. Export player data to Remotion JSON:
```bash
curl -X POST "http://localhost:8800/api/pipeline-export/{player_name}"
```

2. Render:
```bash
cd remotion && npx remotion render SeasonCard --output="../outputs/{video_id}.mp4"
```

## Video structure (7 scenes, 12 seconds)
1. Hook (1.2s) — player silhouette + hook text
2. Card Reveal (1.3s) — identity
3. OVR Shock (1.0s) — number pop
4. Hex Graph (1.5s) — 6-stat radar fill
5. Player Closeup (1.2s) — face + commentary
6. Achievement (1.3s) — milestone number
7. Verdict (3.5s) — tier + CTA

## Image requirements (3 per player)
- `{player}_{season}_hook.png` — full body dramatic
- `{player}_{season}_card.png` — 3/4 body stable
- `{player}_{season}_closeup.png` — face portrait

## Remotion Studio (preview)
```
http://localhost:3334
```
