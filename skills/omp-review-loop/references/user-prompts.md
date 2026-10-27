# User prompts that drove the review loop

Verbatim prompts from the 2026-10-26 pisolino session (`feat/claude-support`, OMP orchestrator). Timestamps are from the session dump. Use these to recognise the request forms this skill must handle.

## Start of the task

```text
@.agents/CLAUDE_ADAPTER_PLAN.md
Read the plan provided.
Orchestrate the implementation in the current worktree.
Prefer launching tasks / smol subagents.
```

Correction, 20:08: "**important**- do not read and implement anything from the @.agents/REFACTORING-2026-10-26.md. it's for another task"

## Review request (first form, 20:24)

```text
/goal launch a new herdr pane and run `/review` command, select code review against the base branc, select main.
fix the findings and report back for a ne review.
your goal is complete once it reports this branch is aproved.
```

Note: this form names a base branch (`main`). The agent started a Codex reviewer, not omp. The user then corrected it (20:47).

## Correction after the Codex mistake (20:47)

```text
after this review from codex, fix it's findings and use omp to `/review`. pass the original task description doc so it can review your work based on it. @.agents/CLAUDE_ADAPTER_PLAN.md
OBS: the original instructions from my last message were for omp not codex.
```

## Scope change (20:48)

```text
wait. you already lauched a review subagent. now the new tab is not neccessary
```

## Review request (current form, 21:00 onward)

Sent five times, unchanged each time (21:00, 21:17, 21:26, 21:38, 21:46):

```text
launch a new herdr tab with an omp agent, use `/review`, select 2 (unstaged changes). reference the doc on the review request too .agents/CLAUDE_ADAPTER_PLAN.md --until aproved
```

Meaning of each part:

- `launch a new herdr tab with an omp agent`: one new tab, agent kind omp.
- `use /review, select 2 (unstaged changes)`: menu option 2, "Review uncommitted changes".
- `reference the doc ... --until aproved`: pass the task doc in the review prompt; keep looping until APPROVE.

## What the sessions showed the skill must fix

- The same request repeated after an APPROVE was treated as a new round each time. The skill's state file and fingerprint check block that when the tree is unchanged.
- A new tab was created for every round, and old tabs were left open. The skill reuses one reviewer.
- Codex was chosen without the user naming it. The skill fixes the reviewer to omp.
