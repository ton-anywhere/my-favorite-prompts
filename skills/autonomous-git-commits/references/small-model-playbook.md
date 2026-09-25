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

From the output, separate:

1. changes made for the current task;
2. pre-existing or unrelated changes;
3. untracked files whose ownership is uncertain.

Preserve groups 2 and 3. Never clean, restore, reset, overwrite, or include them
merely to make the working tree look tidy.

## 3. Form Atomic Groups

For every changed file, state the single purpose it serves. Put files in the same
group only when they are required for one coherent behavior.

Split groups when any of these are true:

- the changes can be understood or reverted independently;
- they affect independent skills, agents, or features;
- the proposed subject needs "and" to join separate actions;
- one file contains unrelated hunks.

When a file contains mixed changes, use patch staging and select only the relevant
hunks. If safe hunk selection is unclear, stop and ask the user instead of staging
the whole file.

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

If the task scope or ownership of changes is ambiguous, ask for clarification.
Never treat a general request to "finish" or "save changes" as permission for
destructive operations or remote publication.

## 5. Stage Precisely

Stage explicit paths or selected hunks. Do not use broad staging commands such as
`git add .` or `git add -A` when unrelated changes exist.

After staging, run `git diff --cached --stat` and `git diff --cached`. Confirm:

- every staged change belongs to the current task's atomic group;
- no unrelated file or hunk is staged;
- the staged diff is complete enough to work on its own;
- no secret, credential, generated artifact, or accidental debug output appears.

If the staged diff is wrong, correct the index without discarding working-tree
changes, then inspect it again.

## 6. Write the Commit Message

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

## 7. Commit Task Changes

Create one commit per atomic group. Continue through the planned groups without
asking for per-commit approval. Do not amend an existing commit unless requested.

After the commit, inspect its result with `git status --short` and
`git log -1 --oneline`. Report:

- the short commit hash for each task commit;
- the exact subject for each task commit;
- any remaining changes, especially unrelated ones left untouched.

Do not push unless the user explicitly requested a push.

## Stop Conditions

Stop and ask the user before continuing when:

- ownership of a change is uncertain;
- an unrelated change is already staged;
- safe hunk separation is unclear;
- the requested operation could discard or rewrite work;
- authorization for a remote or history-rewriting operation is missing;
- command output conflicts with the expected repository state.

When stopping, state the observed fact, the risk, and the smallest decision needed
from the user. Do not guess.
