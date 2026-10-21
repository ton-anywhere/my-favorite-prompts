---
name: advisor-selection
description: Use when choosing, replacing, or reviewing the advisor model in an OMP/oh-my-pi session (the second model that reviews each completed turn), or when evaluating a driver+advisor pair, advisor failovers, or advisor cost on a metered plan.
disable-model-invocation: true
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Advisor Selection

## Purpose

Pick the model for the `advisor` role: a second model that reads each completed turn and can inject notes into the primary session. It is a judgment decision first and a cost decision last.

## Decision order

Apply in order. Stop at the first candidate that clears the bar.

1. **Capability floor — advisor ≥ driver.** Below the floor, the advisor can only rubber-stamp or nitpick. Failure is asymmetric: a missed review ships the bug, and a noisy one burns real turns in the primary loop (`continueSeverity: concern` means its notes keep the loop running).
2. **Independence — a different model family than the driver.** This is the point of a second opinion: decorrelating blind spots. It only pays once the candidate is above the floor, and it is worthless as a substitute for one.
3. **Cost on the right token.** The advisor re-reads the transcript every turn, so cache-read price and price cliffs (long-context tiers, peak/off-peak) dominate; output price is nearly irrelevant. Compute cost per turn from the measured shape — never compare headline $/M.
4. **Operational fit.** Context window ≥ the driver's (it sees the whole transcript); API shape the client speaks; enough format discipline to respect note budgets and not re-raise settled points. Latency only matters when `advisor.syncBacklog` is on, where the primary can wait at backlog.
5. **Privacy.** The advisor sees the entire session — exclude models whose terms allow training on prompts.

## Price is a constraint, not a criterion

Plans express cost in incompatible units: weighted pools (OpenCode Go), plain per-token bills (OpenRouter, first-party APIs), request quotas, credit bundles, free/contributor tiers. A number is only comparable after conversion to the same two figures, at your measured advisor volume:

- **$ per advisor turn** on the route you would actually call — model *plus* provider *plus* caching behavior
- **share of that account's allowance per month** — how much of a pool, quota, or balance the role consumes

Judge by the second figure. If the role consumes a small share of the allowance, price is a tie-breaker; if it consumes a large share, restructure the role or move the advisor to another account. Provider-specific heuristics ("avoid models below a limit", "take the cheapest $/M") are local to one pricing model and break when carried across providers — recompute per route, not per model.

The same model on a different route is a different price: cache support, provider routing, and account fees move per-turn cost by an order of magnitude. See [references/pricing-shapes.md](references/pricing-shapes.md) for how to normalize each plan type and what to measure before trusting a new route.

## Measure, don't assume

- **Per-turn shape:** `scripts/advisor_usage.py` aggregates `~/.omp/agent/sessions/**/__advisor.jsonl` by model. Assumed token counts are usually wrong about cache writes and output length.
- **Cost per turn:** `scripts/advisor_usage.py --costs prices.json` prices each candidate on the measured shape of the advisor you are replacing (`shape_from`), applying the route's `factor`. Prices are $/1M tokens; use `factor: 1` for per-token routes and the plan's multiplier for pooled subscriptions. Measured token counts already embed that route's cache-hit rate, so re-measure after moving providers.
- **Whether the advisor is useful:** act-on rate = notes acted on ÷ notes emitted, per model, over about a week. Below roughly half, the advisor is noise paid for twice — once in tokens, once in turns spent refuting it.

## Plan-specific metering

OpenCode Go normalizes per-model limits into one shared pool, so a listed limit is a divisor, not a budget. Read [references/opencode-go-limits.md](references/opencode-go-limits.md) before comparing candidates on that plan.
