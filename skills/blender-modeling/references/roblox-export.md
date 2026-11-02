# Roblox MeshPart delivery spec

What a Blender-built asset must satisfy to land correctly in Roblox
Studio as a MeshPart. (Platform numbers per Roblox Creator
Documentation as reported by multiple secondary sources, Nov 2026 —
they have conflicted historically (10k vs 20k), so the design targets
below carry margin. Re-verify on create.roblox.com/docs if a number
ever becomes load-bearing.)

## Hard limits

| Item | Limit |
|---|---|
| Triangles per mesh (3D Importer) | 20,000 max — rejected above |
| Triangles per mesh (batch import, historical) | 10,000 |
| Triangles per rigid UGC accessory | 4,000 |
| Texture size | 1024 × 1024 max (auto-downscaled above) |
| MeshPart size | ≤ 2048 studs per axis |

## Design targets (stay under every limit with room)

| Asset class | Target tris |
|---|---|
| Ordinary stylized character | 2,000–5,000 |
| Hero character (one per scene) | ≤ 15,000, decimation planned |
| Props / kit pieces | ≤ 8,000 |
| Small scatter instances (baubles etc.) | ≤ 300 each |

## Scene setup in Blender

- 1 Blender unit = 1 stud. (1 stud ≈ 0.28 m if a real-world conversion
  is ever needed.)
- Origin at ground centre of the asset; asset faces **−Z** (Roblox
  forward).
- Apply ALL transforms before export (Ctrl-A equivalent in script:
  `bpy.ops.object.transform_apply(location=True, rotation=True,
  scale=True)`). Unapplied scale corrupts bevels, normals and size.
- Normals outward: `mesh.normals` recalculated; verify with Face
  Orientation overlay (no red faces) before export.
- Shading is baked at export: set smooth/flat per polygon deliberately.

## Vertex colours

- Attribute name `Col`, FLOAT_COLOR, CORNER domain.
- Roblox multiplies MeshPart.Color × baked vertex colour → set
  MeshPart.Color to white (1,1,1) in Studio or nothing shows correctly.
- Author colours in sRGB but compensate for linear rendering wash-out:
  boost saturation and slightly deepen saturated colours; keep
  near-whites (snow, fur trim) near-white. Split loops at zone
  boundaries to prevent colour bleeding across a hard edge.
- Paint AFTER any sculpt/remesh pass — Dyntopo and Voxel Remesh
  destroy or corrupt colour attributes.
- A mesh with a SurfaceAppearance ignores baked vertex colours for
  tinting in some paths — for vertex-colour assets, use plain
  MeshPart material.

## FBX export settings

```
bpy.ops.export_scene.fbx(
    filepath=..., use_selection=True,
    axis_up='Y', axis_forward='-Z',
    apply_unit_scale=True, global_scale=1.0,
    bake_anim=False, object_types={'MESH'})
```

- Path Mode = Copy (and Embed Textures ON) if textures are ever used.
- One joined mesh per asset file for kit pieces (the game instantiates
  MeshParts per piece; a file with 200 objects is a scene, not an
  asset).
- File ≤ 20 MB transfer ceiling.

## Pre-export checklist

- [ ] Bounding box matches intended stud dimensions (±2%)
- [ ] Tri count within target for its class
- [ ] Origin at ground centre; faces −Z
- [ ] Transforms applied; no negative scale
- [ ] Normals outward everywhere; no non-manifold edges on hero forms
- [ ] Vertex colour attribute present, named `Col`, active
- [ ] QC renders produced from the *exported* file, not the scene
