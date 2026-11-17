# Using Skills

Which skill to run, and when. Skills marked *command* have `disable-model-invocation: true`: agents never load them on their own, so run them explicitly (`/name`).

## Planning work

Answer two questions, in order:

1. **Is the scope clear?** Do you know the goal, the users, and what is in and out of scope? If not, run `/create-prd` first.
2. **Is it more than one PR-sized task?** If not, just do it, or use `/generate-tasks` for a step list. If it is, use `/writing-plans` and then `/epic-task-breakdown`.

```mermaid
flowchart TD
  A{"Scope clear?"} -->|no| PRD["/create-prd"] --> B
  A -->|yes| B{"More than one PR-sized task?"}
  B -->|no| S["do it, or /generate-tasks"]
  B -->|yes| WP["/writing-plans"] --> E["/epic-task-breakdown"] --> X["execute one task per branch"]
```

| Skill | Answers | Input | Output | Kind |
|---|---|---|---|---|
| `create-prd` | What and why: goals, user stories, requirements, non-goals | an idea | `tasks/prd-<feature>.md` | command |
| `writing-plans` | How: files, signatures, tests per task | a PRD, a spec, or scope agreed in chat | one plan | upstream (superpowers) |
| `epic-task-breakdown` | In what pieces: one file and one branch per task | a plan | `tasks/<epic>/` | command |
| `generate-tasks` | Steps for a small, single-branch change | a PRD or requirements | `tasks/tasks-<feature>.md` | command |
| `executing-plans`, `subagent-driven-development` | Build it | a plan or an epic task | code | upstream (superpowers) |

Examples:

- New product or MVP: `/create-prd`, then `/writing-plans`, then `/epic-task-breakdown`.
- Feature on an existing project, with the scope settled in conversation: `/writing-plans`, then `/epic-task-breakdown`.
- One small change: do it directly, or `/generate-tasks`.
