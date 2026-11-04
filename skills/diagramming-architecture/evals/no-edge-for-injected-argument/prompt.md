---
tags: [diagramming-architecture, designing-layered-architecture]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep]
---

Our Mermaid dependency diagram uses `A --> B` for "A depends on B". Application module `billing.ts` exports `createBilling({ ledger, clock })`. The composition root builds `ledger` from application module `ledger.ts` and passes it in. `billing.ts` calls `ledger.post(entry)` and imports only a type from `contracts.ts`, never `ledger.ts`.

Should the diagram get `billing --> ledger`? Answer yes or no and say why.
