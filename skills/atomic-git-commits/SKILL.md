---
name: atomic-git-commits
description: "Invoke immediately for ANY git workflow: inspecting (status/diff/log/show), staging (add/stage), committing (commit/amend/reset), branch mgmt (branch/checkout/merge/rebase), remotes (push/pull/fetch), or repo state (stash/worktree). Also on commit-message advice, suggestions, or 'good commit message'. TRIGGER on: git, commit, status, diff, add, stage, branch, merge, push, pull, log, revert, stash, worktree, 'what changed', 'save changes', 'commit this', 'show me the diff', 'commit messages', 'good commit message', 'suggest commit', 'make a commit'. This skill is AUTHORITATIVE for commit-message format and MUST be followed even when the user only says 'commit' or 'save changes'."
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Atomic Git Commits

Create small commits with self-contained intent and consistently useful messages. Treat these rules as authoritative; do not infer style from repository history, which may be noisy or inconsistent.

## Select the Workflow

Read this skill before running Git commands. Select the workflow from the explicit
profile in the task or runtime; do not infer the profile from the model name.

- **`SMALL_MODEL_PROFILE` active:** Read the entire
  [small-model playbook](references/small-model-playbook.md) before the first Git
  command. Its Required Patch Workflow is mandatory for content commits and
  content amendments.
- **Otherwise:** Use the concise Git workflow below. The patch helper is optional;
  read the playbook if choosing it. Saved patches, checksums, and page receipts are
  not required for this workflow.

## The Principles of Atomicity

1.  **One Purpose per Commit:** Split changes that serve independent purposes. Keep the implementation, its tests, and instructions for the same behavior together when they form one coherent change. File type alone is not a reason to split.
2.  **Relevant Changes Only:** Stage exactly the current group's changes. If a file contains unrelated changes, select only the relevant hunks or lines.
3.  **Coherent Purpose:** Every commit must have one clear goal. If you find yourself using the word "and" in your commit message to join two different actions (e.g., "fix login and update footer"), you should probably split it into two commits.
4.  **Independent Entities:** Changes to independent agents, skills, or features belong in separate commits. A helper, its tests, and its skill instructions are parts of the same skill, not automatically independent entities.
5.  **Useful Subjects:** Describe the concrete change so a reader can understand its purpose without the conversation.
6.  **Moves and Renames:** Never combine a file move or rename with content changes to that file in one commit. Commit the move or rename first, with the file content unchanged, then commit the content changes separately. This keeps the move visible in the diff and helps Git recognize it as a rename instead of a deletion and addition.

## Commit Workflow

1. **Inspect:** Run `git status --short`. Read the relevant tracked diffs and untracked content. Preserve unrelated staged and working changes.
2. **Plan:** Assign every changed and untracked path to a commit group or an explicit exclusion before proposing the sequence. Include supporting tests, fixtures, and instructions. List multiple commits in dependency order.
3. **Stage one group:** Use explicit paths for whole-file changes and hunk selection for shared files. With `SMALL_MODEL_PROFILE` active, use the playbook's helper instead. Resolve unrelated staged work before committing; do not silently include or unstage it.
4. **Review:** Read the complete staged diff and run `git diff --cached --check`. Confirm it contains exactly the group. Recover truncated output by reading every remaining range. A file list or statistic is not a content review. Resolve failed checks before proceeding.
5. **Commit when authorized:** Approval for an entire listed sequence covers its groups; do not ask again for every group. Complete one group before staging the next. A commit request does not authorize a push.
6. **Verify:** Inspect the resulting committed diff and message. Report the short hash, subject, and remaining changes. If a hook changed the result, inspect it before an authorized repair.

## Write the Subject

Use Conventional Commits:

```text
<type>(<scope>): <imperative description>
```

-   **Type:** Use the narrowest accurate type: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `build`, `ci`, `style`, or `revert`.
-   **Logic vs Documentation:** Use `feat` or `fix` if the logic, behavior, or capabilities of the skill/agent change. Use `docs` ONLY for pure documentation/explanation changes that do not alter how the agent/skill functions.
-   **Scope:** Use a concise scope (e.g., a component, directory, or feature name). Omit if no single scope accurately describes the change. Do not repeat the type as the scope (e.g., avoid `docs(docs)`).
-   **Mood:** Use a lowercase imperative verb (e.g., `add`, `remove`, `tune`, `refactor`). Preserve technical identifiers such as API. Do not use `added`, `updated`, or `fixes`.
-   **Conciseness:** Keep the complete subject, including type and scope, at or below 70 characters. Prefer shorter subjects when clear. Avoid punctuation at the end.
-   **No Filler:** Be direct. Eliminate filler words like "I think," "maybe," or "just."

Good examples:

```text
feat(gnome): add AI server controls
test(gnome): cover AI server control actions
perf(router): tune idle model unloading
docs: add small model decode optimization guide
```

Avoid vague subjects such as `fix bug`, `update files`, `misc changes`, or `work in progress`.

## Body

- Do not include a commit message body.

## Respect the requested workflow

- If asked only for suggestions, do not stage or commit.
- If asked to proceed with one commit, do not silently create the rest.
- Do not impose unrelated checks on documentation or configuration the user has already validated.
- Check the resulting subject and empty body against the rules above. Repair an invalid message within the authorized scope.

## Rebase without a terminal editor

Use this workflow for authorized edits, reordering, squashing, or removal of older commits. For changes to HEAD only, use `git commit --amend`.

1. Confirm a clean working tree and no active rebase. Record the original HEAD hash for recovery and comparison.
2. Identify BASE: the parent of the oldest affected commit. Inspect the range. If it contains merge commits, choose a workflow that preserves them; ordinary rebase can flatten merges.
3. Run `git rebase -i BASE` with `GIT_SEQUENCE_EDITOR` set to a command or script that edits Git's supplied todo file in place and exits successfully. Use command-scoped editor overrides, not global configuration changes.
4. Preserve entries and order except where the task requires changes. Use `edit` for content or message changes, `squash`/`fixup` to combine commits, and `drop` to remove commits.
5. At each `edit` stop, verify HEAD, then amend:
   - **Message:** `git commit --amend -m "new message"`
   - **Content:** follow the selected commit workflow, then amend. With `SMALL_MODEL_PROFILE` active, use the helper's `commit --amend --message` with the intended subject.
6. Run `git rebase --continue` after each stop. For squash message prompts, use a noninteractive `GIT_EDITOR` script that updates the supplied message file in place.

### Precautions

- Rewrite published or shared commits only with explicit authorization. Obtain authorization before pushing rewritten history.
- If a command fails, inspect the state before continuing. Resolve conflicts, stage resolved files, and continue. Use `--skip` only when dropping that commit's changes is intended. Use `git rebase --abort` to restore the state before the rebase.
- Do not call `git rebase --continue` inside `--exec` or reset and recreate commits merely to avoid an editor.
- Verify the resulting history, messages, working tree, and final diff against the original HEAD. Message-only changes must leave the final tree unchanged.
