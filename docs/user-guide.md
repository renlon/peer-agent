# User Guide

The goal is simple:

After installation, a user should be able to speak naturally inside either Codex or Claude Code and ask the other agent to review, patch, edit, or debate a file, with an optional judge at the end of a debate.

This assumes the user has already installed and authenticated the underlying agent CLIs, and has already installed any project-specific development tools their repository needs.

## Natural-language examples

The most reliable trigger style is explicit intent:

- "Ask Claude to review ..."
- "Ask Codex to patch ..."
- "Debate this with Claude ..."
- "Debate this with Codex and include a judge ..."

### From Codex

- "Ask Claude to review `src/auth.ts`."
- "Have Claude debate this change with you."
- "Debate this file with Claude and include a judge."

The installed Codex skill maps those requests to the helper commands:

- `ask-claude`
- `peer-debate`

### From Claude Code

- "Ask Codex to review `src/server.ts`."
- "Have Codex propose a patch for this file."
- "Debate this implementation with Codex and include a judge."

The installed Claude skill maps those requests to:

- `ask-codex`
- `peer-debate`

## What the installed commands do

- `ask-claude`: asks Claude Code to work on one file in `review`, `patch`, or `edit` mode
- `ask-codex`: asks Codex to work on one file in `review`, `patch`, or `edit` mode
- `peer-debate`: has both agents take turns on one file and can optionally add a judge pass
- `peer-agent-doctor`: verifies that the install, skill files, and expected CLI flags are present

Those commands are the backend. The primary user experience is still the natural-language skill path inside Codex and Claude Code.

## Supported requests

- `review`: use when you want findings, risks, and suggested changes only
- `patch`: use when you want a proposed diff without applying it
- `edit`: use when you explicitly want the peer agent to modify the target file
- `debate`: use when you want both agents to take turns evaluating the same file
- `judge`: ask for a final ruling as part of the debate request

## What "natural language" actually means here

This project does not do its own natural-language parsing. Instead, it installs skill definitions into Codex and Claude Code so those tools know:

- when a user is asking for cross-agent help
- which helper command to run
- what defaults to use for review versus patch versus debate

So the natural-language experience depends on the skills being installed correctly, not just the binaries existing on `PATH`.

If you need the low-level shell forms for automation or troubleshooting, see [Usage Guide](usage.md).

## Current limits

- The target must currently be a file.
- The bridge snapshots one target file before invocation.
- Session memory across repeated follow-up requests is not implemented yet.
- Complex repo-wide architectural debates are still better served by passing explicit paths and instructions.
