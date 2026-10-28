---
name: subagent-teams
description: Automatically break suitable tasks into delegated work: spawn subagents for independent or long-running parts, run independent pieces in parallel, and form a small role-based team under one coordinator when a task needs several specialists at once. Verify everything that comes back before reporting it. Use when a task is large, multi-part, parallelizable, long-running, research-heavy, or needs specialist roles (research, building, checking, quality control) working at the same time.
---

# Subagents and Teams

Delegate so the user stays unblocked and the work gets specialist depth,
without losing track of what is running or reporting results you have not
checked. You remain responsible for the whole result, including anything a
subagent or team produced.

## Decide the shape first

**Do it yourself** when the task is a single step, tightly sequential, a
quick answer, or the user asked you personally. Delegation has overhead;
spend it only where it buys parallelism, depth, or responsiveness.

**One subagent** when one well-bounded piece can run in the background
while you stay with the user: a research pass, a long build, a big read.

**Parallel subagents** when two or more parts are truly independent (no
shared files, accounts, carts, or browser state between them). Spawn them
all in the same turn, one per part.

**A team with a coordinator** when the task needs several specialists whose
work interlocks: spawn ONE coordinator and let it fan out to its own
workers. Nesting stops there; a coordinator's workers do not spawn their
own subagents. The coordinator consolidates everything into one result.

**Never delegate live website work to a generic subagent.** Signing in,
clicking, forms, checkouts, and other multi-step work on real websites goes
through the browser route, not a child agent.

## Write briefs that stand alone

A subagent starts from your brief, not from the user's trust in you. Every
brief states:

1. The task and the outcome wanted, in the user's terms.
2. The facts it needs that are not obvious from context: names, dates,
   constraints, earlier decisions, attempt limits, stop conditions.
3. What "done" looks like and what to report back: result first, evidence,
   failures and uncertainties preserved, never smoothed over.
4. The limits: what not to touch, what needs approval, what is out of scope.

Pass only the information the task needs. Never include passwords, codes,
or unrelated private history in a brief, and never let a brief expand the
user's authorization: a subagent's authority is exactly the authority in
the original request, restated, never enlarged.

## Forming a team

Give the team a small written charter before work starts:

- **Roles**: a handful of named roles, each with a one-line job (for
  example: dispatcher, researcher, builder, fact checker, quality gate).
  One role owns consolidation; the user hears one voice, not five.
- **Decision rule**: state up front how the team decides (coordinator
  decides, majority vote, or a named role breaks ties), and which
  decisions are never the team's to make and must go back to the user.
- **Evidence rule**: any role can be required to show its sources; a
  data-first role can feed every other role the same verified packet
  before a decision, so votes and conclusions rest on shared facts.
- **Quality gate**: for high-stakes deliverables, one role's only job is
  checking the work against the brief, with the power to send it back.
- **Lessons**: when a job ends, distill what went wrong and right into a
  short team note the next job reads first. Teams that do not keep lessons
  repeat their mistakes.

## While work runs

- Tell the user in one line what you delegated and what you are still
  handling yourself, then keep serving the conversation. Do not narrate
  the machinery.
- Never promise a finish time you do not control; report the last observed
  state instead.
- Do not poll in a loop. Results arrive on their own; answer status
  questions from a single fresh check, in plain words: running, done,
  blocked, or failed.
- Long work follows the status-checkpoint discipline: result first at
  every milestone, silence never counts as an update.

## When results come back

- Read the full report, not its summary, before relaying conclusions.
  Reconcile numbers and claims against the underlying evidence; where a
  summary and the full output disagree, the full output governs.
- Before repeating any irreversible action a worker may already have
  completed (a send, a purchase, a deletion), establish whether it already
  took effect. A failed report does not prove nothing happened.
- If a worker failed or was interrupted, inspect what it actually did
  before deciding to retry, replace, or close it. Do not silently drop
  delegated work.
- Report to the user as one result: what was asked, what was done, what
  was verified, and what is still open. Attribute team findings to the
  team plainly; keep internal agent bookkeeping out of the reply.

## Templates

**Subagent brief**

> Task: <what to do>. Outcome: <what done looks like>. Context you need:
> <facts, decisions, identifiers>. Constraints: <limits, stop conditions,
> what needs approval>. Report back: result first, then evidence, then
> anything that failed or is uncertain.

**Team charter**

> Mission: <the standing job>. Roles: <name, one-line job> x N.
> Coordinator: <name> consolidates and speaks for the team. Decisions:
> <rule>. Evidence: <what every decision must rest on>. Gates: <what the
> quality gate checks before anything ships>. Never: <the team's hard
> limits>. Lessons live in: <file or note the team reads first>.
