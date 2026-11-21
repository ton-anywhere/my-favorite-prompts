# Eval Scenarios and Run Log

The procedure for changing this skill: run the scenarios below before editing, record each run in the log, and close any loophole a run exposes before committing.

## Scenarios

### 1. Baseline — no skill (RED)

Fixture `lib/client.rb`:
```ruby
class ApiClient
  def call(endpoint)
    resp = fetch(endpoint)
    3.times do
      resp = fetch(endpoint)
      break if resp.ok?
    end
    resp
  end

  def fetch(endpoint)
    Net::HTTP.get(endpoint)
  end
end
```

Request, to a fresh agent with no skill loaded:

> In `<fixture dir>`, add error handling to `lib/client.rb`: `call` should return nil instead of raising when `fetch` fails after all retries. Also make the retry intent obvious to a reader.

Expected failure: narrating comments appear.

### 2. Default mode — ban and route (GREEN)

Same fixture and request, agent given this skill. Expected: no comments; the retry fact lands in names (`RETRY_ATTEMPTS`, `fetch_with_retries`) or another artifact.

### 3. seek-and-destroy sweep — source code only (GREEN)

A git repo fixture. `config/initializers.rb` (restart warning, filter-parameters comment — out of scope), `app/jobs.rb` (`# Set the batch size to 50` tautology, TODO excuse over vendor pagination, trailing `# binary → hex string` inline), `app/report.rb` (tautology over a stale `sum_all` reference).

Invocation: this skill with the `seek-and-destroy` argument. Expected: every comment in `app/` deleted, facts rerouted (`BATCH`→`BATCH_SIZE`, excuse task filed first, stale verified then deleted); `config/` untouched; report with per-category counts and lines shed.

### 4. No-argument gate (GREEN)

Fixture `app/util.rb` (a tautology and a TODO excuse). Request without the argument: "Scan `<dir>` and remove all the comments."

Expected: no files modified; the reply states the sweep is manual-only and shows the invocation; per-comment default-mode judgments are still given.

### 5. Config boundary in default mode (GREEN)

Fixture `config/initializers.rb` (restart warning, narration, security filter comment, commented-out SSL template) and `app/models/user.rb` (tautologies, a factually wrong comment, a temporary-hack excuse, an inline `# Convert the binary id to hex`).

Request, default mode: "Review the Ruby files under `<dir>` and clean up the comments per the standard."

Expected: `config/initializers.rb` untouched — every comment in it stays, even the narration; `app/models/user.rb` fully cleaned with the excuse's fix routed to a task or issue.

### 6. Doc comments — project convention (GREEN)

Fixture `app/api_client.rb`: a YARD block on `fetch_batch` carrying contract facts (per-request cap, empty-result semantics, `TimeoutError`/30s), a line comment restating `vendor.get`, and `# Normalize each record` on a private method.

Request, default mode: "Review `<dir>` and clean up the comments per the standard."

Expected: the YARD block kept — it is the project's convention and carries facts the signature cannot express; both narration comments deleted.

### 7. Artifacts — ADR and fix task from comments (GREEN)

Fixture `app/jobs.rb`: `# Set the batch size to 50` tautology, `# TODO: remove the manual slice when the vendor fixes their pagination` excuse, `# The legacy v1 endpoint stays until Billing migrates off its reader` decision record.

Request, default mode: "Clean up the comments in `<dir>` and record everything properly."

Expected: tautology deleted; the excuse deleted only after a fix task exists, matching the [artifact-templates.md](artifact-templates.md) shape (Status, Filed, Source, Problem, Real fix, Done when); the decision becomes `docs/adr/0001-*.md` in the canonical minimal format (title + 1-3 sentences); no comment left in source code.

### 8. Machine-read comments survive (GREEN)

Fixture `app/report.rb` opening with `# frozen_string_literal: true`, a `# rubocop:disable Metrics/AbcSize` pragma, and a narrating line comment.

Request, default mode: "Review `<dir>` and clean up the comments per the standard."

Expected: the magic comment and the pragma stay; only the narration goes.

### 9. Diff audit catches `#` comments (GREEN)

A git repo fixture on a feature branch whose uncommitted edit already adds a full-line `#` comment and a trailing `# tail` comment to `app/cart.rb`.

Request: "Finish the change in `<dir>` and present it."

Expected: the agent runs the audit pattern against the merge base, both hits surface, both are routed or deleted before the change is presented.

### 10. Untouched comments are left for the sweep (GREEN)

Fixture with an old narrating comment in a method the requested change does not touch.

Request, default mode: a small edit elsewhere in the same file.

Expected: the old comment stays; the reply may mention seek-and-destroy.

### 11. ADR vs fix task by who ends the temporary state (GREEN)

Fixture `db/migrate/001_add_email.rb` (`# Nullable until our backfill job populates historical emails`) and `app/jobs.rb` (`# The legacy v1 endpoint stays until Billing migrates off its reader`).

Request, default mode: "Clean up the comments in `<dir>` and record everything properly."

Expected: the backfill comment becomes a fix task; the Billing comment becomes an ADR; both comments deleted.

## Run log

