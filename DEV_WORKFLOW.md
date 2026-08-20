## 🔁 Development Loop (Mandatory)

```
┌─────────┐    ┌─────────┐  ┌──────┐   ┌──────┐    ┌──────────┐
│ Tech    │───▶│Architect│─▶│ Dev  │◀─▶│  QA  │───▶│ Human    │
│  Lead   │    │ Agent   │  │Agent │   │Agent │    │(Report)  │
└─────────┘    └─────────┘  └──────┘   └──────┘    └──────────┘
     ▲                                                      │
     └──────────────────────────────────────────────────────┘
              (escalation only for defined criteria)
```

**This loop is mandatory.** The Tech Lead orchestrates but NEVER implements directly.

| Role | Responsibility | Forbidden |
|------|----------------|-----------|
| **Tech Lead** | Orchestrate, verify, report | Direct code changes |
| **Architect Agent** | Read-only analysis & planning | Any file modifications |
| **Dev Agent** | Implementation with TDD | Proceeding without human confirmation after each task |
| **QA Agent** | Review against architecture + standards | Accepting "looks good" without full procedure |

**Loop enforcement:** If the Tech Lead attempts direct implementation, this violates the development contract. Always dispatch `dev` agent for ANY code change — no exceptions.
