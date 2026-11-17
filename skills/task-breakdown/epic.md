# Epic

For work with two or more independently mergeable tasks. Exactly two kinds of document; every fact lives in one of them.

```
tasks/[epic-name]/
├── README.md          why and what — no implementation steps
└── [slug].md         how — one file per task, the only place with sub-task checkboxes
```

## Phase 1

Write the complete `README.md` (template below). Its Tasks table names each task's branch, what it delivers (the working state after it), and what it needs; it replaces separate milestone tables and dependency diagrams. Fold a plan given as input into the README and delete the plan file: the epic has no third document. Write no task file yet.

## Phase 2

Write one task file per README row (template below), with Interfaces and Relevant Files in each. README content is linked from task files, never copied.

Epic tasks have no numbers: the README table order is the work order, files are named by slug, sub-tasks are unnumbered checkboxes, and other tasks are referred to by name. Reordering or inserting a task changes only the table.

Each task file is a valid plan for `subagent-driven-development`: every file has the same fixed heading `# Task 1: [Name]` (one task per file, so the `1` never changes), which lets `task-brief <slug>.md 1` extract it; its Interfaces block carries what neighbouring tasks use; and the reviewer copies the README's Global Constraints.

## Branches

- Each task gets its own branch, cut from `main` and merged alone; the owner usually creates it by hand, so there is no branch-creation task.
- Use one shared branch only when tasks would break `main` unless merged together, and say why in the README.
- A task that changes no code (an operation, a hand-run migration) has no branch: `none (no code)`.
- A branch name appears only in the README table.

## README template

```markdown
# Epic: [Name]

**Goal:** [One or two sentences.]

**Source of truth:** [What wins when another doc disagrees with this epic.]

## Decisions

- **[Decision].** [Reason.]
- **Out of scope:** [...]

## Global Constraints

- [Project-wide rules every task obeys.]

## Tasks

Check a sub-task in its task file when done, and the task here when its file is complete.

| Done | Task | Branch | Delivers | Needs |
|------|------|--------|----------|-------|
| [ ] | [Name](slug.md) | `feature/[epic]-[slug]` | [working state after this task] | — |
| [ ] | [Other name](other-slug.md) | none (no code) | [...] | Name |

[One paragraph on order and merging.]

## Review Focus

1. **[Input or failure mode no happy-path test hits]**: [expected behavior]. → [task name]
```

Review Focus lists up to five such inputs; each names the task whose test pins it.

## Task file template

```markdown
# Task 1: [Name]

**Epic:** [README](README.md) (decisions, global constraints; Review Focus N is tested here)

**Outcome:** [What the owner observes when the task is done.]

**Interfaces:**
- Consumes: [exact signatures this task uses from earlier tasks, or "nothing"]
- Produces: [exact names, parameters, and return types later tasks rely on]

## Background

- [Only facts the implementer cannot find quickly: file:line, library behavior, external data details.]

## Sub-tasks

- [ ] **[Failing test]**: file, test names, assertions.
  - _Verify:_ [command] → [expected failure]
- [ ] **[Implementation]**: file, signature, values.
  - _Verify:_ [command] → [expected output]

## Relevant Files

- `path/to/file` — [why]

## Notes

- [Gotchas]
```
