# Goal
Write a git commit message for the staged diff given in the user message.
Output only the raw message in Conventional Commits format: type(scope): description.

## Commit Types

| Type | Use for |
| --- | --- |
| feat | new capability or behavior change |
| fix | restore intended behavior |
| docs | documentation only, no behavior change |
| test | add or fix tests only |
| refactor | restructure without behavior change |
| perf | faster or cheaper existing behavior |
| chore | maintenance, deps, config |
| build | build system or packaging |
| ci | CI pipeline or automation |
| style | formatting or whitespace only |
| revert | undo a previous commit |

## Verify
Wrap it under 80 characters. Run the command below to verify your commit-message:

```bash
printf '%s' <commit-message> | wc -m
```

## Output

Output only your commit message.
One line, no body, no markdown, no backticks, lowercase.
