#!/usr/bin/env python3
"""Fetch live natural events from NASA's EONET API (v3). No API key needed.

Usage:
    eonet.py categories
    eonet.py events [--category ID[,ID...]] [--source ID] [--status open|closed|all]
                    [--days N] [--limit N] [--start YYYY-MM-DD] [--end YYYY-MM-DD]
                    [--bbox minLon,maxLat,maxLon,minLat] [--raw]

Standard library only.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://eonet.gsfc.nasa.gov/api/v3"


def get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "nasa-eonet-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def cmd_categories(_args):
    data = get("/categories")
    for cat in data["categories"]:
        print(f"{cat['id']:14} {cat['title']}")


def latest_point(event):
    points = [g for g in event.get("geometry", []) if g.get("type") == "Point"]
    return points[-1] if points else None


def cmd_events(args):
    params = {}
    for key in ("category", "source", "status", "days", "limit", "bbox", "start", "end"):
        value = getattr(args, key)
        if value is not None:
            params[key] = value
    data = get("/events", params)
    if args.raw:
        print(json.dumps(data, indent=2))
        return
    for event in data["events"]:
        cats = ", ".join(c["title"] for c in event["categories"])
        state = "closed " + event["closed"] if event.get("closed") else "open"
        line = f"{event['title']} | {cats} | {state}"
        geo = latest_point(event)
        if geo:
            lon, lat = geo["coordinates"]  # GeoJSON order: longitude first
            line += f" | latest {lat:.2f}, {lon:.2f} on {geo['date']}"
            if geo.get("magnitudeValue") is not None:
                unit = geo.get("magnitudeUnit") or ""
                line += f" | magnitude {geo['magnitudeValue']} {unit}".rstrip()
        print(line)
    print(f"({len(data['events'])} events)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="NASA EONET natural events (no API key).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("categories", help="List the 13 event categories")

    ev = sub.add_parser("events", help="List events with optional filters")
    ev.add_argument("--category", help="Category ID(s), comma separated, e.g. wildfires,severeStorms")
    ev.add_argument("--source", help="Source ID(s), comma separated, e.g. InciWeb")
    ev.add_argument("--status", choices=["open", "closed", "all"], help="Default: open")
    ev.add_argument("--days", type=int, help="Only events from the last N days")
    ev.add_argument("--limit", type=int, help="Max events returned")
    ev.add_argument("--start", help="Range start, YYYY-MM-DD")
    ev.add_argument("--end", help="Range end, YYYY-MM-DD")
    ev.add_argument("--bbox", help="minLon,maxLat,maxLon,minLat (upper left, then lower right)")
    ev.add_argument("--raw", action="store_true", help="Print the full JSON response")

    args = parser.parse_args(argv)
    if args.command == "categories":
        cmd_categories(args)
    else:
        cmd_events(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
