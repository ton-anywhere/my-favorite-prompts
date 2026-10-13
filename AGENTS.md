# Repository Guidelines

## Project Structure & Module Organization
This repository is a prompt, skill and agents workspace, not a compiled app.

- `prompts/`: reusable prompt fragments (`*.md`).
- `agents/`: agent definitions and role templates.
- `skills/`: local skills, one per folder (`skills/<skill-name>/SKILL.md`).
- `metaprompt/`: metapromtps - prompts that generate prompts.

Upstream checkouts are used as a linked dependency;
- `superpowers/`
- `lambdatest-agent-skills/`
- `impeccable/`
- `steipete-agent-scripts/`

## Build, Test, and Development Commands
- `./bootstrap.sh`: clones/updates `superpowers/`, `lambdatest-agent-skills/`, and `impeccable/`, links `skills/` into `~/.agents/skills`, links custom opencode skills into `~/.opencode/skills`, and maintains symlinks.
- `./flatten_superpowers.sh`: creates/refreshes symlinks from `superpowers/skills/*` into local `skills/`.
- `git -C superpowers pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C lambdatest-agent-skills pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C impeccable pull --ff-only origin main`: updates the upstream checkout without merge commits.
- `git -C steipete-agent-scripts pull --ff-only origin main`: updates the upstream checkout without merge commits.

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
