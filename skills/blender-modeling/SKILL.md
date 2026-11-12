---
name: blender-modeling
description: Model stylized game assets and characters in Blender (headless, via bpy scripts) the professional way — reference-driven, proportion-first, structurally built — instead of assembling primitives. Covers the full pipeline: reference planes and proportion landmarks, blockout, subdivision cage modeling with edge/support loops, sculpt passes, Geometry Nodes assists (scatter, garlands, snow caps), vertex-colour zones, game-engine export (FBX for Roblox MeshParts), and hard render QC gates (silhouette test, reference side-by-side, blocks test). Use when asked to model, remodel, or build 3D assets/characters/props in Blender, to create or fix FBX/OBJ/GLB game assets, or when a generated model "looks like blocks" or "looks blobby". Includes the failure-mode table for primitive-silhouette and unstructured-subdivision models and how to fix each.
---

# blender-modeling

Goal: an asset that **survives the owner's eyes** — it reads as the
reference, at final scale, in a flat render, before anyone is told what
it is.

> Study notes behind this skill: `~/workspace/research_notes/blender-modeling-study-20261102/`
> (sources cited per claim). This file is the executable summary.

## The one law

**Never model from imagination or from primitives alone.** Every asset
starts from reference images placed in the scene as orthographic
planes, with proportions measured off them as numbers. Both historical
failures of this workflow (see the failure table) came from skipping
that step: code generated shapes, nobody designed them.

## Hard gates (an asset is not done until all pass)

1. **Reference gate** — at least a front reference (front + side for
   characters) is loaded into the Blender scene as image planes at
   final scale before the first vertex is placed. No reference, no
   modeling.
2. **Proportion gate** — landmark heights measured from the reference
   (ground, hem, belt, chin, eye line, brim, crown) are written into
   the build script as constants, and the blockout matches them before
   any detail exists.
3. **Silhouette gate** — a flat-black render (front/side/back) reads
   instantly as the subject. Judged on the render, not the script.
4. **Blocks test** — if a viewer could describe the model as "a bunch
   of blocks/primitives put together", it fails, however beveled or
   subdivided it is. Primitive *silhouettes* may never survive to the
   final mesh.
5. **Side-by-side gate** — final render and reference at identical
   framing, landmark lines compared. Landmarks within ~3% of total
   height or the model goes back.
6. **Hero-piece gate** — for a kit, ONE piece is built to full standard
   and approved by the owner before any batch production. Never batch
   an unproven shape language.

## The pipeline (in order; do not skip stages)

### 0. Reference & proportions
- Generate or gather the reference (front orthographic, neutral pose,
  flat background; side view too for characters). Save it under the
  project's `assets-3d/refs/`.
- Measure landmarks as fractions of total height. Write them down in
  the build script header. Decide the **shape language** deliberately:
  circles = friendly, inverted triangle (wide base) = stable, squares
  = sturdy. An unbroken egg/oval is *not* a shape language — it has no
  landmarks.
- Place the refs in the scene as image planes (`bpy.data.images.load` +
  Empty image objects, or mesh planes with the image as emission
  material), scaled so the character's height on the plane equals the
  target height in units, one on the front axis, one on the side axis,
  offset behind the modeling space.

