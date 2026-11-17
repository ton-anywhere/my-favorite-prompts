---
name: installing-agent-skills
description: >
  Use when installing, adding, vendoring, linking or removing an agent skill
  (a SKILL.md package) into this workspace or into one project directory.
  Triggers: install this skill, add skill, third-party skill, vendor skill,
  link skill, skill not loading, agents-skills, .agents/skills, omp skill
  install, plugin link, upstream skill checkout. Default placement is
  user-level; a named directory means directory-scoped.
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Installing agent skills

## Overview

A skill is installed when its `SKILL.md` directory is reachable from a discovery
root. One source of truth per skill; every other reference to it is a symlink.
Copies drift.

| Root | Visibility |
|---|---|
| `agents-skills/<name>` → `~/.agents/skills` | user level, every project |
| `<directory>/.agents/skills/<name>` | that directory only |

## Placement

| The ask | Link | Target style |
|---|---|---|
| "install it", no path given — **default** | `agents-skills/<name>` | relative |
| a directory or project is named | `<dir>/.agents/skills/<name>` | absolute |

A directory-scoped skill MUST NOT appear in `agents-skills/`: that leaks it into
every project.

## Source

| Upstream shape | Do this |
|---|---|
| published on `skills.omp.sh` | `omp skill install -g <pkg>`; no checkout, nothing to link |
| multi-skill repo shipped as a plugin | `omp plugin link <path>` |
| multi-skill repo, or one you will reuse | checkout at repo root (below) |
| one skill folder, no local patches, one-off | copy into `skills/<name>/`, auto-linked |
| authored here | `skills/<name>/` plus `license` and `metadata.author` frontmatter |

For a GitHub repo, clone it and link it. `omp skill install` takes Skillshare
registry specs (`@scope/name`) or a local directory, and with `-g` it writes the
user-global `skills.json` — omp's own registry, not this repo's tracked links.

## User-level install (default)

1. `git clone <url> <checkout>` at the repo root; add `<checkout>/` to
   `.gitignore` in the existing cluster.
2. `bootstrap.sh`: declare `<X>_DIR="$ROOT/<checkout>"`; add an
   `if [[ -d "$<X>_DIR/.git" ]]` block that runs `pull --ff-only origin main`
   or clones; add
   `ln -sfn "../<checkout>/<skill-path>" "$AGENTS_SKILLS_DIR/<name>"` in the
   third-party block — before the local-skills loop, which runs last so local
   overrides win.
3. `LOCAL_NOTES.md`: provenance URL, update command, and the escape hatch — a
   local edit breaks `pull --ff-only`, so switch to `fetch --prune` plus the
   `local-custom` branch.
4. Verify: `bash -n bootstrap.sh`, run it,
   `readlink -f ~/.agents/skills/<name>/SKILL.md`, then invoke one of the
   skill's own scripts. A skill that only parses is not verified.
5. Commit `.gitignore`, `bootstrap.sh`, `LOCAL_NOTES.md` and the tracked
   symlink as one `feat(skills):` commit.

## Directory-level install

1. Source: this repo's gitignored checkout when several projects share it; the
   project itself when it must travel with that project.
2. `mkdir -p <dir>/.agents/skills && ln -sfn <absolute-source> <dir>/.agents/skills/<name>`
3. Touch nothing else: no `agents-skills/` link, no `.gitignore` entry, no
   `bootstrap.sh` block.
4. Record the link in this repo's `LOCAL_NOTES.md`. `bootstrap.sh` does not
   recreate it, so documentation is the only recovery path.
5. Verify both ways: `readlink -f <dir>/.agents/skills/<name>/SKILL.md` resolves
   and `~/.agents/skills/<name>` does not exist.

## Traps

| Trap | Reality |
|---|---|
| README says `cp -r … ~/.claude/skills/` | that directory holds only `synced/` on this machine; nothing loads from a copy there |
| `agents-skills/` looks like a plugin folder | it is a generated link farm; its symlinks are tracked and belong in the commit, but never edit files through it |
| absolute target inside this repo | breaks when the worktree moves; relative for repo-local checkouts, absolute only for external paths |
| `pull --ff-only` on a patched checkout | fails on every run; use `fetch --prune` and `local-custom` |
| `./bootstrap.sh` aborts on an unrelated dirty upstream | the link section never runs and existing links stay stale — after a failed run, re-check `readlink` instead of assuming links were rebuilt |

## Common mistakes

- Copying a skill into two roots instead of linking one.
- Installing directory-scoped by adding the link to `agents-skills/`.
- Committing the symlink without the `.gitignore`/`bootstrap.sh` edit, or the
  reverse: the install is only reproducible when they land together.
