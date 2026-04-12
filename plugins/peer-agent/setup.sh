#!/usr/bin/env sh
set -eu

# ──────────────────────────────────────────────
# Peer-Agent Plugin — Setup Script
#
# Called by the Claude Code plugin system after install.
# Handles three things:
#   1. Detect and remove old install.sh skill copies
#      from ~/.claude/skills/ to prevent duplicates
#      (the plugin system now provides the skills).
#   2. Install CLI tools (ask-codex, peer-debate, etc.)
#      via install.sh --cli-only.
#   3. Report what happened.
# ──────────────────────────────────────────────

PLUGIN_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$PLUGIN_DIR/../.." && pwd)

CLAUDE_SKILL_BASE=${CLAUDE_HOME:-"$HOME/.claude"}/skills
CODEX_SKILL_BASE=${CODEX_HOME:-"$HOME/.codex"}/skills

# Known skills that install.sh previously copied
PEER_SKILLS="peer-agent peer-consensus"

# ── Step 1: Migrate away from old install.sh skill copies ──

migrated=0
for skill in $PEER_SKILLS; do
  old_dir="$CLAUDE_SKILL_BASE/$skill"
  if [ -d "$old_dir" ]; then
    rm -rf "$old_dir"
    echo "Migrated: removed old $old_dir (now provided by plugin)"
    migrated=$((migrated + 1))
  fi

  old_codex_dir="$CODEX_SKILL_BASE/$skill"
  if [ -d "$old_codex_dir" ]; then
    rm -rf "$old_codex_dir"
    echo "Migrated: removed old $old_codex_dir (now provided by plugin)"
    migrated=$((migrated + 1))
  fi
done

if [ "$migrated" -gt 0 ]; then
  echo "Cleaned up $migrated old skill installation(s) from install.sh"
fi

# ── Step 2: Install CLI tools only ──

"$REPO_DIR/install.sh" --cli-only

# ── Step 3: Summary ──

echo ""
echo "peer-agent plugin setup complete."
echo "Skills are now managed by the Claude Code plugin system."
echo "CLI tools (ask-codex, peer-debate, etc.) installed to PATH."
if [ "$migrated" -gt 0 ]; then
  echo "Note: Old skill copies were removed. No duplicates."
fi
