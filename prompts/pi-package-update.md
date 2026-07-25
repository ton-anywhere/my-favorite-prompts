# Pi Package Update Protocol (git-based)

## Context

Only git-installed pi packages are used. NPM packages are excluded due to security concerns.

## Workflow

### 1. Preview (non-destructive)

Test the new version for a single run without touching settings:

```bash
pi -e git:github.com/user/repo@new-ref
```

### 2. Inspect changes

Review what actually changed before applying:

```bash
cd ~/.pi/agent/git/<host>/<path>
git fetch origin
git log --oneline v1..origin/v2
git diff v1..origin/v2 --stat
```

### 3. Apply

Only after steps 1 and 2 pass:

```bash
pi install git:github.com/user/repo@v2
```

## Notes

- Refs are pinned tags or commits — `pi update --extensions` won't auto-advance them.
- Reverting is as simple as re-running the old ref.
- Project-level installs live in `.pi/git/`; global in `~/.pi/agent/git/`.
