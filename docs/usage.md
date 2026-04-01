# Usage Guide

`peer-agent` is usually used from inside Codex or Claude Code through the installed `peer-agent` skill.

After installation, the normal workflow is:

1. Open your repository in Codex or Claude Code.
2. Ask for cross-agent help in natural language.
3. Let the installed skill translate that request into the helper command.

## Natural-language examples

One good fit is production-risk code where a second opinion matters before you ship a fix.

From Codex:

- "Ask Claude to review `src/billing/webhook_handler.ts` for duplicate-charge risk, idempotency gaps, and missing tests."
- "Ask Claude to patch `src/billing/webhook_handler.ts` with the smallest safe change."
- "Debate `src/billing/webhook_handler.ts` with Claude and include a judge."

From Claude Code:

- "Ask Codex to review `src/billing/webhook_handler.ts` for duplicate-charge risk and missing tests."
- "Have Codex edit `src/billing/webhook_handler.ts` directly."
- "Debate this file with Codex and include a judge."

## Installed commands

The install flow places four helper commands on `PATH` under `${PEER_AGENT_BIN_DIR:-~/.local/bin}`:

- `ask-claude`: backend helper that asks Claude Code to `review`, `patch`, or `edit` one target file
- `ask-codex`: backend helper that asks Codex to `review`, `patch`, or `edit` one target file
- `peer-debate`: backend helper that alternates between Claude Code and Codex for a structured debate about one target file
- `peer-agent-doctor`: verification helper that checks the install, skills, and expected CLI features

You normally do not need to run these directly. They are most useful for debugging, automation, or understanding what the installed skill is doing under the hood.

## Supported requests

- `review`: return findings, risks, and suggested changes only
- `patch`: return a proposed patch without applying it
- `edit`: let the peer CLI modify the target file directly
- `debate`: have both agents take turns evaluating the same file
- `judge`: ask for a final ruling as part of a debate request; it is not a standalone helper command

## Direct command reference

If you do need the low-level helpers directly, these are the main forms:

```bash
ask-claude review "/absolute/or/relative/path/to/file" "focus on correctness and tests"
ask-claude patch "/absolute/or/relative/path/to/file" "propose a minimal fix"
ask-claude edit "/absolute/or/relative/path/to/file" "make the change directly"

ask-codex review "/absolute/or/relative/path/to/file" "focus on correctness and tests"
ask-codex patch "/absolute/or/relative/path/to/file" "propose a minimal fix"
ask-codex edit "/absolute/or/relative/path/to/file" "make the change directly"

peer-debate "/absolute/or/relative/path/to/file" "debate correctness risks" --judge
peer-agent-doctor
```

## Behavior

- Relative paths are resolved against the current working directory unless `--cwd` is provided.
- Prefer quoted absolute paths when invoking the helpers manually from another agent session.
- `review` returns Markdown findings only.
- `patch` returns proposed patch text only, preferably as a unified diff.
- `edit` allows the peer CLI to update only the specified target file unless the instruction explicitly widens scope.
- `peer-debate` alternates between Claude Code and Codex for up to 10 rounds and can add an optional judge pass.
- Commands block until the peer CLI returns.
- Results are printed to stdout and saved under `${PEER_AGENT_HOME:-~/.local/share/peer-agent}/artifacts/`.
- Target content is snapshotted at launch time before the peer CLI starts. Saved artifact metadata records which snapshot was used.

## Artifacts

- Reviews are saved under `artifacts/reviews/`.
- Patch proposals are saved under `artifacts/patches/`.
- Edit summaries are saved under `artifacts/edits/`.
- Debate transcripts and judge rulings are saved under `artifacts/debates/`.
- Failure logs are saved under `artifacts/logs/`.
- Artifact names follow `<launch-timestamp>-<peer>-<target-name>-sha<target-sha12>.<ext>`.
- Each saved artifact or failure log also gets a sidecar metadata file named `<artifact-name>.meta.json`.
- Metadata sidecars include launch timestamp, artifact save timestamp, target path, target mtime, target SHA-256, target byte size, whether content was truncated, and the requested versus actual execution cwd.

## Current limits

- Targets must be files. Directories, PRs, and whole-repo reviews are not first-class yet.
- The helpers snapshot one file, not the full repository graph, so complex review quality still depends on the peer agent reading additional files on its own.
- There is no session-memory layer yet. Each `ask-*` call is currently one-shot.
- The wrappers assume recent Claude Code and Codex CLI versions that support the flags used by `peer-agent-doctor`.

## Failure behavior

- Missing target files, missing peer CLIs, or non-zero peer exits fail the helper.
- Failures are surfaced on stderr and also written to `artifacts/logs/`.
- `peer-agent-doctor` is the fastest way to verify the local install before blaming the wrappers.
