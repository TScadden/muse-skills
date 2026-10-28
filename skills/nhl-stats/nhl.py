#!/usr/bin/env python3
"""nhl.py -- live NHL data for fantasy hockey research.

Free official NHL APIs (same backend as NHL.com), no key:
  Web API:   https://api-web.nhle.com/v1/...      (/now paths 307-redirect)
  Stats API: https://api.nhle.com/stats/rest/en/... (cayenneExp filters)
  Search:    https://search.d3.nhle.com/api/v1/search/player

Rate-limit courtesy: every command makes a handful of SEQUENTIAL
requests. Never parallelize calls to these hosts (Cloudflare 429s
on bursts).

READ-ONLY. Prints concise human-readable text; times print in the timezone
named by NHL_TZ (default UTC).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import os

LOCAL_TZ = ZoneInfo(os.environ.get("NHL_TZ", "UTC"))
SEASON_ID = 20262027  # 2026-27 NHL season (verified live Oct 11, 2026)
WEB = "https://api-web.nhle.com/v1"
STATS = "https://api.nhle.com/stats/rest/en"
SEARCH = "https://search.d3.nhle.com/api/v1/search/player"

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
_VENV_SITE = os.path.join(SKILL_DIR, ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
if os.path.isdir(_VENV_SITE) and _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "muse-nhl-skill/1.0"})


def fail(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def get(url, params=None, what="NHL API"):
    try:
        r = SESSION.get(url, params=params, timeout=25)
    except requests.RequestException as e:
        fail(f"could not reach {what} ({e})")
    if r.status_code == 404:
        fail(f"{what} has no data for that request (404)")
    if r.status_code == 429:
        fail(f"{what} rate-limited us (429) -- try again in a minute")
    if not r.ok:
        fail(f"{what} returned HTTP {r.status_code}")
    try:
        return r.json()
    except ValueError:
        fail(f"{what} did not return JSON")


def denver_time(utc_str, fmt="%-I:%M %p"):
    dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return dt.astimezone(LOCAL_TZ).strftime(fmt)


def denver_date(utc_str):
    dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    return dt.astimezone(LOCAL_TZ).strftime("%a %b %d")


def short_date(iso_date):
    # "2026-10-10" -> "Oct 10"
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%b %d")
    except ValueError:
        return iso_date


def loc(val):
    """Unwrap NHL localized {"default": ...} dicts."""
    if isinstance(val, dict):
        return val.get("default", "?")
    return val if val is not None else "?"


# ---------------------------------------------------------------- scores

FINAL_STATES = ("OFF", "FINAL")


def game_line(g):
    away = g["awayTeam"]["abbrev"]
    home = g["homeTeam"]["abbrev"]
    state = g.get("gameState", "")
    if state in FINAL_STATES:
        a = g["awayTeam"].get("score", "?")
        h = g["homeTeam"].get("score", "?")
        return f"Final: {away} {a} @ {home} {h}"
    if state == "LIVE":
        a = g["awayTeam"].get("score", 0)
        h = g["homeTeam"].get("score", 0)
        pd = g.get("periodDescriptor") or {}
        clock = g.get("clock") or {}
        per = pd.get("number", "?")
        remaining = clock.get("timeRemaining", "")
        return f"LIVE: {away} {a} @ {home} {h} -- P{per} {remaining}".rstrip()
    # scheduled
    when = denver_time(g["startTimeUTC"])
    day = denver_date(g["startTimeUTC"])
    return f"{away} @ {home} -- {day}, {when} MDT"


def cmd_scores(args):
    date = args.date
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            fail(f"'{date}' is not a valid date (use YYYY-MM-DD)")
        url = f"{WEB}/score/{date}"
        label = date
    else:
        url = f"{WEB}/score/now"
        label = "today"
    data = get(url, what="NHL scores")
    games = data.get("games", [])
    if not games:
        print(f"No NHL games {label}.")
        return
    print(f"NHL scores ({label}, {len(games)} games):")
    for g in games:
        print(f"  {game_line(g)}")


# ---------------------------------------------------------------- player

def cmd_player(args):
    name = args.name.strip()
    if not name:
        fail("give me a player name")
    results = get(
        SEARCH, params={"culture": "en-us", "q": name}, what="NHL player search"
    )
    if not isinstance(results, list) or not results:
        fail(f"no NHL player found for '{name}'")
    # prefer an exact name match, then an active player
    low = name.lower()
    pick = next(
        (p for p in results if p.get("name", "").lower() == low), None
    ) or next((p for p in results if p.get("active")), results[0])
    pid = pick["playerId"]
    d = get(f"{WEB}/player/{pid}/landing", what="NHL player page")
    pos = {"C": "C", "L": "LW", "R": "RW", "D": "D", "G": "G"}.get(
        d.get("position"), d.get("position", "?")
    )
    print(f"{loc(d.get('firstName'))} {loc(d.get('lastName'))} ({pos}, {d.get('currentTeamAbbrev','?')})")
    sub = (d.get("featuredStats") or {}).get("regularSeason", {}).get("subSeason")
    if sub:
        print(
            f"  Season: {sub.get('gamesPlayed',0)} GP, {sub.get('goals',0)} G, "
            f"{sub.get('assists',0)} A, {sub.get('points',0)} P, "
            f"{sub.get('plusMinus',0):+}  "
            f"(PP: {sub.get('powerPlayPoints',0)} pts, SOG: {sub.get('shots',0)})"
        )
    else:
        print("  Season: no stats yet")
    last5 = d.get("last5Games") or []
    if last5:
        print("  Last 5:")
        for g in last5:
            where = (
                f"@ {g['opponentAbbrev']}"
                if g.get("homeRoadFlag") == "R"
                else f"vs {g['opponentAbbrev']}"
            )
            print(
                f"    {short_date(g.get('gameDate','?'))} {where}: "
                f"{g.get('goals',0)}G {g.get('assists',0)}A "
                f"{g.get('points',0)}P ({g.get('toi','?')} TOI)"
            )


# ---------------------------------------------------------------- team schedule

def cmd_team_schedule(args):
    abbr = args.abbr.strip().upper()
    if not abbr.isalpha() or len(abbr) > 3:
        fail(f"'{args.abbr}' is not a valid team abbreviation (e.g. UTA, TOR, EDM)")
    d = get(f"{WEB}/club-schedule-season/{abbr}/now", what=f"NHL schedule for {abbr}")
    games = [g for g in d.get("games", []) if g.get("gameState") == "FUT"]
    if not games:
        print(f"No upcoming games found for {abbr}.")
        return
    games = games[: args.limit]
    print(f"Upcoming {abbr} games (next {len(games)}):")
    for g in games:
        home = g["homeTeam"]["abbrev"] == abbr
        opp = g["awayTeam"]["abbrev"] if home else g["homeTeam"]["abbrev"]
        where = f"vs {opp}" if home else f"@ {opp}"
        print(f"  {denver_date(g['startTimeUTC'])} {where} -- {denver_time(g['startTimeUTC'])} MDT")


# ---------------------------------------------------------------- standings

def cmd_standings(_args):
    d = get(f"{WEB}/standings/now", what="NHL standings")
    rows = d.get("standings", [])
    if not rows:
        fail("NHL standings came back empty")
    divs = {}
    for t in rows:
        divs.setdefault(t.get("divisionName", "?"), []).append(t)
    print("NHL standings:")
    for div in sorted(divs):
        print(f"  {div}:")
        for t in sorted(divs[div], key=lambda x: -x.get("points", 0)):
            abbr = loc(t.get("teamAbbrev"))
            print(
                f"    {abbr:3}  {t.get('gamesPlayed',0):2} GP  "
                f"{t.get('wins',0)}W-{t.get('losses',0)}L-{t.get('otLosses',0)}OT  "
                f"{t.get('points',0)} pts"
            )


# ---------------------------------------------------------------- leaders

LEADER_STATS = {"points": "points", "goals": "goals", "assists": "assists"}


def cmd_leaders(args):
    prop = LEADER_STATS[args.by]
    params = {
        "cayenneExp": f"seasonId={SEASON_ID} and gameTypeId=2",
        "sort": json.dumps([{"property": prop, "direction": "DESC"}]),
        "limit": args.limit,
    }
    d = get(f"{STATS}/skater/summary", params=params, what="NHL skater stats")
    rows = d.get("data", [])
    if not rows:
        fail("no skater stats returned")
    print(f"NHL {args.by} leaders (2026-27):")
    for i, p in enumerate(rows, 1):
        print(
            f"  {i:2}. {p.get('skaterFullName','?')} "
            f"({p.get('positionCode','?')}, {p.get('teamAbbrevs','?')}) -- "
            f"{p.get('gamesPlayed',0)} GP, {p.get('goals',0)} G, "
            f"{p.get('assists',0)} A, {p.get('points',0)} P"
        )


def cmd_goalie_leaders(args):
    params = {
        "cayenneExp": f"seasonId={SEASON_ID} and gameTypeId=2 and gamesPlayed>=5",
        "sort": json.dumps([{"property": "savePct", "direction": "DESC"}]),
        "limit": args.limit,
    }
    d = get(f"{STATS}/goalie/summary", params=params, what="NHL goalie stats")
    rows = d.get("data", [])
    if not rows:
        fail("no goalie stats returned")
    print(f"NHL goalie save% leaders, min 5 GP (2026-27):")
    for i, p in enumerate(rows, 1):
        sv = p.get("savePct")
        sv_s = f"{sv:.3f}" if isinstance(sv, (int, float)) else "?"
        gaa = p.get("goalsAgainstAverage")
        gaa_s = f"{gaa:.2f}" if isinstance(gaa, (int, float)) else "?"
        print(
            f"  {i:2}. {p.get('goalieFullName','?')} ({p.get('teamAbbrevs','?')}) -- "
            f"{p.get('gamesPlayed',0)} GP, {p.get('wins',0)} W, "
            f"{gaa_s} GAA, {sv_s} SV%"
        )


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Live NHL data (official APIs, no key)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scores", help="games and scores for a date (default: today)")
    p.add_argument("date", nargs="?", default=None, help="YYYY-MM-DD")

    p = sub.add_parser("player", help="player season stats + last 5 games")
    p.add_argument("name", help="player name, e.g. 'Clayton Keller'")

    p = sub.add_parser(
        "team-schedule", help="upcoming games for a team (e.g. UTA)"
    )
    p.add_argument("abbr", help="3-letter team code")
    p.add_argument("--limit", type=int, default=7)

    sub.add_parser("standings", help="current NHL standings by division")

    p = sub.add_parser("leaders", help="season skater leaders")
    p.add_argument("--by", choices=["points", "goals", "assists"], default="points")
    p.add_argument("--limit", type=int, default=15)

    p = sub.add_parser("goalie-leaders", help="goalie save% leaders, min 5 GP")
    p.add_argument("--limit", type=int, default=10)

    args = ap.parse_args()
    try:
        {
            "scores": cmd_scores,
            "player": cmd_player,
            "team-schedule": cmd_team_schedule,
            "standings": cmd_standings,
            "leaders": cmd_leaders,
            "goalie-leaders": cmd_goalie_leaders,
        }[args.cmd](args)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()
