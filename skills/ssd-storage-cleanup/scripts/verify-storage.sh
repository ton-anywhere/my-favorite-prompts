#!/usr/bin/env bash

set -u
set -o pipefail

# This script only reads metadata and measures paths. It emits JSON Lines so a
# failed or unavailable measurement remains machine-readable.

OPEN_SOURCE_ROOT="${OPEN_SOURCE_ROOT:-/home/airtonp/code/open-source}"
TON_ANYWHERE_ROOT="${TON_ANYWHERE_ROOT:-/home/airtonp/code/ton-anywhere}"
HOME_DIR="${HOME:-/home/airtonp}"

json_escape() {
	local value=$1
	value=${value//\\/\\\\}
	value=${value//\"/\\\"}
	value=${value//$'\n'/\\n}
	value=${value//$'\r'/\\r}
	value=${value//$'\t'/\\t}
	printf '%s' "$value"
}

human_bytes() {
	local bytes=$1
	if command -v numfmt >/dev/null 2>&1; then
		numfmt --to=iec --suffix=B "$bytes" 2>/dev/null || printf '%sB' "$bytes"
	else
		printf '%sB' "$bytes"
	fi
}

bytes_from_human() {
	local value=$1
	value=${value//[[:space:]]/}
	value=${value%B}
	if command -v numfmt >/dev/null 2>&1; then
		numfmt --from=auto --to=none "$value" 2>/dev/null || true
	fi
}

emit() {
	local candidate=$1
	local path=$2
	local bytes=$3
	local human=$4
	local status=$5
	local details=$6
	local path_json=null

	if [[ -n "$path" ]]; then
		path_json="\"$(json_escape "$path")\""
	fi

	printf '{"candidate":"%s","path":%s,"size_bytes":%s,"size_human":"%s","status":"%s","details":"%s"}\n' \
		"$(json_escape "$candidate")" \
		"$path_json" \
		"$bytes" \
		"$(json_escape "$human")" \
		"$(json_escape "$status")" \
		"$(json_escape "$details")"
}

emit_path() {
	local candidate=$1
	local path=$2
	local details=${3:-}
	local bytes
	local human

	if [[ ! -e "$path" && ! -L "$path" ]]; then
		emit "$candidate" "$path" 0 "0B" "missing" "$details"
		return
	fi

	bytes=$(du -sx -B1 -- "$path" 2>/dev/null | awk 'NR == 1 { print $1 }')
	human=$(du -sx -h -- "$path" 2>/dev/null | awk 'NR == 1 { print $1 }')
	if [[ "$bytes" =~ ^[0-9]+$ ]]; then
		emit "$candidate" "$path" "$bytes" "${human:-$(human_bytes "$bytes")}" "present" "$details"
	else
		emit "$candidate" "$path" null "" "unreadable" "$details"
	fi
}

printf '{"type":"metadata","schema":"ssd-storage-cleanup/v1","script":"verify-storage.sh","scope":"initial","exhaustive":false,"note":"Starting inventory only; inspect additional large paths and application-specific caches."}\n'

emit_path "npm_cache" "$HOME_DIR/.npm" "npm cache path"
emit_path "apt_cache" "/var/cache/apt" "unprivileged measurement; run sudo du for a complete audit"
emit_path "pip_cache" "$HOME_DIR/.cache/pip" "pip cache path"
emit_path "uv_cache" "$HOME_DIR/.cache/uv" "uv cache path"
emit_path "rubocop_cache" "$HOME_DIR/.cache/rubocop_cache" "exact RuboCop cache path"
emit_path "thumbnail_cache" "$HOME_DIR/.cache/thumbnails" "exact thumbnail cache path"
emit_path "sublime_cache" "$HOME_DIR/.cache/sublime-text-3/Cache" "exact Sublime Text cache path"
emit_path "bun_install_cache" "$HOME_DIR/.bun/install/cache" "Bun package cache; does not include global packages"
emit_path "bun_global_packages" "$HOME_DIR/.bun/install/global" "protected global Bun packages"
emit_path "brave_cache_protected" "$HOME_DIR/.cache/BraveSoftware" "protected browser data"
emit_path "chrome_cache_protected" "$HOME_DIR/.cache/google-chrome" "protected browser data"
emit_path "tmp" "/tmp" "systemd tmpfiles policy; inspect entries older than 30 days"

journal_output=$(journalctl --disk-usage --no-pager 2>/dev/null || true)
if [[ -n "$journal_output" ]]; then
	journal_human=$(printf '%s\n' "$journal_output" | sed -nE 's/.*take up ([0-9]+([.][0-9]+)?[[:space:]]*[KMGTP]I?B?).*/\1/p' | head -n 1)
	journal_bytes=$(bytes_from_human "$journal_human")
	if [[ "$journal_bytes" =~ ^[0-9]+$ ]]; then
		emit "system_journal" "" "$journal_bytes" "$(human_bytes "$journal_bytes")" "present" "$journal_output"
	else
		emit "system_journal" "" null "" "present" "$journal_output"
	fi
else
	emit "system_journal" "" null "" "unavailable" "journalctl --disk-usage returned no output"
fi

if command -v docker >/dev/null 2>&1; then
	if command -v jq >/dev/null 2>&1; then
		docker_rows=$(docker system df --format '{{json .}}' 2>/dev/null || true)
		if [[ -n "$docker_rows" ]]; then
			while IFS= read -r row; do
				[[ -z "$row" ]] && continue
				type=$(jq -r '.Type' <<<"$row")
				total=$(jq -r '.TotalCount' <<<"$row")
				active=$(jq -r '.Active' <<<"$row")
				size=$(jq -r '.Size' <<<"$row")
				reclaimable=$(jq -r '.Reclaimable' <<<"$row")
				candidate_type=${type,,}
				candidate_type=${candidate_type//[^a-z0-9_-]/_}
				size_bytes=$(bytes_from_human "$size")
				if [[ "$size_bytes" =~ ^[0-9]+$ ]]; then
					emit "docker_${candidate_type}" "" "$size_bytes" "$size" "present" "total=$total active=$active reclaimable=$reclaimable"
				else
					emit "docker_${candidate_type}" "" null "$size" "present" "total=$total active=$active reclaimable=$reclaimable"
				fi
			done <<<"$docker_rows"
		else
			emit "docker_system_df" "" null "" "unavailable" "docker system df returned no rows"
		fi
	else
		emit "docker_system_df" "" null "" "unavailable" "missing command: jq"
	fi
else
	emit "docker_system_df" "" null "" "unavailable" "missing command: docker"
fi

if command -v snap >/dev/null 2>&1; then
	disabled_rows=$(snap list --all --unicode=never 2>/dev/null | awk 'NR > 1 && $NF == "disabled" { print $1 "\t" $3 }')
	disabled_bytes=0
	disabled_count=0
	missing_snap_files=0
	while IFS=$'\t' read -r snap_name snap_revision; do
		[[ -z "$snap_name" ]] && continue
		disabled_count=$((disabled_count + 1))
		snap_path="/var/lib/snapd/snaps/${snap_name}_${snap_revision}.snap"
		snap_bytes=$(du -sx -B1 -- "$snap_path" 2>/dev/null | awk 'NR == 1 { print $1 }')
		if [[ "$snap_bytes" =~ ^[0-9]+$ ]]; then
			disabled_bytes=$((disabled_bytes + snap_bytes))
		else
			missing_snap_files=$((missing_snap_files + 1))
		fi
	done <<<"$disabled_rows"
	emit "snap_disabled_revisions" "/var/lib/snapd/snaps" "$disabled_bytes" "$(human_bytes "$disabled_bytes")" "present" "disabled_revisions=$disabled_count unavailable_snap_files=$missing_snap_files"
else
	emit "snap_disabled_revisions" "/var/lib/snapd/snaps" null "" "unavailable" "missing command: snap"
fi

for root in "$OPEN_SOURCE_ROOT" "$TON_ANYWHERE_ROOT"; do
	if [[ ! -d "$root" ]]; then
		emit "workspace_root" "$root" 0 "0B" "missing" "workspace root"
		continue
	fi

	while IFS= read -r -d '' path; do
		emit_path "node_modules" "$path" "project dependency tree"
	done < <(find "$root" -type d -name node_modules -prune -print0 2>/dev/null)

	while IFS= read -r -d '' path; do
		emit_path "build_output" "$path" "Rust target or JavaScript dist directory"
	done < <(find "$root" -type d \( -name .git -o -name node_modules \) -prune -o -type d \( -name target -o -name dist \) -print0 2>/dev/null)
done

emit_path "rustup_toolchains" "$HOME_DIR/.rustup/toolchains" "compiler installations; preserve active and referenced toolchains"
if [[ -d "$HOME_DIR/.rustup/toolchains" ]]; then
	while IFS= read -r -d '' path; do
		emit_path "rustup_toolchain" "$path" "exact toolchain"
	done < <(find "$HOME_DIR/.rustup/toolchains" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
fi

codex_base="$HOME_DIR/.codex/packages/app-server-daemon"
emit_path "codex_packages" "$HOME_DIR/.codex/packages" "Codex application packages"
if [[ -d "$codex_base/releases" ]]; then
	while IFS= read -r -d '' path; do
		emit_path "codex_release" "$path" "Codex app-server release"
	done < <(find "$codex_base/releases" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
fi
codex_current=$(readlink -f "$codex_base/current" 2>/dev/null || true)
if [[ -n "$codex_current" ]]; then
	emit "codex_current_release" "$codex_current" null "" "present" "current symlink target"
else
	emit "codex_current_release" "$codex_base/current" null "" "missing" "current symlink"
fi

emit_path "omp_agent_storage" "$HOME_DIR/.omp/agent" "OMP application state; requires separate review"
emit_path "omp_model_cache" "$HOME_DIR/.omp/agent/cache" "OMP model-runtime downloads; do not remove wholesale"
emit_path "omp_tiny_models" "$HOME_DIR/.omp/agent/cache/tiny-models" "OMP tiny and memory model downloads"
emit_path "omp_stt_runtime" "$HOME_DIR/.omp/agent/cache/stt-runtime" "OMP speech-to-text runtime"
emit_path "omp_tts_runtime" "$HOME_DIR/.omp/agent/cache/tts-runtime" "OMP text-to-speech runtime"
