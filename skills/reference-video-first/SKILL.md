---
name: reference-video-first
description: Build a video modeled on a reference by watching the actual reference first, sampling frames across it, and writing a format spec before producing anything.
---

# Build Videos From the Watched Reference First

## Watch the actual reference before building

- Download and watch every reference video the user sends or names before you design, generate, or render anything modeled on it. Never build from a description, a thumbnail, or a guess about the format.

- Sample frames at regular short intervals across the whole reference, not only the opening seconds. Caption systems, shot rhythm, and presenter presence often change after the opening.

- Write a short format spec from what you watched before production starts. Cover frame shape, footage type, whether a presenter appears and how, caption style and timing, pacing, and sound.

- Confirm any part of the spec you could not establish from the reference, and mark it as your choice rather than part of the reference format.

## Build to the spec, then compare

- Build only footage types the spec calls for. When the reference uses moving footage throughout, do not substitute still images with pan or zoom moves.

- Match the caption system exactly as sampled. Note whether every word appears in sync or only selected words, and whether opening lines build cumulatively before the main caption pattern starts.

- Compare quality check frames from your render against reference frames side by side before delivery, and fix any mismatch in frame shape, footage type, presenter presence, or captions before the user sees it.

- Show the user storyboard frames or a short test segment built to the spec before a full render when the format is new to you.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Ask the user which single reference video to match exactly when several references differ, and build a shot by shot map of that one before generating clips.

- Transcribe the reference narration and read its on screen text from the sampled frames when the spoken and written words may differ.
