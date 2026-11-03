---
name: sound-design-pass
description: Add a deliberate sound-design pass to an edited video: detect the moments that need sound, write a cue sheet, place real SFX under the voice and music, and verify placement acoustically. Use after picture lock on explainers, spec ads, jump-cut edits, trailers, and social edits. Learned from a creator workflow in which the AI watches the cut and places sounds from a library.
---

# Sound Design Pass

The gap this closes: our edits ship with voice and a music bed, and the picture does all the work alone. Professional edits sound designed: transitions breathe, builds land, hits thump. This pass adds that layer deliberately, from a cue sheet, never by sprinkling sounds at random.

## Scope

- Applies to: jump-cut and explainer editing systems, spec ads, trailers, and any social edit where picture events carry meaning.
- Does NOT apply to any series whose format the user has locked (for example a talk-over-scenery series with a fixed voice, music bed, and caption format). Only add sound design there if the user explicitly asks for that episode.
- Faith content rule: never place a comic or percussive sound over spoken scripture or a speaker's solemn moment. When in doubt, leave the moment dry.

## Workflow

1. **Detect events** on the locked cut:
   - Scene changes: `ffmpeg -i in.mp4 -vf "select='gt(scene,0.35)',showinfo" -f null -` for cut points.
   - Frame sampling at each cut plus any text, title, diagram, or UI event the storyboard names.
   - Word timings from the existing whisper transcript: elements that build ON a word get their cue on that word.
2. **Write the cue sheet** before touching audio: timestamp, event, sound class, intensity (soft, medium, hard). One cue per event; density cap of about one cue per 1.5 seconds in talk-driven edits, and silence is a valid choice for most moments. The cue sheet is part of the edit's paper trail.
3. **Map event to class**:
   - Hard cut with subject change → whoosh (soft) or nothing
   - Element builds, diagram step, text pop → pop or click
   - Build toward a reveal → riser ending exactly on the reveal frame
   - Title or logo lands → slam (hard) or chime (soft, faith-safe)
   - Success or completion beat → chime
   - Rapid jump-cut run → at most a soft click on the first and last cut, never every cut
4. **Place and mix**: starter kit in a local `sfx-kit/` folder you create once (click, pop, whoosh, riser, slam, chime; all peaked at -6 dBFS so levels are predictable). Place with ffmpeg `adelay` and `amix`/`sidechain`-free manual gains. Starting levels: cues sit 14 to 20 dB under voice peaks; a slam may come up to 10 dB under for a title hit. Trim clicks and pops tight; a cue that starts early or rings into the next word is a defect.
5. **Verify acoustically** (same discipline as the caption gates): check the waveform at every cue point, confirm no cue starts mid-word or masks a word onset, and confirm the mix still passes the delivery spec (h264, High, yuv420p, faststart) after the final mux. Re-transcribe the finished file when speech matters; the words must survive the sounds.

## Kit notes

- The kit sounds are synthesized locally (ffmpeg and numpy), so they are license-clean and regenerable. Regenerate rather than downloading random sounds of unknown license.
- A real licensed SFX library can replace kit sounds one-for-one later; the cue sheet and mix rules do not change.
