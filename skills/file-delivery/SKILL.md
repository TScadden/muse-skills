---
name: file-delivery
description: Deliver files so they arrive whole: attach the file itself, state its exact size, give every file a unique name, and switch channels when a download truncates.
---

# File Delivery That Arrives Whole

## Attach the file itself

- Attach the actual file in chat whenever the user asks for a file. Treat a repository link or download link as a backup channel only, never as the delivery.

- State the file's exact size from disk in the same message, so the user can check the download against it.

- Give every delivered file its own unique filename, and version every file in a revised set. Save a rebuilt file under a new filename before attaching it, because the app can show a stale cached attachment at a reused path.

## Choose a channel that survives the file

- Expect chat downloads of large files to truncate silently at varying sizes while reporting done. For a large APK or archive, prefer an established direct route to the user's device when one exists, such as a direct device push you have already set up for large builds.

- Switch the delivery channel on the first truncation instead of resending the same file through the route that just failed.

- Shrink the file before delivery only with a method you have verified changes the size. Check the build configuration first, since an already compressed package gains almost nothing from another compression pass.

## Verify before calling it delivered

- Read the file's size on disk with `muse.exec` before sending, and compare it with the size you state.

- Treat a received size that differs from the stated size as not delivered, and say so plainly with the expected size.

- Explain a truncation only with a cause you have verified in the build or the channel. When the cause is unproven, report the two sizes and what you checked, and leave the explanation open.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Include a checksum alongside the stated size when the file is large and the receiving channel cannot report its size reliably.

- Split a build by architecture or platform when the user only needs one target, so the delivered file starts smaller.
