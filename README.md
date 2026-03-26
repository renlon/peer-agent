# peer-agent

`peer-agent` is a small cross-CLI bridge for coding agents. It lets Codex ask Claude Code for a review, lets Claude Code ask Codex for a review, and can run a structured back-and-forth debate with an optional judge pass.

The current implementation is intentionally narrow:

- no third-party Python dependencies
- file-targeted workflows instead of repo-wide orchestration
- user-level install, not project-local setup
- optional skill entrypoints for both Codex and Claude Code

The intended user outcome is:

- install once at the user level
- work from any repo
- use natural language inside either Codex or Claude Code to ask the other agent to review, patch, edit, judge, or debate a file
- stay language-agnostic across different codebases

## Why this can be a real repo

The code was already most of the way there. The reusable core is a handful of Python scripts plus prompt templates. What was missing was product shape:

- a clean repo layout
- a one-command installer
- explicit skill files for both tools
- a health check
- documentation that does not assume your machine

This repo now provides those pieces.

## What gets installed

`./install.sh` copies the project into `${PEER_AGENT_HOME:-~/.local/share/peer-agent}`, symlinks commands into `${PEER_AGENT_BIN_DIR:-~/.local/bin}`, and installs personal skills for:

- Codex: `~/.codex/skills/peer-agent/SKILL.md`
- Claude Code: `~/.claude/skills/peer-agent/SKILL.md`

Installed commands:

```bash
ask-claude
ask-codex
peer-debate
peer-agent-doctor
```

## Prerequisites

- Python 3
- `claude` on `PATH` for Claude delegation
- `codex` on `PATH` for Codex delegation
- both CLIs already authenticated in their own normal way

Users are responsible for setting up the underlying tools and credentials themselves. `peer-agent` does not install, log in to, or manage credentials for Claude Code, Codex CLI, or project-specific toolchains such as Xcode and Xcode Command Line Tools.

Current development target:

- Claude Code 2.1.81 or newer
- Codex CLI 0.116.0 or newer

Those are the versions validated during this extraction.

## Install

```bash
git clone <your-repo-url> peer-agent
cd peer-agent
./install.sh
peer-agent-doctor
```

More detail:

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)

## Platform Notes

The current installer is a POSIX shell script. In practice, that means:

- it is intended for Unix-like environments
- it is not Bash-specific and does not require Zsh specifically
- it should work in `sh`-compatible shells on macOS and Linux
- it is not a native Windows installer

As of March 22, 2026, the official Claude Code docs I checked say Claude Code supports macOS, Linux, and Windows via WSL, while the official OpenAI Codex CLI quickstart I checked explicitly lists macOS and Linux release artifacts. Based on that, the safest support statement for this repo today is: macOS and Linux first, with WSL only as an unverified follow-up target.

## Example usage

```bash
ask-claude review docs/plan.md "focus on correctness and missing tests"
ask-codex patch src/app.ts "propose the smallest safe fix"
peer-debate src/server.py "debate whether the retry logic is safe" --judge
```

From Codex, the installed `peer-agent` skill teaches it to use `ask-claude` and `peer-debate`.

From Claude Code, the installed `peer-agent` skill teaches it to use `ask-codex` and `peer-debate`.

## Distribution recommendation

For today, the best distribution shape is:

1. Publish this as a normal GitHub repository.
2. Tag releases.
3. Keep the install path to one command: `./install.sh` for cloned installs, and later a raw `curl ... | sh` installer if you want zero-friction onboarding.
4. Treat the skills as required for natural-language UX, not optional decoration. The bridge binaries and the installed skills are a matched set.

That is better than starting with a full rewrite to JavaScript or an MCP server because it keeps setup low and matches how both tools already work today.

Before publishing, add an explicit license. Without one, people can read the repo but do not automatically have permission to reuse or redistribute it.

## Current limitations

- Single-file snapshotting is the core abstraction today.
- No shared session memory yet.
- No direct MCP transport between tools.
- No official Windows installer yet.
- Debate quality still depends on how much extra context each CLI decides to read.

## Repo layout

```text
peer-agent/
├── README.md
├── install.sh
├── uninstall.sh
├── docs/
├── prompts/
├── scripts/
└── skills/
    ├── claude/
    └── codex/
```

## Next likely improvements

- add a session-memory registry for follow-up requests
- add directory and PR targets
- add a machine-readable `doctor --json`
