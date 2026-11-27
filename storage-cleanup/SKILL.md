---
name: storage-cleanup
description: Free disk space on Muse's own machine by clearing regenerable caches, stale build outputs, and stale duplicate tool installs, measuring before and after. Use when the user asks to clean up storage, free space, or run a cleanup, or when disk pressure threatens work. Never deletes databases, backups, or project work product.
---

# Storage Cleanup

Free space on the local machine by removing only what regenerates on its own, and report exactly what was freed.

## Steps

1. **Measure first.** `df -h` on the home mount, then size the usual areas (depth-1 `du` is enough; full-tree scans are slow on a full disk):
   - `~/.cache` by subfolder
   - `~/.gradle`, `~/.pub-cache`, `~/.npm`
   - the workspace's top folders and its `tools/` folder
2. **Clear the safe list** (all pure download/build caches; each re-creates itself on next use):
   - `~/.cache/pip`, `~/.cache/uv`, `~/.cache/go-build`
   - `~/.cache/huggingface` (model downloads)
   - `~/.cache/puppeteer`, `~/.cache/ms-playwright` (browser binaries)
   - `~/.cache/audioseal`, `~/.cache/thumbnails`, `~/.cache/fontconfig`
   - `~/.cache/gh`, `~/.cache/hatch-thumbnails`, `~/.cache/mesa_shader_cache`, `~/.cache/bun`
   - `~/.npm/_cacache`, `~/.gradle/caches`, `~/.gradle/wrapper` (re-downloads on next build)
   - `~/.pub-cache` (Dart/Flutter packages; re-fetched by the next `pub get`)
3. **Prune stale build outputs.** First confirm no flutter, dart, or gradle process is running; if one is, skip this step entirely. Then remove `build/` and `.dart_tool/` directories under the workspace whose newest contained file is 14+ days old (test: the directory contains no file newer than 14 days). **Never prune a `build/` directory inside a `node_modules/` tree** — those are shipped package contents, not build outputs, and removing them breaks the package until reinstall. Only the build outputs go; the checkout's source stays.
4. **Prune old browser downloads:** files in `~/workspace/browser_downloads` older than 14 days.
5. **Measure again** with `df -h` and report the freed amount and the new free total.
6. **Surface, do not delete,** whatever is still big: project work-product folders and tool installs. Name each with its size and let the owner decide. Duplicate versions of a tool (for example an older Blender next to a newer one) are removed only with the owner's explicit yes, then verified gone.

## Hard rules

- Never delete a database or its backups, under any framing of "cleanup."
- Never delete project work product (media projects, source trees, deliverables) without the owner naming the specific items.
- Never delete temp files owned by a running job; confirm the owning process is dead first.
- A cache being large is not a surprise and not a problem by itself; the win is the freed total, so report that number, not a folder-by-folder diary.
