# Installation Guide

Install `peer-agent` once at the user level, then use it from any repository.

The bridge talks to the `claude` and `codex` CLIs. It does not depend on the application stack in the repository you are working on.

## Recommended install path

```bash
git clone https://github.com/renlon/peer-agent.git
cd peer-agent
./install.sh
peer-agent-doctor
```

## What `./install.sh` does

1. Copies prompts, scripts, docs, and bundled skill assets into `${PEER_AGENT_HOME:-~/.local/share/peer-agent}`.
2. Symlinks `ask-claude`, `ask-codex`, `peer-debate`, and `peer-agent-doctor` into `${PEER_AGENT_BIN_DIR:-~/.local/bin}`.
3. Installs the personal Codex skill under `~/.codex/skills/peer-agent/`.
4. Installs the personal Claude Code skill under `~/.claude/skills/peer-agent/`.

Installed commands:

- `ask-claude`: asks Claude Code to `review`, `patch`, or `edit` one file
- `ask-codex`: asks Codex to `review`, `patch`, or `edit` one file
- `peer-debate`: runs both agents against the same file in alternating rounds, with an optional judge pass
- `peer-agent-doctor`: checks the install and confirms the required CLIs, flags, and skill files are available

## Prerequisites

- Python 3
- Claude Code installed and authenticated
- Codex CLI installed and authenticated
- `~/.local/bin` on `PATH`, or a custom `PEER_AGENT_BIN_DIR` already on `PATH`

You are responsible for setting up those underlying tools yourself. `peer-agent` does not provision or authenticate:

- Claude Code
- Codex CLI
- project-specific toolchains such as Xcode or Xcode Command Line Tools
- repository-specific credentials, SDKs, or cloud logins

Validated locally:

- Claude Code `2.1.81`
- Codex CLI `0.116.0`

## Operating system support

The current install flow is based on `install.sh`, which uses POSIX shell behavior, Unix paths, and symlinks.

That means the current repo is:

- validated on macOS
- likely portable to Linux with the same directory conventions
- not a native Windows install flow

The script uses `/usr/bin/env sh`, so it does not require Bash or Zsh specifically as long as the environment provides a standard POSIX-style shell.

## Why `install.sh` matters

Natural-language use inside Codex and Claude Code depends on the skill files being installed into each tool's personal skill directory.

That means setup is two-part:

1. install the command-line helpers
2. install the skill definitions

`./install.sh` already does both in one step. After that, the normal way to use `peer-agent` is from inside Codex or Claude Code, not by memorizing the helper commands.

## Verification

Run:

```bash
peer-agent-doctor
```

Expected checks:

- both CLIs found
- required CLI flags found
- Codex skill file installed
- Claude skill file installed

## Troubleshooting

If `peer-agent-doctor` says the bin directory is not on `PATH`, add it in your shell config:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

If Codex or Claude Code does not notice the new `peer-agent` skill right away, start a new session after running `./install.sh`.

If the doctor reports a missing skill, rerun `./install.sh`.
