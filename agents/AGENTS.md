# Agent Prompt Authoring Guide

This folder contains agent system prompts. When editing them, stay in a prompt
engineering role: improve instructions, boundaries, handoffs, and verification
contracts without adopting the agent persona you are editing.

## Drift Controls

- Keep role boundaries explicit. Tech lead orchestrates; build implements; QA
  reviews; plan remains read-only.
- Prefer mechanical handoff requirements over broad warnings. Name required
  inputs, output shape, acceptance checks, and stop conditions.
- Add recovery behavior for known failure modes, not just stronger adjectives.
- Keep "minimal" prompts compact but not context-free. A subagent brief must
  still include task, scope, out-of-scope, acceptance check, paths, and expected
  output.
- Put generic runtime/tool hygiene in the global initialization instructions,
  such as `dotfiles/instructions.md`, instead of repeating it in every agent.
- Keep role-specific drift controls in the agent prompt that owns the behavior.
  For example, tech-lead dispatch discipline belongs in `tech-lead-agent.md`.

## Evidence Standard

When tuning an agent after a drift report:

1. Inspect the session export or transcript.
2. Separate confirmed behavior from inferred prompt risk.
3. Patch the smallest instruction surface that would have changed the outcome.
4. Preserve existing role separation unless the evidence shows the boundary is
   itself the problem.

## Verification

- For Markdown-only prompt edits, run a targeted readback of the changed
  sections.
- For shell script edits elsewhere in the repo, run `bash -n <script>`.
- Do not update `superpowers/` internals unless that upstream checkout is the
  intended target.
