#!/usr/bin/env bash
# Print the pane id of the agent running in a labelled tab of one workspace.
#
# Usage: find-agent-pane <label> [workspace-id]
#
# The workspace defaults to $HERDR_WORKSPACE_ID, so a same-labelled tab in another
# workspace can never match. Exit status: 0 with the pane id on stdout,
# 1 when the label has no tab or its tab has no agent, 2 on usage/dependency error.
set -euo pipefail

for tool in herdr jq; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "find-agent-pane: $tool is required" >&2
    exit 2
  }
done

if [ $# -lt 1 ]; then
  echo "usage: find-agent-pane <label> [workspace-id]" >&2
  exit 2
fi
label=$1
workspace=${2:-${HERDR_WORKSPACE_ID:-}}
if [ -z "$workspace" ]; then
  echo "find-agent-pane: pass a workspace id or run inside a herdr pane (HERDR_WORKSPACE_ID is unset)" >&2
  exit 2
fi

# herdr reports a bad workspace on stderr with a non-zero status, so both streams
# are captured: either failure shape becomes one line.
query() {
  local response
  if ! response=$("$@" 2>&1); then
    echo "find-agent-pane: $(printf '%s' "$response" | jq -r '.error.message' 2>/dev/null || printf '%s' "$response")" >&2
    exit 2
  fi
  printf '%s' "$response"
}

tabs=$(query herdr tab list --workspace "$workspace")
mapfile -t matches < <(printf '%s' "$tabs" | jq -r --arg label "$label" '
  .result.tabs[] | select(.label == $label) | .tab_id
')
if [ "${#matches[@]}" -eq 0 ]; then
  echo "find-agent-pane: no '$label' tab in workspace $workspace" >&2
  exit 1
fi
if [ "${#matches[@]}" -gt 1 ]; then
  echo "find-agent-pane: several '$label' tabs in workspace $workspace:" >&2
  printf '  %s\n' "${matches[@]}" >&2
  exit 1
fi
tab=${matches[0]}

panes=$(query herdr pane list --workspace "$workspace")
pane=$(printf '%s' "$panes" | jq -r --arg tab "$tab" '
  first(.result.panes[] | select(.tab_id == $tab and .agent != null) | .pane_id) // empty
')
if [ -z "$pane" ]; then
  echo "find-agent-pane: tab $tab in workspace $workspace has no agent" >&2
  exit 1
fi

printf '%s\n' "$pane"
