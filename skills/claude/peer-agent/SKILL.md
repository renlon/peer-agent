---
name: peer-agent
description: Ask Codex to review, patch, edit, or debate a file from Claude Code using the installed ask-codex and peer-debate helpers.
allowed-tools: Bash(ask-codex:*), Bash(peer-debate:*), Bash(peer-agent-doctor:*)
---

# Peer-Agent Delegation Skill

Use this skill when the user explicitly wants a Codex second opinion from within Claude Code.

If the helper commands are missing or the user reports setup issues, run `peer-agent-doctor` first and summarize the failure instead of guessing.

## Trigger intent

- "Ask Codex to review this file"
- "Have Codex patch this"
- "Let Codex edit this file"
- "Debate this with Codex"
- "Ask Codex to judge the disagreement"

## Workflow

### For single-agent delegation
1. Resolve the target to a concrete file path.
2. Choose the action:
   - `review` for critique only
   - `patch` for a proposed diff
   - `edit` only when the user explicitly wants Codex to change the file
3. Run `ask-codex {action} <target> [instruction...]`
4. Return or summarize Codex's result.

### For debate
1. Resolve the target to a concrete file path.
2. Determine options from user intent:
   - rounds (default 3)
   - first speaker (default claude)
   - mode `review` or `patch` (default `review`)
   - whether to include a judge ruling
3. Run `peer-debate <target> [instruction...] [--max-rounds N] [--first-speaker claude|codex] [--mode review|patch] [--judge]`
4. Return or summarize the transcript.

## Available commands

```bash
ask-codex review <target> [instruction...]
ask-codex patch  <target> [instruction...]
ask-codex edit   <target> [instruction...]
peer-debate <target> [instruction...] [options]
peer-agent-doctor
```

## Rules

- Prefer `review` unless the user clearly wants a patch or direct edit.
- Keep `edit` scope to the specified file unless the instruction explicitly widens scope.
- Default debate settings are 3 rounds, Claude first, `review` mode, no judge.
- Saved artifacts live under `${PEER_AGENT_HOME:-~/.local/share/peer-agent}/artifacts/`.
