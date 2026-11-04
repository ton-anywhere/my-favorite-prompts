#!/usr/bin/env python3
"""Inspect omp session headers.

Sessions live at ~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<id>.jsonl.
Line 1 holds the title; line 2 holds the header (id, cwd, repository).

  omp_sessions.py stale
      id<TAB>recorded cwd<TAB>primary worktree, for sessions whose cwd is gone.

  omp_sessions.py verify <id> [<id> ...]
      OK/FAIL per id: exactly one transcript, with an existing recorded cwd.
"""
import glob
import json
import os
import signal
import sys

try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except AttributeError:
    pass

ROOT = os.path.join(os.path.expanduser("~"), ".omp", "agent", "sessions")


def headers():
    for path in sorted(glob.glob(os.path.join(ROOT, "*", "*.jsonl"))):
        try:
            with open(path) as f:
                f.readline()
                yield path, json.loads(f.readline())
        except (OSError, json.JSONDecodeError):
            continue


def stale():
    for path, header in headers():
        cwd = header.get("cwd")
        if cwd and not os.path.isdir(cwd):
            repo = header.get("repository") or {}
            print(header.get("id"), cwd, repo.get("primaryWorktreeRoot", "-"), sep="\t")


def verify(ids):
    hits = {i: [] for i in ids}
    for path, header in headers():
        if header.get("id") in hits:
            hits[header["id"]].append((path, header.get("cwd")))
    failed = False
    for i in ids:
        found = hits[i]
        cwd = found[0][1] if found else None
        ok = len(found) == 1 and bool(cwd) and os.path.isdir(cwd)
        failed |= not ok
        detail = f"{found[0][0]}\t{cwd}" if found else "missing"
        print("OK" if ok else "FAIL", i, detail, sep="\t")
    return 1 if failed else 0


if len(sys.argv) >= 2 and sys.argv[1] == "stale":
    stale()
elif len(sys.argv) >= 3 and sys.argv[1] == "verify":
    sys.exit(verify(sys.argv[2:]))
else:
    sys.exit(__doc__)
