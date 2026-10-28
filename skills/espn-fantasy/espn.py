#!/usr/bin/env python3
"""espn.py -- read-only ESPN fantasy hockey parser (your league).

Two-step architecture (no cookies, no network from this skill):
  1. FETCH: a logged-in browser task GETs ESPN's JSON API views and saves
     the raw JSON to a file.
  2. PARSE: this script reads the saved JSON and prints human-readable output.

League, season, and team come from the environment variables
ESPN_FHL_LEAGUE_ID, ESPN_FHL_SEASON_YEAR, ESPN_FHL_LEAGUE_NAME, and
ESPN_FHL_TEAM_NAME (see SKILL.md). Built against a total-points (FPTS)
league; verify your own league's scoring before relying on the output.

JSON field usage (locked against real league JSON Oct 11, 2026):
  team points -> team['points']; roster points ->
  entry['playerPoolEntry']['appliedStatTotal']; names from
  player['firstName']+' '+player['lastName']; positions/slots via
  espn_api's POSITION_MAP; NHL teams via PRO_TEAM_MAP; activity types
  via ACTIVITY_MAP. This is a total-points league: no head-to-head
  matchups exist, so 'scoreboard' shows the live points race.

READ-ONLY. This skill never makes roster moves, waiver claims, trades,
or posts anything to the league.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
_VENV_SITE = os.path.join(
    SKILL_DIR,
    ".venv",
    "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
)
if os.path.isdir(_VENV_SITE) and _VENV_SITE not in sys.path:
    sys.path.insert(0, _VENV_SITE)

try:
    from espn_api.hockey.constant import (
        ACTIVITY_MAP,
        POSITION_MAP,
        PRO_TEAM_MAP,
    )
except ImportError as e:
    print(
        "Error: espn_api package not importable "
        f"({e}). Run with the skill venv: .venv/bin/python espn.py ...",
        file=sys.stderr,
    )
    sys.exit(1)

LEAGUE_ID = int(os.environ.get("ESPN_FHL_LEAGUE_ID", "0"))
YEAR = int(os.environ.get("ESPN_FHL_SEASON_YEAR", "2027"))
MY_TEAM_NAME = os.environ.get("ESPN_FHL_TEAM_NAME", "")
LEAGUE_NAME = os.environ.get("ESPN_FHL_LEAGUE_NAME", "Your league")
LOCAL_TZ = ZoneInfo(os.environ.get("ESPN_FHL_TZ", "UTC"))


def fail(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    if not os.path.exists(path):
        fail(f"file not found: {path}")
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        fail(f"could not read {path}: {e}")
    if not isinstance(data, dict):
        fail(f"{path} does not look like ESPN JSON (expected an object)")
    return data


def check_league(data, path):
    if "teams" not in data:
        fail(f"{path} has no 'teams' key -- fetch with ?view=mTeam (see SKILL.md)")
    if "id" in data and data["id"] != LEAGUE_ID:
        fail(f"{path} is league {data['id']}, not the configured league ({LEAGUE_ID}). Set ESPN_FHL_LEAGUE_ID.")


def build_teams(data):
    """Raw team dicts from saved mTeam+mRoster JSON, sorted by team id.

    NOTE: we parse the raw JSON directly instead of espn_api's Team class:
    this is a total-points league (no head-to-head matchups), and the
    schedule/matchup shape differs from what espn_api's Matchup expects.
    Only the constant maps (POSITION_MAP, PRO_TEAM_MAP, ACTIVITY_MAP)
    come from the package.
    """
    teams = data.get("teams")
    if not isinstance(teams, list) or not teams:
        fail("no teams found -- fetch with view=mTeam (see SKILL.md)")
    for t in teams:
        roster = t.get("roster")
        if not roster or "entries" not in roster:
            fail(
                f"team {t.get('id')} has no roster entries -- "
                "fetch with view=mRoster (see SKILL.md)"
            )
        if isinstance(t.get("name"), str):
            t["name"] = t["name"].strip()
    return sorted(teams, key=lambda x: x.get("id", 0))


def team_points(t):
    """Total season fantasy points: direct 'points' field on the team."""
    pts = t.get("points")
    return round(float(pts), 1) if isinstance(pts, (int, float)) else None


def team_record(t):
    o = (t.get("record") or {}).get("overall") or {}
    return (
        o.get("wins", 0),
        o.get("losses", 0),
        o.get("ties", 0),
    )


def fmt_pts(pts):
    return f"{pts:.1f}" if pts is not None else "n/a"


def my_team(teams):
    for t in teams:
        if (t.get("name") or "").lower() == MY_TEAM_NAME.lower():
            return t
    fail(f"team '{MY_TEAM_NAME}' not found in this league JSON")


def player_name(pp):
    """firstName + lastName (fullName spacing is unreliable after PDF
    text extraction, so never trust it)."""
    first = (pp.get("firstName") or "").strip()
    last = (pp.get("lastName") or "").strip()
    full = f"{first} {last}".strip()
    return full or pp.get("fullName") or f"player {pp.get('id')}"


def player_points(entry):
    """Season fantasy-point total: playerPoolEntry.appliedStatTotal."""
    val = (entry.get("playerPoolEntry") or {}).get("appliedStatTotal")
    return round(float(val), 1) if isinstance(val, (int, float)) else None


def cmd_standings(args):
    data = load_json(args.json_file)
    check_league(data, args.json_file)
    teams = build_teams(data)
    ordered = sorted(teams, key=lambda t: t.get("playoffSeed", 99))
    print(f"{LEAGUE_NAME} standings ({YEAR} season), {len(teams)} teams:")
    for t in ordered:
        w, l, ti = team_record(t)
        print(
            f"{t.get('playoffSeed', '?')}. {t.get('name')} -- "
            f"{fmt_pts(team_points(t))} pts ({w}W-{l}L-{ti}T)"
        )


def cmd_team(args):
    data = load_json(args.json_file)
    check_league(data, args.json_file)
    team = my_team(build_teams(data))
    w, l, ti = team_record(team)
    print(
        f"{team.get('name')} -- {fmt_pts(team_points(team))} pts, "
        f"{w}W-{l}L-{ti}T"
    )
    entries = (team.get("roster") or {}).get("entries", [])
    for e in entries:
        ppe = e.get("playerPoolEntry") or {}
        pp = ppe.get("player") or {}
        pos = POSITION_MAP.get(pp.get("defaultPositionId"), "?")
        slot = POSITION_MAP.get(e.get("lineupSlotId"), "?")
        nhl = PRO_TEAM_MAP.get(pp.get("proTeamId"), "")
        nhl = f", {nhl}" if nhl else ""
        inj_status = pp.get("injuryStatus") or e.get("injuryStatus")
        inj = (
            f" [{inj_status}]"
            if inj_status not in (None, "ACTIVE", [], "")
            else ""
        )
        print(
            f"  {player_name(pp)} ({pos}{nhl}) [{slot}]{inj} "
            f"-- {fmt_pts(player_points(e))} pts"
        )


def cmd_scoreboard(args):
    """Total-points league: no head-to-head matchups exist, so the
    'scoreboard' is the live points race."""
    data = load_json(args.json_file)
    check_league(data, args.json_file)
    teams = build_teams(data)
    ordered = sorted(teams, key=lambda t: t.get("playoffSeed", 99))
    mine = my_team(teams)
    leader_pts = team_points(ordered[0])
    my_pts = team_points(mine)
    print(f"{LEAGUE_NAME} points race ({YEAR} season) -- top 8:")
    for t in ordered[:8]:
        pts = team_points(t)
        behind = ""
        if leader_pts is not None and pts is not None and t != ordered[0]:
            behind = f" ({leader_pts - pts:.1f} back)"
        mark = "  <-- your team" if t.get("id") == mine.get("id") else ""
        print(
            f"  {t.get('playoffSeed', '?')}. {t.get('name')} -- "
            f"{fmt_pts(pts)} pts{behind}{mark}"
        )
    if mine not in ordered[:8] and my_pts is not None and leader_pts is not None:
        print(
            f"  Your team is at {my_pts:.1f} pts "
            f"({leader_pts - my_pts:.1f} behind the lead)"
        )


def parse_activity(topics, teams):
    """Mirror of espn_api/hockey/activity.py, with graceful fallbacks.

    Returns list of (datetime, team_name, action, player_name).
    Only transaction message types (ACTIVITY_MAP) are kept.
    """
    team_names = {t.get("id"): t.get("name") for t in teams} if teams else {}
    player_map = {}
    if teams:
        for t in teams:
            for e in (t.get("roster") or {}).get("entries", []):
                pp = (e.get("playerPoolEntry") or {}).get("player") or {}
                pid = pp.get("id")
                if isinstance(pid, int):
                    player_map[pid] = player_name(pp)
    rows = []
    for topic in topics:
        try:
            dt = datetime.fromtimestamp(
                topic["date"] / 1000, tz=timezone.utc
            ).astimezone(LOCAL_TZ)
        except (KeyError, TypeError, ValueError, OSError):
            continue
        for msg in topic.get("messages", []):
            msg_id = msg.get("messageTypeId")
            if msg_id not in ACTIVITY_MAP:
                continue
            # team id selection mirrors activity.py:
            # 244 (trade) -> from, 239 -> for, everything else -> to
            if msg_id == 244:
                team_id = msg.get("from")
            elif msg_id == 239:
                team_id = msg.get("for")
            else:
                team_id = msg.get("to")
            team_name = team_names.get(team_id, f"team {team_id}")
            action = ACTIVITY_MAP[msg_id]
            target_id = msg.get("targetId")
            pname = player_map.get(target_id, f"player {target_id}")
            rows.append((dt, team_name, action, pname))
    rows.sort(key=lambda r: r[0], reverse=True)
    return rows


def cmd_activity(args):
    data = load_json(args.json_file)
    topics = data.get("topics")
    if not isinstance(topics, list):
        fail(
            f"{args.json_file} has no 'topics' list -- "
            "fetch the communication URL (see SKILL.md)"
        )
    teams = None
    if args.league_json:
        league_data = load_json(args.league_json)
        check_league(league_data, args.league_json)
        teams = build_teams(league_data)
    rows = parse_activity(topics, teams)
    if args.limit < 1:
        fail("--limit must be at least 1")
    print(f"Recent league activity (showing {min(args.limit, len(rows))} of {len(rows)}):")
    for dt, team_name, action, player_name in rows[: args.limit]:
        when = dt.strftime("%a %b %d, %-I:%M %p")
        print(f"  {when} -- {team_name}: {action} {player_name}")


def cmd_freeagents(_args):
    fail(
        "freeagents is not available in v1 -- it needs an x-fantasy-filter "
        "request header the browser fetch step cannot set"
    )


def main():
    ap = argparse.ArgumentParser(
        description="Read-only ESPN fantasy hockey JSON parser "
        "(configured league)"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("standings", help="full league table with points")
    p.add_argument("json_file", help="saved league JSON (mTeam+mRoster+mMatchup+mScoreboard)")

    p = sub.add_parser("team", help="your team roster with positions and points")
    p.add_argument("json_file", help="saved league JSON (mTeam+mRoster+mMatchup+mScoreboard)")

    p = sub.add_parser("scoreboard", help="current matchup period scores")
    p.add_argument("json_file", help="saved league JSON (mTeam+mRoster+mMatchup+mScoreboard)")

    p = sub.add_parser("activity", help="recent adds/drops/trades")
    p.add_argument("json_file", help="saved communication JSON")
    p.add_argument(
        "league_json",
        nargs="?",
        default=None,
        help="optional saved league JSON (resolves team/player names)",
    )
    p.add_argument("--limit", type=int, default=10)

    sub.add_parser("freeagents", help="deferred in v1")

    args = ap.parse_args()
    try:
        {
            "standings": cmd_standings,
            "team": cmd_team,
            "scoreboard": cmd_scoreboard,
            "activity": cmd_activity,
            "freeagents": cmd_freeagents,
        }[args.cmd](args)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()
