---
name: babysitter
description: Use when supervising a constrained local model that repeats tool failures, loses mutable state, follows the wrong instructions, or needs an evidence-backed workflow intervention.
---

# Babysitting Small Models

Use this skill to diagnose and improve the system around a constrained model.
The target is a reliable next run. Do not turn the skill into instructions that
belong in the constrained model's prompt or task skill.

## Establish what happened

Read the session, effective prompt, available tools, active model, thinking
level, and the exact skill files that the model actually read. Treat the raw
trace as primary evidence.

Classify each problem before proposing a change:

| Finding | Meaning | Intervention surface |
|---|---|---|
| A required skill or reference was not loaded | Prompt-routing failure | Initial prompt or invocation syntax |
| A model repeats an action after state changed | State-tracking failure | Checkpoint in the target task skill or a deterministic helper |
| A command is red because an expected check returned nonzero | Shell-status failure | Command construction or target task skill |
| A command hides a failed mutation behind a later success | Masked failure | Command construction or target task skill |
| The trace shows a permission, process, or provider failure | External failure | Runtime configuration or tooling |
| The model persists with a disproven strategy | Capability limit | Stronger model or a simpler task split |

Count both recorded tool errors and semantic failures hidden by shell sequencing.
Do not infer an index reset, missing hook, cache loss, or harness defect without
direct trace evidence.

## Find the smallest control

Change the surface that owns the failure. Keep a routing error in the initial
prompt. Keep a repeatable task procedure in its task skill. Use a script or a
tool constraint when prose cannot reliably control the behavior.

Prefer one explicit state check after each mutation that changes the next
decision. For Git, the relevant facts are the current working tree, index, and
scoped diff. For other tools, identify the equivalent persisted state.

When a mutation's exit status matters, keep its command separate from reporting
commands. A later successful `echo`, `status`, or `diff` must not hide it.

Make conditional runtime facts visible in the prompt. Verify that a harness
invoked the requested skill rather than merely mentioning its name. In Pi,
`/skill:name` must begin the message; text containing that string does not
invoke the skill.

Do not add a rule merely because one model made one mistake. Add it when the
trace shows a reusable decision failure. Remove ambiguous wording before adding
more instructions.

## Make the fragile action executable

When the model understands the goal but repeatedly fails a mechanical step,
prefer a small helper over more prose. Good candidates are hunk selection,
format conversion, structured extraction, and other repeatable transformations.

Give the helper a narrow contract: explicit inputs, no inferred ownership,
fail-closed handling of ambiguity, a meaningful nonzero exit status, and output
that shows the resulting state. Put it with the target task skill and give the
model its exact path. Verify the helper on a disposable fixture before relying
on it in an autonomous run.

Keep judgment with the supervising agent. A helper should constrain a fragile
mechanical action, not silently decide scope, intent, or authorization.
