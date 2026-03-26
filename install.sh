#!/usr/bin/env sh
set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
INSTALL_ROOT=${PEER_AGENT_HOME:-"$HOME/.local/share/peer-agent"}
BIN_DIR=${PEER_AGENT_BIN_DIR:-"$HOME/.local/bin"}
CODEX_SKILL_DIR=${CODEX_HOME:-"$HOME/.codex"}/skills/peer-agent
CLAUDE_SKILL_DIR=${CLAUDE_HOME:-"$HOME/.claude"}/skills/peer-agent

copy_tree() {
  src=$1
  dest=$2
  if [ "$src" = "$dest" ]; then
    return
  fi
  rm -rf "$dest"
  mkdir -p "$dest"
  cp -R "$src"/. "$dest"/
}

install_file() {
  src=$1
  dest=$2
  mkdir -p "$(dirname "$dest")"
  cp "$src" "$dest"
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run peer-agent" >&2
  exit 1
fi

mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
copy_tree "$REPO_DIR/docs" "$INSTALL_ROOT/docs"
copy_tree "$REPO_DIR/prompts" "$INSTALL_ROOT/prompts"
copy_tree "$REPO_DIR/scripts" "$INSTALL_ROOT/scripts"
copy_tree "$REPO_DIR/skills" "$INSTALL_ROOT/skills"

chmod +x \
  "$INSTALL_ROOT/scripts/ask-claude" \
  "$INSTALL_ROOT/scripts/ask-codex" \
  "$INSTALL_ROOT/scripts/peer-debate" \
  "$INSTALL_ROOT/scripts/peer-agent-doctor"

ln -sfn "$INSTALL_ROOT/scripts/ask-claude" "$BIN_DIR/ask-claude"
ln -sfn "$INSTALL_ROOT/scripts/ask-codex" "$BIN_DIR/ask-codex"
ln -sfn "$INSTALL_ROOT/scripts/peer-debate" "$BIN_DIR/peer-debate"
ln -sfn "$INSTALL_ROOT/scripts/peer-agent-doctor" "$BIN_DIR/peer-agent-doctor"

install_file \
  "$REPO_DIR/skills/codex/peer-agent/SKILL.md" \
  "$CODEX_SKILL_DIR/SKILL.md"
install_file \
  "$REPO_DIR/skills/claude/peer-agent/SKILL.md" \
  "$CLAUDE_SKILL_DIR/SKILL.md"

echo "Installed peer-agent resources to $INSTALL_ROOT"
echo "Installed commands to $BIN_DIR"
echo "Installed Codex skill to $CODEX_SKILL_DIR"
echo "Installed Claude skill to $CLAUDE_SKILL_DIR"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo "Warning: $BIN_DIR is not currently on PATH" >&2
    ;;
esac

echo "Next step: peer-agent-doctor"
