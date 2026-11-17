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
   | One task, but long or reviewed task by task | `/plan` (approve with **save**), then `/task-breakdown` single list |
   | Several mergeable tasks | `/plan` (approve with **save**), then `/task-breakdown` epic |

   For one task, add `/task-breakdown` only when you need what it adds: a file in `tasks/` that outlives the session, `Verified` bullets recording what was checked, `Task N` headings for `subagent-driven-development`, or a split into an epic when the plan turns out bigger.

```mermaid
flowchart TD
  A{"Scope clear?"} -->|"no, feature or change"| BR["/brainstorming"] --> B
  A -->|"no, new product needing numbered requirements"| PRD["/create-prd"] --> B
  A -->|yes| B{"How big?"}
  B -->|trivial| D["just do it"]
  B -->|"one task"| P1["/plan, approve with execute"]
  B -->|"one long or reviewed task"| P2["/plan, approve with save"] --> S["/task-breakdown (single list)"] --> X
  B -->|"several mergeable tasks"| P3["/plan, approve with save"] --> E["/task-breakdown (epic)"] --> X["execute each task: by hand or subagent-driven-development"]
```

| Skill | Answers | Input | Output | Kind |
|---|---|---|---|---|
| `brainstorming` | What, why, and which approach: intent, goals and non-goals, constraints, approaches compared, the decided how | an idea or request | `.agents/docs/superpowers/specs/<date>-<topic>-design.md` | command, upstream (superpowers) |
| `create-prd` | What and why: user stories, numbered functional requirements, success metrics, deferred items | an idea | `tasks/prd-<feature>.md` | command |
| `/plan` | How, as decisions: approach, critical files, verification; explored read-only, enforced by OMP | a request, spec, or PRD | `local://<slug>-plan.md` (session-local) | OMP built-in mode |
| `task-breakdown` | In what pieces: a single list for one mergeable task, an epic (one file and branch per task) for more; each task with interfaces, tests, and verify steps | a plan, a spec, a PRD, or requirements | `tasks/tasks-<feature>.md` or `tasks/<epic>/` | command |
| `executing-plans`, `subagent-driven-development` | Build it | a task list or an epic task file | code | upstream (superpowers) |

Notes:

- `/plan` is not a skill: it is OMP's native plan mode, a harness mode that keeps the working tree read-only while the agent explores and ends with an approval prompt. It exists only in OMP.
- `brainstorming` and `create-prd` are alternatives; run one, not both. A spec carries more than a PRD (the approaches and the decided how) but has no requirement ids to cite.
- `brainstorming` ends by asking you to run `/plan` on the approved spec (patched on the `local-custom` branch of `superpowers/`; upstream invokes `writing-plans`). `writing-plans` is no longer part of this flow: `task-breakdown` writes the per-task interfaces, tests, and verify steps it would add.
- `/plan` keeps its plan only in the session (`local://`). Run `/task-breakdown` before the session ends; it folds the plan into the epic README.
- `subagent-driven-development` runs on `task-breakdown` output directly: pass an epic task file (`task-brief 01-slug.md 01`) or a single list (`task-brief tasks-x.md 1`).

Examples:

- Feature or change on an existing project, scope unclear: `/brainstorming`, then pick a row in the table above.
- One task with the scope settled: `/plan`, then approve with execute.
- Feature with several mergeable tasks: `/plan` (save), then `/task-breakdown`.
- New product or MVP: `/create-prd`, then `/plan` (save), then `/task-breakdown`.
- Trivial change: do it directly.
