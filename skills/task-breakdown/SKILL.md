---
name: task-breakdown
description: Use when the owner asks to break a saved plan, or a spec with a decided approach, into tasks — a single task file for one user story or an epic folder with one task file and branch per story — or to update, check off, or record results in an existing task file or epic (/task-breakdown <plan>).
disable-model-invocation: true
license: Apache-2.0 (see LICENSE)
metadata:
  author: Airton Ponce @ton-anywhere
  source: https://github.com/snarktank/ai-dev-tasks/blob/main/generate-tasks.md
  fork: https://github.com/ton-anywhere/ai-dev-tasks
  original-author: Ryan Carson @snarktank
  modified: Merged by Airton Ponce from his rewrite of the Apache-2.0 generate-tasks.md (INVEST validation, specificity rules, BLOCKED markers) and his epic-task-breakdown skill (epic layout, per-task branches, tracking conventions).
---

# Rule: Breaking Work into Tasks

## Goal

Turn a plan that has already decided how the work is built into task files. Each task file tells a developer, or a developer agent, **what** to deliver and how to prove it is done. **How** to build each piece is the developer's decision; the overall approach is the plan's.

## Files

Read each file before the step that needs it:

| File | Read for |
|---|---|
| [invest.md](invest.md) | What counts as a task (its own user story), breakdown principles, INVEST validation |
| [task-template.md](task-template.md) | The one task template, used for a single task and for every epic task |
| [sub-tasks.md](sub-tasks.md) | What a sub-task contains, and the final Verification sub-task |
| [epic.md](epic.md) | The epic README, branches, and the epic's two phases |

## Output Shape

Count the **tasks**: the pieces that each have a user story of their own ([invest.md](invest.md)). Pieces without a user story are sub-tasks, not tasks.

| Tasks | Shape |
|---|---|
| 1 | **Single task**: one file, `<tasks dir>/tasks-[feature-name].md`, in [task-template.md](task-template.md) format without the Epic line |
| 2 or more | **Epic**: `<tasks dir>/[epic-name]/README.md` plus one `[slug].md` per task, in the same template with the Epic line ([epic.md](epic.md)) |

`<tasks dir>` is where the project keeps agent-produced plans and tasks: the folder its rules name (for example `.agents/tasks/`) or the one where the input plan already lives. Use `tasks/` only when the project has no such convention.

A single task has no Goal, Milestones, Global Constraints, or numbered parent tasks. Its project-wide constraints and branch go under **Notes**.

## Input Gate

This gate applies when creating tasks; updating or checking off an existing task file skips it.

The input must decide **how** the work is built: it names the approach and the parts of the system that change. A saved `/plan` file does, and so does a spec whose approach was approved. Proceed with such an input.

When the input only says **what** is wanted (a PRD, a requirements list, a feature request, a one-line description), write nothing and don't explore the code for it. Reply in one or two lines with the next step from the project's skill guide (`docs/using-skills.md` in the prompts repo), and end your turn:
- scope unclear (goal, users, or in/out of scope undecided) → `/brainstorming` (or `/create-prd` for a new product), then `/plan`, then `/task-breakdown` on the saved plan;
- scope clear → `/plan` on the input, approved with **save**, then `/task-breakdown` on the saved plan.

When the owner says to proceed anyway, record each design decision you make under the task's **Notes** as `Decided: <decision> (no plan)`, and list them in the rundown.

## Process

