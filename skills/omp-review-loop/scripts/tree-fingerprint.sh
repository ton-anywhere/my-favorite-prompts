#!/bin/sh
# Print one SHA-256 for the working tree: staged and unstaged tracked changes
# plus the content of untracked files. The loop state file is excluded so that
# recording a round does not change the fingerprint.
set -eu

cd "$(git rev-parse --show-toplevel)"
state=':(exclude).agents/omp-review-loop.json'

{
  git diff HEAD --binary -- . "$state"
  git ls-files --others --exclude-standard -z -- . "$state" | xargs -0 -r sha256sum
} | sha256sum | cut -d ' ' -f 1
