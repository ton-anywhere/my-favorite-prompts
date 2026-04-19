#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
SUPERPOWERS_SKILLS_DIR="$REPO_ROOT/superpowers/skills"

die() {
  echo "error: $*" >&2
  exit 1
}

[[ -d "$SUPERPOWERS_SKILLS_DIR" ]] || die "missing source directory: $SUPERPOWERS_SKILLS_DIR"
mkdir -p "$SKILLS_DIR"

for source in "$SUPERPOWERS_SKILLS_DIR"/*; do
  [[ -d "$source" ]] || continue
  skill_name="$(basename "$source")"
  dest="$SKILLS_DIR/$skill_name"
  relative_target="../superpowers/skills/$skill_name"

  if [[ -e "$dest" && ! -L "$dest" ]]; then
    echo "skip (exists and not symlink): $dest"
    continue
  fi

  ln -sfn "$relative_target" "$dest"
  echo "linked: $dest -> $relative_target"
done
