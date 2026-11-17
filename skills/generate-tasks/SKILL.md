---
name: generate-tasks
description: Use when the owner asks to generate a task list from requirements, a PRD, or a feature request (/generate-tasks <plan>).
disable-model-invocation: true
---

# Rule: Generating a Task List from User Requirements

## Role & Core Instructions
You are an expert senior software architect and technical project planner with 15+ years of experience leading complex feature implementations. You strictly follow every rule in this document and produce outputs that a junior developer can execute with minimal ambiguity.

**Mandatory Thinking Process:**
Think step-by-step thoroughly before outputting anything.
1. Deeply analyze the provided PRD/requirements and existing codebase.
2. Apply every section of this document in exact sequence.
3. Perform full INVEST validation on every task.
4. Only then generate output.

## Goal
To guide an AI assistant in creating a detailed, step-by-step task list in Markdown format based on user requirements, feature requests, or existing documentation. The task list should guide a developer through implementation.

## Output
- **Format:** Markdown (`.md`)
- **Location:** `/tasks/`
- **Filename:** `tasks-[feature-name].md` (e.g., `tasks-user-profile-editing.md`)

## Process

1. **Receive Requirements:** The user provides a feature request, task description, or points to existing documentation (e.g. `docs/PRD.md`).

2. **Analyze Requirements:** The AI analyzes the functional requirements, user needs, and implementation scope from the provided information.

3. **Assess Current State:** Review the existing codebase to understand existing infrastructure, architectural patterns and conventions. Also, identify any existing components or features that already exist and could be relevant to the provided requirements. Then, identify existing related files, components, and utilities that can be leveraged or need modification.

4. **Phase 1: Generate Parent Tasks:** Based on the requirements analysis, create the file and generate the main, high-level tasks required to implement the feature. **IMPORTANT: Always include task 0.0 as the first task. For features added to an existing project, this is "Create feature branch". For greenfield projects, replace it with "Initialize project" (repo setup, project scaffolding, initial dependencies, CI configuration) — branching is not the first concern when there's no repo yet.** Use your judgement to create a modular breakdown. Let the number of tasks be driven by the breakdown principles and INVEST criteria below — do not constrain the count artificially. A large feature may need 15+ parent tasks; a small one may need 3. Prefer more tasks that are each Small, Independent, and Testable over fewer tasks that bundle concerns. Prioritize separation of concerns (e.g., separating data ingestion from schema, or search logic from generation logic). After listing the parent tasks, **identify and call out Deliverable Milestones** — points in the task sequence where the app is in a working, testable state even without the full feature complete (e.g., "After task 4.0: app runs with keyword search, no AI yet"). Present these tasks and milestones to the user. Inform the user: "I have generated the high-level tasks based on your requirements. Ready to generate the sub-tasks? Respond with 'Go' to proceed."

5. **Wait for Confirmation:** Pause and wait for the user to respond with "Go".

6. **Phase 2: Generate Sub-Tasks:** Once the user confirms, break down each parent task into smaller, actionable sub-tasks necessary to complete the parent task. Ensure sub-tasks logically follow from the parent task and cover the implementation details implied by the requirements. For each sub-task, follow the specificity rules below.

7. **Identify Relevant Files:** Based on the tasks and requirements, identify potential files that will need to be created or modified. List these under the `Relevant Files` section, including corresponding test files if applicable.

8. **Generate Final Output:** Combine the parent tasks, sub-tasks, milestones, data sources, relevant files, and notes into the final Markdown structure.

9. **Save Task List:** Save the generated document in the `/tasks/` directory with the filename `tasks-[feature-name].md`.

## Task Breakdown Principles

When generating parent tasks, follow these heuristics to ensure a clean implementation:

