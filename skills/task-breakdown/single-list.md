# Single List

For work with exactly one independently mergeable task. One file: `tasks/tasks-[feature-name].md` (e.g., `tasks-user-profile-editing.md`), on one branch.

## Phase 1

Create the file with Goal, Source of truth, Constraints, the parent tasks (`1.0`, `2.0`, …) without sub-tasks, and the Milestones table: points in the task sequence where the app is in a working, testable state even without the full feature complete (e.g., "After task 4.0: app runs with keyword search, no AI yet").

## Phase 2

Add the sub-tasks under each parent task in the same file, then Relevant Files and Notes.

## Template

```markdown
# Tasks: [Feature Name]

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Update the file after completing each sub-task, not just after completing an entire parent task. Under each checked sub-task, add `Verified <YYYY-MM-DD>: <what was run and observed>`.

## Goal

[One or two sentences.] Branch: `feature/[feature-name]`.

## Source of truth

[What wins when another doc disagrees with this list, e.g. the PRD, `docs/`, a glossary.]

## Constraints

- [Project-wide rules every task obeys.]

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 [Sub-task description 1.1]
    - _Verify:_ [command] → [expected output]
  - [ ] 1.2 [Sub-task description 1.2]
- [ ] 2.0 Parent Task Title _(deliverable: describe the working state of the app after this task)_
  - [ ] 2.1 [Sub-task description 2.1]
- [ ] 3.0 Parent Task Title (may not require sub-tasks if purely structural or configuration)

## Milestones

| After    | You have                              |
|----------|---------------------------------------|
| **N.0**  | [Description of working app state]    |
| **M.0**  | [Description of next working state]   |

## Relevant Files

- `path/to/file` — Brief description of why this file is relevant.
- `path/to/test_file` — Unit tests for the above.

## Notes

- [Any project-specific commands, environment requirements, or gotchas]
```
