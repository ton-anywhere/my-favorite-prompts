---
name: epic-draft
description: Use when the owner asks to draft, split, or outline an epic or a large piece of work into tasks before any of them is planned; not for writing a plan, task sub-tasks, or code.
disable-model-invocation: true
---

# Epic draft

An epic draft is the input to a later planning pass, not a plan. Say what each task is, why it sits in that order, and how it is accepted. Leave design, steps and code to the planner. Example: `tasks/skill-access-control/` in pi-orchestrator.

## Location

Put the epic in the folder where the project keeps agent-produced plans and tasks, as `<tasks dir>/<epic-name>/` with a kebab-case name. That folder is the one the project's rules name (for example `.agents/tasks/`), or the one where existing epics live (`tasks/` in pi-orchestrator). Look at the existing epic folders first and do not reuse a name. If the project has neither, ask where to put it before creating anything.

## Files

- `README.md`:
  - a one-paragraph purpose and scope boundary;
  - a line `Status: draft.` saying each task needs a plan before work starts;
  - a Mermaid `flowchart` of dependencies, only when at least one task depends on another;
  - the task list, in dependency order, each linked to its file with a one-line summary;
  - `## Open decisions`, only for choices that change the outcome, numbered, each with the draft's assumption.
- One file per task, named in kebab-case without a number. Each has a `## <title>` heading and one paragraph covering:
  - what the user can do or observe once this task is merged alone;
  - what changes and where (name only files and symbols you have checked; otherwise say they are to be located);
  - why it sits where it does in the order;
  - the tests that task adds, naming the test file and cases;
  - an acceptance check in one sentence.

## Rules

- One paragraph per task file. No checklists, sub-tasks, numbered steps, or code.
- Each code task carries its own tests. Never add a separate tests, smoke, or QA task file.
- A task has its own user-visible outcome. A piece that only matters together with others (a server half, a client half, docs) is part of that task, not a task of its own.
- Do not edit code, commit, or start the work.

## Check

Before reporting, read the folder back: every task has a file, every README link resolves, the diagram has no node for a removed task, and each task file is one paragraph. Report the path and the task list in a few lines.
