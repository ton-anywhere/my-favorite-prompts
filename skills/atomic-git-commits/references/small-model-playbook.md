# Atomic Git Commits: Small-Model Playbook

Use this playbook when `SMALL_MODEL_PROFILE` is active or when explicitly choosing
the patch helper. Follow it in order.
Read this entire playbook and the parent `SKILL.md` with the file-reading tool
before the first Git command. Read any remaining ranges if output is truncated.

## 1. Identify the Requested Operation

Classify the user's request before running commands:

- **Inspect:** status, diff, log, show, or "what changed."
- **Change repository state:** add, stage, restore, reset, stash, branch, checkout,
  merge, rebase, or revert.
- **Commit:** create or amend a commit.
- **Remote:** fetch, pull, or push.

Do only the requested class of operation. An inspection request does not authorize
staging or committing. A request to edit files does not authorize a commit.

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

Keep an implementation, its tests, and instructions for that same behavior
together when they serve one purpose. Different file types do not by themselves
make independent entities. Decide from the actual changes, not repository history.

When a file contains mixed changes, prepare its intermediate content for the
current group. Use the parent skill's required patch helper; do not stage the
whole working file. If safe separation is unclear, preserve work and ask.

Assign every changed and untracked path to a commit group or an explicit exclusion
before proposing the sequence. Include supporting tests, fixtures, and instructions.
Show the groups in dependency order before staging. A path with mixed changes can
appear in multiple groups; state the changes selected for each group.

## 4. Respect Authorization Boundaries

Read the user's latest message literally.

- "Review," "inspect," or "show the diff" authorizes inspection only.
- "Stage this" authorizes staging only.
- "Commit this" authorizes one commit for the clearly identified change.
- A commit does not authorize a push.
- A push, pull, reset, rebase, merge, revert, stash, or branch switch must be
  explicitly requested.

If authorization is missing or ambiguous, explain the proposed operation and ask
for approval. Never treat a general request to "finish" or "save changes" as
permission for destructive operations or remote publication.

## 5. Required Patch Workflow

Use [`../scripts/commit_patch.py`](../scripts/commit_patch.py) for every content
commit and content amendment. Run it through `python3` with its absolute path.
Skill-relative references do not change the shell's working directory.

Create a fresh artifact directory with `mktemp -d /tmp/atomic-commits.XXXXXX`.
Reuse the returned absolute directory for this sequence. Use a different patch
and checksum filename for each group. Preserve existing artifacts when a name
collides; select a fresh name instead of removing them.

1. **Prepare:** Supply explicit `--file REPO_PATH CONTENT_FILE` pairs or `--delete REPO_PATH`. Use the working file directly when all its changes belong to this group. For shared files, use temporary content containing only this group's changes. Working files must remain intact. Prepare the next patch after the preceding commit, against current HEAD.
2. **Review:** Run `review PATCH --sha256-file CHECKSUM_FILE --page 1`. Read the entire page, then run the exact next command printed by the helper in a new tool call. Repeat until delivery is complete and the checksum file is saved.
3. **Stage:** Run `stage PATCH --reviewed-sha256-file CHECKSUM_FILE` after reading every review page. The helper checks the complete staged tree against the patch.
4. **Verify:** Run `verify PATCH --reviewed-sha256-file CHECKSUM_FILE --page 1`. Read every page of the staged diff, one tool call at a time, following the printed next command. Complete this before committing.
5. **Commit:** Once authorized, use the printed commit command with the intended `--message`. For a content amendment, prepare only the additional changes relative to current HEAD and add `--amend` to commit. Already committed files do not need to be supplied again.

Each page contains at most 80 lines or 8,000 bytes of diff content. The helper
tracks consecutive page delivery in sidecar JSON files beside the checksum file.
It creates the checksum only after the final review page. For this paged workflow,
commit also requires all verification pages. Keep these artifacts until the sequence
is complete; stale state requires a new review checksum filename.

Run each helper command separately, with visible output and its original exit
status. Use no pipelines, filters, output suppression, or trailing success commands.
If the tool still truncates a page, read the missing bytes from the saved patch
before continuing. For a truncated verification page, save the complete staged
diff and read the missing content. A file list, statistic, or checksum is not a
content review.

