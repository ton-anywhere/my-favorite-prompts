---
name: atomic-git-commits
description: "Invoke immediately if the Navigator mentions: inspecting changes (status, diff, log, show), staging/adding files (add, stage), creating commits (commit, amend, reset), branch management (branch, checkout, merge, rebase), remote operations (push, pull, fetch), or repository state (stash, worktree), or asks for advice/suggestions on commit messages or git strategy. TRIGGER ANYTHING RELATED TO GIT WORKFLOW INCLUDING COMMIT MESSAGE SUGGESTIONS AND ADVICE. Trigger words: git, commit, status, diff, add, stage, branch, merge, push, pull, log, revert, stash, worktree, 'what changed', 'save changes', 'commit this', 'show me the diff', 'commit messages', 'good commit message', 'suggest commit'"
---

# Atomic Git Commits

Create small commits with self-contained intent and consistently useful messages. Treat these rules as authoritative; do not infer style from repository history, which may be noisy or inconsistent.

## Small-Model Profile

If `SMALL_MODEL_PROFILE` is active, read
[`references/small-model-playbook.md`](references/small-model-playbook.md) completely
before planning, running a Git command, or replying. The playbook expands this
skill; it does not replace or weaken any rule in this file.

## The Principles of Atomicity

1.  **One Change per Commit:** Do not bundle unrelated changes. If you are working on a bug fix, a refactor, and a documentation update, create three separate commits.
2.  **Relevant Files Only:** Only stage and commit the files that belong to the current change. If a file contains multiple unrelated changes, only commit the relevant ones (using `git add -p` if necessary).
3.  **Coherent Purpose:** Every commit must have one clear goal. If you find yourself using the word "and" in your commit message to join two different actions (e.g., "fix login and update footer"), you should probably split it into two commits.
4.  **Independent Entities:** Even if files are in the same directory or share a category, if they represent different entities (e.g., two different agents, two different skills), they MUST be in separate commits.
5.  **Future-Proofing:** Write the commit as a letter to your future self. Assume the reader doesn't have the context of your current thought process. Answer: *Why* was this change needed? *What* effect does it have?

## Commit Workflow

1.  **Inspection:** Inspect the working tree and relevant diffs. Do not use prior commit messages as a style source.
2.  **Grouping:** Group changes by a single coherent purpose (Principles 1 & 3). If a change is not tightly coupled to the others, it must be separated.
3.  **Planning:** For multi-step tasks, list the proposed commits in execution order before starting. This ensures the correct sequence of dependencies.
4.  **Staging:** Stage only the files relevant to the current atomic commit (Principle 2). Preserve unrelated staged or untracked work.
5.  **Authorization:** Create commits only with explicit user authorization, one approved commit at a time.

## Write the Subject

Use Conventional Commits:

```text
<type>(<scope>): <imperative description>
```

-   **Type:** Use the narrowest accurate type: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `build`, `ci`, `style`, or `revert`.
-   **Logic vs Documentation:** Use `feat` or `fix` if the logic, behavior, or capabilities of the skill/agent change. Use `docs` ONLY for pure documentation/explanation changes that do not alter how the agent/skill functions.
-   **Scope:** Use a concise scope (e.g., a component, directory, or feature name). Omit if no single scope accurately describes the change. Do not repeat the type as the scope (e.g., avoid `docs(docs)`).
-   **Mood:** Use lowercase imperative mood (e.g., `add`, `remove`, `tune`, `refactor`). Do not use `added`, `updated`, or `fixes`.
-   **Conciseness:** Keep the subject at or below 50 characters. Avoid punctuation at the end.
-   **No Filler:** Be direct. Eliminate filler words like "I think," "maybe," or "just."

Good examples:

```text
feat(gnome): add AI server controls
test(gnome): cover AI server control actions
perf(router): tune idle model unloading
docs: add small model decode optimization guide
```

Avoid vague subjects such as `fix bug`, `update files`, `misc changes`, or `work in progress`.

## Add a Body only when needed

Use a body when the subject cannot explain the *why* or a non-obvious tradeoff. 
- Separate it with a blank line.
- Wrap at 72 characters.
- Do not repeat the diff in the body.

## Respect the requested workflow

- If asked only for suggestions, do not stage or commit.
- If asked to proceed with one commit, do not silently create the rest.
- Do not impose unrelated checks on documentation or configuration the user has already validated.
- After committing, report the short hash and subject concisely.
