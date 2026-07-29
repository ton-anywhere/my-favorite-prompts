---
name: prompt-feedback-review
description: Use when reviewing feedback about Codex or OpenCode agent drift, missed skill usage, weak tests, repeated review loops, bad handoffs, or prompt/context failures, especially when the user asks to inspect sessions, subsessions, commits, agent instructions, AGENTS.md files, skills, or model configs and preview prompt or skill fixes before implementation.
---

# Prompt Feedback Review

## Overview

Turn concrete agent failures into small, durable instruction changes. Investigate what happened from primary evidence, distinguish confirmed drift from prompt risk, and preview fixes without implementing them unless the user later asks.

## Workflow

1. **Restate the feedback target.**
   Identify the reported drift, the affected agent or skill, and the artifact to inspect: session ID, session export, commit, project directory, agent file, `AGENTS.md`, skill, model config, or review comment.

2. **Gather primary evidence before diagnosing.**
   - If the request involves OpenCode sessions, use the `opencode-session-investigation` skill.
   - Read parent sessions and relevant subsessions when the drift may have happened in a delegated agent.
   - Read the current agent, skill, `AGENTS.md`, or config files before suggesting changes to them.
   - For commit-based feedback, inspect the commit diff and any touched instructions or tests that explain the pattern.

3. **Classify the failure.**
   Use these labels:
   - **Confirmed drift:** visible in prompts, tool calls, diffs, final reports, logs, or commit changes.
   - **Not confirmed:** the available evidence does not show the reported behavior.
   - **Inferred prompt risk:** not proven in the trace, but the current instructions allow or encourage the failure.
   - **External/tooling limit:** caused by permissions, missing tools, runtime behavior, or model/config constraints rather than prompt wording alone.

4. **Find the smallest durable fix.**
   Prefer existing instruction surfaces before adding new ones:
   - Clarify or remove ambiguous existing lines.
   - Tighten the relevant skill trigger or workflow.
   - Update the responsible agent prompt.
   - Add a project-local `AGENTS.md` only for project-specific conventions.
   - Add a new skill only when the process is reusable across projects.
   - Add tool permissions, scripts, or config changes when prose cannot reliably prevent the failure.

5. **Preview changes, do not implement.**
   Unless the user explicitly asks to edit files now, present proposed changes as a git diff. Keep the diff scoped to the files that should change.

## Review Heuristics

- Ambiguity beats accumulation: when a file is already large, look for unclear or conflicting lines to revise or remove before adding more rules.
- A missed skill invocation is usually a trigger or workflow problem. Check both the skill description and the agent's instruction to consult skills.
- A repeated review loop is often caused by a trigger that fires too broadly, a completion gate that never becomes satisfiable, or unclear handoff ownership.
- Weak test output may belong in a domain skill, such as `verify-specs`, when the rule is reusable across repositories.
- Project-specific rules belong near the project, such as `AGENTS.md` under the relevant directory, when they should not affect unrelated codebases.
- Do not assume the role described inside an agent file or session. Read it as evidence only.

## Output Shape

Answer in this order:

1. **Opinion:** prompt, skill, agent edit, project `AGENTS.md`, config change, or no change.
2. **Evidence:** concise findings tied to session IDs, commits, file paths, or quoted instruction lines.
3. **Recommended changes:** explain why each surface is the right place.
4. **Preview diff:** include a git diff when changes are proposed and the user asked not to implement yet.
5. **Residual risk:** note anything unverified or dependent on future behavior.

## Common Fix Patterns

- Tighten a skill description when Codex failed to invoke the right skill.
- Add a mandatory first-pass checklist when agents skipped critical evidence or mechanical checks.
- Replace vague "be strict" language with specific accept/reject criteria.
- Add explicit "do not implement yet; preview only" output instructions for diagnostic prompts.
- Add handoff rules when parent and subagent responsibilities were unclear.
- Add permission denies or operational guardrails for mechanical behaviors that prompts alone should not police.

## Diff Preview Template

```diff
diff --git a/path/to/file b/path/to/file
--- a/path/to/file
+++ b/path/to/file
@@
-old instruction
+new instruction
```
