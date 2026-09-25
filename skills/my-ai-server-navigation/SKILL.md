---
name: my-ai-server-navigation
description: Use when an agent outside the my-ai-server repository needs to find its authoritative operational, networking, model, or troubleshooting guidance.
---

# Navigating my-ai-server

On this machine, the checkout is `~/code/ton-anywhere/my-ai-server`. Start with `~/code/ton-anywhere/my-ai-server/AGENTS.md`.

Treat the `my-ai-server` repository as the source of truth for this AI server. Locate its checkout, then read root `AGENTS.md` first. It defines the working rules and points to the authoritative guide for each task. Use paths below relative to the repository root.

| Need | Read |
|---|---|
| Launch, stop, logs, or router services | `LLAMA-SERVER.md`; for plist work, also `launchd/AGENTS.md` and the relevant plist |
| Endpoint failures or client checks | `TROUBLESHOOTING.md` → “Model Endpoint Not Working” |
| Hostnames, routes, ports, or topology | `NETWORKING.md` |
| Persistent host settings, startup, or sleep | `MACHINE-CONFIGURATION.md` |
| Model provenance or chat templates | Follow “Model Documentation and Verification” in root `AGENTS.md`. Resolve the runtime path, then read `MODEL.md` in that model's canonical directory on `ai-server`. |
| Inference terms | `docs/inference-basics.md` |
| Prior incident evidence | Relevant entry in `post-mortems/`; read `post-mortems/AGENTS.md` first |
| Hermes VM work | `hermes/AGENTS.md`, then its linked runbooks |

Read the narrowest linked guide for the task. Treat runtime state as current evidence; repository docs describe the managed setup and verification steps.
