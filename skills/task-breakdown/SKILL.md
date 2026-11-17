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
  modified: Merged by Airton Ponce from his rewrite of the Apache-2.0 generate-tasks.md (INVEST validation, specificity rules, milestones, BLOCKED markers) and his epic-task-breakdown skill (epic layout, per-task branches, tracking conventions).
---

# Rule: Breaking Work into Tasks

## Core Instructions

**Mandatory Thinking Process:**
Think step-by-step thoroughly before outputting anything.
1. Deeply analyze the provided plan, PRD, or requirements and the existing codebase.
2. Apply every section of this document, and of the files it sends you to, in exact sequence.
3. Perform full INVEST validation on every task.
4. Only then generate output.

## Goal

To guide an AI assistant in creating a detailed, step-by-step task list in Markdown format based on an implementation plan, a PRD, user requirements, or feature requests. The task list should guide a developer who has not seen this codebase through implementation without additional research.

## Files

Read these before the step that needs them:

| File | Read for |
|---|---|
| [invest.md](invest.md) | Task Breakdown Principles and INVEST Validation, applied to every task |
| [sub-tasks.md](sub-tasks.md) | Sub-Task Specificity Rules |
| [single-list.md](single-list.md) | The single-list shape: its two phases and template |
| [epic.md](epic.md) | The epic shape: its two phases, branches, and templates |

## Output Shape

Count the **independently mergeable tasks**: pieces that each leave `main` working when merged alone.

| Count | Shape | Read |
|---|---|---|
| 1 | **Single list**: `tasks/tasks-[feature-name].md` | [single-list.md](single-list.md) |
| 2 or more | **Epic**: `tasks/[epic-name]/README.md` plus one `NN-[slug].md` per task | [epic.md](epic.md) |

## Process

1. **Receive Input:** The user provides an implementation plan (for example from `writing-plans`), a PRD (for example `tasks/prd-[feature].md`), a feature request, or a task description.

2. **Analyze Requirements:** Analyze the functional requirements, user needs, and implementation scope from the provided information. With a plan as input, its decisions stand; with a PRD or requirements, you make them here.

3. **Assess Current State:** Review the existing codebase to understand existing infrastructure, architectural patterns and conventions. Also, identify any existing components or features that already exist and could be relevant to the requirements. Then, identify existing related files, components, and utilities that can be leveraged or need modification.

4. **Phase 1: Generate Tasks:** Read [invest.md](invest.md). Generate the main, high-level tasks required to implement the feature, following its Task Breakdown Principles, and run its INVEST Validation on every task. Choose the [Output Shape](#output-shape), read that shape's file, and write its Phase 1 output.

5. **Wait for Confirmation:** Present the Phase 1 output to the user and say: "I have generated the high-level tasks based on your requirements. Ready to generate the sub-tasks? Respond with 'Go' to proceed." Then stop and wait for the user to respond with "Go". If a task seems too large (e.g., "Implement AI and UI"), suggest splitting it here.

6. **Phase 2: Generate Sub-Tasks:** Once the user confirms, read [sub-tasks.md](sub-tasks.md). Break down each task into smaller, actionable sub-tasks necessary to complete it. Ensure sub-tasks logically follow from the task and cover the implementation details implied by the requirements. Write them as the shape's Phase 2 describes.

7. **Identify Interfaces and Relevant Files:** For each task, write its Interfaces block: what it consumes from earlier tasks and what it produces for later ones, with exact names and types. Then identify the files that will need to be created or modified and list them under `Relevant Files`, including corresponding test files.

8. **Self-Review:** Run the [Self-Review Step](#self-review-step-mandatory) and fix what fails.

9. **Save and Report:** Save the files and report the paths written plus the self-review line.

## Self-Review Step (Mandatory)

After completing the full task list:
- Confirm all specificity rules ([sub-tasks.md](sub-tasks.md)) are met by every sub-task.
- Verify every task follows the INVEST checklist ([invest.md](invest.md)).
- Ensure milestones (single list) or the Delivers column (epic) are realistic and provide working, testable states.
- Check that no tasks are vague or require the developer to do extra research.
- Check interface consistency: every name a task Consumes matches, exactly, what an earlier task Produces (`clearLayers()` in one task and `clearFullLayers()` in another is a bug).
- Check that no fact is written twice: in an epic, task files link to the README instead of copying it.

End the report with: `Self-review: <N> tasks and <M> sub-tasks checked; fixed: <list, or none>; blocked: <ids, or none>`.

## Tracking and History

- When a sub-task is done, check it and add a bullet under it: `Verified <YYYY-MM-DD>: <what was run and observed>`. In an epic, check the task's README row when its file is complete. Nothing else carries status.
- A completed task is history. A later change is a dated bullet under it (`Changed <date>:`, `Superseded by NN.M:`, `Decided:`), never an edit to its text.

## Planning Writes Only Task Files

While planning, write only under `tasks/`. A value the owner supplies ("my window is 204800", "ok add it") goes into the task documents, not into live config, state, or code. Live changes happen only when the owner says to execute a task.

## Interaction Model

The process explicitly requires a pause after Phase 1 — the parent tasks and milestones of a single list, or the README of an epic — to get user confirmation ("Go") before generating the detailed sub-tasks. This ensures the high-level plan aligns with user expectations before diving into details.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Writing sub-tasks or task files before the owner says "Go" | Stop after Phase 1 |
| Running INVEST on sub-tasks only | INVEST applies to every task |
| Skipping the self-review line | End the report with it |
| An epic as one file with only parent tasks | README plus one file per task, full sub-tasks |
| Plan kept next to the README | Fold its decisions into the README, delete it |
| Global constraints or steps repeated in task files | Link to the README |
| One epic branch by default | A branch per task |
| Checking a sub-task without a `Verified` bullet | Record what was run and observed |
| Rewriting a completed task after a change | Add a dated note under it |
| Editing live config while planning | Record the value in the task files |
