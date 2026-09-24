---
name: ssd-storage-cleanup
description: Use when the user asks to audit or reclaim SSD storage on this Linux machine, including package caches, journals, Snap revisions, or Docker build cache.
disable-model-invocation: true
---

# SSD Storage Cleanup

Use this skill to reclaim space without treating storage pressure as permission to delete broadly. Cache cleanup and installation-location changes are different operations.

## Do Not Clear Automatically

Prioritize safety over maximum space recovery.

Do not clear, move, modify, or delete any Chrome or Brave data. This includes profiles, browser caches, extensions, downloads, cookies, and configuration directories.

Do not clear the following without a separate, item-specific user request:

- Docker volumes, containers, images in use, and Docker or containerd configuration.
- Global package installations, compiler toolchains, project dependencies, and build output.
- Complete Discord or Obsidian profiles. Treat application caches as separate review items.
- Application and agent state, including sessions, authentication, history, and local databases.
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

Snap retention cannot be set below two revisions. A disabled revision is a rollback copy, so its removal needs confirmation even though it is not active.

Never delete arbitrary files in `/var/log`; manage journal size only with `journalctl`.

## Completion

Report reclaimed space from `df -h /`, list changes made, restate protected data that was untouched, and leave unresolved review items unchecked.
