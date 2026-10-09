---
name: atomic-git-commits
description: "Invoke immediately for ANY git workflow: inspecting (status/diff/log/show), staging (add/stage), committing (commit/amend/reset), branch mgmt (branch/checkout/merge/rebase), remotes (push/pull/fetch), or repo state (stash/worktree). Also on commit-message advice, suggestions, or 'good commit message'. TRIGGER on: git, commit, status, diff, add, stage, branch, merge, push, pull, log, revert, stash, worktree, 'what changed', 'save changes', 'commit this', 'show me the diff', 'commit messages', 'good commit message', 'suggest commit', 'make a commit'. This skill is AUTHORITATIVE for commit-message format and MUST be followed even when the user only says 'commit' or 'save changes'."
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Atomic Git Commits

Create small commits with self-contained intent and consistently useful messages. Treat these rules as authoritative; do not infer style from repository history, which may be noisy or inconsistent.

## STOP GATE — READ BEFORE ANY GIT COMMAND

**Before you run or report any git command (status, add, commit, amend, push, etc.), you MUST:**

1.  **Load this file in full** (`read` the `atomic-git-commits/SKILL.md`). Do not work from memory or a one-line description — the detailed rules (especially Conventional Commits) are only enforced here.
2.  **Comply with every rule below** before executing the command. If your planned commit message does not match the format, do not commit yet — fix it first.
3.  **Self-audit the result.** After any commit, verify the subject matches the pattern `^(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)]+\))?!?:\s+.+$` and uses lowercase imperative mood with no trailing punctuation. If it does not, amend it until it does.

This gate exists because a plain prompt like "commit" is still a git-workflow task that requires these rules. Never treat it as a shortcut.

## Small-Model Profile

If `SMALL_MODEL_PROFILE` is active, read
[`references/small-model-playbook.md`](references/small-model-playbook.md) completely
before planning, running a Git command, or replying. The playbook expands this
skill; it does not replace or weaken any rule in this file.

## The Principles of Atomicity

1.  **One Change per Commit:** Do not bundle unrelated changes. If you are working on a bug fix, a refactor, and a documentation update, create three separate commits.
2.  **Relevant Changes Only:** Prepare one saved patch containing exactly the current commit's changes. For shared files, supply the intermediate content for that commit, not the final content containing later groups.
3.  **Coherent Purpose:** Every commit must have one clear goal. If you find yourself using the word "and" in your commit message to join two different actions (e.g., "fix login and update footer"), you should probably split it into two commits.
4.  **Independent Entities:** Even if files are in the same directory or share a category, if they represent different entities (e.g., two different agents, two different skills), they MUST be in separate commits.
5.  **Future-Proofing:** Write the commit as a letter to your future self. Assume the reader doesn't have the context of your current thought process. Answer: *Why* was this change needed? *What* effect does it have?
6.  **Moves and Renames:** Never combine a file move or rename with content changes to that file in one commit. Commit the move or rename first, with the file content unchanged, then commit the content changes separately. This keeps the move visible in the diff and helps Git recognize it as a rename instead of a deletion and addition.

## Commit Workflow

1.  **Inspection:** Inspect the working tree and relevant diffs. Do not use prior commit messages as a style source.
2.  **Grouping:** Group changes by a single coherent purpose (Principles 1 & 3). If a change is not tightly coupled to the others, it must be separated.
3.  **Planning:** For multi-step tasks, list the proposed commits in execution order before starting. This ensures the correct sequence of dependencies.
4.  **Patch review and staging:** Follow the required patch workflow below for each content commit. Preserve unrelated staged and untracked work.
5.  **Authorization:** Create only explicitly authorized commits, one group at a time. Approval for an entire listed sequence remains valid; do not request approval again for each group in that sequence.

## Required Patch Workflow

Use [`scripts/commit_patch.py`](scripts/commit_patch.py) for every content commit,
including whole-file changes. Resolve its path from this skill's directory, not
the repository's working directory. Run it through `python3`.

