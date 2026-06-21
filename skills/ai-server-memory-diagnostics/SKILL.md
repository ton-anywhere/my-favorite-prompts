---
name: ai-server-memory-diagnostics
description: Use when investigating swap, memory pressure, compressor usage, llama.cpp memory, Metal/unified memory, or model-server RAM issues on the Mac Studio ai-server.
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# AI Server Memory Diagnostics

## Purpose

Diagnose memory pressure on the Mac Studio `ai-server` without trusting misleading single-number summaries. For llama.cpp on macOS, `ps` RSS often understates the real cost; use `vmmap` physical footprint and swapped writable regions.

## Quick Workflow

1. Confirm the remote host and global memory state:

```bash
ssh ai-server vm_stat
ssh ai-server sysctl vm.swapusage
ssh ai-server memory_pressure
```

Key fields:
- `vm.swapusage`: total, used, free encrypted swap.
- `Pages stored in compressor`: logical pages compressed.
- `Pages occupied by compressor`: RAM consumed by compressed pages.
- `Swapins` / `Swapouts`: whether swap is active over time.

Convert 16 KiB pages to GiB with:

```text
GiB = pages * 16384 / 1024 / 1024 / 1024
```

2. Find the model processes:

```bash
ssh ai-server "ps aux | grep -E 'llama|mlx|omlx' | grep -v grep"
ssh ai-server "ps aux | sort -nrk 6 | head -30"
```

Treat `ps` RSS as a rough clue only. On macOS unified memory, llama.cpp / Metal allocations and swapped anonymous memory may not appear as expected in RSS.

3. Confirm listeners, health, and tmux panes before assuming a model is alive:

```bash
ssh ai-server "lsof -nP -iTCP:8080 -sTCP:LISTEN"
ssh ai-server "lsof -nP -iTCP:8081 -sTCP:LISTEN"
ssh ai-server "curl -sS --max-time 2 http://127.0.0.1:8080/health"
ssh ai-server "curl -sS --max-time 2 http://127.0.0.1:8081/health"
ssh ai-server "zsh -lc 'tmux ls'"
ssh ai-server "zsh -lc 'tmux list-panes -a -F \"#{session_name}:#{window_index}.#{pane_index} #{pane_current_command} #{pane_pid}\"'"
ssh ai-server "zsh -lc 'tmux capture-pane -pt llama-server-coder:0.0 -S -200'"
```

Use `zsh -lc` for tmux commands because non-login SSH shells may not have tmux on `PATH`. If a port is not listening but a tmux session remains, capture the pane tail; crash lines such as `killed` often survive in scrollback.

4. Inspect each suspicious PID with `vmmap`:

```bash
ssh ai-server "vmmap -summary <pid> | tail -80"
```

Read these lines first:
- `Physical footprint`
- `Physical footprint (peak)`
- `Writable regions`
- `MALLOC_LARGE`
- `shared memory`
- `mapped file`
- `TOTAL`

The most important columns are:
- `RESIDENT`: currently in RAM.
- `DIRTY`: private writable memory currently resident.
- `SWAPPED`: private writable memory moved to swap.
- `VIRTUAL`: address space, not direct RAM usage.

5. Attribute the pressure to launch profiles.

Compare the active command line to `AGENTS.md` model profiles. High-risk flags include:
- `--ctx-size` with very large contexts.
- `--parallel`, especially with `--no-kv-unified`.
- `--cache-ram`.
- large `--batch-size` / `--ubatch-size`.
- multiple co-resident models.

## Interpretation Rules

- Large swap plus large `MALLOC_LARGE swapped` usually means model heap, KV cache, prompt cache, or batching buffers have been pushed out.
- Large `shared memory swapped` can point at shared model/runtime buffers rather than ordinary app memory.
- Large `mapped file` is often model weights or file-backed mappings; it is less alarming than dirty writable swap.
- `Physical footprint` is a better process-level signal than RSS for model servers on macOS.
- Near-full swap plus high `memory_pressure` free percentage usually means the system had earlier pressure and has not reclaimed swap; still inspect `vmmap` to find retained swapped writable regions.
- A crashed model server can leave a tmux shell alive. Verify the port and health endpoint, not just the tmux session name.
- Prompt-cache/checkpoint saves can be the immediate crash trigger. In tmux tails, look for `prompt_save`, `created context checkpoint`, state sizes in MiB/GiB, then `killed`.
- Compressor usage is not free. If many pages are stored in compressor and swap is nearly full, the machine is under real pressure.
- System daemons with tiny RSS are rarely the cause when model PIDs show tens of GiB in `vmmap`.

## Output Shape

When reporting findings, include:

```text
Global:
- swap used / total
- compressor pages stored and occupied, converted to GiB if useful
- current memory pressure/free percentage

Per model PID:
- command summary and port
- listener and /health status
- physical footprint and peak
- swapped writable total
- largest swapped regions, especially MALLOC_LARGE/shared memory

Tmux / crash evidence:
- relevant session and pane
- last crash line, if any
- prompt-cache or checkpoint sizes near the crash

Conclusion:
- likely memory source
- safest restart or relaunch profile change
```

## Common Mistakes

| Mistake | Better move |
|---|---|
| Trusting `ps` RSS alone | Use `vmmap -summary <pid>` |
| Treating all virtual memory as RAM | Focus on footprint, resident, dirty, and swapped columns |
| Blaming small macOS services first | Inspect model PIDs before system daemons |
| Ignoring compressor stats | Compressor plus near-full swap means real pressure |
| Treating full swap as current pressure by itself | Compare with `memory_pressure`; full swap can be residue from an earlier spike |
| Trusting a tmux session name | Check listener and `/health`; capture pane tail for killed processes |
| Looking only at total swap | Attribute swap to process regions with `vmmap` |
| Forgetting launch flags | Tie memory pressure back to context, parallelism, cache, and co-resident models |
