---
name: nhl-stats
description: Live NHL data from the league's official public APIs (no key): scores, player season stats and recent form, team schedules, standings, and scoring/goalie leader boards. Sequential requests only.
---

# nhl

Live NHL data from the league's official public APIs (the same backend as
NHL.com). No key, no auth. Built for the fantasy hockey war room:
start/sit schedule checks, waiver-wire research, player form, live scores.

## Tool

`nhl.py` — a small Python CLI (shebang points at
the skill's own venv at `.venv/`, which has `requests` installed).
Run it directly:

```
nhl.py <command> [options]
```

If the venv is ever missing, recreate it with:
`python3 -m venv .venv && .venv/bin/pip install requests`

## Commands

Output is concise human-readable text, one result per line, ready to
paste into chat. All times print in your timezone (set NHL_TZ; default UTC).

- `scores [YYYY-MM-DD]` (default: today)
  Games for the date: away @ home, score, and status. Finals show the
  score, live games show period + clock, scheduled games show the Denver
  start time. Example:
  `nhl.py scores` or `nhl.py scores 2026-10-10`
- `player <name>`
  Search the name, take the best match (exact match preferred, then
  active players), and print: team abbrev, position, season GP/G/A/
  points/plus-minus with power-play points and shots, then the last 5
  games (date, opponent, G/A/points, ice time). Example:
  `nhl.py player "Clayton Keller"`
- `team-schedule <ABBR> [--limit 7]`
  Upcoming games for the team: date (Denver), opponent, home/away.
  ABBR is the 3-letter code (UTA = Utah Mammoth, TOR, EDM, ...).
  Errors clearly on an unknown abbrev. Example:
  `nhl.py team-schedule UTA --limit 5`
- `standings`
  Current NHL standings grouped by division: team, GP, W, L, OT, points.
  Example: `nhl.py standings`
- `leaders [--by points|goals|assists] [--limit 15]`
  Season skater leaders via the stats REST API: rank, name, position,
  team, GP, G, A, P. Example: `nhl.py leaders --by goals --limit 5`
- `goalie-leaders [--limit 10]`
  Goalie save-percentage leaders (minimum 5 GP): name, team, GP, W,
  GAA, SV%. Example: `nhl.py goalie-leaders --limit 5`

## Rate-limit rule

The NHL sits Cloudflare in front of these APIs and 429s on bursts
(~32 concurrent requests). Every command makes a handful of
**sequential** requests. Never parallelize calls to these hosts, and
don't hammer them in a loop — one command per question, then stop.

## Notes

- `/now` endpoints (score, standings, club schedule) return a 307
  redirect to a dated URL; the CLI follows redirects automatically.
- The 2026-27 season id is `20262027` (verified live Oct 11, 2026).
- Several web-API fields (names, team abbrevs) come back as localized
  `{"default": ...}` dicts; the CLI unwraps them.
- `scores` game states: `OFF`/`FINAL` = final, `LIVE` = in progress,
  `FUT` = scheduled.
- These APIs are unofficial-but-stable community-documented endpoints;
  if one starts 404ing across the board, check
  github.com/Zmalski/NHL-API-Reference for a migration before assuming
  the skill is broken.

## Attribution

Data: NHL official public APIs (api-web.nhle.com, api.nhle.com/stats/rest,
search.d3.nhle.com). Reference: github.com/sci220/claude-nhl-api-skill and
github.com/Zmalski/NHL-API-Reference.
## Available connectors

Use `muse.connector_search` to find the current connector docs before following
recovered instructions.
