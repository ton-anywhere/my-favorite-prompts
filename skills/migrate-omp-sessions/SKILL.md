---
name: migrate-omp-sessions
description: Move oh-my-pi (omp) sessions whose recorded working directory no longer exists, usually a removed git worktree, into a live project directory so `/resume` stops prompting for a path. Use when resuming an omp session asks for a new directory, or when asked to migrate omp sessions off stale worktrees. Applies to omp only, not Claude Code or Codex session stores.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Migrate omp sessions

## What is stale

Each session is `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<id>.jsonl` plus an artifact directory of the same basename. Line 2 of the `.jsonl` is the header: `cwd`, `repository.sessionWorktreeRoot`, `repository.primaryWorktreeRoot`. A session is stale when `cwd` no longer exists:

```bash
python3 scripts/omp_sessions.py stale
```

The user names the destination project; default to the current checkout only when the request says "here". Report candidates grouped by worktree and migrate only what was asked for (one session, one worktree, or all). Sessions from other repositories stay out of scope.

## Migrate through omp, not the filesystem

Relocation must go through omp: it moves the transcript with its artifacts, rewrites the header `cwd`, and takes a writer lease. Never `mv` or hand-edit session files.

Start omp with its working directory set to the destination project, then use either entry point:

- `/resume` — picker; `Tab` toggles current folder / all projects, typing filters. Selecting a stale session relocates it, or opens a directory overlay when the header lacks usable repository metadata.
- `/resume <session-id>` — resolves ids across projects without the picker; preferred for batches.

Relocation is automatic only when `repository.primaryWorktreeRoot` exists; sessions without that metadata always need the directory overlay. In that overlay, typing the destination and pressing Enter moves the session into a **child** of it, because Enter confirms the highlighted suggestion (the directory's own children are listed once the typed prefix resolves). Type a unique prefix of the parent instead — `/path/to/parent/proj` where `proj` is the only match — so the lone suggestion is the destination itself. Correct a session that landed in a subdirectory with `/move <absolute destination>` from inside it.

Inside Herdr, drive a scratch pane and leave the user's panes alone:

```bash
herdr pane split --current --direction right --cwd <destination> --no-focus
herdr agent start mig --kind omp --pane <pane-id>
herdr agent prompt mig "/resume <session-id>"
```

Resume the next id from the session the pane now hosts. It takes 1–3 s per session; detect completion on the filesystem (transcript under the destination project's session dir, gone from the old one), not by scraping screen text. Close the pane when finished.

## Verify

```bash
python3 scripts/omp_sessions.py verify <session-id> ...
```

Every id must appear exactly once with an existing recorded `cwd`, its artifact directory must have moved with the transcript, and `/resume` in the destination must list it under *current folder*.

## Pitfalls

- A session held by another live omp process refuses relocation. Close that process, then retry.
- `repository.sessionWorktreeRoot` still names the removed worktree afterwards. omp keeps it deliberately; a valid `cwd` makes later resumes take the unchanged path. Do not rewrite it.
- Empty leftover directories under `~/.omp/agent/sessions/` are harmless; leave them.
