# Single List

For work with exactly one independently mergeable task. One file: `tasks/tasks-[feature-name].md` (e.g., `tasks-user-profile-editing.md`), on one branch.

## Phase 1

Create the file with Goal, Source of truth, Global Constraints, the parent tasks as `### Task N: [Title]` headings without sub-tasks, and the Milestones table: points in the task sequence where the app is in a working, testable state even without the full feature complete (e.g., "After Task 4: app runs with keyword search, no AI yet").

Parent tasks are headings, not checkboxes, so `subagent-driven-development` can extract each one with its `task-brief` script (it splits a plan on `Task <id>` headings). That script cuts only at the next `Task` heading, so `## Tasks` is the last section of the file: anything after it would leak into the last task's brief. A parent task is done when all its sub-tasks are checked.

## Phase 2

Add the sub-tasks under each parent task heading in the same file, then each task's Interfaces block, then Relevant Files and Notes.

## Template

```markdown
# Tasks: [Feature Name]

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each sub-task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps. A task is done when all its sub-tasks are checked.

Update the file after completing each sub-task. Under each checked sub-task, add `Verified <YYYY-MM-DD>: <what was run and observed>`.

## Goal

[One or two sentences.] Branch: `feature/[feature-name]`.

## Source of truth

[What wins when another doc disagrees with this list, e.g. the PRD, `docs/`, a glossary.]

## Global Constraints

- [Project-wide rules every task obeys.]

## Milestones

| After    | You have                              |
|----------|---------------------------------------|
| **Task N** | [Description of working app state]  |
| **Task M** | [Description of next working state] |

## Relevant Files

- `path/to/file` — Brief description of why this file is relevant.
- `path/to/test_file` — Unit tests for the above.

## Notes

- [Any project-specific commands, environment requirements, or gotchas]

## Tasks

### Task 1: [Parent Task Title]

**Interfaces:**
- Consumes: [exact signatures this task uses from earlier tasks, or "nothing"]
- Produces: [exact names, parameters, and return types later tasks rely on]

- [ ] 1.1 [Sub-task description 1.1]
  - _Verify:_ [command] → [expected output]
- [ ] 1.2 [Sub-task description 1.2]

### Task 2: [Parent Task Title] _(deliverable: describe the working state of the app after this task)_

- [ ] 2.1 [Sub-task description 2.1]

### Task 3: [Parent Task Title] (may not require sub-tasks if purely structural or configuration)

```
