---
name: sxi-content
description: "Manage SeasonXI content production — images, music, prompts, YouTube. Use when the user wants to: generate image prompts, create Nanobanana/Midjourney prompts, manage Suno music, prepare YouTube upload, check production status, or work on the 10-day content plan."
---

# SXI Content — Production Management

## Image prompts (Nanobanana)
Prompt sets in: configs/image_prompts/prompt_sets/
Format: {player}_{season}_{hook|card|closeup}.txt

Dashboard copies prompts automatically:
http://localhost:3001 → select player → HOOK/CARD/CLOSEUP/SUNO tabs

## Suno music prompts
configs/suno_prompts.txt — 6 player themes (instrumental)

## YouTube upload
```bash
cd C:\ProjectS\seasonXI
uv run python -m seasonxi.content.youtube_upload --video outputs/{video}.mp4 --player {id} --season {season}
```

## Production plan
Obsidian: C:\Users\Storm Credit\Desktop\쇼츠\seasonXI\02_Production\
- production_plan.md (A/B/C priority 30 seasons)
- weekly_plan.md (Day 1-7)
- today_queue.md (daily checklist)

## 10-day schedule (3 videos/day)
Day 1: Messi 2011-12, Ronaldo 2016-17, Mbappe 2018-19
Day 2: Messi 2014-15, Ronaldo 2007-08, Mbappe 2021-22
... (see 02_Production/10day_plan.md)
