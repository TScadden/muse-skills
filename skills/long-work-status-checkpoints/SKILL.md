---
name: long-work-status-checkpoints
description: Keep the user informed during long or delegated work with result-first status checkpoints, so work never goes silent and 'done' always means verified.
---

# Long Work Status Checkpoints

## Purpose
Stop long or delegated work from going silent, so the user never has to ask whether it is done.

## Workflow
1. At the start of any work expected to run long, span restarts, or be delegated, state in one line: what counts as done, the current milestone, and when the next checkpoint will come.
2. Report at every milestone, result first: the first line says done or not done and the concrete result, then the blocker or next step if any.
3. Never let active long work sit silent past a checkpoint: post a short status at each completed stage and at least every 40 minutes while work is running, even if the status is 'still on step X, no result yet'.
4. If the reporting chain breaks (a restart, a finished subagent, a handed-off run), the next worker re-establishes status proactively from the last recorded milestone before doing more silent work; it does not wait to be asked and does not restart the account from zero.
5. When the user asks 'done?' or 'is it done?', treat it as a missed checkpoint: answer the state plainly in the first line, then what remains and when the next update lands.
6. Close with the verified result and how it was verified, not with 'building now' or a promise.

## Output Contract
Each checkpoint is short: state (done / in progress / blocked), the result or milestone reached, what remains, and the next checkpoint time or trigger. No checkpoint is a long narrative or a plan restated.

## Operating Rules
1. A status update is owed even when nothing changed; silence is never the update.
2. Report the result before the explanation; detail follows only as far as it helps the user judge the state.
3. Do not claim done on an intermediate artifact (build started, code written, CI queued); done means the deliverable exists and was verified.
4. If a checkpoint will be missed, say so before it passes, with the new time.
## Available connectors

Use `muse.connector_search` to find the current connector docs before following
recovered instructions.
