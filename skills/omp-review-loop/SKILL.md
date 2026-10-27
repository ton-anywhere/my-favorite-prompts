---
name: omp-review-loop
description: Run an omp /review loop in one herdr pane (never a tab) against the uncommitted changes, fixing findings until the reviewer approves. Invoke only by hand.
argument-hint: "[task-doc-path] [--max-rounds N]"
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# OMP Review Loop

Run this only when the user invokes it. The loop is complete when the omp reviewer returns `Verdict: APPROVE` for the current tree. Then stop. Do not start another reviewer for the same tree.

The user's original requests are in `references/user-prompts.md`.

## Fixed choices

- Reviewer: always omp (`--kind omp`). Never codex, claude, or a subagent unless the user names one.
- Review target: "Review against the base branch (PR Style)" per default (option 1). Use "Review uncommitted changes" (option 2) if there are unstaged changes.
- Driver: the dev agent that runs this skill launches the pane and drives the omp menu itself. Do not hand the herdr steps to a subagent.
- Location: the reviewer runs in a herdr **pane**, split beside your current pane. Never create a tab. A tab is a separate screen and is hard for the user to find.
- Panes: one review pane for the whole loop. Keep it open at the end.
- Task doc: Provided by ask the user. Otherwise, infer it from the available info from the code, commit messages, branch name.
- Round cap: `--max-rounds N`, default 5. At the cap, stop and report.

## Preflight

1. `test "${HERDR_ENV:-}" = 1`. If it fails, stop and say you are not in Herdr.
2. `ROOT=$(git rev-parse --show-toplevel)`. Use the absolute `$ROOT` for every `--cwd`. A relative or `$PWD` value can land the pane in the wrong directory.
3. There must be something to review: uncommitted changes (`git -C "$ROOT" status --porcelain` is non-empty) or commits ahead of the base (`git -C "$ROOT" rev-list --count <base>..HEAD` is greater than 0). If neither, stop: there is nothing to review. The base defaults to `main`.
4. If you received a doc, reference only it on the review reques. Do not open other plan or docs.
5. Fingerprint: `FP=$(sh <skill base directory>/scripts/tree-fingerprint.sh)`.

## State

State lives in `$ROOT/.agents/omp-review-loop.json`. The fingerprint script excludes this file.

```json
{"reviewer": "omp-review", "pane_id": "w4V:p9", "task_doc": ".agents/CLAUDE_ADAPTER_PLAN.md", "rounds": 2, "last_fingerprint": "<sha>", "last_verdict": "APPROVE"}
```

Decide before launching anything:

- If the file says `last_verdict` is `APPROVE` and `last_fingerprint` equals `$FP`: the tree has not changed since approval. Report "Already approved at round N; tree unchanged. Not launching." and stop. This rule prevents repeat launches.
- If the tree changed after an approval, that is a new round. Say so in the report.
- If no state file exists, this is round 1.

## Reviewer setup

Create the reviewer only when no live reviewer exists. Check with `herdr agent get <reviewer>`. If the agent is live and idle, reuse it.

Split a new pane beside the current one. Do not use `herdr tab create`.

```sh
herdr pane split --current --direction right --cwd "$ROOT"
```

Take the new pane's `pane_id` from the output. Set `PANE=<pane_id>`, then:

```sh
herdr agent start omp-review --kind omp --pane "$PANE"
```

Save the reviewer name and pane to the state file.

Wait until the omp TUI is ready for input: `herdr agent get omp-review` shows `interactive_ready: true` and `agent_status: idle`. Then read the pane and confirm the input box is visible.

## Round

Everything below is typed into the omp TUI. Do not use `herdr agent prompt`; it submits text without showing you the input box. Use the pane ID from setup (`$PANE`).

1. Type the review command into the input box without submitting it:

   ```sh
   herdr pane send-text "$PANE" "/review <small prompt>"
   ```

   Read the pane (`herdr pane read "$PANE" --source visible`). Check that the input box holds the full text, unchanged. If it is truncated, or an autocomplete popup has replaced it, fix the input before going on. Do not submit a partial command.

2. Submit it:

   ```sh
   herdr pane send-keys "$PANE" enter
   ```

   Read the pane. The "Review Mode" menu should be showing with options 1 to 4.

3. Choose the target interactively. Read the screen after every key and check it before sending the next one.
   - If there are uncommitted changes, choose option 2 "Review uncommitted changes": `herdr pane send-keys "$PANE" down enter`.
   - Otherwise choose option 1 "Review against a base branch": `herdr pane send-keys "$PANE" enter`. In the branch picker, check that the base (`main` by default) is highlighted, then confirm it with `enter`.
   - If the screen does not show the expected menu or picker, do not send keys. Report what it shows.

4. Wait for the review to settle:

   ```sh
   herdr agent wait omp-review --timeout 3000000
   ```

5. Read the output and extract the verdict:

   ```sh
   herdr agent read omp-review --source recent-unwrapped --lines 240
   ```

   Take the last match of `grep -oiE 'verdict: *(approve|request[ _]changes)'`. Match case-insensitively: `Verdict:`, `VERDICT:`, `REQUEST CHANGES`, and `REQUEST_CHANGES` all occur. If there is no match, read more lines. If it still has no match, report "no verdict" and stop. Do not guess.

   The verdict is only the last line. Keep the numbered findings above it. Read the whole findings block, increasing `--lines` until its first finding is in view. If the block is cut off, read further up before acting on it.

6. Update the state file with `rounds`, `last_fingerprint`, and `last_verdict`.

7. Branch on the verdict:
   - `APPROVE`: stop and report.
   - `REQUEST_CHANGES`: go through the numbered findings one by one and implement each one in the worktree yourself. Push back only on minor findings (severity low or nit), and only with a written reason in the report. Never decline a high or medium finding; if one seems wrong, implement it and say so in the report. Do not let the reviewer edit files. Run the repo's verification before the next round (`sh scripts/verify.sh` when the repo has it, per its AGENTS.md). Recompute `$FP`, then start the next round. If `rounds` has reached the cap, stop and report the open findings.

## Review prompt

Type this as one line into the omp input box (step 1 of the round). It is the text the reviewer sees; it is not sent as a separate prompt.

```text
/review Review the changes above. Read <task doc> first. Do not edit files. Report every actionable defect as a numbered finding with file:line, severity, what is wrong, and the fix to make. Then end with one line: `Verdict: APPROVE` or `Verdict: REQUEST_CHANGES`.
```

## Failure handling

- Usage limit or quota message in the reviewer pane: stop, report the message and the reset time, and keep the state file.
- The agent does not start or the menu never appears: report the screen output. Do not split a second pane or create a tab to retry.
- The reviewer edits files despite the prompt: inspect the change with `git diff`, record it in the report, and rerun verification.
- If the same review request arrives after an APPROVE, do not launch. Reply with the existing approval, its pane ID, and the current git state.

## Report

When the reviewer approves, stop working and report back. Do not start another round.

Give the user:

- Final verdict and round number.
- Reviewer pane ID.
- For each round, what was fixed and what was left open.
- Whether the tree is approved (fingerprint recorded) and whether anything is uncommitted.

Do not close the reviewer pane unless the user asks.
