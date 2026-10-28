# Contributing a skill to this library

This library is the owner's single, shareable collection of Muse skills.
The standing rule: **whenever a new skill is created for the owner, or one
is loaded from elsewhere and kept, a sanitized copy is added here, fully
ready to go** — meaning another person's Muse can install it from this
repo alone, following `SETUP.md`, with no other context.

## What "fully ready to go" means

A new skill folder under `skills/<name>/` must have:

1. A `SKILL.md` that starts with front matter: `name` (matching the folder)
   and a `description` that says what the skill does and when to use it.
2. Any tool scripts it needs, using paths relative to the skill folder
   (never absolute paths into someone's home directory).
3. A `requirements.txt` if its scripts need Python packages, and a note in
   the `SKILL.md` about any non-Python dependency (for example
   `pdftotext`).
4. Placeholders, never real values, for anything personal (see the
   checklist below), with every placeholder listed in its `catalog.json`
   entry.
5. An entry in `catalog.json` and a row in the `README.md` skills table.

## Sanitization checklist (short form)

The full rules live in `PRIVACY_AND_SANITIZATION.md`. In brief, before a
skill is added:

- Replace names, contact details, account and league IDs, team names, home
  coordinates, and timezones with placeholders or environment variables.
- Delete captured data: sample API responses, exports, caches, virtual
  environments, lock files, and scratch/recovery files.
- Generalize project-specific values (brand tokens, internal paths) or
  reduce the skill to its transferable method as a template, and say which
  you did in its catalog `origin` field.
- Grep the result for personal patterns and run the skill's smoke test.

## After adding

- Verify the folder loads: the front matter parses, scripts run their
  `--help` or smoke command, and no file references a path that only exists
  on the original machine.
- Commit with a message that names the skill and whether it is original,
  generalized, or third-party.
