# llama.cpp Changelog Relevance Guide

Use this guide to filter the changelogs between the current version and the latest release. The goal is to highlight only what is relevant to the user's specific environment and models.

## User Environment Context
- **Hardware:** Mac Studio M3 Ultra (Apple Silicon, Metal, Unified Memory)
- **Key Models:** Qwen3.6 (Reasoning), LFM2.5 (Reasoning), Gemma 4 (Coder), DiffusionGemma.

## Priority Filtering Rules

### 1. High Priority (Highlight these)
These changes directly impact the performance, stability, or features of the user's models.
- **Metal/Apple Silicon:** Any mentions of "Metal", "Apple Silicon", "Unified Memory", or "MLX" (if applicable).
- **Reasoning & Loops:** Fixes or improvements to "reasoning loops", "StepFun parser", or "thinking" modes.
- **Attention Mechanisms:** "Flash Attention", "Flash Attention 2", or "Paged Attention" (specifically for Apple Silicon).
- **Architecture Support:** Explicit support for "Qwen", "Gemma 4", or "Liquid AI / LFM".
- **Context Window:** Improvements to "KV Cache", "Context Window", "Prompt Cache", or "Long Context" handling.

### 2. Medium Priority (Mention briefly)
These are important for general maintenance but usually don't offer a "game-changing" experience for the user's current workflow.
- **Dependency Updates:** Updates to `cpp-httplib`, `json`, or other standard libraries.
- **General Bugfixes:** Minor bug fixes that don't affect the core reasoning or coding models.
- **Quantization:** Improvements to `Q8_0`, `Q4_K_M`, etc.

### 3. Low Priority / Noise (Ignore these)
Do not highlight these changes unless specifically asked, as they do not apply to the user's hardware.
- **NVIDIA/CUDA:** Any mention of "CUDA", "cuBLAS", "Triton", "FP8 CUDA".
- **AMD/ROCm:** Any mention of "ROCm", "HIP", "Radeon".
- **Mobile/Embedded:** "Hexagon", "ARM Neon" (unless specifically for Apple Silicon), "Qualcomm".
- **Desktop CPU:** "AVX-512", "AMX", "AVX2" (these are for Intel/AMD CPUs).
- **WebGPU:** Unless the user specifically mentions wanting to run in a browser.
