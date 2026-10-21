#!/usr/bin/env python3
"""Advisor usage and cost helper for OMP.

  advisor_usage.py [ROOT]                  per-model averages from __advisor.jsonl
  advisor_usage.py --costs prices.json     $/turn per candidate, cheapest first

ROOT defaults to ~/.omp/agent/sessions.

prices.json:
  {"shape": {"in": 4, "read": 38728, "out": 661},           # optional; else measured
   "models": [{"name": "glm-5.3-flash", "in": 0.15, "read": 0.03, "out": 0.50, "factor": 1}]}

Prices are $/1M tokens. "factor" converts list cost into what the route actually
charges: 1 for per-token providers, pool_monthly / model_monthly_limit for
pooled subscriptions. Cache-write tokens are excluded from the estimate: no
candidate in a Go comparison prices them, so including them would only bias the
models that do.
"""

import json
import os
import signal
import sys
from collections import defaultdict

try:  # piping into head/tail should end quietly
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

ADVISOR_FILE = "__advisor.jsonl"
FIELDS = ("turns", "in", "read", "write", "out", "cost")


def advisor_files(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        if ADVISOR_FILE in filenames:
            yield os.path.join(dirpath, ADVISOR_FILE)


def measure(root):
    agg = defaultdict(lambda: dict.fromkeys(FIELDS, 0))
    for path in advisor_files(root):
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message") or {}
                usage = msg.get("usage") or {}
                if not usage:
                    continue
                row = agg[msg.get("model") or "?"]
                row["turns"] += 1
                row["in"] += usage.get("input", 0) or 0
                row["read"] += usage.get("cacheRead", 0) or 0
                row["write"] += usage.get("cacheWrite", 0) or 0
                row["out"] += usage.get("output", 0) or 0
                row["cost"] += (usage.get("cost") or {}).get("total", 0) or 0
    return agg


def report(agg):
    if not agg:
        print("no advisor usage found", file=sys.stderr)
        return
    print(f"{'model':40} {'turns':>6} {'in':>7} {'cache_read':>11} {'cache_write':>12} {'out':>6} {'cost/turn':>10}")
    for model, row in sorted(agg.items(), key=lambda kv: -kv[1]["turns"]):
        n = row["turns"]
        print(
            f"{model:40} {n:6} {row['in']/n:7.0f} {row['read']/n:11.0f} {row['write']/n:12.0f} "
            f"{row['out']/n:6.0f} ${row['cost']/n:9.5f}"
        )


def shape_of(agg, model):
    row = agg[model]
    n = row["turns"] or 1
    return {k: row[k] / n for k in ("in", "read", "out")}


def cost_table(price_file, agg):
    with open(price_file) as fh:
        spec = json.load(fh)
    # Compare candidates on the shape of the advisor being replaced, not the
    # average across every model that ever held the role.
    source = spec.get("shape_from") or max(agg, key=lambda m: agg[m]["turns"], default=None)
    if spec.get("shape"):
        shape, label = spec["shape"], "from prices.json"
    elif source in agg:
        shape, label = shape_of(agg, source), f"measured from {source}"
    else:
        print("no shape: pass \"shape\" or \"shape_from\" in prices.json", file=sys.stderr)
        return
    rows = []
    for m in spec["models"]:
        raw = (
            shape["in"] * m.get("in", 0)
            + shape["read"] * m.get("read", 0)
            + shape["out"] * m.get("out", 0)
        ) / 1e6
        rows.append((raw * m.get("factor", 1), raw, m))
    print(
        f"shape: in={shape['in']:.0f} read={shape['read']:.0f} out={shape['out']:.0f}  ({label})"
    )
    for pooled, raw, m in sorted(rows):
        print(f"{m['name']:32} factor={m.get('factor', 1):<5} ${raw:8.5f}/turn raw  ${pooled:8.5f}/turn charged")


def main(argv):
    if len(argv) >= 2 and argv[0] == "--costs":
        agg = measure(os.path.expanduser("~/.omp/agent/sessions"))
        report(agg)
        cost_table(argv[1], agg)
        return 0
    report(measure(os.path.expanduser(argv[0] if argv else "~/.omp/agent/sessions")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
