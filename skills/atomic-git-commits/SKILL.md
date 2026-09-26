---
name: atomic-git-commits
description: "Invoke immediately for ANY git workflow: inspecting (status/diff/log/show), staging (add/stage), committing (commit/amend/reset), branch mgmt (branch/checkout/merge/rebase), remotes (push/pull/fetch), or repo state (stash/worktree). Also on commit-message advice, suggestions, or 'good commit message'. TRIGGER on: git, commit, status, diff, add, stage, branch, merge, push, pull, log, revert, stash, worktree, 'what changed', 'save changes', 'commit this', 'show me the diff', 'commit messages', 'good commit message', 'suggest commit', 'make a commit'. This skill is AUTHORITATIVE for commit-message format and MUST be followed even when the user only says 'commit' or 'save changes'."
---

# Atomic Git Commits

Create small commits with self-contained intent and consistently useful messages. Treat these rules as authoritative; do not infer style from repository history, which may be noisy or inconsistent.

## STOP GATE — READ BEFORE ANY GIT COMMAND

**Before you run or report any git command (status, add, commit, amend, push, etc.), you MUST:**

1.  **Load this file in full** (`read` the `atomic-git-commits/SKILL.md`). Do not work from memory or a one-line description — the detailed rules (especially Conventional Commits) are only enforced here.
2.  **Comply with every rule below** before executing the command. If your planned commit message does not match the format, do not commit yet — fix it first.
3.  **Self-audit the result.** After any commit, verify the subject matches the pattern `^(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)]+\))?!:\s+.+$` and uses lowercase imperative mood with no trailing punctuation. If it does not, amend it until it does.

This gate exists because a plain prompt like "commit" is still a git-workflow task that requires these rules. Never treat it as a shortcut.

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
6.  **Moves and Renames:** Never combine a file move or rename with content changes to that file in one commit. Commit the move or rename first, with the file content unchanged, then commit the content changes separately. This keeps the move visible in the diff and helps Git recognize it as a rename instead of a deletion and addition.

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

## Add a Body only when requested

- Separate it with a blank line.
- Wrap at 72 characters.
- Do not repeat the diff in the body.

## Respect the requested workflow

- If asked only for suggestions, do not stage or commit.
- If asked to proceed with one commit, do not silently create the rest.
- Do not impose unrelated checks on documentation or configuration the user has already validated.
- After committing, run the STOP GATE self-audit: confirm the subject matches `^(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)]+\))?!:\s+.+$`, lowercase imperative, no trailing punctuation. Amend if it fails, then report the short hash and subject concisely.