1. Prepare the exact content each selected file must have after this commit. Use temporary content files for partial changes; the working file itself is suitable only when all its changes belong to this group.
2. Run `prepare` with a distinct patch path and explicit `--file REPO_PATH CONTENT_FILE` pairs. Use `--delete REPO_PATH` for deletions. Run `--help` for arguments. Prepare the next patch after the previous commit, against the current index.
3. Run `review`. Read the complete patch and check every change against the group's purpose. Record its printed SHA256 only after review; a file list or diff statistic is not a content review.
4. Run `stage` and then `verify`, passing `--reviewed-sha256` to both. Read the complete staged diff. It must contain exactly the reviewed group.
5. Once authorized, run `commit` with that same patch, SHA256, and `--message`. The helper verifies the complete staged tree immediately before committing and checks the resulting tree and message afterward.

Example for one change in a shared file (`atomic_skill_dir` is the absolute directory containing this skill):

```sh
python3 "$atomic_skill_dir/scripts/commit_patch.py" prepare /tmp/01-timeout.patch --file settings.txt /tmp/01-settings.txt
python3 "$atomic_skill_dir/scripts/commit_patch.py" review /tmp/01-timeout.patch
python3 "$atomic_skill_dir/scripts/commit_patch.py" stage /tmp/01-timeout.patch --reviewed-sha256 SHA_FROM_REVIEW
python3 "$atomic_skill_dir/scripts/commit_patch.py" verify /tmp/01-timeout.patch --reviewed-sha256 SHA_FROM_REVIEW
python3 "$atomic_skill_dir/scripts/commit_patch.py" commit /tmp/01-timeout.patch --reviewed-sha256 SHA_FROM_REVIEW --message 'fix(settings): increase timeout'
```

The helper rejects pre-existing staged changes, changed patches, stale HEAD/index
state, whitespace errors, and staged content outside the reviewed patch. A failed
check blocks the commit. Inspect the failure and preserve work; do not append a
successful command to mask the exit status or bypass the helper with `git add`,
`git apply`, or direct content commits. If a hook changes the committed content,
inspect the reported commit before deciding on an authorized repair.

The SHA256 binds commands to reviewed bytes; it cannot prove that a model read
them or replace judgment about which changes belong together.

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

## Body

- Do not include a commit message body.

## Respect the requested workflow

- If asked only for suggestions, do not stage or commit.
- If asked to proceed with one commit, do not silently create the rest.
- Do not impose unrelated checks on documentation or configuration the user has already validated.
- After committing, run the STOP GATE self-audit: confirm the subject matches `^(feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert)(\([^)]+\))?!?:\s+.+$`, lowercase imperative, no trailing punctuation. Amend if it fails, then report the short hash and subject concisely.

## Rebase without a terminal editor

Use this workflow for authorized edits, reordering, squashing, or removal of older commits. For changes to HEAD only, use `git commit --amend`.

1. Confirm a clean working tree and no active rebase. Record the original HEAD hash for recovery and comparison.
2. Identify BASE: the parent of the oldest affected commit. Inspect the range. If it contains merge commits, choose a workflow that preserves them; ordinary rebase can flatten merges.
3. Run `git rebase -i BASE` with `GIT_SEQUENCE_EDITOR` set to a command or script that edits Git's supplied todo file in place and exits successfully. Use command-scoped editor overrides, not global configuration changes.
4. Preserve entries and order except where the task requires changes. Use `edit` for content or message changes, `squash`/`fixup` to combine commits, and `drop` to remove commits.
5. At each `edit` stop, verify HEAD, then amend:
   - **Message:** `git commit --amend -m "new message"`
   - **Content:** edit files, follow the required patch workflow, and use the helper's `commit --amend --message` with the intended subject.
6. Run `git rebase --continue` after each stop. For squash message prompts, use a noninteractive `GIT_EDITOR` script that updates the supplied message file in place.

### Precautions

- Rewrite published or shared commits only with explicit authorization. Obtain authorization before pushing rewritten history.
- If a command fails, inspect the state before continuing. Resolve conflicts, stage resolved files, and continue. Use `--skip` only when dropping that commit's changes is intended. Use `git rebase --abort` to restore the state before the rebase.
- Do not call `git rebase --continue` inside `--exec` or reset and recreate commits merely to avoid an editor.
- Verify the resulting history, messages, working tree, and final diff against the original HEAD. Message-only changes must leave the final tree unchanged.
