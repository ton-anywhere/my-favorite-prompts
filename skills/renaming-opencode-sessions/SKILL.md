---
name: renaming-opencode-sessions
description: Use when you need to rename an opencode session - bypasses the interactive /rename command by updating the SQLite database directly
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

### Single Session Rename

```python
import sqlite3

db_path = "~/.local/share/opencode/opencode.db"
session_id = "ses_25dd535caffemzyEEcQaZZFdqZ"
new_title = "Index page redesign & centered search implementation"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current title
cursor.execute("SELECT id, title FROM session WHERE id=?", (session_id,))
result = cursor.fetchone()
if result:
    print(f"Current: {result[1]}")
    # Update title
    cursor.execute("UPDATE session SET title=? WHERE id=?", (new_title, session_id))
    conn.commit()
    print(f"Updated to: {new_title}")
else:
    print("Session not found!")

conn.close()
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
