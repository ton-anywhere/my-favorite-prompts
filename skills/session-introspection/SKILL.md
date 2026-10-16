---
name: session-introspection
description: Review the completed session for verified skill usage, observed instruction problems, and focused evidence-based changes.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Session Introspection

Review the current session after the user manually invokes this skill. Produce a
concise report. Propose changes, but do not edit skills, prompts, or other files.

## Review

Use the current session transcript and available tool evidence as the source of
truth.

1. Reconstruct the relevant session outcome and decisions.
2. List every skill that was actually used. Include only skills supported by
   direct session evidence, such as an explicit invocation or loaded skill
   instructions. List this section before all findings.
3. Inspect the used skills and prompts against what happened in the session.
4. Report only gaps, inconsistencies, conflicts, or missed instructions that
   the session evidence supports. Do not propose general improvements.
5. For each supported issue, create one ranked recommendation.

Do not infer that a skill was used from the task topic or from behavior alone.
Do not classify missing skills or inferred skills as used skills. If the session
does not provide enough evidence to verify a skill, say so briefly instead of
guessing.

## Output

Keep the report concise. Use this order:

### Skills used

List the verified skill names. Add one short evidence note for each skill.

### Ranked recommendations

Use one compact finding card per recommendation:

```text
P1 · High impact · High confidence
Target: <skill or prompt file>

Issue: <observed problem>
Evidence: <brief session evidence>
Explanation: <high-level reason the guidance should change>

Replace with:
<exact replacement Markdown or prompt text>
```

Rank recommendations by expected impact first, then by confidence. Use lower
priority labels when appropriate. Keep the explanation high level. Keep the
replacement text exact and limited to the smallest focused change.

If no issue has sufficient session evidence, write:

```text
No evidence-based changes recommended.
```

Do not apply any recommendation automatically.
