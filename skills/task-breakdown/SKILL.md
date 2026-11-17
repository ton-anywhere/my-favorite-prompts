---
name: task-breakdown
description: Use when the owner asks to break a plan, PRD, or requirements into tasks under tasks/ — a single task list for one small change or an epic folder with one file and branch per task — or to update, check off, or record results in an existing task list or epic (/task-breakdown <plan or requirements>).
disable-model-invocation: true
license: Apache-2.0 (see LICENSE)
metadata:
  author: Airton Ponce @ton-anywhere
  source: https://github.com/snarktank/ai-dev-tasks/blob/main/generate-tasks.md
  fork: https://github.com/ton-anywhere/ai-dev-tasks
  original-author: Ryan Carson @snarktank
  modified: Merged by Airton Ponce from his rewrite of the Apache-2.0 generate-tasks.md (INVEST validation, specificity rules, BLOCKED markers) and his epic-task-breakdown skill (epic layout, per-task branches, tracking conventions).
---

# Task Breakdown

Turns a plan, PRD, or requirements into tasks a developer can pick up without asking anything. Every fact lives in exactly one document.

## Choose the shape

Count the **independently mergeable tasks**: pieces that each leave `main` working when merged alone.

| Count | Shape |
|---|---|
| 1 | **Single list:** `tasks/tasks-<feature>.md`, one branch |
| 2 or more | **Epic:** `tasks/<epic>/README.md` plus one `NN-<slug>.md` per task, one branch per task |

## Process

1. **Read the input and the code.** Find the existing modules, conventions, and tests the work touches. With a plan as input, its decisions stand; with a PRD or requirements, you make them here.
2. **Draft the task table** (columns below) and show it to the owner with: "Ready to write the sub-tasks? Reply 'Go'." Stop until the owner answers. The split into tasks is the expensive decision to redo, so it is approved before any detail is written.
3. **Write the files** in the shape chosen above.
4. **Self-review, then report.** Check every sub-task against [Sub-task rules](#sub-task-rules) and fix what fails: an unnamed file ("the config test file") or a Verify without an expected output is a failure. The final message must contain:
   - the paths written;
   - `Self-review: <N> sub-tasks checked; fixed: <list, or none>; blocked: <ids, or none>`.

## Epic layout

```
tasks/<epic>/
├── README.md          why and what — no implementation steps
└── NN-<slug>.md       how — one file per task, the only place with sub-task checkboxes
```

A plan given as input is folded into the README and deleted; the epic has no third document.

**README.md**, in this order:

1. **Goal**: one or two sentences.
2. **Source of truth**: one line naming what wins when a doc disagrees with this epic (for example the README's decisions, `docs/`, a PRD, a glossary).
3. **Decisions**: each with its reason, plus an *Out of scope* line.
4. **Constraints**: project-wide rules every task obeys.
5. **Tasks**: one table, then one paragraph on order and merging. The table replaces milestone tables and dependency diagrams.

   | Done | Task | Branch | Delivers | Needs |
   |------|------|--------|----------|-------|
   | [ ] | [01 Name](01-slug.md) | `feature/<epic>-01-slug` | observable result | — or task numbers |

6. **Review Focus**: up to five inputs no happy-path test hits, each with the expected behavior and `→ task NN`, the task whose test pins it.

**NN-<slug>.md**, in this order:

1. Title and one header line: `**Epic:** [README](README.md) (decisions, constraints; Review Focus N is tested here)`. README content is linked, never copied.
2. **Outcome**: what the owner observes when the task is done.
3. **Background**: only facts the implementer cannot find quickly (file:line, library behavior). A task that ingests external data names the source URL, format, fields, and expected volume here.
4. **Sub-tasks**: numbered `N.M` checkboxes, test first (see [Sub-task rules](#sub-task-rules)).
5. **Relevant Files**, then **Notes**.

## Single-list layout

`tasks/tasks-<feature>.md`, in this order: **Goal**, **Source of truth**, **Constraints**, **Sub-tasks** (numbered `1.M`), **Relevant Files**, **Notes**. The branch is named once, under Goal.

## Sub-task rules

Each sub-task:

- names the exact files, function signatures (with return types when not obvious), values, and test names it needs; a database change names every column with type, nullability, and index;
- ends with `_Verify:_` giving a command and the output that means it passed;
- passes INVEST: **I**ndependent of unfinished sub-tasks (else reorder or split), **N**egotiable (states the outcome, not a mechanism the code could choose), **V**aluable on its own, **E**stimable, **S**mall enough for one focused session, **T**estable through its Verify;
- is marked `⚠️ BLOCKED: <what must be known>` when it depends on information nobody has yet.

When splitting work into tasks: deliver the simplest version that works end to end first, and make each upgrade its own task; split a pipeline into independently testable stages; put core logic before UI.

## Branches

- Each epic task gets its own branch, cut from `main` and merged alone; the owner usually creates it by hand.
- Use one shared branch only when tasks would break `main` unless merged together, and say why in the README.
- A task that changes no code (an operation, a hand-run migration) has no branch: `none (no code)`.
- A branch name appears once: the README table (epic) or under Goal (single list).

## Tracking and history

- When a sub-task is done, check it and add a bullet under it: `Verified <YYYY-MM-DD>: <what was run and observed>`. In an epic, check the task's README row when its file is complete. Nothing else carries status.
- A completed task is history. A later change is a dated bullet under it (`Changed <date>:`, `Superseded by NN.M:`, `Decided:`), never an edit to its text.

## Planning writes only task files

While planning, write only under `tasks/`. A value the owner supplies ("my window is 204800", "ok add it") goes into the task documents, not into live config, state, or code. Live changes happen only when the owner says to execute a task.

## Common mistakes

| Mistake | Fix |
|---|---|
| Writing sub-tasks before the owner approves the task table | Show the table, wait for "Go" |
| An epic as one file with only parent tasks | One file per task, full sub-tasks |
| Plan kept next to the README | Fold its decisions into the README, delete it |
| Constraints or steps repeated in task files | Link to the README |
| One epic branch by default | A branch per task |
| Checking a sub-task without a `Verified` bullet | Record what was run and observed |
| Rewriting a completed task after a change | Add a dated note under it |
| Editing live config while planning | Record the value in the task files |
