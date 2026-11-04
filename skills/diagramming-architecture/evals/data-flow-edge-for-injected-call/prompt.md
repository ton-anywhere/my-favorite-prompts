---
tags: [diagramming-architecture, designing-layered-architecture]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep]
---

Our Mermaid data-flow diagram uses `A --> B` for "A calls B and work travels along the edge". Application module `workflow.ts` receives `notifier`, typed as interface `Notifier`, in `createWorkflow({ notifier })`. The composition root passes the concrete Slack adapter. At runtime workflow calls `notifier.send(message)`, which posts to Slack.

In this data-flow diagram, should there be an edge from workflow to the Slack notifier? Answer yes or no and say why.
