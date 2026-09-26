# Stage One Diff Hunk

Use `stage-hunk.sh` when one file has hunks for different commit groups. Inspect
`git diff -- <path>` and choose a literal that appears in only the target hunk.
Each example starts with no staged change for its path. The script stages the
complete matching hunk and prints its staged diff.

## Example 1: Stage the first hunk

Assume `git diff -- config/features.conf` shows two separate hunks:

```diff
@@ -1 +1 @@
-feature_alpha=false
+feature_alpha=true
@@ -20 +20 @@
-feature_beta=false
+feature_beta=true
```

Stage only the first hunk:

```bash
/home/airtonp/.pi/agent/skills/autonomous-git-commits/scripts/stage-hunk.sh \
  config/features.conf 'feature_alpha=true'
```

The `feature_beta` hunk stays unstaged.

## Example 2: Stage a later hunk

Assume `git diff -- aliases` shows two separate hunks:

```diff
@@ -10 +10 @@
-alias co='pi'
+alias co='pi --no-extensions'
@@ -50 +50 @@
-alias ll='ls -l'
+alias ll='ls -lah'
```

Stage only the `alias ll=` hunk:

```bash
/home/airtonp/.pi/agent/skills/autonomous-git-commits/scripts/stage-hunk.sh \
  aliases 'alias ll='
```

The `alias co=` hunk stays unstaged.

## Example 3: Choose a unique literal

Assume `git diff -- 'editor settings.conf'` shows two hunks that both contain
`enabled=true`:

```diff
@@ -4,2 +4,2 @@
-theme_enabled=false
-style=light
+theme_enabled=true
+style=dark
@@ -25,2 +25,2 @@
-autosave_enabled=false
-delay=30
+autosave_enabled=true
+delay=5
```

Use `style=dark` to identify only the theme hunk. Quote the path because it
contains a space:

```bash
/home/airtonp/.pi/agent/skills/autonomous-git-commits/scripts/stage-hunk.sh \
  'editor settings.conf' 'style=dark'
```

The autosave hunk stays unstaged.
