# Epic

For work with two or more tasks, each with its own user story. An epic is a README plus one task file per task, and every fact lives in exactly one of them.

```
<tasks dir>/[epic-name]/
├── README.md     why and what: decisions, global constraints, the task table. No implementation steps.
└── [slug].md     one task, in task-template.md's format with the **Epic:** line
```

Task files follow [task-template.md](task-template.md) with its `**Epic:** [README](README.md)` line. They link to the README; they never copy from it. The reviewer of a task copies the README's Global Constraints.

Epic tasks have no numbers. The README table's order is the work order, files are named by slug, and other tasks are referred to by name. Reordering or inserting a task changes only the table.

## Phase 1

Write the complete `README.md` (template below). Also write each task file, filling every section except **Sub-tasks**: the heading, the Epic line, User story, Interfaces, Background, Relevant Files and Notes. Fold a plan given as input into the README and delete the plan file; the epic has no third document.

## Phase 2

After the owner approves Phase 1, add the **Sub-tasks** section to each task file, following [sub-tasks.md](sub-tasks.md).

## Branches

- Each task gets its own branch, cut from the project's integration branch and merged alone. The owner usually creates it by hand, so there is no branch-creation sub-task.
- Use one shared branch only when tasks would break the integration branch unless merged together, and say why in the README.
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

Check a task here when every sub-task in its file is checked.

| Done | Task | Branch | Delivers | Needs |
|------|------|--------|----------|-------|
| [ ] | [Name](slug.md) | `feature/[epic]-[slug]` | [the user story's outcome once merged] | — |
| [ ] | [Other name](other-slug.md) | none (no code) | [...] | Name |

[One paragraph on order and merging.]

## Review Focus

1. **[Input or failure mode no happy-path test hits]**: [expected behavior]. → [task name]
```

Review Focus lists up to five such inputs; each names the task whose test pins it.
