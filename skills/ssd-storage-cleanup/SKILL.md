---
name: ssd-storage-cleanup
description: Use when the user asks to audit or reclaim SSD storage on this Linux machine, including package caches, journals, Snap revisions, or Docker build cache.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# SSD Storage Cleanup

Use this skill to reclaim space without treating storage pressure as permission to delete broadly. Cache cleanup and installation-location changes are different operations. The candidates in this skill and the verification script are initial examples, not an exhaustive inventory.

## Do Not Clear Automatically

Prioritize safety over maximum space recovery.

Do not clear, move, modify, or delete any Chrome or Brave data. This includes profiles, browser caches, extensions, downloads, cookies, and configuration directories.

Do not clear the following without a separate, item-specific user request:

- Docker volumes, containers, images in use, and Docker or containerd configuration.
- Global package installations, compiler toolchains, project dependencies, and build output.
- Complete Discord or Obsidian profiles. Treat application caches as separate review items.
- Application and agent state, including sessions, authentication, history, and local databases.
- OMP model-runtime downloads under `~/.omp/agent/cache`, including tiny, speech-to-text, and text-to-speech models.
- Rustup toolchains and Codex application releases. Treat both as installed runtimes, not disposable caches.
- User files in Downloads, Documents, repositories, or the Trash.

Never delete a directory merely because its name resembles a cache. Measure it and identify its owner first. Do not use broad cleanup commands, wildcard deletion, or recursive deletion outside a reviewed exact path.

Package uninstalls and `docker volume prune` are not routine cache cleanup. Do not suggest either unless the user separately requests it.

## Archival Audit Is Read-Only

An archival audit can identify large, inactive user-file or project candidates and report their size, mount, symlink, Git worktree, and full-path dependency risks. It must not copy, move, rename, archive, delete, or create a manifest.

Report candidates as options, not a cleanup plan. Any later archive requires a separate user-approved list of exact paths, destination, verification method, rollback plan, and expected path-link impact.

## Installation Locations Need Separate Approval

Do not change an installation, data, cache, or runtime location as part of routine cleanup. This includes configuration changes, environment variables, symlinks, bind mounts, `/etc/fstab`, service overrides, and data migrations.

Only change a location after the user approves the exact source, destination, services affected, rollback plan, and downtime.

## Plan Before Action

1. Record a baseline: `df -h /`, relevant top-level directory sizes, and `journalctl --disk-usage`. Check mount ownership and active processes before touching their data.
2. Create two checklists before mutations: an agent checklist for exact user-owned cleanup and `/tmp/ssd-storage-cleanup-sudo-todo.md` for sudo commands the user must run personally.
3. State exact paths or cache managers, estimated reclaimable space, and exclusions. Do not start cleanup until the user explicitly confirms the reviewed checklist.
4. Run only confirmed non-sudo items. Re-measure the affected path and `df -h /` after each item.
5. Never request or handle a sudo password. Wait for the user to run the sudo checklist and review the output before the next recommendation.

## Initial Verification Script

Run `scripts/verify-storage.sh` from this skill directory, or use its absolute path, before cleanup. The script does not mutate files. It emits one JSON object per line with the candidate name, path, byte count when available, human-readable size, status, and measurement details. Its metadata marks the report as an initial, non-exhaustive inventory.

Override the default workspace roots when needed:

```bash
OPEN_SOURCE_ROOT=/exact/open-source-root \
TON_ANYWHERE_ROOT=/exact/ton-anywhere-root \
bash scripts/verify-storage.sh
```

Treat `missing`, `unavailable`, and `unreadable` rows as audit results. Do not convert them into deletion commands without a separate review.

After the initial report, look for additional cleanup opportunities. Inspect filesystem-level consumers and application-specific caches that the script does not name:

```bash
du -x -h --max-depth=1 /home/airtonp /var /opt /tmp 2>/dev/null | sort -h
```

For every new large path, identify its owner, active users, retention policy, and exact cleanup command before proposing or running a mutation. Keep new findings separate from confirmed candidates.

## High-Probability Cache Candidates

Measure first. Include only relevant confirmed candidates in the checklist.

| Candidate | Inspect | Clear only after confirmation |
| --- | --- | --- |
| npm cache | `npm cache verify` | `npm cache clean --force` |
| Apt cache | `sudo du -x --max-depth=1 /var/cache \| sort -h` | `sudo apt autoclean`; use `sudo apt clean` only if all downloaded archives may go |
| Docker build cache | `docker system df` | `docker builder prune -a` after confirming active workloads are unaffected |
| System journal | `sudo journalctl --disk-usage` | `sudo journalctl --vacuum-size=<approved-size>` |
| pip cache | `python3 -m pip cache info` | `python3 -m pip cache purge` |
| uv cache | `uv cache dir` | `uv cache clean` |
| RuboCop cache | `du -sh ~/.cache/rubocop_cache` | Remove only that exact cache directory after confirming no RuboCop process is active |
| Thumbnail or Sublime cache | `du -sh ~/.cache/thumbnails ~/.cache/sublime-text-3/Cache` | Clear only the confirmed cache directory after closing the related application |
| Snap revisions | `sudo snap list --all --unicode=never` | Remove only revisions marked `disabled`; keep active revisions |
| Bun install cache | `bun pm cache` from a Bun project | `bun pm cache rm`; do not remove global packages |
| System temporary files | `find /tmp -mindepth 1 -maxdepth 1 -mtime +30 -print`; inspect `/usr/lib/tmpfiles.d/tmp.conf` | Run `sudo systemd-tmpfiles --clean` only after review; this systemd version may not support a dry-run flag |

