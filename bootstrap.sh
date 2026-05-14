#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SUPERPOWERS_DIR="$ROOT/superpowers"
LAMBDATEST_AGENT_SKILLS_DIR="$ROOT/lambdatest-agent-skills"
SKILLS_DIR="$ROOT/skills"
AGENTS_SKILLS="$HOME/.agents/skills"

if [[ -d "$SUPERPOWERS_DIR/.git" ]]; then
  git -C "$SUPERPOWERS_DIR" pull --ff-only origin main
else
  git clone https://github.com/obra/superpowers.git "$SUPERPOWERS_DIR"
fi

if [[ -d "$LAMBDATEST_AGENT_SKILLS_DIR/.git" ]]; then
  git -C "$LAMBDATEST_AGENT_SKILLS_DIR" pull --ff-only origin main
else
  git clone https://github.com/LambdaTest/agent-skills.git "$LAMBDATEST_AGENT_SKILLS_DIR"
fi

if [[ -e "$AGENTS_SKILLS" && ! -L "$AGENTS_SKILLS" ]]; then
  echo "Refusing to replace existing non-symlink: $AGENTS_SKILLS" >&2
  exit 1
fi

mkdir -p "$HOME/.agents"
ln -sfn "$SKILLS_DIR" "$AGENTS_SKILLS"
ln -sfn ../superpowers/skills "$SKILLS_DIR/superpowers"
ln -sfn ../lambdatest-agent-skills/rspec-skill "$SKILLS_DIR/rspec-skill"

echo "Skills linked into Codex at $AGENTS_SKILLS"
