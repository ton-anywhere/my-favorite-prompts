---
name: designing-layered-architecture
description: Use when designing or reviewing a project's module structure, deciding where a dependency belongs, introducing dependency injection, or checking that layers and dependencies stay acyclic.
---

# Designing Layered Architecture

## Overview

Design by dependency direction, not by folder names. A module depends on what it uses, nothing depends on the composition root, and the dependency graph is a DAG.

## Layers

| Layer | Responsibility | May depend on |
|---|---|---|
| Composition root | Construct, wire, inject, start | Everything; used by nothing |
| Application / policy | Use cases and the interfaces they need; no I/O | Policy and interfaces only |
| Adapters | Implement interfaces: storage, HTTP, process launchers, model providers | Policy interfaces + their library |
| Frameworks / libraries | Third-party runtime (web framework, ORM, agent harness) | Below them |
| External systems | Database, server, CLI, child process | Nothing in the app |

These are responsibilities, not mandatory directories. Add a layer only when it owns a rule.

## Rules

- **One direction:** outer depends on inner. If an inner module imports an outer one, invert the dependency with an interface.
- **DAG:** no cycles, including through shared utilities. If two modules need each other, one of them owns the contract.
- **Interfaces live with the policy; adapters implement them.** Inject through parameters or constructors, not globals, singletons, or ambient imports.
- **Declaring is not using.** The composition root may construct the database, provider, or launcher and pass them down. Policy code never imports the concrete adapter. A module that receives `SqliteStore` typed as `Store` depends on `Store`.
- **Diagrams state design; the checker enforces imports.** The dependency diagram states intended import direction at the author's granularity, with interfaces drawn; a data-flow diagram shows the significant runtime calls and may skip interfaces. Neither is completed from an import list; see `diagramming-architecture`.
- **Replaceability test:** swapping one adapter should change only that adapter and the composition root. If policy code changes, the seam is wrong.
- **Framework types stay at the edge.** Do not leak ORM, HTTP, or harness types into core.
- **One reason to change per module.** Small and flat beats speculative abstraction.

## Pattern

```ts
// core/interfaces.ts
export interface Store { save(item: Item): Promise<void> }

// adapters/sqlite-store.ts
export class SqliteStore implements Store { /* ... */ }

// composition root
const app = createApp({ store: new SqliteStore(path) })
```

## Verification

1. Write every edge as "A depends on B", naming the call through B or the interface B defines. Drop edges that only describe construction, injection, or a value passed through.
2. Run a cycle check over resolved imports (`madge --circular`, `depcruise`, `import-linter`, or a small script).
3. Confirm the composition root has one outgoing edge, to the application entry. Any other outgoing edge must be a real call.
4. Replace one adapter mentally and confirm the policy files stay untouched.

## Common Mistakes

| Mistake | Fix |
|---|---|
| CLI entry imports the DB, HTTP client, and provider | Move construction into an app factory; the root only wires |
| Drawing "A declares B" as a dependency | Draw only the design relation (see `diagramming-architecture`) |
| Shared `utils` imported by both sides of a boundary | Move the concept to its owner or duplicate the small piece |
| Service locator or global container | Pass dependencies explicitly |
| Core imports ORM/framework types | Map at the adapter boundary |
| One directory per layer with no rule | Merge layers that do not own behavior |

## See Also

- `codebase-design` for interface, implementation, seam, and depth vocabulary.
- `diagramming-architecture` for drawing and validating dependency and data-flow diagrams.
