# SETUP — a walkthrough for the Muse agent reading this

A person has sent you this repository and asked you to set these skills up
for them. This file is your instructions. Work through the steps in order,
keep the person informed in plain language, and do not skip the
verification step. By the end, the person should be able to just ask you
for things naturally ("where was this photo taken?", "who's winning my
fantasy league?", "check that drug's label") and have the right skill fire.

## Ground rules (read first, always in force)

1. **Read before you run.** Open every `SKILL.md` and skim every script
   before executing anything from this repo. If a script does something you
   did not expect from its skill description, stop and tell the user.
2. **No skill here needs an API key or a payment, and none should ever ask
   for your password.** The data tools read free, keyless public APIs. Two
   skills do work through your own existing sign-ins, which is a different
   thing: **espn-fantasy** reads your league in a browser where you are
   already signed in to ESPN (its parser never touches the network and
   never sees a password), and **people-search-scrub** finishes opt-out
   confirmations from your own email inbox. Signing in as yourself, in
   your own browser, where a skill's steps call for it is normal. Anything
   beyond that (a credential prompt you did not expect, a paywall, an ID
   request) is a stop sign: hand it to the user.
3. **Placeholder values are the user's private data.** Ask for them in
   conversation, store them in your own memory of the user or in the
   installed copy only, and never send them back to this repository or
   anywhere else. Never invent a value.
4. **Stop at walls.** Sign-in prompts, payment screens, ID requests, and
   captchas you cannot complete are hand-offs to the user with exact steps,
   not obstacles to work around.
5. **Never overwrite silently.** If a skill folder already exists on the
   user's machine, ask before replacing it.

## Step 1 — Get the files

- If you have shell access and `git`: `git clone <this repo's URL>` into a
  working folder, for example `~/workspace/muse-skills-library/`.
- Otherwise, download the repository ZIP from its GitHub page in the
  browser and unzip it to the same kind of folder.
- Confirm you can see `catalog.json` and the `skills/` folder before going
  on. If the repo is private and you cannot reach it, tell the user plainly
  and ask them to share access; do not guess at contents.

## Step 2 — Present the catalog and let the user pick

- Read `catalog.json`. It lists every skill with a one-line description, its
  kind (playbook or tool), its setup needs, and its placeholders.
- Show the user the skills as a short plain-language list (name + what it
  does for them). Offer "install all of them" first; installing a playbook
  costs nothing and tools can be set up lazily, but let the user deselect.
- Note which selected skills are **tools** (they need Step 5) and which need
  **placeholders** (Step 4).

## Step 3 — Install the skill folders

For each selected skill:

1. Copy `skills/<name>/` to `~/workspace/custom-skills/<name>/`, exactly,
   keeping its internal structure. (This is the standard custom-skills
   location; if the user's setup uses a different one, use theirs.)
2. Confirm the installed folder contains a `SKILL.md` whose front matter
   `name` matches the folder name.
3. Do not copy any `.venv`, `__pycache__`, or `cache` folders if they exist
   in your download; they are rebuilt in Step 5.

## Step 4 — Personalize the placeholders

Work through the selected skills that list placeholders in `catalog.json`,
one skill at a time, asking conversationally:

- **gods-eye**: the user's home latitude and longitude (they can read it
  from any map app; a nearby town center is fine if they prefer not to be
  exact) and their IANA timezone. Record them as `GODS_EYE_HOME_LAT`,
  `GODS_EYE_HOME_LON`, `GODS_EYE_TZ`. The cleanest setup is to export these
  in the shell profile or wrap the command; if your environment cannot
  persist environment variables, write them into a private note in the
  installed skill folder named `LOCAL_VALUES.md` and pass `--lat/--lon` on
  each call instead. Tell the user which method you used.
- **nhl-stats**: optionally `NHL_TZ` for their timezone (default UTC).
- **espn-fantasy**: their ESPN fantasy hockey league ID (it is in the
  league's URL on espn.com), the season year (the year the season ends,
  e.g. 2027 for 2026-27), their league's name, their team name, and
  optionally `ESPN_FHL_TZ`. Same storage rule as above; the values also go
  into the two fetch URLs in the installed `SKILL.md` in place of
  `<LEAGUE_ID>` and `<SEASON_YEAR>`, and `<YOUR_TEAM_NAME>` where it appears.
- **people-search-scrub**: full name, phone number, city and state, and the
  email where opt-out confirmations land. Store these in your private
  memory of the user. Only write them into the installed `SKILL.md` copy if
  the user agrees; either way, they never leave the user's machine.
- **design-system-audit**: no install-time values. The first time it is
  used, fill its Project values section from that app's theme source.

## Step 5 — Set up the tools

For each installed skill with a `requirements.txt`:

```bash
cd ~/workspace/custom-skills/<name>
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Skill-specific notes:

- **espn-fantasy**: `pdfjson.py` additionally needs `pdftotext` on the PATH
  (the poppler tools). Check with `which pdftotext`; if missing, tell the
  user it is only needed for the PDF recovery step and note it as pending
  rather than blocking the install. Its fetch step (in its `SKILL.md`)
  happens in a browser signed in to the user's own ESPN account; that
  sign-in is the user's to complete if the browser is not already there.
- **geo-sleuth**: do not create a venv by hand. Run
  `python3 scripts/doctor.py` inside its folder and follow its report; it
  manages its own dependencies (uv) and may download a browser component on
  first run. That download is expected.
- **drug-info**: no setup; the script uses only the Python standard library.

## Step 6 — Verify every installed skill

Do all of these and report the results honestly; a failed check is a
finding to fix or report, not a step to skip quietly.

1. For each installed skill, search for it by name with your skill search
   and confirm it now appears with the right description.
2. Smoke tests for tools (use the values from Step 4 where needed):
   - `nhl-stats`: `.venv/bin/python nhl.py scores` prints today's games or
     a clear "no games" line.
   - `gods-eye`: `.venv/bin/python geo.py weather --lat <LAT> --lon <LON>`
     prints current conditions for that point.
   - `drug-info`: `python3 druginfo.py label ibuprofen` prints FDA label
     sections (or run the equivalent label command from its `SKILL.md`).
   - `espn-fantasy`: no live smoke test exists; verify
     `.venv/bin/python espn.py --help` prints usage, and explain to the
     user that the first real test happens when they save their first
     league JSON (the fetch step in its `SKILL.md`).
   - `geo-sleuth`: `python3 scripts/doctor.py` reporting healthy is its
     verification.
3. Read each smoke test's actual output before claiming success. A printed
   error is not a pass with a footnote.

## Step 7 — Teach-back summary

Close by telling the user, in one short message:

- which skills are installed and where they live,
- which values you stored for personalization and where you stored them,
- anything left pending (for example `pdftotext`),
- one example request per installed skill, in their words, that they can
  try right away.

## Keeping the library current (for the library owner's Muse)

When your user creates a brand-new skill, or installs one from elsewhere
and it proves useful, offer to add it here so the library stays their
single, shareable collection:

1. Sanitize a copy using the checklist in `PRIVACY_AND_SANITIZATION.md`
   (the short version lives in `CONTRIBUTING.md`): placeholders in,
   personal data out, no caches, venvs, samples with real data, or local
   absolute paths.
2. Make it fully ready to go: front matter on the `SKILL.md`, a
   `requirements.txt` if it has a tool, and a catalog entry.
3. Add the folder under `skills/`, add its entry to `catalog.json` and the
   table in `README.md`, and push.

## Troubleshooting

- **A skill does not appear after install**: confirm the folder name matches
  the `name` in its `SKILL.md` front matter and that the folder sits in the
  custom-skills directory your setup actually reads.
- **`ModuleNotFoundError` when running a tool**: the venv from Step 5 is
  missing or the command was run with a different Python. Re-run Step 5 and
  invoke tools exactly as their `SKILL.md` shows.
- **`pdftotext: command not found`**: install the poppler tools for the
  platform, or leave the espn-fantasy PDF recovery step pending and use
  direct JSON saves where the browser allows them.
- **geo-sleuth's first command is slow**: it installs dependencies once.
  Let it finish; later runs are fast.