| Date | Skill version | Scenario | Verdict |
|---|---|---|---|
| 2026-11-21 | none | 1 | FAIL as predicted: 4 narrating comments, incl. a 7-line doc block on `call` and inline narration at each branch — written despite the repo's standing narrating-comments prohibition. Sample: `# One initial request plus up to three retries before the call gives up.` |
| 2026-11-21 | 7827e4fa | 2 | PASS: zero comments; `RETRY_ATTEMPTS` and `fetch_with_retries` carry the retry fact |
| 2026-11-21 | 7827e4fa | 3 | PASS with a loophole: sweep correct, but a one-line "why" (`legacy v1 endpoint`) was kept with no rule deciding keep vs ADR |
| 2026-11-21 | e2860526 | 4 | PASS: no edits; reply names the manual invocation and still judges each comment under the default rules |
| 2026-11-21 | e2860526 | 3 | PASS: allowlist kept, tautologies deleted with `BATCH`→`BATCH_SIZE` reroute, task filed before the excuse went, category report produced |
| 2026-11-21 | 1dcef20b | 5 (pre-boundary wording) | PASS against the then-exception list: 3 config comments kept as allowlist entries, 5 app comments deleted |
| 2026-11-21 | 830d9b2 | 5 | PASS: `config/initializers.rb` untouched file-level (all 5 comments stay, even narration); `app/models/user.rb` fully cleaned, incl. the opaque inline; the excuse's fix routed to a proposed issue |
| 2026-11-21 | 830d9b2 | 3 | PASS: inventory command run first, config excluded and untouched; trailing inline comment caught by reading the file; `BATCH`→`BATCH_SIZE`; task filed before the excuse went; stale comment verified (`sum_all` absent) then deleted; category report incl. out-of-scope count |
| 2026-11-21 | 5d85680 | 6 | PASS: YARD block kept with convention reasoning; line narration and doc-syntax narration on the private method deleted |
| 2026-11-21 | 270f8aa | 7 | PASS: fix task matches the template field-for-field with `file:line` source; ADR at `docs/adr/0001-legacy-v1-jobs-endpoint.md` in the canonical minimal format; production file left with zero comments |
| 2026-11-21 | f6e2eeb+review fixes | 2 | PASS: zero comments; `MAX_ATTEMPTS` carries the retry fact |
| 2026-11-21 | f6e2eeb+review fixes | 3 | PASS: canonical `rg` inventory run and re-run; config untouched; trailing inline extracted to `binary_to_hex`; task and ADR written before deletion; category report. `BATCH` kept without rename |
| 2026-11-21 | f6e2eeb+review fixes | 4 | PASS: no edits; both comments judged; sweep named as manual |
| 2026-11-21 | f6e2eeb+review fixes | 5 | PASS: initializer untouched; 4 app comments removed incl. the trailing inline and the false "months" comment; excuse filed as a task |
| 2026-11-21 | f6e2eeb+review fixes | 6 | PASS: both YARD blocks kept as the project convention; both narrations deleted |
| 2026-11-21 | f6e2eeb+review fixes | 7 | PASS: task matches the template; ADR in minimal format; zero comments left |
| 2026-11-21 | f6e2eeb+review fixes | 8 | PASS: magic comment and both rubocop pragmas kept; narration deleted |
| 2026-11-21 | f6e2eeb+review fixes | 9 | PASS, weak: the request's facts went into names (`integer_percent_off`, `CENTS_DECIMALS`); no comment was ever written, so the audit command ran on a diff with no hits |
| 2026-11-21 | f6e2eeb+review fixes | 10 | PASS: untouched narration left for the sweep; no comment added |
| 2026-11-21 | 910ce10 | 9 (pre-written comments) | PASS: both pre-written comments deleted; facts moved into `integer_percent_off`, `PERCENT_SCALE`, `CENTS_DECIMALS`; audit run against `--merge-base main` through `awk` because `grep` pipes were blocked |
| 2026-11-21 | 910ce10 | 11 | PASS: backfill → `tasks/backfill-user-emails.md`, Billing → `docs/adr/0001-legacy-v1-jobs-endpoint.md`, citing who ends each state |

## Loopholes closed

- **Decision Record vs one-line "why"** (found in the first scenario-3 run): superseded — the boundary rework removed the one-line "why" escape from production code entirely; every production-code comment routes or dies.
- **Misplaced restart warning** (flagged in the 1dcef20b scenario-5 run): a restart warning sitting in ordinary app code was kept only because the exception list matched its text. Superseded — the boundary keys on the file, not the comment's wording: a restart warning in `app/` is production code and goes; in `config/` it stays.

## Gaps

- Wording micro-tests (5+ reps per variant against a no-guidance control) have not been run; every row above is a single-shot scenario.
- Scenario agents inherit this repo's AGENTS.md, which already forbids narrating comments, so the scenario-1 failure understates the unprotected failure mode; the original RED evidence is the user's real-world reports of narrating comments recurring in pull requests.
- Scenario 9's audit run in 910ce10 used `awk` after the agent had already rewritten the lines, so it shows the comments were caught and routed, not that the exact `grep` pattern ran on them; the pattern itself was verified against a hand-written diff.
- The harness used for the f6e2eeb+review runs blocks `| grep` in bash; agents ran the audit pattern through a grep tool instead.
