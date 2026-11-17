# Tasks: Breakdown Principles and INVEST Validation

Applies to every **task**: a parent task in a single list, or a README row and its task file in an epic. Sub-tasks follow [sub-tasks.md](sub-tasks.md).

## Task Breakdown Principles

When generating tasks, follow these heuristics to ensure a clean implementation:

1. **Infrastructure First**: Start with environment setup, framework configuration, and basic boilerplate.
2. **Data vs. Schema**: Separate the creation of database structures (ActiveRecord/Migrations) from the logic that populates or ingests data.
3. **Simplest Working Version First**: Before implementing the full/optimal solution, deliver a simpler version that works end-to-end. For example: implement keyword search before semantic search, or render static data before wiring up an API. Each upgrade to a more sophisticated approach should be its own task. This creates natural deliverable milestones and makes each stage independently testable.
4. **Pipeline Decomposition**: For complex logic (like RAG or multi-step processing), break the pipeline into independent, testable stages (e.g., 1. Keyword Search, 2. Semantic Search Upgrade, 3. Answer Generation, 4. Pipeline Orchestration). Do not merge pipeline stages into a single task.
5. **Logic vs. UI**: Implement core backend services and API logic before building the frontend views and loading states.
6. **Cross-Cutting Concerns**: Treat Observability (logging, tracing, metrics) and Performance (caching, optimization) as distinct high-level tasks if they are significant.
7. **Verification**: Always include a final task for benchmarking, specialized testing, or "Gold Standard" validation.

Let the number of tasks be driven by these principles and the INVEST criteria below — do not constrain the count artificially. A large feature may need 15+ tasks; a small one may need 3. Prefer more tasks that are each Small, Independent, and Testable over fewer tasks that bundle concerns. Prioritize separation of concerns (e.g., separating data ingestion from schema, or search logic from generation logic).

## INVEST Validation

Before presenting the tasks (Phase 1), and again before saving (Phase 2), review each task against the INVEST checklist. Fix violations before continuing:

- **Independent**: Can this task be implemented without another unfinished task being done first? If not, reorder or split.
- **Negotiable**: Does it describe the *outcome*, not prescribe the mechanism? (e.g., "user receives results in their language" not "add a language toggle dropdown")
- **Valuable**: Does completing this task leave the system in a better state? Is it a meaningful step forward on its own?
- **Estimable**: Is it specific enough for a developer to estimate the work? Apply the specificity rules in [sub-tasks.md](sub-tasks.md).
- **Small**: Can a developer complete it in a single focused session or branch? If not, split it further.
- **Testable**: Is there a clear, observable way to verify it's done?