Snap retention cannot be set below two revisions. A disabled revision is a rollback copy, so its removal needs confirmation even though it is not active.

Never delete arbitrary files in `/var/log`; manage journal size only with `journalctl`.

## Temporary Directory Cleanup

Use `systemd-tmpfiles` for system-managed temporary files. Do not use `rm -rf /tmp/*`.

The standard policy is usually visible in `/usr/lib/tmpfiles.d/tmp.conf`. The `D /tmp ... 30d` rule makes entries older than 30 days eligible. Check the age list first:

```bash
find /tmp -mindepth 1 -maxdepth 1 -mtime +30 -print
```

`systemd-tmpfiles --clean` applies all configured cleanup policies. It is not a `/tmp`-only command. Some systemd versions do not provide a dry-run flag. Treat the age audit as the review step. Preserve active application, browser, agent, and model-server temporary paths.

## Project Dependencies and Build Outputs

Project dependencies and build outputs are not routine cache cleanup. Audit them separately and request exact project paths before removal.

Inventory JavaScript dependencies across the named workspace roots:

```bash
find /home/airtonp/code/open-source /home/airtonp/code/ton-anywhere \
  -type d -name node_modules -prune -exec du -sh {} + | sort -h
```

There is no universal root command that safely removes every `node_modules`. After approval of an exact project path, use its lockfile and package manager to reinstall:

- Bun: remove only the reviewed project `node_modules`, then run `bun install`.
- npm: remove only the reviewed project `node_modules`, then run `npm ci` when `package-lock.json` exists.
- Yarn: remove only the reviewed project `node_modules`, then run `yarn install --frozen-lockfile` when the project uses `yarn.lock`.

Audit Rust and JavaScript build output separately:

```bash
find /home/airtonp/code/open-source /home/airtonp/code/ton-anywhere \
  -type d \( -name target -o -name dist \) -prune -exec du -sh {} + | sort -h
```

For one reviewed Rust project, use `cargo clean`. If the installed helper exists, prefer its dry-run first:

```bash
command -v cargo-clean-all
cargo-clean-all --dry-run /exact/root
cargo-clean-all -y /exact/root
```

`cargo-clean-all` can discover nested Cargo projects and remove their `target` directories. Verify every selected path and remeasure after it runs. Do not treat `bun run build` as cleanup; it regenerates build output. Do not run broad `git gc --prune=now` as routine cleanup; Git object reachability, worktrees, and recovery require a separate review.

## OMP Storage and Model Caches

`omp gc` maintains OMP application storage. It does not clear Bun caches, JavaScript dependencies, Rust targets, or downloaded model runtimes.

Run the dry-run first:

```bash
omp gc --json
```

Apply only after reviewing its exact result:

```bash
omp gc --json --apply
```

The default GC phases cover unreferenced blobs, cold session archives, and database WAL checkpointing. `--stale` additionally removes old debug reports and collaboration replicas. Treat all OMP GC actions as application-state mutations and require item-specific confirmation.

Inspect large local model caches separately:

```bash
du -sh ~/.omp/agent/cache/tiny-models \
  ~/.omp/agent/cache/stt-runtime \
  ~/.omp/agent/cache/tts-runtime
```

Do not remove `~/.omp/agent/cache` wholesale. These directories contain downloadable model runtimes and weights. Stop related workers, identify the exact model category, and obtain separate approval before removing one. `omp tiny-models` supports model listing and download, not a general purge command.

## Rustup Toolchains

Rust toolchains are compiler installations. Do not remove one only because its directory is large.

Inspect the installed list, active default, overrides, and workspace references:

```bash
du -x -h --max-depth=1 ~/.rustup/toolchains | sort -h
rustup toolchain list
rustup show active-toolchain
rustup override list
rg -n --hidden --glob '!**/.git/**' --glob '!**/node_modules/**' --glob '!**/target/**' \
  'nightly|stable|beta' /home/airtonp/code 2>/dev/null
ps -eo pid=,user=,comm=,args= | rg '(^|/)(cargo|rustc|rustup)( |$)'
```

Keep the active/default toolchain and every channel named by a repository `rust-toolchain` or `rust-toolchain.toml`. Remove only an exact reviewed toolchain after confirmation:

```bash
rustup toolchain uninstall <exact-toolchain>
```

Verify the toolchain list, target path, and `df -h /` after removal. Do not use a bulk uninstall command.

## Codex Application Releases

Codex app-server releases are installed runtimes. They are separate from Codex sessions, credentials, and configuration. Preserve application state.

Inspect the release inventory and active version:

```bash
du -sh ~/.codex/packages/app-server-daemon/releases/* | sort -h
readlink -f ~/.codex/packages/app-server-daemon/current
cat ~/.codex/packages/app-server-daemon/auto-update-version
codex --version
```

Check active Codex processes before removal. If the user explicitly requests Herdr inspection, use it only from a Herdr-managed pane after verifying `HERDR_ENV=1`; otherwise do not inspect a focused Herdr session from outside Herdr.

Preserve the release named by `current`. Keeping the immediately previous release is a rollback choice. Remove only an explicit list of older release directories after confirmation. Never use `rm -rf ~/.codex/packages/app-server-daemon/releases/*`.

After removal, verify `current`, `auto-update-version`, `codex --version`, the retained release list, and `df -h /`. No supported local Codex release-pruning command is assumed; do not infer one from directory names.

## Completion

Report reclaimed space from `df -h /`, list changes made, restate protected data that was untouched, and leave unresolved review items unchecked. For repository-wide helpers, report the helper's selected paths and verify the resulting paths independently; do not rely only on its reported byte total.
