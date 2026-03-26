---
name: "peer-agent"
description: "Use when the user wants to involve Claude Code -- for reviews, patches, edits, debates, or judge rulings on any file. Backed by ask-claude and peer-debate helpers."
---

# Peer-Agent Delegation Skill

Use this skill when the user wants to involve Claude Code during the current Codex session, or when they want Claude and Codex to debate/evaluate together.

If the helper commands are missing or a user reports setup issues, run `peer-agent-doctor` first.

## Trigger phrases (natural language -- match intent, not exact words)

### Single-agent delegation (Codex asks Claude)
- "Ask Claude to review this file"
- "Have Claude look at this code"
- "Get Claude's opinion on this"
- "What would Claude think about this?"
- "Ask Claude to patch / fix this"
- "Have Claude edit this file to do X"

### Debate / evaluation (Claude and Codex together)
- "Debate this file with Claude"
- "Have Claude and Codex review this together"
- "Get both agents to evaluate this"
- "Start a debate about this code"
- "I want a second opinion -- debate this"
- "Have the agents discuss this"
- "Run a peer debate on this file"

### Judge ruling
- "Judge this debate"
- "Get a final ruling on this"
- "Have Claude judge Codex's review"

## Workflow

### For single-agent delegation (review, patch, edit):
1. Resolve the target to a concrete file path.
2. Choose the action:
   - `review` for critique only (default)
   - `patch` for a proposed diff
   - `edit` only when explicitly asked to change the file
3. Run: `ask-claude {action} <target> [instruction...]`
4. Return or summarize Claude's result.

### For debate:
1. Resolve the target to a concrete file path.
2. Determine options from user intent:
   - Number of rounds (default: 3)
   - Who speaks first (default: claude)
   - Mode: review or patch (default: review)
   - Whether to include a judge ruling
3. Run: `peer-debate <target> [instruction...] [--max-rounds N] [--first-speaker claude|codex] [--mode review|patch] [--judge]`
4. Return or summarize the debate transcript.

## Available commands
```
ask-claude review <target> [instruction...]
ask-claude patch  <target> [instruction...]
ask-claude edit   <target> [instruction...]
peer-debate <target> [instruction...] [options]
```

## peer-debate options
- `--max-rounds N` (1-10, default 3)
- `--first-speaker claude|codex` (default claude)
- `--mode review|patch` (default review)
- `--judge` (add a judge ruling after debate)
- `--judge-agent claude|codex` (who judges, default: opposite of last speaker)
- `--quiet` (only print final transcript)

## Rules
- Prefer `review` unless the user clearly wants a patch or direct edit.
- For `edit`, keep scope to the specified file unless explicitly widened.
- For debate, default to 3 rounds with Claude speaking first unless the user specifies otherwise.
- All results are saved to `${PEER_AGENT_HOME:-~/.local/share/peer-agent}/artifacts/` (reviews/, patches/, edits/, debates/).
- This is a user-level skill -- works from any project, no repo-local setup needed.
