#!/usr/bin/env sh
set -eu

INSTALL_ROOT=${PEER_AGENT_HOME:-"$HOME/.local/share/peer-agent"}
BIN_DIR=${PEER_AGENT_BIN_DIR:-"$HOME/.local/bin"}
CODEX_SKILL_DIR=${CODEX_HOME:-"$HOME/.codex"}/skills/peer-agent
CLAUDE_SKILL_DIR=${CLAUDE_HOME:-"$HOME/.claude"}/skills/peer-agent

rm -f \
  "$BIN_DIR/ask-claude" \
  "$BIN_DIR/ask-codex" \
  "$BIN_DIR/peer-debate" \
  "$BIN_DIR/peer-agent-doctor"

rm -rf "$INSTALL_ROOT/scripts" "$INSTALL_ROOT/prompts" "$INSTALL_ROOT/docs" "$INSTALL_ROOT/skills"
rm -rf "$CODEX_SKILL_DIR" "$CLAUDE_SKILL_DIR"

echo "Removed peer-agent commands and skills."
echo "Artifacts remain under $INSTALL_ROOT/artifacts unless you delete them manually."
