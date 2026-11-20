# Using Skills

Which skill to run, and when. Skills marked *command* have `disable-model-invocation: true`: agents never load them on their own, so run them explicitly (`/name`).

## Planning work

Answer two questions, in order:

1. **Is the scope clear?** Do you know the goal, the users, and what is in and out of scope? If not:
   - run `/brainstorming` by default: it settles what and why, then compares approaches and writes a spec;
   - run `/create-prd` instead for a new product or MVP whose tasks should cite numbered requirements (`FR 12`).
2. **How big is it?** Pick the row:

   | Situation | Do |
   |---|---|
   | Trivial change | just do it |
   | One task, scope clear | `/plan`, then approve with **execute** |
   | One task that spans sessions or needs a review per step | `/plan` (approve with **save**), then `/task-breakdown` single task |
   | Several tasks, each with its own user story | `/plan` (approve with **save**), then `/task-breakdown` epic |

   For one task, add `/task-breakdown` only when you need what it adds: a task file that outlives the session, a final Verification sub-task with `Verified` bullets recording what was checked, a `# Task 1` heading for `subagent-driven-development`, or a split into an epic when the plan turns out to hold several user stories.

```mermaid
flowchart TD
  A{"Scope clear?"} -->|"no, feature or change"| BR["/brainstorming"] --> B
  A -->|"no, new product needing numbered requirements"| PRD["/create-prd"] --> B
  A -->|yes| B{"How big?"}
  B -->|trivial| D["just do it"]
  B -->|"one task"| P1["/plan, approve with execute"]
  B -->|"one task, multi-session or reviewed per step"| P2["/plan, approve with save"] --> S["/task-breakdown (single task)"] --> X
  B -->|"several user stories"| P3["/plan, approve with save"] --> E["/task-breakdown (epic)"] --> X["execute each task: by hand or subagent-driven-development"]
```

| Skill | Answers | Input | Output | Kind |
|---|---|---|---|---|
| `brainstorming` | What, why, and which approach: intent, goals and non-goals, constraints, approaches compared, the decided how | an idea or request | `.agents/docs/superpowers/specs/<date>-<topic>-design.md` | command, upstream (superpowers) |
| `create-prd` | What and why: user stories, numbered functional requirements, success metrics, deferred items | an idea | `tasks/prd-<feature>.md` | command |
| `/plan` | How, as decisions: approach, critical files, verification; explored read-only, enforced by OMP | a request, spec, or PRD | `local://<slug>-plan.md` (session-local) | OMP built-in mode |
| `task-breakdown` | In what pieces: a single task file for one user story, an epic (one task file and branch per story) for more; every task in one template, with a user story, interfaces, outcome-level sub-tasks and a final Verification sub-task | a saved plan, or a spec with a decided approach (anything less is sent back to `/plan`) | `tasks/tasks-<feature>.md` or `tasks/<epic>/` (or the project's agent-artifact folder, such as `.agents/tasks/`) | command |
| `executing-plans` | Build it inline, one final review of the branch | a task list or an epic task file | code | command, upstream (superpowers) |
| `subagent-driven-development` | Build it, one reviewed task at a time | a task list or an epic task file | code | command, upstream (superpowers) |

Notes:

- `/plan` is not a skill: it is OMP's native plan mode, a harness mode that keeps the working tree read-only while the agent explores and ends with an approval prompt. It exists only in OMP.
- `brainstorming` and `create-prd` are alternatives; run one, not both. A spec carries more than a PRD (the approaches and the decided how) but has no requirement ids to cite.
- `brainstorming` ends by asking you to run `/plan` on the approved spec (patched on the `local-custom` branch of `superpowers/`; upstream invokes `writing-plans`). `writing-plans` is no longer part of this flow: `task-breakdown` writes the per-task interfaces, tests, and verify steps it would add.
- `/plan` keeps its plan only in the session (`local://`). Run `/task-breakdown` before the session ends; it folds the plan into the epic README.
- `subagent-driven-development` runs on `task-breakdown` output directly: every task file has the heading `# Task 1`, so pass any of them (`task-brief <slug>.md 1`, `task-brief tasks-x.md 1`).
- Executing with subagents: `orchestrate` (OMP magic keyword) or `subagent-driven-development`. `orchestrate` is a prompt contract only: it accepts any request or plan, runs independent slices in parallel, and has no per-task review or ledger. `subagent-driven-development` runs tasks one at a time, each with a fresh implementer and a spec-and-quality review, keeps a ledger that survives compaction, and needs `task-breakdown` output. Rule of thumb: `orchestrate` for a plan you trust, low-risk tasks, or independent tasks you want in parallel; `subagent-driven-development` for work spanning sessions or tasks risky enough to need a review gate (security, concurrency, path handling).

Examples:

- Feature or change on an existing project, scope unclear: `/brainstorming`, then pick a row in the table above.
- One task with the scope settled: `/plan`, then approve with execute.
- Feature with several mergeable tasks: `/plan` (save), then `/task-breakdown`.
- New product or MVP: `/create-prd`, then `/plan` (save), then `/task-breakdown`.
- Trivial change: do it directly.
