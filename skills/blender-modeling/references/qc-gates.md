# QC gates — fill-in form

Run on the **exported** asset. Every line gets a factual answer; "looks
fine" is not an answer. Attach the renders named here to the report.

Asset: ____________  Reference: ____________  Date: ________

## Landmark comparison (side-by-side gate)

Fractions of total height, measured on the reference and on the front
render of the model. Tolerance ±0.03.

| Landmark | Reference | Model | Δ | Pass? |
|---|---|---|---|---|
| Crown / top | 1.00 | | | |
| Hat brim | | | | |
| Eye line | | | | |
| Chin | | | | |
| Belt / waist | | | | |
| Hem | | | | |
| Boot top | | | | |
| Ground | 0.00 | | | |

Max width (fraction of height): ref ______ model ______

## Gates

- [ ] **Reference gate** — refs were in the scene as planes at final
      scale during the build (name the files): ____________
- [ ] **Proportion gate** — all landmarks above within tolerance
- [ ] **Silhouette gate** — flat-black front/side/back renders read
      instantly as the subject (files: ____________)
- [ ] **Blocks test** — no primitive silhouette survives; describe the
      three most complex forms and what they're built from:
      1. ____________ 2. ____________ 3. ____________
- [ ] **Face/structure check** (characters) — brow, sockets, nose,
      collar, cuffs, belt, footwear are modeled forms, not appliqué:
      ____________
- [ ] **Greyscale check** — desaturated render still separates face /
      costume / boots by value
- [ ] **Numbers** — tris ______ (budget ______), bbox ______ studs,
      origin ground-centre ☐, forward −Z ☐
- [ ] **Export check** — transforms applied, normals outward, `Col`
      attribute present (see roblox-export.md checklist)

## Honest remaining gaps

List anything still off — proportion drift, a form that reads weakly,
a tri overage, an angle that doesn't work. Shipping with a written gap
list is acceptable; shipping with an unexamined render is not.

1.
2.
3.