### 1. Blockout (primary forms only)
- Build only the 3–6 primary masses (torso mass, head, limbs, the
  asset's big parts) at the landmark heights. Sculpt route: overlapping
  closed primitives → Voxel Remesh (start ≈ height/40) → Clay Strips /
  Grab / Smooth. Poly route: profile lathes / shaped cages built
  *from the landmark table*, front **and** side profiles both honored
  (a pure lathe is round in plan view — real bodies aren't; scale or
  profile per axis).
- Render the silhouette gate NOW. Fix proportions here — everything
  later is expensive.

### 2. Structure (secondary forms + topology)
- Add the forms that make it *designed*: face planes (brow ridge, eye
  sockets as actual indentations or inset geometry, nose as a modeled
  form, cheeks), costume structure (collar with a held edge, cuffs,
  a belt the torso narrows into — not a band floating on the
  silhouette), footwear built from a **foot profile** (extrude the
  side silhouette of a boot; never a flattened box/sphere "shoe blob").
- Cage rules (subdivision work):
  - Edge loops ring every feature (eyes, mouth, neck, shoulder,
    elbow, wrist) and follow the form's flow; loops perpendicular to
    bend axes where things bend.
  - Held edges come from **support loops** (2-edge rule: one loop each
    side; loop distance = bevel radius) *or* weighted creases
    (Shift-E) — pick one system per asset.
  - Poles park on flat/hidden areas; no triangles/poles on curved
    visible surfaces (they pinch).
  - Judge at Subdivision Level 2. Wrong at L2 = topology bug; never
    raise the level to hide it.
- Appliqué warning: small spheres/caps pasted onto a big form (dot
  eyes on a sphere head, blob "beard") are decoration, not structure.
  Features must be *shaped into* the form or built as forms with their
  own edge flow that intersect the main form convincingly.

### 2b. Panels, prints and recesses on a formed body

- **Panels are shells, not plates.** A grille, face plate or screen that must
  read as part of a rounded body is built as a surface-following shell:
  ray-cast its vertices onto the real body surface, offset along the surface
  by a small constant lift, and solidify *inward* so the rim buries into the
  body all the way around. Corner arcs are sampled from the body's own
  radius. A flat plate placed in front of a curved face always betrays
  itself — overhanging lip, dark gap strip, kinked corner.
- **Recesses are real geometry.** An indented channel framing a panel (the
  pressed-in groove a grille sits in) is a boolean cut whose floor is an
  offset of the body surface, so the groove depth stays constant around
  corners and edge rolls. Re-seat the panel on the recess floor afterwards;
  never fake the groove with texture or a dark line.
- **Prints go under the perforation.** A graphic printed on a perforated
  panel lives inside the panel's own material (or on the baffle beneath),
  and the perforation mask drives both the alpha and the graphic's surface
  colour to hole-dark at every dot. The dots then structure the graphic at
  the same contrast as the bare panel. A graphic laid over the holes reads
  as a smooth decal — a different surface glued on.

### 3. Detail & Geometry Nodes assists
- Tertiary detail last, at a resolution that can hold it (Dyntopo
  after proportions lock; remember Dyntopo/remesh destroys colour
  attributes — paint after).
- Geometry Nodes is for **distribution and parametric forms**, never
  for the hero form itself. Use it for: ornament/light scatter on
  foliage, garlands/ropes along curves, snow caps from up-facing
  faces, stud/bead rows along trim. Recipes:
  `references/geometry-nodes-recipes.md`. Realize instances only at
  the export bake.

### 4. Colour zones
- Vertex colours (attribute `Col`, CORNER domain) are the texture-free
  zone system for Roblox: MeshPart.Color white × baked zones.
- Paint per-part before joining; split loops at zone boundaries to
  stop bleeding; author sRGB values and compensate for the wash-out
  (renderers treat them linearly — boost saturation/depth, keep
  near-whites near-white).
- Greyscale check: desaturate the preview — face/beard/coat/boots must
  still separate by value. If they merge, the *forms* are underbuilt;
  go back to stage 2, don't just recolor.

### 5. Export
- Apply all transforms (scale especially — unapplied scale corrupts
  bevels, normals, and the export size). Recalculate normals outward.
- FBX: axis Up = Y, Forward = −Z, Apply Scalings = Unit Scale, 1 unit
  = 1 stud, origin at ground centre, object facing −Z.
- Budgets: hard ceiling 20k tris/mesh (Roblox importer, current docs);
  design ≤ 8k props, ≤ 15k hero characters, prefer 2–5k for ordinary
  stylized characters. Decimate *after* the QC renders if over.
- Full spec: `references/roblox-export.md`.

### 6. QC renders & gates
- Standard set: 3/4 beauty render (Cycles, three-point light, ground),
  front ortho render, silhouette render, side-by-side sheet
  (reference | model, same framing, landmark lines drawn).
- Run every gate in §"Hard gates" against the renders and **report the
  results factually**, including what is still off. A render you
  haven't looked at is not a QC pass.

## Failure-mode table

| Symptom | Root cause | Fix |
|---|---|---|
| "A bunch of blocks put together" | Final mesh = beveled primitives; no form work; blockout shipped as final | Back to stage 1: rebuild primary forms as shaped masses (profiled lathes, extruded silhouettes, sculpt+remesh); primitives are scaffolding only |
| Smooth but blobby / plush egg ("looks worse") | Subdivision applied to unstructured forms; no landmarks; lathe-only proportions (huge belly, tiny legs); features as appliqué blobs | Proportion landmarks from reference; build secondary structure (face planes, collar, seated belt, real boots); give the silhouette a waist, a hem line, a chin line |
| Face reads as stickers on a ball | Eyes/nose/beard pasted onto a sphere; no brow, sockets, or edge flow | Model the brow ridge and eye area as geometry; nose as an intersecting form with its own shading; beard as a shaped shell whose top edge flows under the mustache, hem waved by design |
| Belt/trim floats like a life ring | Subdivision shrinks the body profile after the band was fitted | Fit trim to the *post-subdivision* profile, or build trim as lathe bands whose edges embed into the body |
| Wobbly highlights, pinching | Uneven support-loop spacing, sliver faces, poles on curved areas | Even the loops, dissolve slivers, move poles to flat/hidden spots |
| Colours look pastel in engine | Vertex colours authored as sRGB but rendered linearly | Richness pass when painting: boost saturation (s^~0.7) and deepen saturated colours slightly; keep near-whites clean |
| Model huge/tiny in Studio | Unapplied scale / wrong FBX unit setting | Apply transforms; Apply Scalings = Unit Scale; verify bounding box in studs before export |
| Dark or inside-out patches in Studio | Flipped normals | Recalculate outside; check Face Orientation before export |
| Scatter modifier replaced the mesh with instances | GN graph forgot to join the source geometry back | Join Geometry node takes source + instances (recipes file) |
| GN graph crashes on Blender 4.x | Built with pre-4.0 `inputs.new()` API | Use `tree.interface.new_socket(...)` |
| Whole asset renders WHITE (or unshaded) after adding a GN scatter, though every part's vertex colours check out | Realizing instances leaves an **empty material slot** on the host mesh; on join, every polygon keeps material_index 0 (the empty slot) and the appended vertex-colour material is never used | Clear the host mesh's material slots right after applying the GN modifier (`obj.data.materials.clear()`), before joining/painting. Diagnose by printing the joined object's material list — `[None, 'VCOL']` is the tell |
| Panel reads as a separate plate stuck on the body (lip, gap strip, kinked corner) | Flat panel placed in front of a curved/rounded face; its edges and corners cannot follow the form | Rebuild it as a surface-following shell (see "Panels, prints and recesses"): ray-cast onto the body surface, solidify inward so the rim buries in, corner arcs from the body's own radius |
| Graphic on a perforated panel looks like a smooth sticker | Print composited over the perforation, so the holes never interrupt it and it follows different surface logic than the panel | Print under the perforation (see "Panels, prints and recesses"): the mask drives the graphic's surface colour to hole-dark at every dot, so the dots structure it at full panel contrast |

## Scripting notes (headless Blender via bpy)

- Build scripts live beside the assets (`assets-3d/build/`), run with
  `blender --background --python build_<asset>.py`. Keep a shared lib
  for primitives/paint/export/render so every asset gets the same
  pipeline and preview setup.
- Everything measurable goes in the script header: landmark table,
  palette, tri budget. A reviewer should be able to check the script's
  numbers against the reference without opening Blender.
- Custom geometry beats primitives for designed shapes: profile
  extrusion for footwear/profiles, angle-aware lathes (radius varies
  with angle for front/back asymmetry), vertex displacement along
  designed curves (hat flops, beard hems) with subdivision applied
  *after* shaping.
- Preview renders are part of the build, not an afterthought: the
  script ends by rendering the standard QC set.

## References in this skill

- `references/geometry-nodes-recipes.md` — three production GN recipes
  with full node wiring (scatter, garland-along-curve, snow cap).
- `references/roblox-export.md` — Roblox MeshPart delivery spec.
- `references/qc-gates.md` — the gate checklist as a fill-in form.

## Companion skills (adopted Nov 3, 2026)

This skill is the taste and QC layer: what good looks like, and the
gates an asset must pass. Two adopted companions supply the technical
layers beneath it:

- **`blender`** (MartinRapcan/blender-claude-skill, MIT) — bpy
  correctness: data-API over context-dependent operators, join vs
  boolean vs parent discipline, normals and manifold checks, color
  spaces, numeric render verification (`verify_render`), and the
  failure-mode table for headless scripts. Its scripts hard-require
  Blender 5.x (version assert, 5.x-only light APIs); the doctrine and
  references apply on any version. Always run headless builds with
  `--python-exit-code 1` so a crashed script cannot look successful.
  Run its scripts on a Blender 5.x install kept beside the older
  pipeline Blender; migrate a project deliberately, not by accident.
- **`blender-image-to-3d`** (majidmanzarpour/blender-game-skills, MIT)
  — the measured version of these gates for image-to-3D work:
  silhouette IoU and band-width tolerances via `compose_review.py` /
  `world_gate.py`, `validate.py` topology and budget checks, and
  `roundtrip.py`, which re-imports an export into a blank scene and
  renders what actually arrived. Run validate + roundtrip on game
  exports before they leave this machine. Scripts load on Blender
  4.0.2; the skill's stated floor is 4.2, so treat deep-pipeline
  results on 4.0.2 with care.
