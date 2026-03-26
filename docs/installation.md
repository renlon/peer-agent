# Installation Guide

This project is designed to be installed once at the user level and then work from any repository.

It does not depend on the application stack in the target repository. The bridge talks to the `claude` and `codex` CLIs, not to a specific application runtime.

## Recommended install path today

```bash
git clone <your-repo-url> peer-agent
cd peer-agent
./install.sh
peer-agent-doctor
```

What `./install.sh` does:

1. Copies prompts, scripts, docs, and bundled skill assets into `${PEER_AGENT_HOME:-~/.local/share/peer-agent}`.
2. Symlinks `ask-claude`, `ask-codex`, `peer-debate`, and `peer-agent-doctor` into `${PEER_AGENT_BIN_DIR:-~/.local/bin}`.
3. Installs the personal Codex skill under `~/.codex/skills/peer-agent/`.
4. Installs the personal Claude Code skill under `~/.claude/skills/peer-agent/`.

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

Validated locally during extraction:

- Claude Code `2.1.81`
- Codex CLI `0.116.0`

## Operating system support

The current install flow is based on `install.sh`, which uses POSIX shell behavior, Unix paths, and symlinks.

That means the current repo is:

- validated on macOS
- likely portable to Linux with the same directory conventions
- not a native Windows install flow

It is also shell-compatible rather than Bash-specific. The script uses `/usr/bin/env sh`, so it does not require Bash or Zsh specifically as long as the environment provides a standard POSIX-style shell.

## Why the installer is the primary distribution path

Natural-language invocation in Claude Code and Codex depends on the skill files being installed into each tool's personal skill directory.

That means setup is two-part:

1. install the command-line helpers
2. install the skill definitions

`./install.sh` already does both in one step, which is why it should remain the main onboarding path.

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

If the doctor reports a missing skill, rerun `./install.sh`.
