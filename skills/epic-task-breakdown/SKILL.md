---
name: epic-task-breakdown
description: Use when turning an implementation plan or spec into an epic of task files under tasks/<epic>/, when breaking a plan into independent tasks with their own branches, or when maintaining, updating, or checking off an existing epic folder.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Epic Task Breakdown

Turns a plan (for example from `writing-plans`) into an epic folder. The epic holds exactly two kinds of document, and every fact lives in one of them.

## Layout

```
tasks/<epic>/
├── README.md          why and what — no implementation steps
└── NN-<slug>.md       how — one file per task, the only place with sub-task checkboxes
```

The plan is folded into the README and then deleted. An epic has no third document.

### README.md, in this order

1. **Goal**: one or two sentences.
2. **Decisions**: each with its reason, plus an *Out of scope* line.
3. **Constraints**: project-wide rules every task obeys.
4. **Tasks**: one table, one row per task:

   | Done | Task | Branch | Delivers | Needs |
   |------|------|--------|----------|-------|
   | [ ] | [01 Name](01-slug.md) | `feature/<epic>-01-slug` | observable result | — or task numbers |

   Below the table, one paragraph on order and merging. This table replaces milestone tables and dependency diagrams.
5. **Review Focus**: up to five inputs that no happy-path test hits. For each, give the expected behavior and `→ task NN`, the task whose test pins it.

### NN-<slug>.md, in this order

1. Title and one header line: `**Epic:** [README](README.md) (decisions, constraints; Review Focus N is tested here)`. Do not copy README content.
2. **Outcome**: what the owner observes when the task is done.
3. **Background**: only facts the implementer cannot find quickly (file:line, library behavior).
4. **Sub-tasks**: numbered `N.M` checkboxes, test first. Each one names exact files, signatures, values, and test names, and ends with `_Verify:_` giving a command and its expected output.
5. **Relevant Files**, then **Notes**.

## Branches

- Each task gets its own branch, cut from `main` and merged alone.
- Use one shared branch only when tasks would break `main` unless merged together. Say why in the README.
- A task that changes no code (an operation, a migration run by hand) has no branch: write `none (no code)`.
- The branch name lives only in the README table, not in the task file.

## Tracking

When a sub-task is done, check it in its task file. When a whole task file is done, check its row in the README. Nothing else carries status.

## Planning writes only the epic

While planning, write only under `tasks/<epic>/`. A value the owner supplies ("my window is 204800", "ok add it") goes into the epic's documents, not into live config, state, or code. Live changes happen only when the owner says to execute a task.

## Common mistakes

| Mistake | Fix |
|---|---|
| A single task file with only parent tasks | One file per task, full sub-tasks |
| Plan kept next to README | Fold its decisions into README, delete it |
| Constraints or steps repeated in task files | Link to the README |
| Milestones table and diagram as well as the task table | Delivers/Needs columns |
| One epic branch by default | A branch per task |
| Editing live config while planning | Record the value in the epic |
