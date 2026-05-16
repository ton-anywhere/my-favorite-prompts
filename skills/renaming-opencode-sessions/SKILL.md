---
name: renaming-opencode-sessions
description: Use when you need to rename an opencode session - bypasses the interactive /rename command by updating the SQLite database directly
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Renaming OpenCode Sessions

## Overview

Renames opencode sessions programmatically by updating the SQLite database at `~/.local/share/opencode/opencode.db`. This bypasses the interactive `/rename` command which requires manual TUI access.

## When to Use

- User requests renaming a session but doesn't want to do it manually
- You have the session ID and desired new title
- Batch renaming multiple sessions (automate with loop)

**Do NOT use for:** Creating new sessions, deleting sessions, or other session management tasks.

## How It Works

OpenCode stores session metadata in a SQLite database. The `session` table contains:
- `id` - Session UUID (e.g., `ses_25dd535caffemzyEEcQaZZFdqZ`)
- `title` - Display name shown in `opencode session list`

Updating this field directly achieves the same result as `/rename` without interactive input.

## Implementation

The logic lives in [`rename_session.py`](./rename_session.py) — this file is the **single source of truth**.

### Usage Examples

```bash
# Command-line arguments (preferred)
./rename_session.py ses_25dd535caffemzyEEcQaZZFdqZ "Index page redesign & centered search"

# Environment variables
SESSION_ID="ses_abc123" NEW_TITLE="Bugfix PR" ./rename_session.py

# As Python module
python3 rename_session.py ses_xyz789 "Feature implementation"
```

### From Another Script/Agent

```python
import subprocess
from pathlib import Path

skill_dir = Path(__file__).parent  # or wherever the skill is located
script_path = skill_dir / "renaming-opencode-sessions" / "rename_session.py"

subprocess.run([
    "python3", str(script_path),
    "ses_25dd535caffemzyEEcQaZZFdqZ",
    "New Session Title"
])
```

### Verification

After renaming, verify with:
```bash
opencode session list | grep <session_id>
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `sessions` table name | Table is singular: `session` |
| Forgetting `conn.commit()` | Changes won't persist without commit |
| Wrong database path | Always `~/.local/share/opencode/opencode.db` |
| Not expanding `~` in Python | Use `os.path.expanduser("~/...")` or full path |

## Real-World Impact

**Before:** Manual process requiring TUI access - tedious for batch operations  
**After:** One-liner Python script - automatable and scriptable
