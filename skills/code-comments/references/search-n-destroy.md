# search-n-destroy

The manual sweep mode of `code-comments`, started only when the user invoked the skill with the `search-n-destroy` argument. A request to "remove all comments" without that argument never reaches this file; if you are reading it without the argument present, stop and apply the default rules in [SKILL.md](../SKILL.md) instead.

The sweep deletes every comment in source code and fixes what those comments were papering over. The parent SKILL.md's *The ban's scope* is the canonical exemption list — config files, machine-read comments, convention doc comments. This file never overrides it.

This procedure adapts [Matt Pocock's comment-cleanup prompt](https://x.com/mattpocockuk/status/2123798388227403983) to the [comments-are-a-code-smell rule](https://x.com/tonanywhere/status/2123816876790665658).

## 1. Scope

The whole current codebase's source code, always: the repo root from `git rev-parse --show-toplevel`. A pass too large for one review is split by directory, with the remainder listed in the report — never silently narrowed.

## 2. Inventory first

List candidates with a command, not by scrolling. Skip this step = incomplete pass.

```bash
rg -n --no-heading -g '!*.md' -g '!config/**' -g '!*.yml' -g '!*.yaml' -g '!*.json' -g '!*.jsonc' -g '!*.toml' -g '!*.ini' -g '!*.cfg' -g '!*.conf' -g '!*.properties' -g '!Dockerfile*' -g '!Containerfile*' -g '!Makefile*' -g '!Justfile' -g '!.env*' -g '!*.tf' -g '!*.tfvars' '^\s*(#|//|/\*|\*)|\s(#|//)\s' "$ROOT"
```

The inventory flags candidates, not findings: a hit is never deleted only because it matched. Drop without listing every hit the scope in [SKILL.md](../SKILL.md) exempts.

## 3. Classify each candidate

| Category | Test | Action |
|---|---|---|
| Tautology | A competent reader gets the fact from the code alone | Delete |
| Excuse | Papers over a hack ("workaround for…", "TODO", "temporary") | Delete **and** file an issue or task naming the real fix |
| Stale | References code, APIs, or facts that no longer exist | Delete |
| Decision Record | A decision whose context or trade-offs a future reader needs | Move into an ADR, then delete |
| Project doc convention | A doc comment (rustdoc, javadoc, godoc, docstring, YARD) in a format the project already uses | Keep; the mode adapts to the project's doc convention |
| Out of scope | The file sets configuration, not behavior | Keep; never a candidate |

A doc comment in a project with no such convention is an ordinary candidate, classified like any other comment.

When you cannot tell whether a file is configuration or source code, keep the comment and list the file in the report.

## 4. Fix

- Delete comments directly; the diff shows each removal.
- Every Excuse gets its issue or task filed before the comment goes — an unrecorded excuse is a lost bug report. Use the project's issue tracker, or its task file location; the fix-task template is in [artifact-templates.md](artifact-templates.md).
- Every Decision Record becomes one ADR per decision, in `docs/adr/` with sequential numbering (template in [artifact-templates.md](artifact-templates.md)); create the directory lazily when the project has no ADR location, and say so in the report.
- A Tautology that hides a naming defect is not just deleted: rename the construct so the fact survives, under the rename rule in [SKILL.md](../SKILL.md).

## 5. Report

End the pass with the numbers:

- Comments per category: tautologies deleted, excuses deleted (with the issues or tasks filed), stale deleted, decision records moved (with the ADRs written), out-of-scope hits skipped, files listed as uncertain configuration.
- Lines shed.
- Deferred comments (ratchet): every candidate not handled this pass, with its reason.
