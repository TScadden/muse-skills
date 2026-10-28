---
name: limited-download-guard
description: Acquire an export or archive that carries a download limit or an expiry without burning attempts: verify each attempt on disk before any retry.
---

# Limited Download Guard

## Check the limit before the first attempt

- Read the export notice for its download limit, its expiry time and its expected size before starting the download. Write those three facts into the working notes for the task.

- Save the archive under `~/workspace` from the start, never in a temporary folder. A long download outlives temporary storage.

- Tell the user before any sign in step that can send a verification prompt to their phone, and agree the exact moment you will trigger it. Read the number the prompt shows from the prompt itself and give the user that number once, without guessing a second number.

## Verify on disk before any retry

- After every download attempt, check the destination folder with `muse.exec` and record the file name, its size on disk and whether the size is still growing before you judge the attempt.

- Treat an attempt as succeeded only when the file size is stable and matches the expected size, or when the archive opens and lists its contents. A browser message alone never proves the file arrived.

- If the first attempt looks failed, diagnose from the file on disk and the download state before clicking download again. Never spend a second attempt to test whether the first one worked.

- Count every click against the stated limit out loud in your notes. Stop all retries when one attempt remains and report the state to the user instead of spending the last attempt.

## Recover without spending the archive

- When an attempt fails partway, keep the partial file, note its exact size, and try a resume or a different transfer route for the same attempt before requesting a fresh download.

- When the limit is exhausted or the archive has expired, say so plainly, name what was lost, and create a replacement export scoped as narrowly as the task allows. Confirm the replacement is building before you close the task.

- Update any scheduled watch for the export so it never touches a dead archive again and never triggers another sign in prompt on its own.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Request the narrowest export that covers the need, so the archive is smaller and a replacement export costs less time when one is needed.

- Split a very large export by source or date range when the provider allows it, so one failed archive never carries the whole task.
