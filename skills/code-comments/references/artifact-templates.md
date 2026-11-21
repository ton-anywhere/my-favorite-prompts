# Artifact Templates

The documents a comment becomes. Each template is minimal: fill what the case needs, skip the rest.

## ADR (decision record)

ADRs follow the `domain-modeling` skill's `ADR-FORMAT.md` — that file is canonical. Summary here so a routing decision never blocks on it:

- **Location**: `docs/adr/`, sequential numbering (`0001-slug.md`, `0002-slug.md`, …). Create the directory lazily, when the first ADR is needed.
- **Template**:

```markdown
# {Short title of the decision}

{1-3 sentences: the context, what was decided, and why.}
```

- **Qualification** — all three must hold: hard to reverse, surprising without context, the result of a real trade-off. A decision that is easy to reverse or has no real alternative is not an ADR.

Worked example: *An ADR carries it* in [routing-examples.md](routing-examples.md). Who ends the temporary state decides the artifact: when your own team's planned work ends it ("nullable until our backfill runs"), it is a fix task; when another team or system holds it in place ("until Billing migrates off its reader"), it is an ADR.

## Fix task (from an excuse)

A comment excusing a hack becomes a work item, filed before the comment is deleted. It records the problem, the real fix, and how completion is observable — it is not an implementation plan; when the fix is picked up for planned implementation, `task-breakdown`'s template takes over.

```markdown
# {The real fix, as a short imperative title}

Status: open
Filed: {date}
Source: {file:line of the hack}

## Problem

{What is hacked, and the damage it can cause.}

## Real fix

{What the correct implementation is.}

## Done when

{The observable condition that lets the code be un-hacked.}
```

Worked example — this excuse:

```ruby
# TODO: remove the manual slice when the vendor fixes their pagination
records = fetch_all.first(BATCH)
```

becomes `tasks/vendor-pagination.md`:

```markdown
# Use the vendor's pagination instead of slicing fetch_all

Status: open
Filed: 2026-11-21
Source: app/jobs.rb:9 — `JobsImporter#run`

## Problem

`fetch_all` materializes every vendor record, then `.first(BATCH)` throws
the rest away: imports cost a full fetch for one batch, and any record
beyond the batch is silently dropped.

## Real fix

Call the vendor's paginated endpoint and follow its cursor until exhausted,
storing each page as it arrives.

## Done when

`JobsImporter#run` never materializes the full result set and records
beyond the first batch are imported.
```

## Module doc (from usage prose)

A comment explaining how to use a module becomes its document — the module's README, or its section of the project's usage guide. Structure, in order:

1. **What it does** — one paragraph.
2. **How to use it** — the smallest working example, real code.
3. **What the caller must handle** — units, errors, side effects.
4. **What it does not do** — boundaries worth stating, when they are non-obvious.

In a project whose convention is doc comments (YARD, rustdoc, godoc), the convention's doc comment holds this instead of a separate file — see *Doc comments* in [SKILL.md](../SKILL.md).
