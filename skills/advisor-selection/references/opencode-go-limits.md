# OpenCode Go metering

Applies when any candidate runs through an OpenCode Go / Go Plus subscription. Verify the current numbers on
<https://opencode.ai/v2/docs/console/go>; the *shape* below is what changes a decision, and it has survived several
price revisions.

## One pool, per-model burn rates

The subscription is a single shared allowance, not a separate budget per model. The per-model "Monthly limit" shown in
the docs is the amount of that one model which would exhaust the whole pool.

```text
pool    = $12 / 5h, $30 / week, $60 / month   (Go; Go Plus scales the pool ~4x)
factor  = pool_monthly / model_monthly_limit
charged = raw_cost x factor          # raw_cost = tokens priced at the model's listed rates
```

Consequences worth stating plainly to a user:

- `$15 x 4 = $60 x 1 = $80 x 0.75` — every limit is the same pool seen from a different model.
- Limits are not additive: `$80 + $15` is not `$95`.
- Exhausting the pool blocks **every** paid model, including ones with untouched usage. Free models keep working;
  `Extra usage` / `Use balance` can fall back to pay-as-you-go.
- A $15 bucket therefore means "one bad day locks the plan", not "a small side budget".

## Reading the console

- The "Usage by Model" table shows **raw** cost; the quota bars show **weighted** cost (`raw x factor`).
- The single percentage per window is a sum of per-model percentages, not a dollar-weighted ratio, so small-quota
  models dominate it ([#39822](https://github.com/anomalyco/opencode/issues/39822)).
- The bars are workspace-wide; per-key cost views can be scoped to one key and will not reconcile
  ([#42985](https://github.com/anomalyco/opencode/issues/42985)).
- A percentage on the 5h or weekly bar is a small fraction of the month; only the monthly bar is comparable to a
  month-to-date cost table.

## Cost traps that matter for an advisor

- **Long-context tiers.** Some models double or quintuple prices above a context threshold; an advisor that re-reads a
  long transcript crosses it routinely. Prefer single-tier prices for this role.
- **Peak hours.** DeepSeek doubles 01:00-04:00 and 06:00-10:00 UTC, Monday-Friday.
- **Cache writes.** Where listed, they are the largest line item for an agent that re-reads context; where absent, the
  provider does not charge them, which quietly favors that model.

## Evidence

- [#42985](https://github.com/anomalyco/opencode/issues/42985) — staff confirmation of the shared pool, per-tier caps,
  a $3.47 / 5.8% full lockout, and a resolved 11x report that was view-scope, not metering.
- [#39822](https://github.com/anomalyco/opencode/issues/39822) — "Total %" is a sum of per-model percentages; the
  per-model breakdown was later removed from the UI.
- r/opencodeCLI "Official opencode go limits published" and r/opencode "$15 models are not separate limits" — same
  finding from users, quoted inside the issues above.
