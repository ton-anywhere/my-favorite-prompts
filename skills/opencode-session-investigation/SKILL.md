---
name: opencode-session-investigation
description: Use when investigating opencode sessions, subsessions, agent drift, missed handoffs, tool misuse, or feedback grounded in opencode session exports.
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# OpenCode Session Investigation

## Purpose

Reconstruct what actually happened in an opencode session from exported parent and child sessions. Separate confirmed behavior from prompt risk, then recommend prompt, permission, or workflow fixes.

## Quick Workflow

1. **Start with the best source available.**
   Priority order:
   - **User-provided export:** inspect the provided JSON or markdown first.
   - **CLI JSON export:** if no export was provided, create JSON and use it as the canonical investigation artifact.
   - **TUI markdown export:** create markdown only when a readable transcript/report artifact is useful.

   If the available artifact is JSON, proceed from it directly. Use JSON as the source of truth for message IDs, timestamps, `parentID`, `sessionID`, `finish`, tool states, token metadata, and errors.

   If no export was provided, **create JSON**:
   ```bash
   opencode export <session_id> > session-<short-id>.json
   ```

   If the available artifact is markdown, use it for narrative review and quoting. When exact metadata is needed, run the JSON export command above too.

   During an investigation, OpenCode runtime logs are available at:
   ```text
   /home/airtonp/.local/share/opencode/log
   ```
   Search them by session ID, timestamp, error text, or tool name when exports do not explain runtime behavior:
   ```bash
   rg -n "<session_id|timestamp|error|tool_name>" /home/airtonp/.local/share/opencode/log
   ```
   Treat logs as supporting runtime evidence; use session exports as the canonical source for conversation structure and agent actions.

   To **create markdown**, launch the TUI from the directory where the `.md` should be saved:
   ```bash
   opencode -s <session_id>
   ```
   Then use the export flow:
   1. Press `ctrl+x x` to open **Export Options**. If the shortcut is unreliable, press `ctrl+p`, search `export`, and select **Export session transcript**.
   2. Leave the default filename such as `session-ses_abcd.md`, unless the user requested another name.
   3. Press `return` to confirm. A success toast should say `Session exported to <filename>`.
   4. Exit with `ctrl+d`, then verify the file exists in the directory where `opencode -s` was launched.

2. **Find subsessions.**
   Search the parent transcript for child session IDs and agent metadata:
   ```bash
   rg -n "task_id: ses_|subagent_type|parentID|sessionID|agent" <session_export_or_markdown>
   ```
   Export only the subsessions relevant to the feedback. Prefer JSON exports for investigation; add markdown exports only when readability matters.

3. **Classify evidence.**
   Use direct evidence before conclusions:
   - **Prompt:** what the parent asked the subagent to do
   - **Tool calls:** what commands/files the subagent actually touched
   - **Diff summary:** whether files changed, and which ones
   - **Final report:** what the subagent claimed
   - **Parent reconciliation:** how Tech Lead or parent agent used the result

4. **Verify the feedback literally.**
   For each reported drift, mark it:
   - **Confirmed:** visible in tool calls, diffs, prompts, or final output
   - **Not confirmed:** relevant exports do not show it
   - **Inferred prompt risk:** not proven in this trace, but the agent instructions permit or encourage the drift

5. **Recommend the smallest durable fix.**
   Prefer fixes in this order:
   - Tool permission for mechanical hard stops, such as denying `mkdir`
   - Agent prompt contract for expected alternative behavior
   - Project `AGENTS.md` for project-local conventions
   - New skill only when the process is reusable across projects
   - Helper script only when the same export/parsing steps are repeatedly tedious

## Investigation Notes

- Parent-session narration is not enough. Export child sessions when the question is about a subagent's behavior.
- A subsession summary showing `"files": 0` is useful evidence that the subagent did not edit files, but still inspect tool calls when command misuse is the concern.
- Prefer CLI JSON exports for investigation because they preserve exact metadata such as `finish`, `parentID`, `sessionID`, message and part IDs, tool states, timestamps, token counts, and errors.
- Use TUI-exported markdown as a companion artifact for human review, quoting, and reports. It is easier to skim, but less precise for root-cause analysis.
- If a TUI export does not save where expected, re-run `opencode -s <session_id>` from the desired destination directory and verify the created file path.
- Session exports can include later debugging interactions after the original incident. Anchor findings to exact message IDs, timestamps, and agent names so later investigation activity is not mistaken for the drift.
- OpenCode runtime logs are readable from `/home/airtonp/.local/share/opencode/log`. Correlate matching entries with the session ID and timestamp before using them as evidence.
- Search the OpenCode database only as a last fallback when the session ID/timestamp cannot be found through saved exports or normal export commands.
- Keep findings tied to exact session IDs and agent names so fixes target the right prompt.

## Output Template

```markdown
## Findings

| Feedback | Status | Evidence | Fix |
|---|---|---|---|
| [reported drift] | Confirmed / Not confirmed / Inferred prompt risk | [session id, prompt/tool/diff/final report detail] | [smallest durable change] |

## Recommended Changes

- [agent/prompt/permission/skill change]

## Residual Risk

- [anything not fully verified or still dependent on external permissions]
```

## Common Mistakes

| Mistake | Better move |
|---|---|
| Treating the parent transcript as the whole story | Export relevant child sessions |
| Using TUI markdown as the only evidence | Use CLI JSON as the canonical investigation artifact, then add markdown for readability |
| Starting TUI export from the wrong directory | Launch `opencode -s <session_id>` from the folder where the `.md` should be saved |
| Using database search/export as the default path | Use `opencode export <session_id>` first; database inspection is fallback only |
| Ignoring runtime logs when exports omit an error | Search `/home/airtonp/.local/share/opencode/log`, then correlate entries by session ID and timestamp |
| Trusting an agent's final report | Check tool calls and diffs |
| Calling every prompt loophole a confirmed drift | Label it as inferred prompt risk unless the trace proves it |
| Fixing only with stricter prose | Add permission denies for mechanical behaviors |
| Creating a broad skill for one project convention | Put project-specific rules in agent prompts or `AGENTS.md` |
