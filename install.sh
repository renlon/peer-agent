#!/usr/bin/env sh
set -eu

CLI_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --cli-only) CLI_ONLY=true ;;
  esac
done

REPO_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
INSTALL_ROOT=${PEER_AGENT_HOME:-"$HOME/.local/share/peer-agent"}
BIN_DIR=${PEER_AGENT_BIN_DIR:-"$HOME/.local/bin"}
CODEX_SKILL_BASE=${CODEX_HOME:-"$HOME/.codex"}/skills
CLAUDE_SKILL_BASE=${CLAUDE_HOME:-"$HOME/.claude"}/skills

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

if [ "$CLI_ONLY" = true ]; then
  echo "Installed peer-agent CLI tools to $BIN_DIR (--cli-only, skipping skill copy)"
else
  for skill_dir in "$REPO_DIR"/skills/claude/*/; do
    skill_name=$(basename "$skill_dir")
    install_file \
      "$skill_dir/SKILL.md" \
      "$CLAUDE_SKILL_BASE/$skill_name/SKILL.md"
    echo "Installed Claude skill: $skill_name"
  done

  for skill_dir in "$REPO_DIR"/skills/codex/*/; do
    skill_name=$(basename "$skill_dir")
    install_file \
      "$skill_dir/SKILL.md" \
      "$CODEX_SKILL_BASE/$skill_name/SKILL.md"
    echo "Installed Codex skill: $skill_name"
  done

  echo "Installed peer-agent resources to $INSTALL_ROOT"
  echo "Installed commands to $BIN_DIR"
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo "Warning: $BIN_DIR is not currently on PATH" >&2
    ;;
esac

echo "Next step: peer-agent-doctor"
