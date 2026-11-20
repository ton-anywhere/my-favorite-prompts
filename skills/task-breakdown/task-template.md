# Task Template

Every task file uses this template, whether it is the only task or one task of an epic. The heading is always `# Task 1: [Name]`: there is one task per file, so the `1` never changes, and `task-brief <file> 1` can extract it for `subagent-driven-development`.

Sections in order:

- **Epic line**: present only when the task belongs to an epic.
- **User story**: what the task accomplishes, from the user's point of view, in terms of functionality.
- **Interfaces**: what this task uses from earlier tasks and what it hands to later ones.
- **Background**: facts the implementer can't find quickly.
- **Sub-tasks**: written in Phase 2 only, after the owner approves Phase 1.
- **Relevant Files**
- **Notes**: gotchas, plus the project-wide constraints and the branch name when there is no epic README to hold them.

```markdown
# Task 1: [Task name]

**Epic:** [README](README.md)

## User story
[From the user's perspective: what this task accomplishes in terms of functionality.]

## Interfaces
- Consumes: [exact signatures this task uses from earlier tasks, or "nothing"]
- Produces: [exact names, parameters, and return types later tasks rely on]

## Background
- [Only facts the implementer cannot find quickly: file:line, library behavior, external data details.]

## Sub-tasks
- [ ] **Failing test: [short outcome]**: file, test names, assertions.
- [ ] **Implementation: [short outcome]**: file, the outcome, and any public signature or value another task relies on.
- [ ] **Verification**
  - _Verify:_ [command] → [expected output]
  - _Verify:_ [command or manual check] → [expected observable result]

## Relevant Files
- `path/to/file` — [why]

## Notes
- [Gotchas]
```

Write the `**Epic:**` line only when the task belongs to an epic; a task that stands alone has no epic line.

`_Verify:_` lines appear only under the final **Verification** sub-task. That sub-task gathers the checks that prove the whole task: the new tests, the existing suites the change touches, an end-to-end check when the behavior is observable, and the project's gates.