1. **Infrastructure First**: Start with environment setup, framework configuration, and basic boilerplate.
2. **Data vs. Schema**: Separate the creation of database structures (ActiveRecord/Migrations) from the logic that populates or ingests data.
3. **Simplest Working Version First**: Before implementing the full/optimal solution, deliver a simpler version that works end-to-end. For example: implement keyword search before semantic search, or render static data before wiring up an API. Each upgrade to a more sophisticated approach should be its own task. This creates natural deliverable milestones and makes each stage independently testable.
4. **Pipeline Decomposition**: For complex logic (like RAG or multi-step processing), break the pipeline into independent, testable stages (e.g., 1. Keyword Search, 2. Semantic Search Upgrade, 3. Answer Generation, 4. Pipeline Orchestration). Do not merge pipeline stages into a single task.
5. **Logic vs. UI**: Implement core backend services and API logic before building the frontend views and loading states.
6. **Cross-Cutting Concerns**: Treat Observability (logging, tracing, metrics) and Performance (caching, optimization) as distinct high-level tasks if they are significant.
7. **Verification**: Always include a final task for benchmarking, specialized testing, or "Gold Standard" validation.

## Sub-Task Specificity Rules

Sub-tasks must be concrete enough for a junior developer to implement without additional research. Apply these rules:

- **External data tasks** must include: source URL, file format, relevant field/column names, expected output volume, and any format-specific quirks (e.g., index-based arrays, separate key mapping files). A task like "parse KJV CSV" is not acceptable — "download `t_kjv.csv` from [URL], columns: `b` (book number), `c` (chapter), `v` (verse), `t` (text), join with `key_english.csv` for book names" is.
- **Service/class tasks** must name the file path, the public interface (method signatures and return types where non-obvious), and any singleton/lifecycle constraints.
- **Database tasks** must name every column with its type, nullability, and index strategy.
- **Verification sub-tasks** must state the exact command to run and the expected observable output (e.g., `Verse.by_language("en").count` ≈ 31,102).
- **Tasks that depend on unresolved external information** must be marked `⚠️ BLOCKED` with a clear description of what needs to be known before implementation can begin.

## INVEST Validation

Before finalizing the task list, review each sub-task against the INVEST checklist. Fix violations before saving:

- **Independent**: Can this sub-task be implemented without another unfinished sub-task being done first? If not, reorder or split.
- **Negotiable**: Does it describe the *outcome*, not prescribe the mechanism? (e.g., "user receives results in their language" not "add a language toggle dropdown")
- **Valuable**: Does completing this sub-task leave the system in a better state? Is it a meaningful step forward on its own?
- **Estimable**: Is it specific enough for a developer to estimate the work? Apply the specificity rules above.
- **Small**: Can a developer complete it in a single focused session? If not, split it further.
- **Testable**: Is there a clear, observable way to verify it's done?

## Self-Review Step (Mandatory)
After completing the full task list:
- Confirm all specificity rules are met.
- Verify every task follows the INVEST checklist.
- Ensure milestones are realistic and provide working, testable states.
- Check that no tasks are vague or require the developer to do extra research.

## Output Format

The generated task list _must_ follow this structure:

```markdown
## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [ ] 0.0 Create feature branch
  - [ ] 0.1 Create and checkout a new branch for this feature (e.g., `git checkout -b feature/[feature-name]`)
- [ ] 1.0 Parent Task Title
  - [ ] 1.1 [Sub-task description 1.1]
  - [ ] 1.2 [Sub-task description 1.2]
- [ ] 2.0 Parent Task Title _(deliverable: describe the working state of the app after this task)_
  - [ ] 2.1 [Sub-task description 2.1]
- [ ] 3.0 Parent Task Title (may not require sub-tasks if purely structural or configuration)

## Data Sources

| Source | Format | URL | Key Fields | Volume |
|--------|--------|-----|------------|--------|
| [Name] | [CSV/JSON/API] | [URL] | [field names and meaning] | [~N rows/records] |

_(Omit this section if the feature has no external data dependencies.)_

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

## Interaction Model

The process explicitly requires a pause after generating parent tasks to get user confirmation ("Go") before proceeding to generate the detailed sub-tasks. This ensures the high-level plan aligns with user expectations before diving into details. If a task seems too large (e.g., "Implement AI and UI"), suggest splitting it to the user during Phase 1 to improve testability.

## Target Audience

Assume the primary reader of the task list is a **junior developer** who will implement the feature.
