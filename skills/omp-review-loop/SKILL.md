---
name: omp-review-loop
description: Drive a herdr review loop until the reviewing agent approves, fixing its findings. Launch mode starts an omp reviewer in a tab labeled `reviewer`; peer mode (`--peer <label>`) loops with an already running agent such as `architect` or `tester`. Invoke only by hand.
argument-hint: "[task-doc-path] [--peer <label>] [--max-rounds N]"
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# OMP Review Loop

Run this only when the user invokes it. The loop is complete when the reviewing agent returns `Verdict: APPROVE` for the current tree. Then stop.

The user's original requests are in `references/user-prompts.md`.

## Modes

Pick the mode from the request, before anything else:

- **Launch** (default; plain dev + reviewer): you start a new omp agent in a tab labeled `reviewer` and drive its `/review`. Everything below applies. Do not start another reviewer for the same tree.
- **Peer** (`--peer <label>`, or the user says the review came from the architect, the tester, or another named agent): the agent already exists on a tab with that label. You do not launch it; you read its findings, fix or push back, message it, and repeat until it approves. Read [references/peer-mode.md](references/peer-mode.md) and follow it instead of "Reviewer setup", "Round", and the launch-only parts of "Fixed choices". Preflight and State still apply, except the "something to review" check.

Both modes stay in your own workspace (`WS=$(herdr pane current)`, its `workspace_id`). A tab or agent with the same label or name in another workspace is never yours: do not read, message, or reuse it. Pass `--workspace "$WS"` to `herdr tab list`, `herdr pane list`, and `herdr tab create`.

## Fixed choices

- Reviewer: always omp (`--kind omp`). Never codex, claude, or a subagent unless the user names one.
- Review target: "Review against the base branch (PR Style)" per default (option 1). Use "Review uncommitted changes" (option 2) if there are unstaged changes.
- Driver: the dev agent that runs this skill launches the tab and drives the omp menu itself. Do not hand the herdr steps to a subagent.
- Location: the reviewer runs in its own herdr **tab**, created with `herdr tab create`. Never split a pane for it.
- Label: the tab MUST carry the label `reviewer` (`--label reviewer`).
- Tabs: one review tab for the whole loop. Keep it open at the end.
- Task doc: Provided by ask the user. Otherwise, infer it from the available info from the code, commit messages, branch name.
- Round cap: `--max-rounds N`, default 5. At the cap, stop and report.

## Preflight

1. `test "${HERDR_ENV:-}" = 1`. If it fails, stop and say you are not in Herdr.
2. `ROOT=$(git rev-parse --show-toplevel)`. Use the absolute `$ROOT` for every `--cwd`. A relative or `$PWD` value can land the pane in the wrong directory.
3. There must be something to review: uncommitted changes (`git -C "$ROOT" status --porcelain` is non-empty) or commits ahead of the base (`git -C "$ROOT" rev-list --count <base>..HEAD` is greater than 0). If neither, stop: there is nothing to review. The base defaults to `main`.
4. If you received a doc, reference only it on the review reques. Do not open other plan or docs.
5. Fingerprint: `FP=$(sh <skill base directory>/scripts/tree-fingerprint.sh)`.

## State

State lives in `$ROOT/.agents/omp-review-loop.json` for the reviewer named in it. A different reviewer writes its own file, `$ROOT/.agents/omp-review-loop-<reviewer>.json`. Never overwrite another reviewer's record. The fingerprint script excludes all `omp-review-loop*.json` files.

```json
{"reviewer": "omp-review", "pane_id": "w4V:p9", "task_doc": ".agents/CLAUDE_ADAPTER_PLAN.md", "rounds": 2, "last_fingerprint": "<sha>", "last_verdict": "APPROVE"}
```

Decide before launching anything:

- If the file says `last_verdict` is `APPROVE` and `last_fingerprint` equals `$FP`: the tree has not changed since approval. Report "Already approved at round N; tree unchanged. Not launching." and stop. This rule prevents repeat launches.
- If the tree changed after an approval, that is a new round. Say so in the report.
- If no state file exists, this is round 1.

## Reviewer setup

Create the reviewer only when no live reviewer exists. Check with `herdr agent get <reviewer>`. If the agent is live and idle, reuse it.

Create a new tab with the label `reviewer`. Do not use `herdr pane split`.

```sh
herdr tab create --cwd "$ROOT" --label reviewer --no-focus
```

Take the pane to use from `.result.root_pane` in the output (`.result.tab` is the tab ID). Set `PANE=<root_pane id>`, then:

```sh
herdr agent start omp-review --kind omp --pane "$PANE"
```

Save the reviewer name and `$PANE` (the tab's root pane) to the state file.

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
   - `APPROVE`: handle the remaining findings as in "Post-approval", then report.
   - `REQUEST_CHANGES`: go through the numbered findings one by one and implement each one in the worktree yourself. Map severities: P1 is high, P2 is medium, P3 is low or nit. Push back only on P3 findings. Send each pushback to the reviewer pane as a plain message and wait for its ACCEPT or REJECT before the next round; record the outcome in the report. Never decline a P1 or P2 finding; if one seems wrong, implement it and say so. Do not let the reviewer edit files. Run the repo's verification before the next round (`sh scripts/verify.sh` when the repo has it, per its AGENTS.md). Recompute `$FP`, then start the next round. If `rounds` has reached the cap, stop and report the open findings.

## Post-approval

After `APPROVE`, do not start another `/review` round for the same tree unless the user asks for one. The findings listed above the verdict are still open unless they were fixed:

- Implement the findings you agree with, then run the repo's verification.
- Push back on the rest with a written reason in the report. Never silently ignore a finding.
- Message the same reviewer pane with a plain message (not a `/review` command) using `herdr agent prompt "$PANE" "<message>" --wait`, to report what was fixed. Do not create a tab or start a reviewer. A plain message cannot verify changed code: if the tree changed after the approval, run a new `/review` round on the current tree, and record APPROVE only from that round's verdict.
- If it confirms, update the state file and report. If it raises new findings, repeat this pass.

## Review prompt

Type this as one line into the omp input box (step 1 of the round). It is the text the reviewer sees; it is not sent as a separate prompt.

```text
/review Review the changes above. Read <task doc> first. Do not edit files. Report every actionable defect as a numbered finding with file:line, severity, what is wrong, and the fix to make. Then end with one line: `Verdict: APPROVE` or `Verdict: REQUEST_CHANGES`.
```

## Failure handling

- Usage limit or quota message in the reviewer pane: stop, report the message and the reset time, and keep the state file.
- The agent does not start or the menu never appears: report the screen output. Do not create a second tab or split a pane to retry.
- The reviewer edits files despite the prompt: inspect the change with `git diff`, record it in the report, and rerun verification.
- If the same review request arrives after an APPROVE, do not launch. Reply with the existing approval, its pane ID, and the current git state.

## Report

When the reviewer approves, finish "Post-approval", then report back. Do not start another round.

Give the user:

- Final verdict and round number.
- Reviewer pane ID.
- For each round, what was fixed and what was left open.
- Whether the tree is approved (fingerprint recorded) and whether anything is uncommitted.

Do not close the reviewer tab unless the user asks.
