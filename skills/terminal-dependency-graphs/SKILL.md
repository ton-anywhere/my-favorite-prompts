---
name: terminal-dependency-graphs
description: Use when a user asks to visualize task, subtask, roadmap, checklist, or project-plan dependencies in a terminal-readable format, especially for deciding worktrees, agent parallelization, vertical ASCII graphs, or what can run in parallel.
---

# Terminal Dependency Graphs

## Core Rule

Produce exactly two graphs by default:

1. A high-level task graph for deciding worktrees.
2. A low-level subtask graph for parallelizing agents inside a worktree.

Do not add branch diagrams, summaries, Mermaid, DOT, prose explanations, internal node IDs, or alternate projections unless explicitly requested.

## Workflow

1. Read the source task list and any project instructions that define task order or architecture.
2. Build a dependency DAG before drawing:
   - Write each edge mentally as `prerequisite -> dependent`.
   - Treat a task that is available now as independent until the source says it waits on something.
   - Do not infer that an earlier task depends on a later task just because both eventually feed a shared milestone.
   - Do not use connectors for "related to", "same area", "eventually joins", or "can run in parallel until later".
3. Separate two meanings:
   - **Task-level graph:** use whole tasks only. This graph answers “what worktrees can exist independently?”
   - **Subtask-level graph:** use subtasks only. This graph answers “what agents can work in parallel inside a worktree?”
4. Assign levels top-to-bottom:
   - Level 0 contains only nodes available now.
   - A node appears only after every dependency is in an earlier level.
   - No node on a level may depend on another node on the same level.
5. Validate edge direction before drawing:
   - Every downward arrow means exactly: "the lower node depends on the upper node."
   - Lower-numbered tasks are normally prerequisites for higher-numbered tasks. If an arrow would make `[8.0]` depend on `[12.0]`, stop and prove the source explicitly says so.
   - For each connector, say the edge in plain language: "`[10.0]` depends on `[8.0]` and `[9.0]`." If that sentence is false or merely convenient, remove the connector.
   - Do not make a task depend on itself, including fake “done” duplicates.
6. Validate independence:
   - Same-level nodes must be parallelizable by dependency.
   - If same-level nodes touch the same file or implementation surface, either split ownership clearly or move one later.
7. Draw terminal-first ASCII inside fenced `text` blocks.

## Graph Style

- Always use `GRAPH 1 - TASKS / WORKTREES` and `GRAPH 2 - SUBTASKS / AGENTS`.
- Put `READY NOW / PARALLEL` as the first row/level.
- Use real task numbers as node labels: `7.0`, `10.3`, `14.6`.
- Never expose rendering IDs like `S76`, `T10`, or Mermaid identifiers.
- Keep all requested content inside the requested graphs. Do not create side branches after the main graph.
- Prefer vertical flow with downward arrows.
- Avoid long crossing lines. If the graph becomes too dense or a connector could be read backward, use level bands with arrows between bands.
- Never represent “done” as a duplicate task node.

## Terminal Layout Pattern

Use this shape for dense plans:

```text
GRAPH 1 - TASKS / WORKTREES

READY NOW / PARALLEL
[7.0]   [9.0]
  │       │
  ▼       │
[8.0]     │
  │       │
  └──┬────┘
     ▼
   [10.0]
```

For subtasks, keep the same single graph structure. Do not split into named side diagrams.

## Direction Guardrail

When many independent tasks are ready now, do not draw a vertical line from an unrelated ready-now task into an earlier-numbered task. This makes the earlier task look dependent on the later task.

Bad:

```text
READY NOW / PARALLEL
[7.0]   [12.0]
  │       │
  ▼       │
[8.0]     │
  │       │
  └──┬────┘
     ▼
   [10.0]
```

This says `[10.0]` depends on `[12.0]`. If the source only says `[12.0]` is independent or can run in parallel, keep it separate.

Good:

```text
READY NOW / PARALLEL
[7.0]   [9.0]   [12.0]
  │       │
  ▼       │
[8.0]     │
  │       │
  └──┬────┘
     ▼
   [10.0]
```

Here `[12.0]` is ready now and independent; it has no connector into `[10.0]`.

If ASCII layout makes the relationship unclear, switch to level bands:

```text
READY NOW / PARALLEL
[7.0]   [9.0]   [12.0]

AFTER [7.0]
[8.0]

AFTER [8.0] + [9.0]
[10.0]
```

## Final Validation Checklist

Before answering, check:

- The answer contains exactly the requested number of graphs.
- Every graph is terminal-readable in a fenced `text` block.
- The first line/level contains only immediately parallelizable nodes.
- No same-level node depends on another same-level node.
- Every arrow can be restated as "`dependent` depends on `prerequisite`" with the lower node as the dependent.
- No earlier-numbered task depends on a later-numbered task unless explicitly justified by the source text.
- No ready-now task has a connector into another task unless it is truly a prerequisite of that task.
- No duplicate task nodes exist just to mean “done.”
- No unexplained labels or internal IDs appear.
- No extra branch graphs or prose sections are appended.
