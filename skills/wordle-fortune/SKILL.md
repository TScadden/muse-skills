---
name: wordle-fortune
description: Wordle Fortune. Reveal the next week of NYT Wordle answers (or any date's answer, past or future) using the method from @liam.codez's reverse-engineering video: the game's own date endpoint serves answers about six weeks early. Use whenever the user asks for upcoming Wordle answers, tomorrow's Wordle, this week's Wordles, or a specific date's answer.
---

# Wordle Fortune

The Wordle answer was never hidden. The game asks the New York Times
server for the answer for a date, and that endpoint answers for future
dates too, roughly six weeks ahead (verified Nov 23, 2026: answers were
served through early January 2027). Method by @liam.codez, who proved it
by noting tomorrow's answer a day early and checking it the next day.

## The endpoint

`https://www.nytimes.com/svc/wordle/v2/YYYY-MM-DD.json`

Returns JSON like:

```json
{"id": 1997, "solution": "filth", "print_date": "2026-11-23", "days_since_launch": 1983, "editor": "Tracy Bennett"}
```

- `solution` is that date's answer.
- `days_since_launch` is the puzzle number (puzzle 0 was June 19, 2021).
- `editor` is who picked the answers (Tracy Bennett since November 2022).
- The endpoint works because answers flip at midnight in every timezone,
  so the server must hold answers for dates around "today" worldwide,
  and in practice it serves about six weeks out.

## How to run it

Run the bundled script (stdlib only, no dependencies):

```bash
python3 wordle_fortune.py (from this skill folder)
```

- Default: 7 days starting today, one line per day with the weekday,
  date, puzzle number, answer, and editor.
- `--days N` for a longer or shorter run; `--start YYYY-MM-DD` to begin
  on a specific date (past dates work too, for checking an old puzzle).

If the script is unavailable, fetch the endpoint directly per date with
curl and read `solution` out of the JSON.

## Presenting the answers

- Give the week as a clean day-by-day list: weekday and date, puzzle
  number, answer in caps.
- These are spoilers by design; the user asked for them. No warnings, no
  hedging, just the answers.
- If a date comes back unavailable, say so plainly: answers are only
  published about six weeks out, so far-future dates have no answer yet.
- Never present an answer you did not actually fetch in this run. If the
  fetch fails, say the lookup failed rather than guessing a word.
