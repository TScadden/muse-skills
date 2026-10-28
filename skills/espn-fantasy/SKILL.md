---
name: espn-fantasy
description: Read an ESPN fantasy hockey league through ESPN's JSON API with a fetch-and-parse workflow (a logged-in browser saves the JSON, espn.py parses it locally). Read-only. Verify the league's actual scoring before any strategy work depends on it.
---

# espn-fantasy

Direct structured reads of your ESPN fantasy hockey league through ESPN's
JSON API. Before installing, set your league's values in the placeholders
below and in espn.py (or as environment variables): league ID `<LEAGUE_ID>`,
season year `<SEASON_YEAR>` (the year the season ends), and your team name
`<YOUR_TEAM_NAME>`. Verify your league's actual scoring from its settings
before any strategy work depends on it; this template was built against a
total-points (FPTS) league.
Built for the fantasy war room, replacing fragile DOM scraping of ESPN.

## Architecture: fetch + parse (no cookies, no network)

Cookie-based auth is not available, so this skill works in three steps:

1. **FETCH** — a logged-in browser task GETs ESPN's JSON API views.
   The browser's logged-in session is the auth; no special headers needed.
2. **RECOVER** — the browser cannot return large JSON as text (its
   `get_text` hard-truncates at ~131k chars), so the task saves each API
   page as **PDF** instead. `pdfjson.py` extracts the text with
   `pdftotext`, strips Chrome's repeated `Pretty-print` page headers and
   form-feed page-break artifacts, and writes validated JSON:
   ```
   .venv/bin/python pdfjson.py <browser-saved>.pdf league.json
   ```
3. **PARSE** — `espn.py` reads the saved JSON file and prints
   human-readable output. It never touches the network.

Validated Oct 11, 2026 against real league JSON (14 teams, 1.6 MB):
standings, roster, and points race all match ESPN exactly.

### Fetch URLs

Save each response body verbatim as a `.json` file.

Teams, standings, rosters, matchups, scoreboard (one combined request):

```
https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/<SEASON_YEAR>/segments/0/leagues/<LEAGUE_ID>?view=mTeam&view=mRoster&view=mMatchup&view=mScoreboard
```

League communication / activity:

```
https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/<SEASON_YEAR>/segments/0/leagues/<LEAGUE_ID>/communication/?view=kona_league_communication
```

Note: the season year is **2027** (the 2026-27 NHL season). Year 2027
returns 401 (league exists, private); 2025/2026 return 404.

## Commands

All run from this directory with the skill venv:

```
.venv/bin/python espn.py standings league.json
.venv/bin/python espn.py team league.json
.venv/bin/python espn.py scoreboard league.json
.venv/bin/python espn.py activity comm.json [league.json] [--limit 10]
.venv/bin/python espn.py freeagents
```

- `standings` — full table: team names, W/L/T, total points from the
  team's direct `points` field, ordered by playoff seed. Needs the
  league JSON.
- `team` — <YOUR_TEAM_NAME> roster: name (firstName + lastName; fullName
  spacing is unreliable after PDF extraction), position and lineup slot
  via POSITION_MAP, NHL team via PRO_TEAM_MAP, injury status, season
  points from `playerPoolEntry.appliedStatTotal`. Needs the league JSON.
- `scoreboard` — this is a **total-points league**: no head-to-head
  matchups exist (the API `schedule` carries one aggregate entry, not
  pairings), so the scoreboard is the live points race: top 8 by total
  points with each team's deficit behind the leader; his team is marked.
  Needs the league JSON.
- `activity` — recent adds/drops/trades from the communication JSON:
  team, player, and date (your timezone). Pass the league JSON as a
  second argument to resolve team and player names; without it, raw
  team/player IDs are shown.
- `freeagents` — **deferred in v1.** Exits non-zero with a clear message.
  It needs an `x-fantasy-filter` request header the browser fetch step
  cannot set, so it is not faked.

## Verify the packet, the ballots and eligibility before any move

- Stop the run before any vote when a source screen or fetch comes back garbled, truncated or missing, and say plainly that the run is degraded. Never build a Quant packet, a lineup or a vote on partial reads.

- Cross-check every decision-critical packet line against a second read of the same source before the vote opens. A line that changes on recheck, such as a goalie projection or a skater points total, voids any ballot already cast on the old line and restarts the vote on the corrected packet.

- Reconcile the reported tally against the individual ballots before executing anything, and read the reconciled tally back in the war room report. A summary tally that differs from the ballots never dispatches an execution trip.

- Check lineup slot eligibility from the parsed roster positions before proposing or setting a lineup. A player whose listed positions do not include the target slot cannot fill that slot, and a lineup built on such a fill does not exist.

- Verify each executed move after the fact against the activity read, and report zero transactions plainly when a stopped or voided decision produced none.

## Verify league scoring before strategy work

- Pull the league settings from ESPN through the logged-in browser before any research report, strategy build, or scheduled job change that depends on scoring values.

- Record the verified scoring values with the date checked in the war room files that use them, and name any earlier assumption the verified values contradict.

- Treat standard or generic league scoring as an unverified assumption until the settings pull lands. Build no tier, filter, projection, or valuation on an assumed scoring value.

- Recheck the settings at the start of a new season, after ESPN shows a settings change, and whenever a run reports a scoring surprise.

- Verified for this league on Oct 16, 2026: skaters score goals 2, assists 1, power play points 0.5, shorthanded points 0.5, hat trick bonus 1, shots 0.1, and hits 0.1, while plus minus and blocks score zero. Goalies score wins 4, saves 0.2, and overtime losses 1, with no goals against penalty and no shutout bonus.

## Known v1 limits

- `freeagents` is deferred (see above). Waiver research still goes
  through the browser until a fetch path exists.
- Fetching requires the logged-in browser session; this skill only
  parses saved files and makes zero network requests.
- PDF recovery assumes Chrome's JSON viewer layout (the `Pretty-print`
  header + form-feed page breaks). If ESPN or Chrome changes that
  layout, `pdfjson.py` will fail loudly on JSON validation rather than
  silently corrupt data.

## Rules

- **Read-only.** Never make roster moves, waiver claims, trades, or post
  anything to the league through this skill. All moves go through ESPN's
  interface under the war room's voting rules.
- Never guess at data: a failed parse is a plain-English error with a
  non-zero exit, not an empty result.
- Times render in the timezone set by ESPN_FHL_TZ (default UTC).

## Attribution

Data: ESPN. Field reference: `espn_api` by cwendt94
(https://github.com/cwendt94/espn-api), hockey package source
(team.py, player.py, matchup.py, activity.py, constant.py).

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
