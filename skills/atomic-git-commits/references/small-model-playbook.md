# Atomic Git Commits: Small-Model Playbook

Use this playbook when `SMALL_MODEL_PROFILE` is active or when choosing the patch
helper. Use the file-reading tool to read it and the parent `SKILL.md` completely.
Read any remaining ranges before issuing Git commands in a later tool call.

## 1. Inspect and Plan Once

Run `git status --short`. Read the relevant tracked diffs and complete untracked
files. If output is truncated, read the missing ranges before planning.

Assign every changed and untracked path to commit groups or an explicit
exclusion. Group an implementation with its tests and instructions for the same
behavior. Separate independent purposes. For mixed files, name the selected
changes in each group. Commit an unchanged move before editing the moved file.
Use the actual changes and the parent skill's message rules to decide groups and
subjects. Repository history does not determine the message format or grouping.

Show a short plan in dependency order: **group → selected paths/changes → exact subject**.
Once the groups are clear, proceed with the authorized sequence.

- Inspection authorizes reads. Staging authorizes staging. Editing authorizes edits.
- A commit request authorizes the identified commit. Approval for a sequence covers
  its groups; continue without asking again for each group.
- Push, pull, reset, rebase, merge, revert, stash, and branch switches require
  authorization for that operation. A commit request does not authorize a push.

Preserve unrelated working and staged changes. If ownership or safe separation is
unclear, or unrelated work is already staged, preserve it and ask for the smallest
needed decision. Check authorization against the whole conversation.

## 2. Prepare One Group

Run `mktemp -d /tmp/atomic-commits.XXXXXX` in its own tool call. Copy the returned
absolute directory into later commands. Use literal absolute paths across tool
calls; shell variables may not persist. Each group gets a new patch name, such as
`01.patch`, then `02.patch`. Prepare each group after the previous commit.

Run the helper through `python3` with its absolute path under this skill directory.
References are relative to the skill directory; the shell stays in the repository.

| Selected change | Prepare argument |
|---|---|
| All changes in a tracked or untracked working file | `--worktree REPO_PATH` |
| Only some changes in a file | `--file REPO_PATH EXISTING_CONTENT_FILE` |
| Delete a tracked file | `--delete REPO_PATH` |

Repeat the arguments for all files in the group. `REPO_PATH` is relative to the
repository root. For a mixed file, first create a temporary content file with only
the selected changes applied to HEAD. `--file` **reads this existing input file**;
it does not create it. Keep the working file intact. Whole files need no copies.

Example: replace `/absolute/skill` with this skill's absolute directory and
`/tmp/atomic-commits.EXAMPLE` with the directory returned by `mktemp`:

```sh
python3 /absolute/skill/scripts/commit_patch.py prepare /tmp/atomic-commits.EXAMPLE/01.patch --worktree bin/worktree --worktree README.md
```

For a mixed `settings.txt`, create the selected content at a temporary path first,
then use `--file settings.txt /tmp/atomic-commits.EXAMPLE/selected-settings.txt`.

## 3. Required Patch Workflow

Use [the helper](../scripts/commit_patch.py) for every content commit and content
amendment. After preparation, use this loop:

1. Read the output. For review pages, read every diff line and
   confirm it belongs to the group.
2. Copy the helper's complete `Next:` command into **one new tool call**.
3. Repeat until the helper offers `finalize`. Replace only its `--message` value
   with the planned subject. Run it when the commit is authorized.

The helper prints the command, patch path, checksum path, and next page number.
Reuse them directly. The order is **prepare → review all pages → finalize**.
`finalize` stages the saved patch, checks the complete staged tree against the
reviewed patch, checks whitespace, commits, and checks the committed tree and
message. It stops on the first error and preserves the resulting state for
inspection. It does not print a second copy of the reviewed content.

Run each command separately, with visible output and its original exit status.
Read every review page before the next tool call. Keep errors visible too: run
commands without pipelines, filters, or output redirection.

Review checks:

- Every file and hunk belongs to the group, with no unrelated content.
- The change is complete enough to stand on its own.
- No credential, generated artifact, or accidental debug output is included.
- The subject describes exactly this group, follows Conventional Commits, uses a
  lowercase imperative verb, and has at most 70 characters. Use no message body.

Pages contain at most 80 lines or 8,000 bytes of diff content. The checksum is saved
only after the last review page; `finalize` requires that complete paged review.
Keep the patch, metadata, checksum, and page receipts until the sequence is done.
Receipts track delivery, not comprehension: read the content before continuing.
If a tool truncates output, read the missing content from the saved patch or saved
staged diff before continuing. A statistic or checksum is not a content review.

For content amendments, prepare only additional changes relative to current HEAD
and add `--amend` to the printed finalize command. Previously committed files need
no new inputs. A message-only amendment follows the parent skill.

## 4. Recover from the Actual Error

Read the error before choosing a fix. Correct its input or follow its printed
command. For argument questions, run `prepare --help` before reading script source.

| Observed error | Next action |
|---|---|
| `CONTENT_FILE` is missing | Use `--worktree` for the whole file, or create the selected input file first. Creating directories cannot supply missing content. |
| An artifact already exists | Preserve it. Choose a fresh artifact name. |
| Review is incomplete | Run the printed next page command. |
| Finalize failed | Read the full error and inspect HEAD/index. Correct the cause. Retry the same command only if HEAD is unchanged and the index is still the base or reviewed tree. |
| Patch, HEAD, or index changed | Inspect and preserve work. Prepare and review a new patch only after resolving the changed state. |

The helper rejects stale state, changed patches, whitespace errors, and staged
content outside the patch. Keep these checks; recover through the helper rather
than direct staging or content commits. This profile uses saved checksums and
paged review. Separate `stage`, `verify`, and `commit` commands remain available
for callers that need staged-diff review; this profile uses `finalize`.
If a hook changes committed content, inspect that commit before an authorized
repair. Stop for unexpected changes that the recovery steps above do not explain.

## 5. Finish

After each commit, inspect `git status --short` and `git log -1 --oneline`.
Continue with the next authorized group. Report each short hash and exact subject,
plus remaining changes. Push only when authorized.
