---
name: atomic-git-commits
description: MANDATORY for ALL Git-related operations. Invoke immediately if the Navigator mentions: inspecting changes (status, diff, log, show), staging/adding files (add, stage), creating commits (commit, amend, reset), branch management (branch, checkout, merge, rebase), remote operations (push, pull, fetch), or repository state (stash, worktree). Trigger words: git, commit, status, diff, add, stage, branch, merge, push, pull, log, revert, stash, worktree, 'what changed', 'save changes', 'commit this', 'show me the diff'.
---

# Atomic Git Commits

Create small commits with self-contained intent and consistently useful messages. Treat these rules as authoritative; do not infer style from repository history, which may be noisy or inconsistent.

## Shape the commits

1. Inspect the working tree and relevant diffs. Do not use prior commit messages as a style source.
2. Group changes by one coherent purpose. Each commit should be independently understandable and safely revertible.
3. Split unrelated features, fixes, refactors, tests, documentation, configuration, and cleanup. Keep tightly coupled changes together when separating them would leave a misleading or broken commit.
4. List the proposed commits in execution order before committing when the user asks for a plan.
5. Stage only the approved group. Preserve unrelated staged, unstaged, and untracked work.
6. Create commits only with explicit user authorization, one approved commit at a time.

## Write the subject

Use Conventional Commits:

```text
<type>: <imperative description>
```

- Omit a `(scope)` by default. Use `<type>(<scope>): ...` only when the human partner explicitly requests scoped commits.
- Use the narrowest accurate type: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `build`, `ci`, `style`, or `revert`.
- Write the description in lowercase imperative mood: `add`, `remove`, `document`, `tune`, not `added`, `changes`, or `updated`.
- State the concrete effect, not vague activity.
- Keep the subject ideally at or below 50 characters.
- Do not end the subject with punctuation.

Good examples:

```text
feat: add GNOME AI server controls
test: cover AI server control actions
perf: tune router idle model unloading
docs: explain llama.cpp router parameters
```

Avoid vague subjects such as `fix bug`, `update files`, `misc changes`, or `work in progress`.

## Add a body only when needed

Use a body when the subject cannot explain why the change exists, its observable effect, or a non-obvious tradeoff. Separate it with a blank line, write directly, and wrap around 72 characters. Do not repeat the diff.

## Respect the requested workflow

- If asked only for suggestions, do not stage or commit.
- If asked to proceed with one commit, do not silently create the rest.
- Do not impose unrelated checks on documentation or configuration the user has already validated.
- After committing, report the short hash and subject concisely.
