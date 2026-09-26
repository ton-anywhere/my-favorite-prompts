#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'Usage: %s <path> <unique literal from target hunk>\n' "$0" >&2
  exit 2
fi

path=$1
anchor=$2

if ! git_root=$(git rev-parse --show-toplevel 2>/dev/null); then
  printf 'Not inside a Git working tree.\n' >&2
  exit 2
fi

cd -- "$git_root"

# A pre-existing staged change makes applying one working-tree hunk ambiguous.
if ! git diff --cached --quiet -- "$path"; then
  printf 'Refusing to stage %s because it already has staged changes.\n' "$path" >&2
  exit 2
fi

diff_file=$(mktemp)
patch_file=$(mktemp)
trap 'rm -f -- "$diff_file" "$patch_file"' EXIT

git diff --no-ext-diff --unified=3 -- "$path" > "$diff_file"

if [[ ! -s $diff_file ]]; then
  printf 'No unstaged changes for %s.\n' "$path" >&2
  exit 2
fi

awk -v needle="$anchor" '
function finish_hunk() {
  if (hunk == "") {
    return
  }
  if (index(hunk, needle) != 0) {
    matches++
    selected = hunk
  }
  hunk = ""
}

{
  if (!in_hunks) {
    if ($0 ~ /^@@ /) {
      in_hunks = 1
      hunk = $0 ORS
    } else {
      header = header $0 ORS
    }
    next
  }

  if ($0 ~ /^@@ /) {
    finish_hunk()
    hunk = $0 ORS
    next
  }

  hunk = hunk $0 ORS
}

END {
  finish_hunk()
  if (matches != 1) {
    printf "Expected exactly one hunk containing the supplied literal; found %d.\n", matches > "/dev/stderr"
    exit 2
  }
  printf "%s%s", header, selected
}
' "$diff_file" > "$patch_file"

git apply --cached --check "$patch_file"
git apply --cached "$patch_file"
git diff --cached -- "$path"
