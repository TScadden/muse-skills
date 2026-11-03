---
name: sound-design-pass
description: Local wrapper for sound-designing an edited video. The engine is the installed real-sfx skill (Clipwing, MIT scripts, CC0 UI sounds): real recorded sounds placed on the exact frame, critique loop to a score of 8+, five moments listed for a by-ear check. This wrapper adds the owner's scope guardrails. Use after picture lock on explainers, spec ads, jump-cut edits, trailers, promos, and social edits.
---

# Sound Design Pass (local wrapper over real-sfx)

**Primary engine: the `real-sfx` skill** in the companion `real-sfx` skill in this library. Run its pipeline, not an improvised one:

1. `python scripts/setup.py check` in the real-sfx folder (ffmpeg, libraries, uisfx index).
2. `look.py` the film (frames plus the original sound's spectrogram), then get events from the best source: the project's own cue list or synthesizer script, a screen-recording analysis, a HyperFrames timeline, or `find_moments.py` frame analysis (with `--fine` for soft coloured animation), writing the event list from close-up frames when automation under-reads the picture.
3. `mix.py` to place REAL recordings at the level the author's own sounds had, tuned to the music's notes, mono-checked so nothing vanishes on a phone speaker. Output is always a new MP4 plus a separate SFX WAV track.
4. `critique.py` loop until the score is 8 or higher, then hand the user the five moments to check by ear. Rusty cannot hear; never present a pick as listened to. Say what was measured and what he should listen to.

Doctrine inherited from real-sfx: **sound is never synthesized for motion work.** If no fitting real recording exists, the moment stays quiet and is listed in the report. The bundled uisfx pack (78 CC0 UI cues) covers interface moments; broader whooshes, hits, and foley need a real library, so building one from CC0 sources (Freesound CC0 filter, Sonniss GDC, Mixkit, Pixabay, license checked per file) is the standing way to grow coverage.

## Owner guardrails (these override the engine)

- **Any series whose format the user has locked is out of scope.** For example a talk-over-scenery series with a fixed voice, music bed, and caption format. No SFX layer there unless the user explicitly asks for that episode.
- **Faith content:** never place a comic or percussive sound over spoken scripture or a speaker's solemn moment. When in doubt, leave the moment dry.
- **Delivery gates still apply** to the final file: ffprobe delivery spec (h264, High, yuv420p, faststart) and, when speech matters, a re-transcription check that the words survived the mix.

## Fallback kit

A local `sfx-kit/` folder can hold synthesized sounds (click, pop, whoosh, riser, slam, chime, peaked at -6 dBFS). They are NOT for motion-video sound design (real-sfx doctrine above). They remain available only where the user explicitly wants a generated sound, for example a game UI blip, and are labeled as synthesized wherever used.

## History

Generalized from an adopted creator workflow and its underlying open-source skill.
