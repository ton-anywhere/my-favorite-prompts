# Tasks: Breakdown Principles and INVEST Validation

Applies to every **task**: one task file, standing alone or as one row of an epic. Sub-tasks follow [sub-tasks.md](sub-tasks.md).

**A task has a user story of its own.** Before calling a piece a task, write its user story: what a user can do, or what they observe, once it is merged. A piece that only makes sense together with its siblings ("server half", "client half", "docs", "tests") has no user story. It is a sub-task of the task that does have one, even when it could be merged without breaking `main`.

## Task Breakdown Principles

These heuristics decide the order of the work. Each split they suggest becomes its own task only when that piece has its own user story; otherwise it becomes an ordered sub-task inside the task that has one.

1. **Infrastructure First**: Start with environment setup, framework configuration, and basic boilerplate.
2. **Data vs. Schema**: Separate creating database structures (ActiveRecord/Migrations) from the logic that populates or ingests data.
3. **Simplest Working Version First**: Deliver a simpler version that works end to end before the full solution: keyword search before semantic search, static data before wiring up an API. Each upgrade a user can notice is its own task.
4. **Pipeline Decomposition**: Break complex logic (RAG, multi-step processing) into testable stages (keyword search, semantic search upgrade, answer generation, orchestration). A stage whose output a user sees is a task; a stage they don't see is a sub-task.
5. **Logic vs. UI**: Implement core backend services and API logic before the frontend views and loading states.
6. **Cross-Cutting Concerns**: Observability (logging, tracing, metrics) and performance (caching, optimization) are tasks of their own when an operator or user notices them, and sub-tasks otherwise.
7. **Verification**: Every task ends with a **Verification** sub-task. Benchmarking or "gold standard" validation of the whole feature is a final task of its own only in an epic.

The count follows from the user stories. Don't split one story across several tasks, and don't bundle two stories into one task.

## INVEST Validation

Before presenting the tasks (Phase 1), and again before saving (Phase 2), review each task against the INVEST checklist. Fix violations before continuing:

- **Independent**: Can this task be implemented without another unfinished task being done first? If not, reorder or split.
- **Negotiable**: Does it describe the *outcome*, not prescribe the mechanism? (e.g., "user receives results in their language" not "add a language toggle dropdown")
- **Valuable**: Does it have its own user story, so that a user notices the difference once it is merged alone? A piece that only matters together with its siblings fails this test: fold it into their task as a sub-task.
- **Estimable**: Is it specific enough for a developer to estimate the work? Apply the specificity rules in [sub-tasks.md](sub-tasks.md).
- **Small**: Can a developer complete it in a single focused session or branch? If not, split it further.
- **Testable**: Is there a clear, observable way to verify it's done?
