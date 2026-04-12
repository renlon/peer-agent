#!/usr/bin/env sh
set -eu

# ──────────────────────────────────────────────
# Peer-Agent Plugin — Setup Script
# Installs CLI tools (ask-codex, peer-debate, etc.)
# that the peer-agent and peer-consensus skills depend on.
# ──────────────────────────────────────────────

PLUGIN_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$PLUGIN_DIR/../.." && pwd)

# Delegate to the main install script
exec "$REPO_DIR/install.sh"
