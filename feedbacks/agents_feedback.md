# Agents Feedback Log

Append-only record of one-line feedback about agent performance during project work.

| Agent | Feedback | Implemented? |
|-------|----------|--------------|
| Plan Agent | When starting a new project, break each dependency/gem/lib install as a separate subtask for a setup task. The setup task will substitute "Task 0" when creating new projects. | No |
| Plan Agent | Each new gem task must be a subtask with official documentation analysis (websearch), installation, test installation before handing off to QA | No |
| Plan Agent | Missing pipelines tasks when new project | No |
| Plan Agent | Unit tests must be planned WITH their related code in the same task (TDD), never as isolated separate tasks; only integration/E2E tests spanning multiple completed features belong in a final verification task. | No |
| QA Agents | Specs descriptions must match expectations. | No |
| Tech Lead | Before dispatching the plan agent, keep local startup context light: read only mandatory instructions and task scope, then delegate implementation/spec/schema discovery to plan or explore. | No |
| Tech Lead | After build returns, QA subagent dispatch is mandatory; missing local `qa_agent.md` files are not a valid reason to perform inline QA or mark QA complete. | No |
| QA/Build Agents | order declarations on specs: subject -> before blocks -> lets  | No |
| Plan Agent | Plan agent exposed reasoning/thinking in session `ses_1f924fbb5ffeXtfKBjwTyz417i`; ensure plan uses a no-thinking variant when thinking should be disabled. | No |
| Build Agent | Qwen3-Coder build agent can discover skills but skips `receiving-code-review` on review-fix handoffs; make review/QA/finding tasks hard-gate on invoking that skill first. | No |
| QA Agent | In opencode session `ses_1ecabd1d8ffe6eC4lyVdsUubgB`, QA loaded many irrelevant skills after already having enough evidence; tighten QA skill allowlist/gating and request params to reduce tool-call loops. | No |
| Build/QA Agents | Spec review should flag global nondeterminism stubs like `Kernel.rand`; build must load `verify-specs` for spec edits and `verification-before-completion` before done claims, with repeated runs for flaky findings. | No |
| Tech Lead | After any Build pass that changes files, the dev loop must return to QA; Tech Lead verification is only pre-QA sanity checking and must not end the workflow or mark the task done. | No |

# Quick Tunnings

  - Plan agent creates too-coarse setup tasks: increase planning structure in prompt first; if still shallow, raise top_p slightly.
  - Plan agent misses whole roadmap areas like pipelines: raise planner top_p; consider slightly higher temperature only if it remains too narrow.
  - Plan agent separates unit tests from implementation tasks: prompt/process fix first; sampling changes are secondary.
  - Plan agent exposes thinking/reasoning: disable thinking/preserve_thinking; do not solve with sampling knobs.
  - Tech Lead reads too much before dispatching plan/explore: lower temperature/top_p; reduce startup prompt scope.
  - Tech Lead skips mandatory QA dispatch: prompt/agent-contract fix first; lower temperature if it rationalizes exceptions.
  - QA agent loads irrelevant skills/tools: lower temperature, lower top_p/top_k, raise repeat_penalty slightly, remove presence_penalty.
  - QA agent almost hits context limit: lower top_p/top_k, reduce max_tokens/context budget for the agent, tighten tool/skill allowlist.
  - QA agent gives spec feedback that does not match expectations: lower temperature; make review checklist stricter.
  - QA agent misses nondeterminism/flaky-test issues: raise top_p slightly or improve review checklist; do not raise temperature much.
  - Build agent skips required review-receiving skill: prompt/permission gate first; lower temperature if it keeps improvising around workflow.
  - Build agent edits specs without loading verify-specs: prompt/skill-gate fix first; lower temperature if it ignores gates.
  - Build agent claims done without verification: prompt gate first; lower temperature/top_p if it keeps making premature completion claims.
  - Build/QA agents violate preferred spec declaration order: prompt/style-rule fix first; lower temperature if inconsistency persists.
  - Build agent is unstable or hard to steer: lower temperature, lower top_p, lower top_k, remove presence_penalty.
  - Build agent deletes unrelated files or over-cleans: lower temperature/top_p; add permission denies or explicit destructive-command guardrails.
  - Build agent handles code review poorly: lower temperature, raise repeat_penalty slightly, and hard-gate receiving-code-review.
  - Build agent over-applies cleanup instructions: lower top_p/top_k; make prompt require changed-file scope confirmation before edits.

  I’d also add this meta-rule:

  - If the failure is “ignored required workflow,” fix prompt/gating first.
  - If the failure is “wandered, improvised, or over-expanded,” lower sampling breadth.
  - If the failure is “missed alternatives or edge cases,” raise top_p slightly before raising temperature.
  
