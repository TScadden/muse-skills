# Geometry Nodes recipes

Three production recipes for stylized game assets. All wiring uses the
Blender 4.x API: node groups are created with
`tree.interface.new_socket(name, in_out=..., socket_type=...)` — the
pre-4.0 `inputs.new()` API crashes on 4.x. Modifier inputs are set by
looking up the socket **identifier by name** from
`tree.interface.items_tree`; never hard-code `"Input_2"`.

General rules (from the scatter literature):
- A GN modifier **replaces** the object's geometry with the graph
  output — always Join the source geometry back in, or the mesh
  vanishes into its own instances.
- Masks are continuous fields multiplied into `Density Factor`. Never
  gate scatter with a Switch node.
- Alignment comes free: Distribute Points on Faces outputs a
  **Rotation** field (Euler built from the surface normal) — feed it to
  Instance on Points' Rotation socket.
- Instances are cheap; **Realize Instances only at the export bake**
  (cost is O(instance count × verts per instance)), then decimate.

---

## Recipe 1 — Ornament scatter (baubles/lights on a tree, studs on a surface)

Turns any foliage/prop surface into a decorated one.

Nodes:
1. `NodeGroupInput` / `NodeGroupOutput` (Geometry in/out).
2. `GeometryNodeDistributePointsOnFaces` — `distribute_method =
   'POISSON'`, `Distance Min` ≈ bauble diameter × 1.2,
   `Density Max` tuned so the count lands (density is points/m²).
   Optional mask: `FunctionNodeTexNoise` (or an image texture) →
   `ShaderNodeMath` (clamp) → `Density Factor` for natural clustering.
3. `GeometryNodeObjectInfo` (single bauble) **or**
   `GeometryNodeCollectionInfo` with `separate_children` for 2–4
   bauble variants; set `Pick Instance` = True on the next node.
4. `GeometryNodeInstanceOnPoints` — Points ← Distribute.Points,
   Instance ← Object/Collection Info, Rotation ← Distribute.Rotation,
   Scale ← `FunctionNodeRandomValue` (FLOAT_VECTOR, 0.8–1.25) for
   per-instance size variation.
5. `GeometryNodeJoinGeometry` — inputs: Group Input geometry (the
   foliage) **and** the instances.
6. Group Output.

Bake for export: append `GeometryNodeRealizeInstances` before the
output (or apply the modifier), then a Decimate modifier to budget.

Parameters to expose on the group interface: Density, Seed, Min Scale,
Max Scale. Change the seed, get a new decoration layout — that is the
point of doing it in GN.

## Recipe 2 — Garland / rope along a curve (with beads)

Parametric swag for mantels, archways, sleigh rails.

Nodes:
1. Input: a Curve object (the path). Two branches from Group Input:
2. **Tube branch:** `GeometryNodeSetCurveRadius` (radius profile —
   constant, or a Float Curve for sag taper) →
   `GeometryNodeCurveToMesh` with a `GeometryNodeCurvePrimitiveCircle`
   profile (radius ≈ tube radius, resolution 8–10).
3. **Bead branch:** `GeometryNodeCurveToPoints`
   (`mode = 'EVALUATED'` or LENGTH with a spacing length) →
   `GeometryNodeInstanceOnPoints` with a bead/bauble object; alternate
   two variants via the point index (`FunctionNodeRandomValue` int or
   Index → modulo → Instance Index with a Collection Info).
4. Optional drape control: `GeometryNodeTrimCurve` factor/length input
   exposed as "Garland Length".
5. `GeometryNodeJoinGeometry` (tube + beads) → Group Output.

Expose: Tube Radius, Bead Spacing, Bead Scale, Length. One group
decorates every arch in a kit at consistent quality.

## Recipe 3 — Snow cap (winterize any prop)

Adds a snow shell to whatever faces point up. Reusable across a whole
winter kit — this is the highest-value GN group in a seasonal game.

Nodes:
1. Group Input (host mesh).
2. `GeometryNodeInputNormal` → `GeometryNodeSeparateXYZ` → take **Z**
   (world up in Blender) → `ShaderNodeMath` COMPARE (≥ ~0.55) → this
   is the up-facing selection field. (For a gentler cap, use a
   Map Range ramp 0.35→0.75 instead of a hard compare.)
3. Branch A (selection → cap): `GeometryNodeExtrudeMesh` on the
   selected faces, Offset = cap thickness (0.06–0.12 of asset size),
   then `GeometryNodeSetPosition` with a slight inward pull
   (Position + Normal × −0.02) so the cap overhangs a touch less than
   the silhouette; smooth the result by extruding with a second,
   smaller offset step if the rim looks hard.
4. Branch B: the original geometry, untouched.
5. `GeometryNodeJoinGeometry` (host + cap) → Group Output.
6. Colour: before the join, `GeometryNodeStoreNamedAttribute` writes a
   float attribute `snow` = 1 on the cap branch, 0 on the host; the
   vertex-colour paint step (or an engine material) reads it to paint
   the cap white. If painting directly in Blender, use
   `GeometryNodeSetMaterial` on the cap branch with the snow material
   instead — vertex-colour pipelines prefer the attribute.

Watch out: the cap adds tris on every up-face; on dense meshes raise
the compare threshold or decimate the cap branch separately.

---

## When NOT to use Geometry Nodes

- The hero form of a character or prop (its silhouette is the design —
  model it).
- Faces, hands, feet — anything needing designed edge flow.
- One-off placement of 3–5 objects (manual placement is faster and
  art-directable).
- Anything the engine must animate per-piece (instances bake into one
  mesh on export).
