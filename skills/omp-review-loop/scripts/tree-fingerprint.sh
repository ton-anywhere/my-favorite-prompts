#!/usr/bin/env bash
# Print one SHA-256 for the tree under review: the commit, plus staged and unstaged tracked changes and the
# content of untracked files. HEAD is part of the hash because a clean worktree hashes the same at every commit.
# The loop state file is excluded so that recording a round does not change the fingerprint.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
state=':(exclude).agents/omp-review-loop*.json'

{
  git rev-parse HEAD
  git diff HEAD --binary -- . "$state"
  git ls-files --others --exclude-standard -z -- . "$state" | xargs -0 -r sha256sum
} | sha256sum | cut -d ' ' -f 1
