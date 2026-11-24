#!/usr/bin/env python3
"""Wordle Fortune: fetch the next week of NYT Wordle answers.

Method (reverse engineered by @liam.codez): the Wordle game does not hide
its answers. It asks the New York Times server for the answer for a given
date at https://www.nytimes.com/svc/wordle/v2/YYYY-MM-DD.json, and that
endpoint answers for future dates too, roughly six weeks ahead. Change
the date, get that day's answer.

Usage: python3 wordle_fortune.py [--days N] [--start YYYY-MM-DD]
Defaults: 7 days starting today (local date).
"""
import argparse
import json
import sys
import urllib.request
from datetime import date, timedelta

URL = "https://www.nytimes.com/svc/wordle/v2/{}.json"


def fetch(day):
    req = urllib.request.Request(URL.format(day.isoformat()),
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--start", default=None,
                    help="YYYY-MM-DD, defaults to today")
    args = ap.parse_args()

    start = (date.fromisoformat(args.start) if args.start else date.today())
    rows = []
    for i in range(args.days):
        day = start + timedelta(days=i)
        try:
            data = fetch(day)
        except Exception as exc:
            rows.append((day, None, None, f"unavailable ({exc})"))
            continue
        rows.append((day, data.get("days_since_launch"),
                     data.get("solution"), data.get("editor")))

    for day, num, solution, editor in rows:
        label = day.strftime("%a %b %d, %Y")
        if solution:
            print(f"{label}  Wordle #{num}: {solution.upper()}  (editor: {editor})")
        else:
            print(f"{label}  {editor}")


if __name__ == "__main__":
    sys.exit(main())
