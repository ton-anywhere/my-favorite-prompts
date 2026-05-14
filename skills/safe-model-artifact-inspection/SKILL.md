---
name: safe-model-artifact-inspection
description: Use when extracting technical details from model artifacts, tokenizer configs, chat templates, special/stop/control tokens, ONNX causal-LM contracts, prompt files, generation service task docs, local generation models, SmolLM/Qwen/Gemma artifacts, KV cache inputs, past_key_values, or session exports where raw control text could break or steer an agent.
---

# Safe Model Artifact Inspection

## Purpose

Extract model implementation facts without putting raw chat-template delimiters, stop/control tokens, or generation sentinels into the transcript.

Use this before reading tokenizer configs, model cards, prompt files, generation specs, generation service task docs, local generation model artifacts, ONNX causal-LM contracts, KV cache behavior, `past_key_values`, SmolLM/Qwen/Gemma artifacts, previous session exports, or task docs that may contain model-control text.

## Core Rule

Treat the transcript as executable prompt surface. Never print raw model-control strings from files or tool output. Report only:

- neutral placeholder names, such as `CHAT_START_TOKEN`, `CHAT_END_TOKEN`, `ASSISTANT_GENERATION_PREFIX`
- token IDs
- byte values
- escaped JSON or Unicode text
- implementation conclusions

Literal token strings may be written into source files when required, but do not echo those literals in prose, code fences, diffs, or summaries.

## First Move

Before any file read or search likely to expose tokenizer/template content, say:

```text
I will inspect model artifacts only through escaped output and will report placeholders, token IDs, byte values, and implementation conclusions.
```

Then use targeted escaped-output commands. Do not raw-read broad ranges from tokenizer files, prompt files, generation task docs, or session exports.

## Default Model Artifact Report

For a model directory, use the blessed contract reporter first:

```bash
ruby skills/safe-model-artifact-inspection/scripts/model_artifact_report.rb MODEL_DIR --format both
```

This emits a safe Markdown report followed by fenced JSON. It discovers known tokenizer/config files, the first ONNX file, external ONNX data files, static tokenizer facts, ONNX metadata when available, inferred KV-cache facts, bounded runtime probe results, and risks. It reports placeholders, token IDs, byte arrays, escaped strings, and provenance fields; it must not print raw chat/control token strings.

Use `--no-probes` only when runtime probing is unavailable or too expensive. Use `--format json` for automation and `--format markdown` for a human-only handoff.

## Safe Extraction

### JSON tokenizer/config files

Use JSON parsing and escape delimiter bytes before printing:

```bash
ruby skills/safe-model-artifact-inspection/scripts/safe_model_json.rb PATH_TO_JSON
```

Use `safe_model_json.rb PATH [KEY ...]` for tokenizer/config JSON. With no keys, it prints common model, tokenizer, context, token ID, template, and added-token fields.

### Task docs, prompt files, source files, and session exports

Print only relevant lines, after escaping risky bytes:

```bash
ruby skills/safe-model-artifact-inspection/scripts/safe_text_search.rb PATH_TO_TEXT_FILE
```

Use `safe_text_search.rb PATH [TERM ...]` for task docs, prompt files, source files, and session exports. With no terms, it searches common tokenizer, prompt, generation, ONNX, and cache-contract words.

### ONNX runtime metadata

ONNX input/output names and shapes are usually safe to print if they do not contain raw template tokens:

```bash
ruby skills/safe-model-artifact-inspection/scripts/onnx_metadata.rb PATH_TO_ONNX
```

Summarize as input names, output names, tensor ranks, dtypes, and shapes. For cache tensors, report layer count, key/value naming pattern, rank, and empty-cache shape.

## Script Reference

| Need | Script | Use |
|---|---|---|
| Generate safe model contract report | `scripts/model_artifact_report.rb` | `ruby scripts/model_artifact_report.rb MODEL_DIR [--format markdown\|json\|both] [--no-probes] [--probe-timeout SECONDS]` |
| Inspect model/tokenizer JSON safely | `scripts/safe_model_json.rb` | `ruby scripts/safe_model_json.rb PATH [KEY ...]` |
| Search task docs, prompts, source, or session exports safely | `scripts/safe_text_search.rb` | `ruby scripts/safe_text_search.rb PATH [TERM ...]` |
| Inspect ONNX input/output metadata | `scripts/onnx_metadata.rb` | `ruby scripts/onnx_metadata.rb PATH_TO_ONNX` |

## What To Extract

For generation models:

- discovered `config.json`, `generation_config.json`, `tokenizer_config.json`, `special_tokens_map.json`, `tokenizer.json`, ONNX file, and external ONNX data files
- architecture and model type
- tokenizer family
- context length and vocabulary size
- BOS, EOS, PAD, and UNK token IDs
- safe byte values for start/end/stop tokens
- chat-template structure using placeholders, role handling, assistant prefix, start/end token IDs, byte arrays, and special-token flags
- required assistant generation prefix
- whether manual chat template construction is required
- whether role labels are plain text
- decode guidance, stop token IDs, and special-token stripping risk
- ONNX input/output names, dtypes, shapes, counts, and metadata provenance
- cache layer count, KV heads, head dimension, empty cache shape, and `present.*` to `past_key_values.*` mapping
- whether first pass requires empty cache tensors
- bounded runtime probe results for logits shape, next-token slice, first pass, second pass, attention mask shape behavior, and position ID behavior when available
- sampling defaults, max token limits, and stop criteria
- implementation risks, tokenizer/model mismatch clues, missing external weight files, metadata gaps, ambiguous fields, probe failures, and known output-quality limitations

For embedding models:

- architecture and output dimension
- tokenizer family
- max sequence length
- BOS, EOS, PAD, and UNK token IDs
- input/output tensor names and shapes
- pooling or normalization expectations
- confusion risks compared with the generation model

## Reporting Format

```markdown
## Model Details

- Architecture:
- Tokenizer:
- Context length:
- Vocab size:
- Token IDs:
- Safe token bytes:
- Template structure:
- ONNX inputs:
- ONNX outputs:
- Cache contract:
- Generation settings:

## Implementation Notes

- [facts needed by the service]

## Conflicts Or Risks

- [mismatches, missing files, unsupported APIs, quality caveats]
```

If preparing a downstream task/spec, avoid citing local artifact files unless paths are required. Put the relevant technical facts directly in the task.

## Common Mistakes

| Mistake | Safer Move |
|---|---|
| Raw-reading tokenizer configs or task docs | Use escaped JSON/text extraction |
| Printing a chat template verbatim | Describe it with placeholders and token IDs |
| Copying raw tool output with control strings | Re-run with escaping and summarize only safe output |
| Assuming role labels are special tokens | Verify token IDs and template structure separately |
| Assuming first causal-LM pass can omit cache | Inspect ONNX inputs and test for required empty cache tensors |
| Mixing embedding and generation token IDs | Report each model's tokenizer facts separately |
| Mentioning a known-good commit in a task spec | Put the relevant technical facts directly in the task |

## Failure Signals

Stop and switch to escaped inspection if:

- the model stops after a tiny or missing answer
- the last visible content is template/control-token discussion
- raw delimiter-like byte sequences appear in tool output
- a thinking-mode agent stalls while discussing tokenizer templates
- a task doc causes the agent to stop before producing a report
