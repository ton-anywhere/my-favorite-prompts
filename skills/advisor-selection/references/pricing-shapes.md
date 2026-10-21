# Pricing shapes and how to normalize them

Use when candidates come from different plans or providers and their headline numbers are not comparable.

## The two figures that decide

At your measured advisor volume (turns per month, tokens per turn):

1. **Cost per advisor turn** on the route you would actually call.
2. **Share of the account's allowance per month** — the fraction of a pool, quota, or balance the role consumes.

Compare with (2); keep (1) for "is this worth optimizing at all". A route that consumes a few percent of an allowance is not worth a capability downgrade; one that consumes a large fraction is a structural problem no model choice fixes.

## Plan types

| Shape | Cost is expressed as | Normalize by | Main traps |
| --- | --- | --- | --- |
| **Weighted pool** (OpenCode Go and similar) | Per-model limits that look like budgets | `factor = pool / limit`; charged = list cost x factor | Limits are divisors, not additive budgets; one pool, global lockout. Details in [opencode-go-limits.md](opencode-go-limits.md). |
| **Plain per-token** (first-party API) | $/M in, out, cache read/write | List price x the route's real token mix | Cache tiers, long-context multipliers, whether cache writes are charged at all. |
| **Aggregator** (OpenRouter and similar) | Per-model $/M, routed to a provider | List price x token mix x cache-hit ratio, plus fee layers | Cache support depends on the routed provider; routing changes price under the same model id; credit-purchase and bring-your-own-key fees are percentages on top; some routes bill cache reads as input. |
| **Request quota** | Requests per window | Advisor consumes ~1 request per turn plus retries; watch per-request surcharges | Long context, tool calls, or reasoning may bill as extra requests; the window, not the month, is the binding limit. |
| **Credit bundle** | Prepaid balance | Balance drained per turn; convert to share of monthly top-up | Balance can silently become pay-as-you-go after exhaustion. |
| **Free / contributor** | No cash price | — | The price is your data or a rate limit. That is a policy decision, not a cost one; advisors see the whole transcript. |

## Same model, different route

Treat model + provider + caching as one priced unit. Before trusting a new route, measure:

- **Cache-hit ratio.** An advisor re-reads a growing transcript; a route that misses cache can cost many times the cached case.
- **Context-tier or long-context multipliers** the route applies above a threshold.
- **Time-of-day pricing** where the provider has peak/off-peak rates.
- **Fee layer** on the account (credit purchase, BYOK surcharge, routing premium).
- **Retries and failures.** A flaky route turns one advisor turn into several billed calls.

## Placing the advisor across accounts

Splitting driver and advisor across providers is often cheaper than optimizing a single plan, and it decorrelates failure modes:

- Driver on a pool-metered subscription, advisor on pay-as-you-go: the advisor cannot exhaust the pool, and pool exhaustion does not silence the advisor mid-session.
- Driver on per-token, advisor on a subscription with headroom: the advisor stops adding to the variable bill.
- Two different subscriptions: acceptable, but each has its own lockout window, so an advisor on the same plan as the driver can be blocked exactly when the review matters most.

Verify with one measured day per route: predicted $/turn against what the console actually billed, and the share of allowance consumed. Predicted-vs-billed divergence is normal on opaque meters; trust the bill.