1. **Receive input** and apply the [input gate](#input-gate). The plan's decisions stand; don't reopen them.
2. **Assess the current state:** read the code the work touches, and the existing patterns, components and utilities it can reuse.
3. **Phase 1: tasks without sub-tasks.** Read [invest.md](invest.md), write each task's user story, and run INVEST on every task. Choose the [output shape](#output-shape), then write the files with every section of [task-template.md](task-template.md) except **Sub-tasks** (plus the README, for an epic).
4. **Rundown, then stop.** Send a [rundown](#rundown) as a plain chat message and end your turn. Write no sub-tasks until the owner approves in their next message. When the owner corrects something, apply it, send a new rundown, and stop again.
5. **Phase 2: sub-tasks.** After approval, read [sub-tasks.md](sub-tasks.md) and add the **Sub-tasks** section to each task file, ending each with its **Verification** sub-task.
6. **Self-review**, then a [rundown](#rundown) of Phase 2 with the self-review line, and stop.

## Rundown

After each phase, give a brief summary of what you wrote, as a plain message: a few bullets, or a short table for an epic.

- the shape (single task or epic) and the path of every file written;
- each task's name and its user story in one line;
- in Phase 2, the sub-task count per task and what the Verification sub-task proves;
- any open question the owner must answer.

Then end your turn. The rundown never uses the `ask` tool or a form, and never asks for a fixed reply such as "Go".

## Facts Are Checked Before They Are Written

Every claim in a user story, Background, or Notes about how the system behaves today (when something runs, which component does what, what an older version did) comes from code or docs you read in this session. Name the file. A claim you couldn't check is either left out or marked `unverified`.

## One Draft, Implementer-Facing

- Keep exactly one copy of each task file. When the session is read-only (plan mode), draft in one session-local file, show the owner that file, and write it to `<tasks dir>` once they approve. Never keep a second copy in sync.
- Task files contain only what the implementer needs. Notes about the planning itself (superseded plans, drafts, review rounds) stay out.
- When the owner asks to review a draft in their editor, open it with their editor. Agent shells often set `$EDITOR`/`$VISUAL` to a no-op such as `true`; in that case use `git config core.editor` without its wait flag (for example `subl`, not `subl -w`).

## Self-Review Step (Mandatory)

Before the Phase 2 rundown:
- Every task follows [task-template.md](task-template.md): same sections, same order, an Epic line only in an epic.
- Every task passes INVEST ([invest.md](invest.md)) and has its own user story.
- Every sub-task follows [sub-tasks.md](sub-tasks.md): outcome, files and assertions only. No code, no private names, no step-by-step recipe. `_Verify:_` lines appear only in the final Verification sub-task.
- Interfaces are consistent: every name a task Consumes matches exactly what an earlier task Produces (`clearLayers()` in one task and `clearFullLayers()` in another is a bug).
- No fact is written twice: epic task files link to the README instead of copying it.
- Every behavioral claim was checked ([facts](#facts-are-checked-before-they-are-written)).

End the Phase 2 rundown with: `Self-review: <N> tasks and <M> sub-tasks checked; fixed: <list, or none>; blocked: <ids, or none>`.

## Tracking and History

- When a sub-task is done, check it. When the task's checks pass, add a bullet under the Verification sub-task: `Verified <YYYY-MM-DD>: <what was run and observed>`. In an epic, check the task's README row once its file is complete. Nothing else carries status.
- A completed task is history. A later change is a dated bullet under it (`Changed <date>:`, `Superseded by <task or sub-task>:`, `Decided:`), never an edit to its text.

## Planning Writes Only Task Files

While planning, write only task files (and, for an epic, its README). A value the owner supplies ("my window is 204800", "ok add it") goes into the task documents, not into live config, state, or code. Live changes happen only when the owner says to execute a task.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Splitting server, clients, docs or tests into separate tasks | No user story of their own: they are sub-tasks of one task |
| A single task with Goal, Milestones, Global Constraints or `### Task N` parents | One file in [task-template.md](task-template.md) format; constraints go in Notes |
| Different templates for single and epic tasks | One template; an epic task only adds the Epic line |
| Writing sub-tasks before the owner approves Phase 1 | Phase 1 has no Sub-tasks section; stop after the rundown |
| Asking for approval with the `ask` tool or "Respond with Go" | A plain rundown, then end the turn |
| Sub-tasks with code, private names, line edits or step-by-step recipes | Outcome, files and assertions; the developer decides how |
| Breaking down a feature request or PRD with no plan behind it | Stop at the input gate and point to `/plan` |
| A `_Verify:_` line under every sub-task | One final Verification sub-task per task |
| A user story or note stating unchecked behavior ("injected at session start") | Check it in code first, or leave it out |
| Two copies of a draft kept in sync | One file; move it on approval |
| Planning notes left in the task file ("supersedes the plan; delete it") | Keep only implementer-facing content |
| Plan kept next to the epic README | Fold its decisions into the README, delete it |
| Global constraints repeated in epic task files | Link to the README |
| One epic branch by default | A branch per task |
| Checking the Verification sub-task without a `Verified` bullet | Record what was run and observed |
| Rewriting a completed task after a change | Add a dated note under it |
| Editing live config while planning | Record the value in the task files |
