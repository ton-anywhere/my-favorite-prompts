---
name: filter-repo
description: Remove files or directories from Git history with git-filter-repo. Use when asked to purge paths from past commits or publish rewritten branches and tags after cleanup. Do not use for ordinary file deletion.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Remove paths from Git history

Use this procedure when unwanted paths must disappear from past commits.
Examples below remove `docs/superpowers/` and `docs/verification/`.
Replace them with the requested paths. Run commands from the repository root.

Explain the commands when asked for guidance. Execute a rewrite or force-push
only when the user authorizes that action. Affected commit IDs change.

## 1. Inspect the repository

```sh
git status --short
git remote -v
git branch -a
git tag
git worktree list
```

Record the remote URL. Preserve unrelated work. Coordinate other active
worktrees before rewriting their shared history.

## 2. Back up and prepare

Choose a new backup filename outside the repository:

```sh
git bundle create ../before-filter.bundle --all
git bundle verify ../before-filter.bundle
```

Stop if backup or verification fails. The bundle retains the original history,
including the unwanted files. It does not save uncommitted changes.

To prevent future additions, add and commit a `.gitignore` rule before filtering
(for example, `__pycache__/`). Skip this step if the rule is already committed.
Obtain authorization before committing; stage only the intended change.

If the only changes are unstaged deletions of the unwanted paths, restore them
temporarily to make the working tree clean:

```sh
git restore -- docs/superpowers docs/verification
git status --short
```

For other changes, save them separately before continuing.

## 3. Remove the paths from history

```sh
git filter-repo --force --invert-paths \
  --path docs/superpowers/ \
  --path docs/verification/
```

`--force` bypasses the fresh-clone check; use it here only after the backup and
clean-worktree checks. This removes the paths from the current checkout too.
No deletion commit is needed. Include former paths if the files were renamed;
path filtering does not follow renames automatically.

By default, this rewrites all local branches and tags. Do not repeat it for each
branch. Local backup branches are rewritten too; the external bundle preserves
the original history.

## 4. Verify removal

```sh
git status --short
git log --all --oneline -- docs/superpowers/ docs/verification/
git branch
git tag
```

The status and path-history checks should print nothing. Confirm that the
expected branches and tags remain.

## 5. Publish branches and tags

`filter-repo` normally removes `origin`. Check before adding it again:

```sh
git remote -v
# If origin is absent, use the URL recorded in step 1:
git remote add origin <recorded-remote-url>
```

Choose which local branches to publish. To update selected branches:

```sh
git push --force origin main <other-branch>
```

Or, if every local branch should be published:

```sh
git push --force origin --all
```

`--all` includes remaining local branches such as `backup/main`. Use explicit
branch names if a local branch should stay local. A remote branch omitted from
the push keeps its old history. For remote-only branches, include them locally
before cleanup and publish their rewritten versions, or explicitly authorize
their deletion. Do not fetch old history back into the cleaned repository.

Keep the existing tag names. To publish tags that have never been pushed:

```sh
git push origin --tags
```

To replace tags already published:

```sh
git push --force origin --tags
```

Updating only `main` leaves old history reachable through other unchanged
remote branches or tags. Coordinate publication with collaborators; cloning
again avoids mixing old and rewritten history. Existing clones and the backup
bundle still contain the original history.

Reference: [git-filter-repo manual](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt).
