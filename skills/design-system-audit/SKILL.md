---
name: design-system-audit
description: Audit app screens against the project's own measured design system: design tokens, type scale, spacing grid, contrast, tile and card construction, touch targets, and motion. Measure everything from the theme source code; never eyeball a screenshot.
---

# Design System Audit (generalized template)

This is the generalized form of an audit built for one specific app. The
method transfers; the values do not. Before the first audit, fill in the
**Project values** section from the app's own theme source, and treat that
filled-in section as the standard. Where the app disagrees with itself, name
the winner in the standard; a listed deviation is never a second standard.

## 0. Project overrides come first

These are house style set by the project's owner. They win over every generic
rule below. Changing one is not an audit fix; flag it for the owner instead.

Template (replace with your project's real overrides):

1. **Brand color stays.** `<TOKEN_NAME>` `<#HEX>` is the brand accent. Never
   propose replacing, darkening, or "improving" it.
2. **Density rule.** State the project's standing density call (for example:
   compact tiles beat large hero cards on the home screen).
3. **Default states.** State standing defaults (for example: summary cards
   start collapsed; expansion animates at `<N>` ms).

## 1. Measure from the source of truth

- Read the standard out of the theme/token files themselves (color tokens,
  text theme, animation durations, shape radii), never from a screenshot.
- If a claim can only come from a screenshot, pixel-sample the exact pixels
  and compute from the sampled hex. Say which method produced each number.
- Record the source file for every measured value in the audit output.

## 2. Tokens

- Every color on a screen resolves to a named token or a theme slot. A raw
  hex value in a screen file is a finding.
- Stock framework surfaces (Material, Cupertino, system) must come from the
  theme, never from per-screen overrides.
- Text styles come from the type scale in the theme: record each screen's
  styles against the scale (size, weight, color token) and flag ad-hoc sizes.

## 3. Spacing and construction

- Spacing snaps to the project's grid (commonly 8 dp). Flag off-grid padding
  and margins.
- Repeated components (tiles, cards, list rows, pills) share one construction:
  same radius, padding, and internal rhythm everywhere they appear.
- Zero or empty states render nothing or the designed empty state, never a
  placeholder slot.

## 4. Contrast

- Compute contrast ratios from the token hex values, foreground on its real
  background token, and check them against WCAG AA for the text size.
- A known, owner-accepted exception is documented as an exception with its
  measured ratio, not silently passed and not re-flagged as new every audit.

## 5. Touch targets and motion

- Interactive elements meet the platform minimum touch target (commonly
  48 dp) or carry a documented exception.
- Durations and curves come from the theme's animation tokens. Flag any
  screen that hard-codes its own timing.

## 6. Audit output contract

For each screen audited, report: the measured standard it was checked
against, each finding with its file and the token or value involved, whether
the fix is mechanical (apply it) or a judgment call (flag it for the owner),
and a re-check of anything the audit itself changed. Never present an option
your own quality check flags as bad as a pick for the owner.
