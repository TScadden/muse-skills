# Privacy and sanitization

This library is built from skills that ran in one person's real daily life.
Before any skill was added, it was sanitized so the library can be shared
without sharing the person. This file records the rules so future additions
follow them too.

## What was removed or replaced

- **Names and contact details** — the owner's name, phone number, email
  addresses, and other people's names became placeholders such as
  `<FULL_NAME>` and `<PHONE_NUMBER>`.
- **Account and league identifiers** — service account IDs, fantasy league
  IDs, and team names became placeholders or environment variables
  (`ESPN_FHL_LEAGUE_ID`, `ESPN_FHL_TEAM_NAME`, and friends).
- **Home location** — home coordinates and the owner's timezone became
  `GODS_EYE_HOME_LAT`, `GODS_EYE_HOME_LON`, and `GODS_EYE_TZ`. Example
  commands in docs use `<LAT>` and `<LON>`, and example destinations were
  removed entirely.
- **Proprietary values** — one app's design audit depended on that app's
  brand tokens and internal file paths. Only its method was kept, as a
  generalized template with a fill-in section.
- **Sample and captured data** — real API responses, league exports, and
  other captured files were excluded. They can contain third parties' names
  and data, not just the owner's.
- **Local machine details** — absolute paths into the owner's home
  directory, virtual environments, caches, lock files, and recovery
  scratch files were removed. Tools were re-pointed at paths inside their
  own skill folder.

## The checklist for anything new

Before a skill is added (see `CONTRIBUTING.md`):

1. Read the whole skill as an outsider. Anything that identifies a person,
   an account, a place someone lives, or a private project comes out or
   becomes a placeholder.
2. Search the text for names, phone numbers, email patterns, long ID
   numbers, coordinates, and home-directory paths. Do not rely on memory
   of what you edited.
3. Check data files and samples separately from prose; real captured data
   never ships.
4. Make the placeholders obvious and list them in `catalog.json`, so the
   installing Muse knows exactly what to ask its user for.
5. Confirm the skill still works after sanitizing: run its smoke test from
   `SETUP.md` with test values.

## A standing rule of this library

Filled-in copies are private by definition. Placeholder values a user
provides during setup live on that user's machine and in their Muse's
memory of them. They are never committed back here.
