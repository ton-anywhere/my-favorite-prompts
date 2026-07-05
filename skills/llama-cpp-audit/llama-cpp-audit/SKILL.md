---
name: llama-cpp-audit
description: Audits the current llama.cpp version on the server, compares it with the latest release, and highlights relevant changelogs for models defined in MODELS.md. Use this when the user wants to know if they should update llama.cpp or to understand the differences between their current version and the latest one.
---

# llama-cpp-audit

This skill automates the process of determining if your `llama.cpp` installation is up-to-date and what improvements you might be missing, specifically tailored to the models you are currently running.

## Overview

Use this skill to get a data-driven recommendation on whether to update your `llama.cpp` installation. It compares your active server version against the latest official releases and filters the changelogs to highlight what actually matters for your specific models (e.g., Qwen3.6, LFM2.5, Gemma 4).

## Workflow

1. **Identify Current Version**:
   - The agent will check the running processes on the `ai-server` to find the active `llama-server` binary.
   - It will then execute that binary with the `--version` flag to get the exact build number and git hash.

2. **Identify Latest Version**:
   - The agent will perform a web search to find the most recent release tag from the official `ggml-org/llama.cpp` GitHub repository.

3. **Analyze Changelogs**:
   - The agent will identify all releases between the current version and the latest version.
   - It will summarize the changelogs for these versions.

4. **Relevancy Filtering (Tailored to your Models)**:
   - The agent will read the `MODELS.md` file in the server's workspace.
   - It will cross-reference the changelogs with the models listed in `MODELS.md` (e.g., Qwen3.6, LFM2.5, DiffusionGemma, Gemma 4).
   - It will specifically highlight changes involving:
     - Performance optimizations (especially for Apple Silicon/Metal).
     - Support for new architectures or special tokens.
     - Stability fixes for reasoning loops or large context windows.

5. **Final Recommendation**:
   - The agent will provide a summary and a clear "Update" or "Wait" recommendation based on the relevance of the changes to your specific workload.

## Examples

**User**: "What's my current llama.cpp version and should I update?"
**Agent**: 
- Finds version 9850.
- Finds latest version b9870.
- Lists changelogs for b9851 through b9870.
- Reads `MODELS.md` and notes that you run Qwen3.6 and LFM2.5.
- Highlights the StepFun reasoning loop fix in b9870.
- **Recommendation**: "You are on 9850. The latest is b9870. The most relevant change is a fix for long reasoning loops in the StepFun parser. If your current reasoning models are working fine, you can wait. If they are getting stuck in loops, update is recommended."
