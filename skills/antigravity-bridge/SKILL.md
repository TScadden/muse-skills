---
name: antigravity-bridge
description: Delegate work to Google Antigravity (the agy CLI) running on a second, always-on computer, reached over SSH through a scheduled-task bridge. CAPABILITY-GATED: never install or set up without first confirming the user has an Antigravity account, an always-on machine, and SSH access. Use when the user wants a second AI agent workforce on their own hardware, or asks to hand work to Antigravity/agy.
---

# Antigravity Bridge: delegate to agy on your own always-on computer

Google Antigravity ships a CLI (`agy`) that runs agentic coding and
research jobs under the user's own Google account. If the user has a
second computer that stays on, Muse can hand self-contained jobs to
that machine's `agy` over SSH and read the results back: a second
workforce, on a separate usage budget, without the user relaying
anything by hand.

## STOP: capability gate (do this before installing or setting up anything)

This skill only works for a specific setup. Do NOT install it, copy its
scripts, or create any bridge files until you have asked the user these
three questions and they have answered yes to ALL three:

1. **Antigravity account**: "Do you have a Google Antigravity account,
   with the `agy` CLI installed and signed in with your Google (Gmail)
   account on the other computer?" The login lives on that machine and
   belongs to the user; you never see or handle the credential.
2. **An always-on second computer**: "Is there another desktop or
   computer that stays on and stays logged in, where Antigravity can
   run?" A locked-after-reboot machine is not enough: Antigravity's
   saved login is tied to the user's interactive session, so the user
   must actually be logged in on that machine when jobs run.
3. **SSH access**: "Can this machine reach that computer over SSH?"
   (A LAN address, a VPN such as Tailscale, or any SSH route the user
   already uses all count.)

If any answer is no or unclear, stop. Explain plainly which piece is
missing and what it would take to have it, and leave the skill
uninstalled. Do not half-install it "for later". If all three are yes,
continue to setup, and record their answers with the placeholders below.

## Placeholders

Ask for these at setup and store the answers privately (your memory of
the user or a `LOCAL_VALUES.md` in the installed folder). Never send
them back to any shared repo.

- `<REMOTE_PC_HOST>`: the SSH host or address of the always-on computer
  (for example a Tailscale IP or a hostname on their LAN).
- `<REMOTE_PC_USER>`: the Windows username on that computer.
- `<REMOTE_BRIDGE_DIR>`: the bridge folder on that computer, default
  `C:\Users\<REMOTE_PC_USER>\agy-bridge`.
- How SSH connects (key file, proxy, or wrapper script) is the user's
  existing setup; ask how they already SSH in and use that route.

## Why a bridge (the one non-obvious fact)

On Windows, Antigravity's saved sign-in is bound to the user's
interactive desktop session. A plain SSH session runs outside that
session, so `agy` started directly over SSH cannot use the saved login
and fails with an auth error. The bridge solves it with a Windows
scheduled task whose principal is `LogonType Interactive`: the task
runs inside the logged-in session, where the login works.

The pipe for every job:

1. Muse writes a `job.json` into `<REMOTE_BRIDGE_DIR>` on the remote
   machine (SCP or an SSH file copy).
2. Muse starts the task over SSH: `Start-ScheduledTask -TaskName AgyBridge`.
3. The task's `run.ps1` reads `job.json`, runs `agy`, and writes
   `out.txt`, `err.txt`, and `done.txt` (the exit code) in the same
   folder.
4. Muse reads those three files back. `done.txt` existing is what
   "finished" means; never assume success from silence.

The two scripts in this folder are the whole bridge:

- `setup-bridge.ps1`: run once on the remote machine (in the user's own
  session, as them) to register the `AgyBridge` task. It uses
  `$env:USERPROFILE`, so it works for any user unchanged.
- `run.ps1`: the task body. It resolves its own folder from its script
  location, so the bridge directory can live anywhere.

Preconditions for every job: the remote machine is on, and the user is
logged in on it. If a job returns an auth error, the session is gone:
log it, wait, and tell the user only if they asked for the work
directly. Never pester them to log in for background delegations.

## Job shapes

Prompt job (the normal case), `job.json`:

```json
{"kind": "prompt", "prompt": "...", "workdir": "C:\\path\\to\\work", "model": "<optional>", "effort": "<optional>", "mode": "<optional>"}
```

`run.ps1` executes `agy -p <prompt> --print-timeout 600s
--dangerously-skip-permissions` plus `--model`, `--effort`, and
`--mode` when present. The skip-permissions flag is why job scoping
below matters: inside the job, agy acts without asking.

Command job, for `agy` subcommands such as listing models:

```json
{"kind": "command", "args": ["models"]}
```

Run `{"kind": "command", "args": ["models"]}` once at setup and record
which models the account actually offers; model names are
account-specific and change over time, so never hardcode another
account's list.

## Quota awareness

Antigravity usage on a Google AI plan is metered in pools (grouped by
model family), each with a short-window limit that refreshes every few
hours and a weekly cap that overrides it. A bridge prompt job with the
prompt `/usage` returns the current percentages and reset times. Probe
it before any unusually large delegation, and periodically if you
delegate often. Sensible house rules: delegate freely above ~25%
weekly remaining in a pool, small jobs only at 10 to 25%, and hold a
pool under 10% until its reset. Keep any paid-overage setting OFF;
enabling overages is spending, and spending is always the user's call.
When the quota is exhausted, delegated work waits; your own work
continues.

## What to delegate, and what to keep

Delegate to agy:

- Codebase comprehension: mapping an unfamiliar repo, tracing how a
  feature flows, "where does X happen" across many files.
- Pattern and symbol hunts across a large workspace.
- Scoped multi-file edits that follow existing patterns: boilerplate
  features, CRUD, test scaffolding, repetitive refactors, dependency
  bumps with test reruns.
- Scoped bug fixes: given a failing test or a stack trace, draft the
  fix and rerun the tests.
- Parallel investigations and batch jobs; headless `-p` supports
  structured JSON output for scripted results.
- Second-opinion reviews from a different model family than the
  author of the work.

Keep with yourself, never delegate:

- Anything gated on the user's explicit approval in your own rules
  (publishing, purchases, sending messages as the user). Delegation
  changes none of those gates.
- Final review and merges. Agy's output is a draft until you have read
  the diff and the relevant tests pass. Agents can claim success they
  did not achieve; verify before reporting anything as done.
- Work that needs the user's personal context or your memory of them.
- Secrets and credentials. Never put them in a job prompt; job files
  and outputs are plain text on the remote machine.

## Job prompt discipline

- Every prompt is self-contained: the goal, the exact files or folders
  in scope, the constraints, what done looks like, and an instruction
  to summarize what changed and what was NOT verified.
- Name the model, effort, and mode when they matter (`plan` mode for
  read-only analysis, `accept-edits` for scoped code work).
- For code work, use a scratch copy or a branch the user controls,
  never their live checkout, and disable pushing on any clone agy
  touches unless the user says otherwise. Review every diff yourself
  before it lands anywhere real.
- Log notable delegations (date, model, one-line job summary) so quota
  use stays explainable to the user.
