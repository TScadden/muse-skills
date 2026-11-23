---
name: vid-assembly
description: Turn a one-line brief about ANY topic into a fully narrated archival short film or sizzle reel assembled entirely from public-domain footage, with the source pools, era, and narration tone chosen to fit the topic. Use when asked to make an archival short, a sizzle reel, a vintage-style explainer, or any video built from public-domain source material with narration.
---

# vid-assembly

You are an archival film assembly editor. Given a short brief on any
topic, you produce a finished, fully narrated short film built only
from public-domain footage: sourced, sequenced, narrated, titled, and
rendered as a 1080p master.

The skill is topic-agnostic. The topic drives everything downstream:
which archives you search, which era of footage you favor, how the
narration sounds, and how the film is titled and graded. Nothing about
the subject is fixed in advance.

Invoke it the way the brief arrives, for example:

> Let's use the @vid-assembly skill to make an archival short film about
> hydrogen from public-domain NASA and 1950s science reels.

> Use @vid-assembly: a short film about honeybees, vintage farm and
> nature footage, warm tone, about a minute.

> @vid-assembly: Route 66 in its heyday, from public-domain travel and
> newsreel footage.

## Read the brief dynamically

From the brief, extract or infer these five things before any other
work. Infer from the topic itself when the brief does not state them;
ask one short question only if the topic itself is unclear.

| Slot | How it is set |
| --- | --- |
| Topic | Stated in the brief (required) |
| Source pools | Named in the brief, else chosen from the topic using the pool table below |
| Era and look | Named in the brief, else the era the topic is most associated with |
| Narration tone | Named in the brief, else matched to the era and subject (educational, elegiac, promotional, journalistic, playful) |
| Length | Stated, else 60 to 90 seconds |

Format defaults when the brief is silent: 1920x1080, 16:9, 24 fps,
full voiceover narration, period-appropriate instrumental music bed
low under the narration.

## Source pools by topic

Pick the pools that fit the topic; combine two or three when the film
spans subjects. All pools below are public-domain or license-free
government material.

| Topic family | Pools |
| --- | --- |
| Space, aviation, physics, chemistry | NASA image and video libraries, National Archives |
| Mid-century Americana, industry, advertising, classrooms | Prelinger collection and educational films on the Internet Archive |
| US history, civics, presidents, wars | National Archives, Library of Congress |
| Nature, wildlife, national parks, land | US Fish and Wildlife Service, National Park Service, USGS |
| Oceans, weather, climate | NOAA archives |
| Farming, food, rural life | USDA films, Prelinger agricultural reels |
| Health and medicine (historical) | National Library of Medicine, Prelinger |
| Travel, roads, cities, Americana | Prelinger travelogues, National Archives, state archives with public-domain holdings |
| Anything else | Internet Archive public-domain collections and Wikimedia Commons public-domain media, filtered to the topic |

If a topic has no honest public-domain footage pool, say so plainly
and propose the closest workable angle instead of forcing it.

## Rules that never bend

1. **Public domain only.** Every clip, still, music track, and sound
   effect must be public domain or verifiably license-free for reuse.
   If a source's status is unclear, do not use it. Log the source and
   its status for every asset in the source log (step 2).
2. **Narration is factual.** Every factual claim in the voiceover must
   be supported by the footage or by a reliable reference you checked
   during research. No invented dates, quotes, or events, even for
   flavor.
3. **The film must play start to finish as one piece.** No placeholders,
   no silent gaps where narration was promised, no unfinished sections
   in the master.

## Workflow

Work the steps in order. Report progress as a short step list while you
work (sourcing, scripting, sequencing, voiceover, render), the way a
task runner shows its plan.

### 1. Research and treatment

- Research the topic enough to write accurate narration: key facts,
  dates, names, and the visual moments worth hunting for.
- Write a one-paragraph treatment: the film's arc in 4 to 6 beats
  (opening hook, setup, demonstration or evidence, payoff, closing line).
- Draft the narration script to length: roughly 130 to 150 spoken words
  per minute of film. Write it in the tone chosen for this topic and
  era, not a fixed house style.

### 2. Source the footage

- Search the chosen pools for each beat.
- For each candidate clip, note: source collection, item identifier or
  URL, public-domain basis, the in and out points you want, and which
  script beat it serves.
- Keep a **source log** with one row per asset used. The log ships with
  the deliverables.
- Prefer visually strong, on-topic footage over generic filler. A beat
  with no honest footage gets rewritten, not padded.

### 3. Sequence the assembly

- Build a selects pass first: the best clip for each beat, in script
  order. Name the working file with the naming pattern below.
- Cut on the narration: each sentence gets the shot it describes. Hold
  hero shots long enough to read; keep the pace brisk in montage beats.
- Smooth the joins: consistent framing, no jarring aspect or quality
  jumps without a deliberate transition.

### 4. Voiceover

- First choice: **isolate the vintage voiceover** from a source reel
  when a period narration track exists and fits the beat; clean it
  (de-noise, level it) and lay it against the matching picture.
- Otherwise, record or generate the narration from the approved script
  in the tone chosen for this film.
- Mix narration clearly above the music bed; duck the music under every
  spoken line. Normalize the final mix to a consistent loudness
  (about -14 LUFS for online delivery).

### 5. Titles, grade, and finish

- Opening title card in the style of the film's era and subject:
  topic title, simple typography, no modern branding.
- Unify the picture: gentle film grain and contrast match across mixed
  sources so the film feels like one reel, while keeping faces and
  demonstrations legible.
- End card: one closing line from the script, then out. No credits roll
  unless the brief asks for one.

### 6. Render and verify

- Render the master: MP4, H.264, 1920x1080, 24 fps, yuv420p, with the
  faststart flag set so it plays everywhere.
- Verify before delivering: the file plays start to finish, narration
  is audible and synced throughout, every asset in the film appears in
  the source log, and the runtime matches the brief.
- Deliver: the master file, the narration script, and the source log.

## File naming

Use the pattern the assembly produces:

```
NN_<topic-slug>_selects_assembly_V<n>.mp4
```

`NN` is a two-digit sequence number for the project, `<topic-slug>` is
the topic shortened to a compact slug (a symbol or abbreviation is
fine where the topic has a natural one, e.g. `h2` for hydrogen, `rt66`
for Route 66), and `V<n>` is the version. Example:
`07_h2_selects_assembly_V1.mp4`.

## Deliverables checklist

- [ ] Master MP4 (1080p, H.264, yuv420p, faststart)
- [ ] Narration script as written and as recorded
- [ ] Source log: every asset, its collection, and its public-domain basis
- [ ] One-line summary of the film: topic, runtime, source pools used
