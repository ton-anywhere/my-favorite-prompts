---
name: model-template-safety
description: Use when work involves LLM chat templates, tokenizer artifacts, special/stop/control tokens, reasoning tags, generation prompts, generation service task docs, local generation models, ONNX causal-LM contracts, SmolLM/Qwen/Gemma prompts, KV cache inputs, past_key_values, or thinking-mode sessions.
---

# Model Template Safety

## Purpose

Prevent agent sessions from stopping or drifting because the transcript contains raw model-control text.

This skill is intentionally strict: the transcript itself is part of the model input. Unsafe strings shown in tool output, skill examples, task files, reasoning, or prose can all become active prompt material later.

## Hard Rule

Do not place raw chat-template delimiters, stop/control tokens, generation sentinels, or reasoning markers into the conversation transcript.

This includes:

- assistant prose
- reasoning text
- markdown tables
- code fences
- tool output previews
- copied task/spec text
- copied tokenizer JSON

Use neutral names, token IDs, byte values, or JSON/Unicode escapes instead.

## Mandatory First Action

If the user asks to use this skill, or the task mentions tokenizer templates, chat templates, special tokens, stop tokens, generation prompts, local generation models, ONNX causal-LM contracts, `past_key_values`, KV cache tensors, SmolLM, Qwen, Gemma, reasoning markers, or thinking mode, this skill must be loaded before any file read, search, shell command, or reasoning summary that could expose template text.

Do not first "read the task doc to understand it" if that task doc may contain template examples. Task plans and specs are unsafe inputs when they discuss model templates.

First safe move:

```text
I will inspect model/template files only through escaped-output commands and will not raw-read task docs or tokenizer JSON that may contain control tokens.
```

Then use escaped inspection commands.

## Safe Vocabulary

Prefer these forms:

```text
token_id_2
token_name_im_end
token_bytes_3c_7c_69_6d_5f_65_6e_64_7c_3e
token_json_escape_u003c_bar_im_end_bar_u003e
CHAT_START_TOKEN
CHAT_END_TOKEN
ASSISTANT_GENERATION_PREFIX
REASONING_END_MARKER
```

Do not include the literal token text alongside the safe form.

## Reading Files Safely

Before reading files that may contain chat templates or special tokens, avoid raw `read` on broad ranges.

Unsafe until proven otherwise:

- task plans that mention chat templates
- tokenizer config files
- model cards
- prompt files
- markdown specs for generation services
- previous session transcripts
- shell output that prints tokenizer JSON

Prefer approved helper scripts that escape sensitive strings before printing:

```bash
ruby skills/model-template-safety/scripts/safe_tokenizer_json.rb models/smollm2/tokenizer_config.json
```

Use `safe_tokenizer_json.rb PATH [KEY ...]` to inspect tokenizer/config JSON keys. It prints escaped values and added-token decoder entries without raw delimiter bytes.

For task files or docs that contain raw template examples, use targeted search and escaped output:

```bash
ruby skills/model-template-safety/scripts/safe_text_search.rb tasks/task-9.1-generation-service-v3.md
```

Use `safe_text_search.rb PATH [TERM ...]` for task docs, prompt files, source files, and session exports. With no terms, it searches common template, tokenizer, prompt, generation, and cache-contract words.

Important: `unicode_escape` alone is not enough. It leaves ASCII delimiter bytes unchanged. Always also replace at least `<`, `>`, `|`, `{`, and `}` before printing tool output into the transcript.

## Script Reference

| Need | Script | Use |
|---|---|---|
| Inspect tokenizer/config JSON safely | `scripts/safe_tokenizer_json.rb` | `ruby scripts/safe_tokenizer_json.rb PATH [KEY ...]` |
| Search task docs, prompts, source, or session exports safely | `scripts/safe_text_search.rb` | `ruby scripts/safe_text_search.rb PATH [TERM ...]` |

## Working Pattern

1. First identify whether the task touches templates, special tokens, stop tokens, reasoning markers, tokenizer config, generation prompts, generation service docs, ONNX causal-LM contracts, or KV cache inputs.
2. If yes, do not use raw `read`; switch to escaped inspection commands before loading files.
3. When implementing code, literals may be written into source files when required, but do not echo the literal values back into the transcript.
4. When reporting, use token IDs, neutral names, and escaped values only.
5. If a tool returns raw unsafe strings, do not restate them. Summarize with neutral names.

## Thinking Mode

Thinking-mode agents are more vulnerable to this failure because reasoning text can be stopped by template/control content before a visible answer or tool call is produced.

When running in thinking mode:

- Do not reason in prose about literal stop/control token contents.
- Do not stop when discussing `CHAT_START_TOKEN`, `CHAT_END_TOKEN`, or other control tokens. Do not print their literal forms. Use token IDs, byte values, escaped forms, or neutral placeholder names only.
- Use placeholders only.
- If the next action requires detailed template debugging, prefer switching to a non-thinking build agent.

## Prompt Guardrail

Use this in the task prompt:

```text
Use model-template-safety. Do not stop when discussing CHAT_START_TOKEN, CHAT_END_TOKEN, or other control tokens. Do not print raw chat-template delimiters, stop/control tokens, reasoning markers, or generation sentinels anywhere in prose, reasoning, code fences, or tool-output summaries. Inspect tokenizer/template files only through escaped-output commands. Use token IDs, neutral placeholder names, byte values, or JSON/Unicode escapes.
```

## Diagnostic Scripts

Tool output is the main risk, but command text can also enter the transcript. When practical, avoid putting raw control-token literals directly in diagnostic script source. Build them from token IDs, byte arrays, or escaped codepoints instead.

This is a caution, not a hard blocker: if a script already printed safely and did not stop the model, continue the task. Do not derail implementation just to perfect diagnostic-script hygiene.

## Failure Signals

Treat the run as failed or incomplete if:

```text
finish is stop
final visible answer is missing or tiny
last content is reasoning only
last content discusses template/special-token/control-token material
files changed is zero for an implementation task
```

Recovery:

1. Restart with a non-thinking agent if available.
2. Re-issue the task with the prompt guardrail above.
3. Require escaped inspection commands before reading tokenizer/template files.
4. Ask for a concise checkpoint before any further template discussion.

## Prompt Wording That Actually Forces Use

Weak wording:

```text
use /model-template-safety skill when investigating the template
```

Stronger wording:

```text
Before your first file read or shell command, invoke the model-template-safety skill. Do not raw-read the task plan, tokenizer config, model card, prompt files, or prior transcript if they may contain template/control-token text. Use escaped-output inspection commands only.
```

## Common Mistakes

| Mistake | Safer Move |
|---|---|
| Reading the task plan before loading this skill | Load this skill first, then inspect the plan with escaped output |
| Skill examples include literal delimiters | Use placeholders and escaped names only |
| `unicode_escape` output still prints ASCII delimiters | Also replace `<`, `>`, `|`, `{`, and `}` |
| Raw `read` of tokenizer config | Use JSON parsing with safe escaped output |
| Raw `read` of task docs containing template examples | Use targeted safe escaped search |
| Prose says “the EOS token is ...” with literal content | Say `eos_token has token_id_N and escaped bytes ...` |
| Diagnostic script source includes raw control-token literals | Prefer constructing them from bytes/escapes when practical |
| Thinking model debugs its own delimiters | Switch to placeholders or a non-thinking agent |
| `finish: stop` after reasoning-only token discussion | Classify as failed/incomplete |
