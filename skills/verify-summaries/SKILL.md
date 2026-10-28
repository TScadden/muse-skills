---
name: verify-summaries
description: Verify delegated work, research, and subagent summaries against the full source before reporting conclusions, and correct wrong relayed claims plainly.
---

# Verify Summaries Against the Full Source Before Reporting

## Treat the summary as a lead, not the finding

- Read the full report, transcript, or primary source behind any delegated run, research pass, or subagent result before you relay its conclusion to the user.

- Give blocking claims extra scrutiny, such as a login being expired, a service being free or paid, a feature being unavailable, or a move being impossible. Verify those claims in the full output or at the live source before you repeat them.

- Check whether the full output contains the very data the summary says is missing. A run that returned complete lineup, standings, or account data cannot also support a claim that access was blocked.

- Reconcile the numbers in the summary against the numbers in the full report. Report only the figures that agree, and name the disagreement when they do not.

## Report what you verified

- State the source you checked, in plain words, when you correct or confirm a summary claim. Say the full report governs when the two disagree.

- Carry research claims about price, availability, or limits as unverified until a live check confirms them. A provider page, a blog post, or an earlier research report does not settle what the live service will accept.

- Label any claim you could not verify as unverified instead of presenting it as fact, and say what check would settle it.

- Correct a wrong relayed claim in one plain line as soon as the full source shows it, without rearguing the summary.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Open the underlying artifact, file, or browser result itself when the full report is ambiguous, and let that primary record settle the claim.

- Ask the delegated worker a narrow follow up question about the disputed line instead of rerunning the whole task.
