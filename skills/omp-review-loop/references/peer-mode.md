# Peer mode

Use when the user names an existing agent by tab label (`architect`, `tester`, or any other): `--peer <label>`, or a request like "you received a review from the architect/tester". The peer already exists and has already produced findings. You are the dev agent: read them, fix, answer, and loop until the peer approves.

## Rules

- Never launch, restart, or replace the peer. Never run `herdr tab create`, `herdr pane split`, or `herdr agent start`.
- Never use the agent in your own tab, and never use a previous or different agent, even if it looks suitable.
- Never run `/review` in the peer. It reviews on its own terms; you only read and message it.
- Do not start a reviewer. The `reviewer` tab and the `Reviewer setup` and `Round` sections do not apply.
- The peer's tab label is `<label>`. Match it exactly, in your workspace only. If no tab there matches, or more than one does, stop and report. Do not look in other workspaces and do not guess.
- Round cap, state file, fingerprint, and "never silently ignore a finding" work as in launch mode.

## Find the peer

```sh
herdr tab list --workspace "$WS"    # find .tab_id where .label == "<label>"
herdr pane list --workspace "$WS"   # panes whose .tab_id matches; pick the one running the agent
```

Set `PANE=<pane_id>` and address the peer by pane ID with `herdr agent read/prompt "$PANE"`. Agent names are not workspace-scoped for your purposes: never address the peer by name.

State file: `$ROOT/.agents/omp-review-loop-<label>.json`, same schema, `reviewer` set to `<label>`.

## Loop

1. Read the peer's findings: `herdr agent read "$PANE" --source recent-unwrapped --lines 240`, increasing `--lines` until the first finding is in view. Read the whole block.
2. Triage every finding. Implement the ones you agree with. Push back on the ones you disagree with, with a reason. Keep the P1/P2/P3 rule from launch mode when the peer uses severities; otherwise, never decline a finding that is a correctness, security, or data-loss defect.
3. Run the repo's verification (`sh scripts/verify.sh` when the repo has it) after the fixes.
4. Message the peer with `herdr agent prompt "$PANE" "<message>" --wait`: say what was fixed, what you disagree with and why, and ask for its verdict. On the first message, ask it to end with one line `Verdict: APPROVE` or `Verdict: REQUEST_CHANGES`.
5. Read the reply. Extract the last `verdict: approve|request[ _]changes` match, case-insensitively. If the peer approves in prose without that line, ask it once for the explicit verdict line. If there is still none, report "no verdict" and stop.
6. Update the state file (`rounds`, `last_fingerprint`, `last_verdict`).
7. `APPROVE`: apply any remaining findings you agreed with and report. `REQUEST_CHANGES`: go to step 1 with its new findings, until the round cap.

A peer that is blocked, working on something else, or shows a quota message: report what the pane shows and stop. Do not send keys to get past it.

## Report

Peer label and pane ID, final verdict and round number, per round what was fixed, pushed back, or left open, and whether anything is uncommitted. Do not close or rename the peer's tab.
