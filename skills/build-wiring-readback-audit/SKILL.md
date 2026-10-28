---
name: build-wiring-readback-audit
description: Audit a built or ported app screen or tool for real data wiring and verified saves before calling it done: inventory every control, trace each save to the canonical store, and verify by readback, not by response code.
---

# Build Wiring and Readback Audit

## Purpose
Prevent screens and tools from being delivered as finished when a control is unwired, a value is a placeholder, or a save never actually landed.

## Workflow
1. Inventory every visible element and control on the screen or tool being delivered. For each one, record its data source, the action it triggers, and the store it writes to.
2. Classify each item as wired, read-only by explicit design, or deferred. Name every deferred item to the user as deferred in the delivery message; never present a read-only port or a placeholder as complete.
3. Trace each save to the canonical store. Check that the code writes the current canonical copy, not a stale local copy, and that no clear-and-replace sync path can wipe records that have not reached the server.
4. Verify by readback, not by response code: after a save, re-read the value from the store, server, or a second surface and confirm it is present and correct. A success response alone is not verification.
5. Exercise the failure path for each data source. On failure, the UI shows the honest missing state (an empty state or `--` for a missing metric); it never invents, estimates, carries over, or silently downgrades a value.
6. Inspect the built artifact itself, not only the source and tests. When source, tests, and the built output disagree, the built output is the ground truth.
7. Run the checklist again on anything the audit changed before delivery.

## Output Contract
The delivery message includes a short wiring table or list: each control or value, its source and write target, its wired / read-only / deferred status, and the readback result for every save the delivery claims. Unverified items are labeled unverified, with the reason.

## Operating Rules
1. No control ships silently dead: a button, refresh, toggle, or add/edit affordance that does nothing is a blocker, not a follow-up.
2. No claim of an external action (added, deleted, saved, synced) without a readback or a receipt from the system that performed it.
3. Archived, ended, or filtered-out records must not surface on unrelated screens; check each list against its filter rule during the inventory.
4. Checked, logged, or completed items behave the same way across every item type on the screen; a type that silently fails to log is a blocker.
5. This audit covers behavior and data flow only; styling stays with the applicable design-audit skill.
## Available connectors

Use `muse.connector_search` to find the current connector docs before following
recovered instructions.
