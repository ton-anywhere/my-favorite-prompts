# Agents Feedback Log

Append-only record of one-line feedback about agent performance during project work.

| Agent | Feedback | Implemented? |
|-------|----------|--------------|
| Plan Agent | When starting a new project, break each dependency/gem/lib install as a separate subtask for a setup task. The setup task will substitute "Task 0" when creating new projects. | No |
| QA Agents | Specs descriptions must match expectations. | No |
| Plan Agent | Each new gem task must be a subtask with official documentation analysis (websearch), installation, test installation before handing off to QA | No |
| Plan Agent | Missing pipelines tasks when new project | No |
| Build Agent | Validation step: Perform `rubocop` and fix any issues before completing the task | No |
| Build Agent | Validation step: Remove Unecessary comments | No |
| Plan Agent | Do not plan the code implementation, only the metacode, happy and edge cases instructions. | No |
| Plan Agent | Unit tests must be planned WITH their related code in the same task (TDD), never as isolated separate tasks; only integration/E2E tests spanning multiple completed features belong in a final verification task. | No |
