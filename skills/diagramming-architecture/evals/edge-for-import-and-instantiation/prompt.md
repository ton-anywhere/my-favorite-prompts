---
tags: [diagramming-architecture, designing-layered-architecture]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep]
---

Our Mermaid dependency diagram uses `A --> B` for "A depends on B". Application module `invoice.ts` does `import { Money } from './money.ts'` and calls `new Money(amount, currency)`. `money.ts` is another application module with pure value logic.

Should the diagram get `invoice --> money`? Answer yes or no and say why.
