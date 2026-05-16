---
name: code-comments
description: "Use when writing new code or reviewing existing code to decide which comments to add, keep, or remove. Defines what makes a comment valuable vs. noise."
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Code Comments Standard

Comments exist to transfer knowledge that cannot be read from the code itself. A comment that restates what the code does is noise. A comment that explains *why* it does it — or warns of a non-obvious consequence — is essential.

---

## Add or Keep Comments When

**A restart or deployment action is required.**
Initializers and certain config files require a server restart to take effect. Always include the restart warning at the top of those files:
```ruby
# Be sure to restart your server when you modify this file.
```

**The "why" is not derivable from the code.**
If a future developer would ask "why is this here?", the comment belongs. Examples:
- A migration column that is intentionally nullable until a later task populates it
- An index that prevents a non-obvious data integrity problem
- A formatter or library chosen for compatibility with a specific infrastructure tool

**An inline operation is opaque.**
Short inline comments on non-obvious expressions are acceptable:
```ruby
trace_id = context.trace_id.unpack1('H*') # binary → hex string
```

**A commented-out block is a deliberate template.**
If a block is commented out because it is optional or environment-specific (e.g. CSP policy, SSL enforcement, DNS rebinding protection), keep it so the path to activation is clear without requiring external research.

**A security concern is present.**
Any configuration that filters sensitive data, enforces access control, or affects security posture should explain what it protects and why. Example: parameter filtering comments explaining partial-match behavior and the goal of limiting log dissemination.

**A health or observability endpoint serves an infrastructure role.**
If a route or config is consumed by load balancers, uptime monitors, or tracing systems, say so explicitly.

---

## Remove or Skip Comments When

**The comment restates the code.**
`# Set version to 1.0` above `config.assets.version = '1.0'` adds nothing.

**The information is authoritative elsewhere.**
Standard Rails environment config options, Puma DSL parameters, and RSpec setup prose are all documented in their official guides. Duplicating them in-file creates maintenance burden without adding value.

**The comment is auto-generated boilerplate.**
Schema file headers, seeds file examples, and generator-output comments can be removed without loss.

**The "why" is already obvious from context.**
Method names, variable names, and surrounding code often make intent clear. Don't add prose that a reader would reach without the comment.

---

## Placement and Tone

- **File-level comments**: top of file, before any `require` or configuration call.
- **Block-level comments**: line immediately above the construct they describe, indented to match.
- **Inline comments**: sparingly — only for opaque expressions (format conversions, magic numbers, binary ops).
- **Section dividers** (`# === SCOPES ===`): avoid in production code; acceptable in long test files only.

---

## Quick Decision Test

Before writing or keeping a comment, ask: *"Would a competent developer, reading only this repository, understand why this line exists without the comment?"*

- **No** → keep the comment.
- **Yes** → remove it.
