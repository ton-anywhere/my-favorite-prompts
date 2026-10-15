#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SUPERPOWERS_DIR="$ROOT/superpowers"
LAMBDATEST_AGENT_SKILLS_DIR="$ROOT/lambdatest-agent-skills"
IMPECCABLE_DIR="$ROOT/impeccable"
STEIPETE_AGENT_SCRIPTS_DIR="$ROOT/steipete-agent-scripts"
MATTPOCOCK_SKILLS_DIR="$ROOT/mattpocock-skills"
SKILLS_DIR="$ROOT/skills"
AGENTS_SKILLS_DIR="$ROOT/agents-skills"
AGENTS_SKILLS="$HOME/.agents/skills"
OPENCODE_AGENTS_SKILLS="$HOME/.opencode/skills"
EXCLUDED_SKILLS=(
  autonomous-git-commits
)
MATTPOCOCK_ENGINEERING_SKILLS=(
  codebase-design
  domain-modeling
  prototype
  research
  wizard
)
MATTPOCOCK_PRODUCTIVITY_SKILLS=(
  handoff
  teach
  writing-for-agents
)

is_excluded_skill() {
  local excluded
  for excluded in "${EXCLUDED_SKILLS[@]}"; do
    [[ "$1" != "$excluded" ]] || return 0
  done
  return 1
}

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

if [[ -d "$IMPECCABLE_DIR/.git" ]]; then
  git -C "$IMPECCABLE_DIR" pull --ff-only origin main
else
  git clone https://github.com/pbakaus/impeccable.git "$IMPECCABLE_DIR"
fi

if [[ -d "$STEIPETE_AGENT_SCRIPTS_DIR/.git" ]]; then
  git -C "$STEIPETE_AGENT_SCRIPTS_DIR" pull --ff-only origin main
else
  git clone https://github.com/steipete/agent-scripts.git "$STEIPETE_AGENT_SCRIPTS_DIR"
fi

if [[ -d "$MATTPOCOCK_SKILLS_DIR/.git" ]]; then
  git -C "$MATTPOCOCK_SKILLS_DIR" pull --ff-only origin main
else
  git clone https://github.com/mattpocock/skills.git "$MATTPOCOCK_SKILLS_DIR"
fi

# Recreate the generated runtime skill directory from its sources.
mkdir -p "$AGENTS_SKILLS_DIR"
find "$AGENTS_SKILLS_DIR" -maxdepth 1 -type l -delete

# Link the upstream Superpowers skills directly into the generated directory.
bash "$ROOT/flatten_superpowers.sh"

# Link local skills into the generated directory.
for skill in "$SKILLS_DIR"/*; do
  [[ -d "$skill" ]] || continue
  name="${skill##*/}"
  is_excluded_skill "$name" && continue
  ln -sfn "../skills/$name" "$AGENTS_SKILLS_DIR/$name"
done

# Link selected third-party skills into the generated directory.
ln -sfn "../lambdatest-agent-skills/rspec-skill" "$AGENTS_SKILLS_DIR/rspec-skill"
ln -sfn "$IMPECCABLE_DIR/.agents/skills/impeccable" "$AGENTS_SKILLS_DIR/impeccable"

for name in "${MATTPOCOCK_ENGINEERING_SKILLS[@]}"; do
  ln -sfn "$MATTPOCOCK_SKILLS_DIR/skills/engineering/$name" "$AGENTS_SKILLS_DIR/$name"
done

for name in "${MATTPOCOCK_PRODUCTIVITY_SKILLS[@]}"; do
  ln -sfn "$MATTPOCOCK_SKILLS_DIR/skills/productivity/$name" "$AGENTS_SKILLS_DIR/$name"
done

mkdir -p "$HOME/.agents"
ln -sfn "$AGENTS_SKILLS_DIR" "$AGENTS_SKILLS"

# syslink custom opencode skills
mkdir -p "$OPENCODE_AGENTS_SKILLS"
ln -sfn "$IMPECCABLE_DIR/.opencode/skills/impeccable" "$OPENCODE_AGENTS_SKILLS/impeccable"

echo "Skills linked into Codex at $AGENTS_SKILLS"
