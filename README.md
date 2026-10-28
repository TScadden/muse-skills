# Muse Skills Library

A collection of ready-to-install skills for **Muse**, Meta's personal AI
agent. Each skill is a folder under `skills/` containing a `SKILL.md`
playbook; some also carry a small tool script. These skills were built and
battle-tested in real daily use, then sanitized for sharing: every personal
detail has been replaced with a placeholder, so nothing about the original
owner travels with the library.

## Hand this repo to your Muse

Send your Muse this repo's link with this message:

> Set up the Muse skills from this repo for me. Read `SETUP.md` and
> `catalog.json` first, then walk me through the whole setup step by step:
> show me the skills, let me pick, install them, ask me for any placeholder
> values, set up the tools, and verify each one works.

That is all a person has to do. `SETUP.md` contains the complete
walkthrough written for the Muse agent itself.

## The skills

| Skill | What it does | Type | Setup |
| --- | --- | --- | --- |
| geo-sleuth | Geolocate a photo with tool-verified reasoning and an evidence trail | Tool | Its doctor script |
| gods-eye | Live flights, weather, quakes, fires, launches, cameras, drive time for any point | Tool | venv + your home coordinates |
| nhl-stats | Live NHL scores, player stats, schedules, standings from the official APIs | Tool | venv |
| espn-fantasy | Read an ESPN fantasy hockey league's JSON: standings, rosters, points race, activity | Tool | venv + your league's values |
| drug-info | FDA drug labels, NDC details, and recalls via openFDA. Reference only | Tool | None |
| people-search-scrub | Remove your number from people-search sites and data brokers, site by site | Playbook | Your details, kept private |
| build-wiring-readback-audit | Prove an app screen's controls are wired and its saves landed before calling it done | Playbook | None |
| design-system-audit | Audit screens against the project's own measured design tokens and standards | Playbook | Fill in project values |
| faith-post-design | Build faith and Hebrew carousels in their established formats | Playbook | None |
| file-delivery | Deliver files whole: attach the file, state its size, unique names, verify | Playbook | None |
| limited-download-guard | Spend limited export downloads wisely: verify on disk before any retry | Playbook | None |
| long-work-status-checkpoints | Result-first status checkpoints for long or delegated work | Playbook | None |
| reference-video-first | Watch the actual reference video and spec its format before building | Playbook | None |
| verify-summaries | Check delegated summaries against the full source before reporting | Playbook | None |

Machine-readable details, including every placeholder to ask about, are in
`catalog.json`.

## Privacy

Everything in this repo is generic. Names, contact details, account and
league identifiers, home coordinates, and proprietary design values were
removed or replaced with placeholders before anything was added. The rules
used are written down in `PRIVACY_AND_SANITIZATION.md`. If you find anything
that looks like a real person's information, treat it as a bug and tell the
repo owner.

## Layout

- `skills/<name>/SKILL.md` — the playbook Muse loads
- `skills/<name>/*.py`, `requirements.txt`, `data/` — tool files where a
  skill has them
- `SETUP.md` — the step-by-step install walkthrough for a Muse agent
- `catalog.json` — the same catalog in machine-readable form
- `CONTRIBUTING.md` — how skills get added (and sanitized) over time

## Credits

`geo-sleuth` is a third-party open-source skill (upstream:
Oldcircle/geo-sleuth), included as installed. `gods-eye` was inspired by
bilawalsidhu/gods-eye-view (MIT). Everything else is original work shared
for other Muse users.
