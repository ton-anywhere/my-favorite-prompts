# Autonomous Git Commits: Small-Model Playbook

Follow this playbook in order. Do not skip a step because the repository looks
simple or because the requested Git operation appears harmless.

## 1. Identify the Requested Operation

Classify the user's request before running commands:

- **Inspect:** status, diff, log, show, or "what changed."
- **Change repository state:** add, stage, restore, reset, stash, branch, checkout,
  merge, rebase, or revert.
- **Commit:** create or amend a commit.
- **Remote:** fetch, pull, or push.

An inspection request does not authorize staging or committing. When the user
requests repository changes under this skill, commit the task changes after
validating them, even if the user did not separately request a commit.

## 2. Inspect Before Changing Anything

Run `git status --short` first. Then inspect only the relevant changes with
`git diff -- <path>` or `git diff --cached -- <path>`.

Use the user's stated scope to determine ownership. When the user asks to commit
all unstaged changes, every tracked unstaged change belongs to the task. Do not
exclude a change because its formatting, style, or inferred intent seems wrong.

Preserve pre-existing staged changes and untracked files whose ownership is not
stated. Never clean, restore, reset, or overwrite them merely to make the
working tree look tidy.

## 3. Form Atomic Groups

For every changed file, state the single purpose it serves. Put files in the same
group only when they are required for one coherent behavior.

Apply the independent-entity split before grouping by a shared purpose. A common
feature, workflow, or user goal does not justify one commit when artifacts can
be understood or reverted independently.

Split groups when any of these are true:

- the changes can be understood or reverted independently;
- they affect independent skills, agents, or features;
- the proposed subject needs "and" to join separate actions;
- one file contains unrelated hunks.

When a file contains mixed changes, use patch staging and select only the relevant
hunks. If selection is uncertain, use the smallest reversible group supported by
the displayed hunk boundaries. Do not stop to ask the user during an autonomous
run; report that grouping decision after completion.

For a multi-step task, show the proposed commit groups in execution order before
staging. Continue with those groups without waiting for per-commit approval.

## 4. Respect Task Boundaries

Read the user's latest message literally.

- "Review," "inspect," or "show the diff" authorizes inspection only.
- "Stage this" authorizes staging only.
- A request to change repository files under this skill authorizes atomic
  commits for the task changes without a separate approval step.
- "Commit this" authorizes one commit for the clearly identified change.
- A commit does not authorize a push.
- A push, pull, reset, rebase, merge, revert, stash, or branch switch must be
  explicitly requested.

For an autonomous commit task, make the best supported local decision and
continue. Report material assumptions after completing the requested commits.
Never treat a general request to "finish" or "save changes" as permission for
destructive operations or remote publication.

## 5. Stage Precisely

Inspect `git diff -- <path>` for each file in the current commit group. Choose
one staging command for each path:

- **Selected hunk:** If the file has changes for different commit groups, run
  `/home/airtonp/.pi/agent/skills/autonomous-git-commits/scripts/stage-hunk.sh <path> '<unique literal from the current hunk>'`.
  The helper stages one hunk and prints its staged diff. Run it before staging
  another change from that path. See the [usage examples](stage-hunk-examples.md).
- **Whole file:** If every unstaged hunk belongs to the current commit group,
  run `git add -- <path>`.

After staging, run `git diff --cached --stat` and `git diff --cached`. Confirm:

- the staged paths and hunks belong to the current commit group;
- the staged diff is complete enough to work on its own;
- the staged diff is free of credentials, generated artifacts, and debug output.

## 6. Preserve Shell Failure Status

The leading `+` and `-` in a unified diff mark added and removed lines. Inspect
the staged file or command output before reporting a source defect.

If staging fails or the staged diff is wrong, inspect `git diff --cached -- <path>`.
Correct only the affected index entry, preserve working-tree changes, and inspect
the staged diff again. Do not use `git reset --mixed HEAD` as generic recovery:
it clears the full index and does not repair an already-created commit.

Use `&&` between dependent commands. Do not run a later successful command after
a command whose failure must remain visible.

When an absent match is valid, use a conditional instead of a bare `grep`. For
example:

```bash
if git diff --cached | grep -q 'pattern'; then
  printf 'match\n'
else
  printf 'no match\n'
fi
```

Do not infer an index reset, hook, or tool failure from a failed commit. First
run `git diff --cached` and use that output to identify the staged state.

## 7. Write the Commit Message

Use:

```text
<type>(<scope>): <imperative description>
```

Choose the narrowest accurate type. Use `feat` or `fix` for behavior changes and
`docs` only when behavior is unchanged. Keep the subject lowercase, imperative,
specific, and no longer than 50 characters. Do not end it with punctuation.

Add a body only when the user requests one. Wrap body lines at 72 characters.

Before committing, verify that the message describes the staged diff and only the
staged diff.

## 8. Commit Task Changes

Create one commit per atomic group. Continue through the planned groups without
asking for per-commit approval. Do not amend an existing commit unless requested.

After the commit, inspect its result with `git status --short` and
`git log -1 --oneline`. Report:

- the short commit hash for each task commit;
- the exact subject for each task commit;
- any remaining changes, especially unrelated ones left untouched.

Before staging the next commit group, run `git status --short` and inspect
`git diff -- <path>` for every file in that group. Recompute the remaining
hunks. Do not use the previous commit's staging plan or hunk answers.

Do not push unless the user explicitly requested a push.

## Early Exit Conditions

Complete autonomous local commits without requesting guidance. End early only
when an operation would discard or rewrite work without authorization, requires
a remote operation without authorization, or cannot proceed because the tool or
repository state prevents a safe local commit.

When ending early, state the observed fact, the completed commits, the remaining
changes, and the external condition that prevented completion.
