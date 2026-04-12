#!/usr/bin/env sh
set -eu

INSTALL_ROOT=${PEER_AGENT_HOME:-"$HOME/.local/share/peer-agent"}
BIN_DIR=${PEER_AGENT_BIN_DIR:-"$HOME/.local/bin"}
CODEX_SKILL_BASE=${CODEX_HOME:-"$HOME/.codex"}/skills
CLAUDE_SKILL_BASE=${CLAUDE_HOME:-"$HOME/.claude"}/skills

rm -f \
  "$BIN_DIR/ask-claude" \
  "$BIN_DIR/ask-codex" \
  "$BIN_DIR/peer-debate" \
  "$BIN_DIR/peer-agent-doctor"

rm -rf "$INSTALL_ROOT/scripts" "$INSTALL_ROOT/prompts" "$INSTALL_ROOT/docs" "$INSTALL_ROOT/skills"

# Remove all skills installed by install.sh
for skill_dir in "$CLAUDE_SKILL_BASE"/peer-agent "$CLAUDE_SKILL_BASE"/peer-consensus; do
  rm -rf "$skill_dir"
done
for skill_dir in "$CODEX_SKILL_BASE"/peer-agent "$CODEX_SKILL_BASE"/peer-consensus; do
  rm -rf "$skill_dir"
done

echo "Removed peer-agent commands and skills."
echo "Artifacts remain under $INSTALL_ROOT/artifacts unless you delete them manually."
