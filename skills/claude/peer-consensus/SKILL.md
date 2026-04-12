---
name: peer-consensus
description: Iterative peer review loop between Claude Code and Codex until both agree a document is ready. Use when the user asks to "review until consensus", "get Codex to sign off", "iterate with Codex until ready", "peer review this doc", "review and revise until done", or any variation of wanting Claude and Codex to collaboratively refine a document through multiple review rounds. Also use when the user says "/peer-consensus". After consensus is reached, proceed directly to implementation without pausing for manual user review — the peer review substitutes for the human checkpoint.
---

# Peer Consensus Review

An iterative review loop: Codex reviews a document, Claude revises based on feedback, and the cycle repeats until both agree it's ready. This replaces the manual "check in with user" step — once consensus is reached, proceed directly to the next phase (implementation, execution, etc.).

## Arguments

`/peer-consensus [file-path] [optional instructions]`

- **file-path**: Path to the document to review. If omitted, use the most recently created or modified document in the current conversation.
- **instructions**: Optional focus areas or constraints for the review (e.g., "focus on API design", "check for security issues").

## The Consensus Loop

### Round Structure

Each round has three phases:

1. **Submit** — Send the document to Codex for review via `ask-codex review <file> [instructions]`
2. **Assess** — Read Codex's feedback. Categorize each item:
   - **Substantive**: Changes to correctness, completeness, architecture, logic, or security
   - **Minor**: Style, formatting, naming preferences, optional suggestions
3. **Revise or Conclude**:
   - If substantive feedback exists: revise the document, announce what changed, start the next round
   - If only minor/no feedback remains: consensus is reached

### Announcing Each Round

At the start of each round, announce clearly:

```
## Peer Consensus — Round N/5

Sending <filename> to Codex for review...
```

After receiving feedback, summarize it before revising:

```
### Codex Feedback (Round N)
- [Substantive] <issue summary> — will fix
- [Substantive] <issue summary> — will fix
- [Minor] <style suggestion> — noted, skipping
```

After revising:

```
### Revisions Made
- <what changed and why>

Sending revised version for Round N+1...
```

### Consensus Detection

Consensus is reached when ANY of these is true:

- Codex's review contains **no substantive suggestions** — only minor items, praise, or "looks good"
- Codex explicitly states the document is ready, approved, or has no blocking issues
- The **Findings** section says "No blocking findings" or equivalent
- The **Recommended Changes** section contains only optional/cosmetic items

When consensus is reached, announce:

```
## Consensus Reached (Round N/5)

Codex and Claude Code agree this document is ready.

### Summary of All Rounds
- Round 1: [brief summary of key feedback and revisions]
- Round 2: [brief summary]
- ...
- Round N: Consensus — no substantive changes remaining

### Final State
<one-line description of the document's final form>
```

### Safety Cap

**Maximum 5 rounds.** If round 5 completes without consensus:

1. Summarize remaining disagreements
2. Present them to the user: "After 5 rounds, these items remain unresolved: [list]. How would you like to proceed?"
3. Do NOT auto-continue past 5 rounds

### Disagreement Handling

If you believe Codex's feedback is incorrect or would make the document worse:

- Do NOT silently ignore it
- Revise what you agree with, then note your disagreement clearly in the round summary
- In the next round's `ask-codex review` call, append an instruction explaining your reasoning so Codex can reconsider with context
- If the same disagreement persists for 2+ rounds, flag it for the user rather than looping

## After Consensus: Auto-Continue

This is the key behavioral change. Once consensus is reached:

**Proceed directly to the next step without pausing for manual user approval.** The Codex peer review serves as the review checkpoint. Specifically:

- If the document is a **plan or design doc**: Begin execution (invoke executing-plans or subagent-driven-development as appropriate)
- If the document is a **spec**: Start implementation
- If the document is **standalone** (not tied to a next step): Report consensus and stop

This overrides the default superpowers behavior of pausing for human approval after plan review. The rationale: the user explicitly chose peer-consensus review as their approval mechanism — asking them to re-approve what two agents already agreed on adds friction without value.

**Exception**: If the consensus summary includes unresolved minor items that could affect implementation, list them briefly before proceeding so the user can interrupt if needed. But do not wait for a response — proceed after a brief pause.

## Error Handling

- If `ask-codex` fails or times out: retry once. If it fails again, report the error and ask the user how to proceed.
- If the document doesn't exist at the given path: ask the user to confirm the path.
- If `ask-codex` is not installed: run `peer-agent-doctor` and report the issue.
