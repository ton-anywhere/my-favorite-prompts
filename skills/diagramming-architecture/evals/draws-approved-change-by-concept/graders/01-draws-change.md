---
type: llm
focus: trace
weight: 1
---

The final Request flow diagram routes checkout through a queue node to an email worker and no longer has a direct `checkout --> mailer` edge.
