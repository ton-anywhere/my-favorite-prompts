---
name: diagramming-architecture
description: Use when drawing, editing, or reviewing an architecture diagram (module dependency graph or data-flow diagram, Mermaid or SVG), when code changes seem to call for a diagram update, or when a review finding says a diagram misses or misdraws edges.
---

# Diagramming Architecture

## Overview

An architecture diagram is **design**: a high-level picture for humans of how the system is meant to be built. The code follows the diagram. Nodes are modules and concepts; classes, files, call sites, and technologies stay in the prose.

**REQUIRED BACKGROUND:** Use `designing-layered-architecture` for layers, interfaces, and the composition root.

## First, name the kind

Every diagram answers one question. Read its heading and notes, decide which kind it is, and apply only that kind's edge rule.

| | Dependency diagram | Data-flow diagram |
|---|---|---|
| Question | Who imports whom? | Whose call does the work? |
| `A --> B` means | A depends on module B | A calls B, and work or data travels along the edge |
| Interfaces | Drawn: the application and the adapters both point at the contracts | Hidden: A points at what it ends up calling, even when B is injected behind an interface A knows |
| Application → adapter | Never: the application points at the interface | Drawn when the application calls that adapter at runtime |
| Checked by | The import checker (`madge`, `depcruise`, a `check-deps` script) | Review against the design docs |

## Shared rules

- **Wiring is invisible in both kinds.** Constructing an instance, passing it down, handing on a context token or factory, registering a provider, installing an extension, and reading start-up configuration get no edge. The composition root gets an edge only to what it runs.
- **Name nodes by concept**: `durable state`, `inference provider`, `orchestrator`. The technology, file path, or class goes in the prose under the diagram; a data-flow diagram reaches an external system through the library that calls it.
- **The diagram leads the code.** New files, a landed task, or a different wiring leave the diagram unchanged. An edge or node changes only when the intended architecture changes, approved by the owner.
- **An existing diagram keeps its author's nodes, granularity, and edges.** A review finding that asks for edges taken from imports or from wiring is answered by quoting the edge rule for that diagram's kind.

## Drawing a new diagram

1. Name the kind.
2. List the nodes at one granularity and group them into layers: composition root, application, adapters, libraries, external systems.
3. Write each edge as one sentence in that kind's terms ("A depends on B" or "A sends work to B").
4. Check acyclicity before drawing a dependency diagram. A cycle is an architecture bug: invert it with an interface, move the shared piece, or merge the modules.
5. Draw `flowchart` with one `subgraph` per layer and short labels. Label an edge only with the data that travels (`|answer|`).
6. Render it when the viewer supports Mermaid; otherwise state that only syntax and edges were checked.

## Layout

- Mermaid auto-layout decides positions; declaration order does not bind it.
- Prefer portable syntax. `%%{init: {"layout": "elk"}}%%` breaks ASCII/TUI renderers; add it only when the viewer supports it.
- If the renderer still crosses lines, hand-draw an SVG instead of adding fake nodes or edges.

## Common Mistakes

| Mistake | Fix |
|---|---|
| `main --> registry` because main imports `createRegistry` and passes it on | Wiring; no edge in either kind |
| An interface node in a data-flow diagram (`tasks --> multiplexer --> herdr`) | `tasks --> herdr` |
| `steps --> herdr` in a dependency diagram because steps calls Herdr at runtime | The application points at the contracts; the call belongs in the data-flow diagram |
| `steps --> states` because `createSteps({ states })` receives it and calls it | Wiring (Shared rules): no edge in the dependency diagram. Draw one only when A imports or instantiates B; the call may be a data-flow edge |
| A separate node for a construct that lives inside each entity, such as its state machine | Part of that entity's module, not a node others depend on |
| `app/store.ts`, `agent.sqlite`, `MLX server :8440` as nodes | `durable state`, `inference provider`; details in the prose |
| Editing the diagram because a task landed | Leave it; change it only for an approved design change |
| A dashed or labelled edge explaining how a value arrives ("uses injected env") | A plain edge, or none |