Example: replace `/absolute/skill` and `/tmp/atomic-commits.EXAMPLE` with the actual
skill directory and the returned artifact directory. Each line is a separate tool
call. For multi-page output, finish the printed continuation commands before
moving to the next step.

```sh
python3 /absolute/skill/scripts/commit_patch.py prepare /tmp/atomic-commits.EXAMPLE/01.patch --file settings.txt /tmp/01-settings.txt
python3 /absolute/skill/scripts/commit_patch.py review /tmp/atomic-commits.EXAMPLE/01.patch --sha256-file /tmp/atomic-commits.EXAMPLE/01.sha256 --page 1
python3 /absolute/skill/scripts/commit_patch.py stage /tmp/atomic-commits.EXAMPLE/01.patch --reviewed-sha256-file /tmp/atomic-commits.EXAMPLE/01.sha256
python3 /absolute/skill/scripts/commit_patch.py verify /tmp/atomic-commits.EXAMPLE/01.patch --reviewed-sha256-file /tmp/atomic-commits.EXAMPLE/01.sha256 --page 1
python3 /absolute/skill/scripts/commit_patch.py commit /tmp/atomic-commits.EXAMPLE/01.patch --reviewed-sha256-file /tmp/atomic-commits.EXAMPLE/01.sha256 --message 'fix(settings): increase timeout'
```

Read the helper's full staged diff. Confirm:

- every staged change belongs to the approved atomic group;
- no unrelated file or hunk is staged;
- the staged diff is complete enough to work on its own;
- no secret, credential, generated artifact, or accidental debug output appears.

The helper rejects pre-existing staged changes, changed patches, stale HEAD/index
state, whitespace errors, and staged content outside the patch. If a command fails,
inspect the failure and preserve work. Correct a recoverable input or sequence error
and follow the printed next command. Do not bypass checks with direct staging or
content commits. If a hook changes committed content, inspect the reported commit
before deciding on an authorized repair.

| Observed error | Recovery |
|---|---|
| Patch, metadata, or checksum already exists | Preserve it; choose a fresh artifact name. |
| Review checksum is not ready | Continue review at the printed page. |
| Nothing is staged | Run the printed stage command, then verify. |
| Incorrect checksum length | SHA256 has 64 hexadecimal characters; reuse the saved review checksum. |
| Patch or base state changed | Preserve work; prepare and review a new patch against current HEAD. |

The receipt records printed bytes, not comprehension. Shell redirection can hide
output even when the helper records delivery. The skill requires visible output;
the helper cannot enforce shell behavior or prevent direct Git bypasses. The legacy
unpaged and literal-checksum options remain available for other callers, but this
profile uses the paged workflow. Reuse the saved checksum; do not recompute it or
read a fresh value from patch metadata at each step.

## 6. Write the Commit Message

Use:

```text
<type>(<scope>): <imperative description>
```

Choose the narrowest accurate type. Use `feat` or `fix` for behavior changes and
`docs` only when behavior is unchanged. Use a lowercase imperative verb and a
specific complete subject no longer than 70 characters, including type and scope.
Prefer shorter subjects when clear. Preserve technical identifiers.
Do not end the subject with punctuation. Measure length with a command when unsure;
do not rely on a manual count.

Do not include a commit message body.

Before committing, verify that the message describes the staged diff and only the
staged diff.

## 7. Commit Only When Authorized

Create exactly one approved commit at a time through the patch helper. Approval
for a named sequence covers its groups; it does not cover additional groups.

After the commit, inspect its result with `git status --short` and
`git log -1 --oneline`. Report:

- the short commit hash;
- the exact subject;
- any remaining changes, especially unrelated ones left untouched.

Do not push unless the user explicitly requested a push.

## Stop Conditions

Stop and ask the user before continuing when:

- ownership of a change is uncertain;
- an unrelated change is already staged;
- safe hunk separation is unclear;
- the requested operation could discard or rewrite work;
- commit or remote-operation authorization is missing;
- command output reveals unexpected repository changes beyond a recoverable input
  or sequence error described above.

When stopping, state the observed fact, the risk, and the smallest decision needed
from the user. Do not guess.
