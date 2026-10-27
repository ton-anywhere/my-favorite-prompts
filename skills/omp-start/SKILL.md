---
name: omp-start
description: DO NOT INVOKE. Used to start a omp(oh-my-pi) session with orchestration.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

Read the plans and specs provided. 
DO NOT look for another doc for guidance. All task requirements are in the doc provided. 
Orchestrate the implementation on the current worktree.
Prefer launching tasks / smol subagents.
Before reporting back to the human, commit your changes  and launch one final slow agent to review your work after completing it.

# IMPORTANT
- Don't launch a review subagent for each subtask.

# FORBIDDEN 
## COMPILATION
The following are forbidden commands. Do not run or instruct subagents to run:
- `bun run build`
- `bun run build:native`
- `cargo build`
- any other command to trigger the projects binary compilation.

**Alternative**: Use `packages/coding-agent/scripts/omp` instead of the build commands above.

## TYPE CHECK
Do not run or instruct subagents to run these commands during implementation or
subtask work:

- `bun check`
- `bun run check:ts`
- `bun run check`
- `bun run ci:check:full`
- Direct tsgo -p tsconfig.json --noEmit

At the end of the task, if type verification is required, run only the smallest
relevant package-scoped check. Run checks sequentially. These commands still
invoke `tsgo` and can use significant memory:

```zsh
bun run --filter @oh-my-pi/pi-coding-agent check:types
```
