# Repository Guidelines

## Project Structure & Module Organization
This repository is a prompt, skill and agents workspace, not a compiled app.

- `prompts/`: reusable prompt fragments (`*.md`).
- `agents/`: agent definitions and role templates.
- `skills/`: local skills, one per folder (`skills/<skill-name>/SKILL.md`).
- `agents-skills/`: generated links to local and selected third-party skills.
- `metaprompt/`: metapromtps - prompts that generate prompts.

Upstream checkouts are used as a linked dependency;
- `superpowers/`
- `lambdatest-agent-skills/`
- `impeccable/`
- `steipete-agent-scripts/`
- `mattpocock-skills/`

Read `LOCAL_NOTES.md` before updating an upstream checkout. It documents the
local-patch branches, rebase workflow, and repository-specific exceptions.

## AI-Generated and Temporary Files

- Save all project-level files generated for another AI under `.agents/`.
- Save all project-level temporary files under `.agents/`.
- Use focused subdirectories such as `.agents/handoffs/`,
  `.agents/prototypes/`, `.agents/wizards/`, `.agents/research/`, and
  `.agents/notes/`.
- Keep authored source files in their canonical directories, such as
  `agents/`, `prompts/`, and `skills/`.
- Treat `agents-skills/` as a generated skill-link directory, not as a place
  for AI-generated artifacts.
- Use the operating system temporary directory only for tool-internal data
  that is not a project artifact.

## Build, Test, and Development Commands
- `./bootstrap.sh`: clones/updates all managed upstream checkouts, builds the generated `agents-skills/` links, links it into `~/.agents/skills`, and links custom OpenCode skills into `~/.opencode/skills`.
- `./flatten_superpowers.sh`: creates/refreshes symlinks from `superpowers/skills/*` into generated `agents-skills/`.
- `git -C superpowers fetch --prune origin`: refreshes upstream refs; rebase `local-custom` manually as documented in `LOCAL_NOTES.md`.
- `git -C lambdatest-agent-skills pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C impeccable pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C steipete-agent-scripts pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C mattpocock-skills fetch --prune origin`: refreshes upstream refs; rebase `local-custom` manually as documented in `LOCAL_NOTES.md`.

## Coding Style & Naming Conventions
- Use Markdown for content and keep sections concise, imperative, and scannable.
- Shell scripts should use `#!/usr/bin/env bash` and `set -euo pipefail`.
- Prefer kebab-case names for skills and most agent files (for example `writing-plans`, `tech-lead-agent.md`).
- Keep each skill self-contained in its own directory with a single canonical `SKILL.md`.
- When creating a new skill, include the license and metadata fields to the frontmatter:
```
  license: MIT
  metadata:
    author: Airton Ponce @ton-anywhere
```

## Testing Guidelines
- No single root test runner exists; validate by change type.
- For shell script edits, run `bash -n <script>` before committing.
- If you modify `superpowers/` internals, run the relevant tests from `superpowers/tests/` (for example `cd superpowers/tests/brainstorm-server && node ws-protocol.test.js`).
