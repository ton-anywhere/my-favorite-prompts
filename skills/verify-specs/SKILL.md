---
name: verify-specs
description: Use before creating, modifying, reviewing, or refactoring spec test files. Better Specs compliance, especially around one behavior per example, meaningful example names, describe/context structure, behavior-over-implementation assertions, `expect` syntax, or spec readability and maintainability problems.
---

# Verify Specs

## Overview

Review RSpec code against Better Specs and return concrete, file-specific findings. Focus on issues that make specs misleading, brittle, hard to debug, or unnecessarily hard to read.

## Review Mode

Treat this as a spec review, not a generic style pass. Prioritize problems that affect failure isolation, behavior coverage, and maintainability before reporting cosmetic cleanup.

## Workflow

0. **Mandatory First Pass** — Run both mechanical audits before touching anything else:
   - [Condition Word Audit](#mandatory-first-pass---condition-word-audit)
   - [Expectation Count Audit](#mandatory-expectation-count-audit)

   Skip either audit = incomplete review.
1. **BDD Phase Pass** — Classify each example into Given, When, and Then before proposing rewrites. Skip this = incomplete review.
2. Identify the spec type: isolated unit spec, request spec, integration/system spec, or another slow end-to-end flow.
3. Apply the high-signal checklist using the audit results from step 0 and the BDD phase pass as starting evidence.
4. Apply the secondary checklist only when it improves clarity without forcing churn.
5. Report findings as narrow rewrites tied to the current file.

## Mandatory First Pass — Condition Word Audit

Before applying any other checklist items, run the audit script against the specific spec file under review:

```bash
ruby skills/verify-specs/scripts/condition_word_audit.rb spec/path/example_spec.rb
```

For whole-project reviews only, run:

```bash
ruby skills/verify-specs/scripts/condition_word_audit.rb --all
```

The script flags candidate `it`/`specify` descriptions containing `when`, `with`, `without`, `for`, or `and`.

**Procedure:**
1. Run the script for the predetermined spec file, or `--all` only when reviewing the whole project.
2. For each candidate, classify whether the word introduces an input/state/branch condition (flag → move to context), signals a split behavior (`and` → consider separate examples), or is intrinsic to the expected behavior (allow).
3. Use the candidates as starting evidence for the review.
4. Continue the full scan for all other Better Specs issues. The script is only an aid; it does not replace reviewing expectations, setup/action/assertion separation, behavior-vs-implementation, coverage, or structure.

**Failure mode to prevent:** Spotting obvious offenders at the top/bottom of a file and stopping there instead of auditing all examples systematically. A missed condition-word candidate means you did not complete Step 0 of your workflow.

## Mandatory Expectation Count Audit

Before applying any other checklist items, run the expectation count audit against the specific spec file under review:

```bash
ruby skills/verify-specs/scripts/expectation_count_audit.rb spec/path/example_spec.rb
```

For whole-project reviews only, run:

```bash
ruby skills/verify-specs/scripts/expectation_count_audit.rb --all
```

The script flags `it`/`specify` blocks containing more than one `expect(...)`.

**Procedure:**
1. Run the script for the predetermined spec file, or `--all` only when reviewing the whole project.
2. For each flagged example, classify whether the expectations describe separate behaviors or one flow outcome.
3. In isolated unit/service specs, split separate behaviors into separate examples.
4. Allow multiple expectations only for non-isolated or expensive integration-style flows where the checks verify one outcome.
5. If allowing a flagged example, state why it is a single behavior.

**Failure mode to prevent:** Running only the condition-word audit and missing body-level multi-expectation examples. Running the audit script alone is not a verify-specs review.

## Mandatory BDD Phase Rule

For isolated RSpec examples, enforce a strict Given/When/Then split:

- **Given:** setup, stubs, doubles, factories, and preconditions belong in `let`, `let!`, or `before`.
- **When:** the action under test belongs in a named `let(:result)` or a `before` block.
- **Then:** each `it` block contains only the expectation for that behavior.

Hard rules:

- `allow(...)` is setup. Do not leave `allow` inside an `it` block. Move it to the nearest relevant `before`.
- `let(:result) { ... }` or another clearly named result/action helper is the preferred place for the action under test.
- Use `let!` or `before { result }` when the action must run before a `have_received` expectation.
- An isolated `it` block should have a single expectation. Split examples when expectations describe different behaviors.
- Do not add a return-value expectation just to force a lazy `let(:result)` to run. If the behavior under test is a spy expectation, make the action eager with `let!` or `before { result }`.
- Do not "fix" inline setup by moving setup to `before` while leaving the action in the `it` block. That still mixes When and Then.

Exception:

- Error assertions such as `expect { action }.to raise_error(...)` keep the action inside the expectation because the action is inseparable from the Then clause.

## High-Signal Checklist

- Check that each isolated example tests one behavior. Flag multiple expectations in a single unit-style `it` block when they represent separate behaviors.
- Allow exceptions for non-isolated specs with expensive setup, such as database-heavy flows, external service integration, or end-to-end behavior. In those cases, flag only true multi-behavior examples, not multiple checks for the same flow outcome.
- Require meaningful example names. Flag vague names like `works`, `returns the value`, or descriptions that document implementation steps instead of behavior.
- Treat condition words in `it` descriptions as structure smells. `when`, `with`, `without`, or `for` inside an example name usually means the condition belongs in a `context`, leaving the `it` description as the Then/expected behavior. Apply `for` with judgment: flag it when it introduces input, state, or branch conditions, not when it is intrinsic to the expected behavior.
- Treat `and` in `it` descriptions as a split-example smell. It often signals two expected behaviors or multiple expectations that should become separate `it` blocks, especially in isolated specs.
- Prefer behavior over implementation. Flag tests that pin private methods, callback order, framework internals, SQL shape, or incidental collaborator calls unless those interactions are the public contract.
- Avoid global stubs for nondeterminism (`Kernel.rand`, `Time.now`, process-wide constants, global config) unless the production code already exposes that dependency globally. Prefer deterministic inputs, dependency injection, or observable behavior at the service boundary.
- Check structure. Use `describe` for the unit under test and `context` for conditions. Prefer method-style names like `.call` and `#valid?`. Nested `context` blocks are acceptable when they separate distinct Given/When conditions and keep example names focused.
- Treat `and` in `context` descriptions as a nesting smell. It often means the context is combining two conditions that may deserve nested contexts.
- Keep descriptions short. If an example name becomes long or conditional, move the condition into a `context`.
- Check that each `it` block contains only assertions (Then), not setup (Given) or actions (When). Flag inline `allow`, factories, doubles, assignments, and method calls like `service.do_something(...)` inside the `it` body. Move setup to `before`/`let`, move the action to `let(:result)`/`before`, and leave one expectation in the example. Exception: error-raising tests using `expect { ... }.to raise_error` are inseparable — action is part of the expectation.

## Secondary Checklist

- Prefer `expect` syntax over `should`. Use `is_expected.to` for one-line implicit-subject expectations.
- Prefer context names that begin with `when`, `with`, or `without` when they describe setup conditions.
- Prefer `let` over instance variables in `before` blocks for named reusable setup. Use `let!` only when eager setup is required.
- Prefer factories over fixtures or oversized inline setup when the project already uses factories.
- Create only the data needed for the current behavior.
- Check valid, invalid, and edge paths when the production code branches.
- Consider shared examples when the same behavior is duplicated across files or contexts.

## Reporting Findings

- Report only issues that materially improve clarity, failure isolation, or maintainability.
- For each finding, name the violated guideline, explain the risk in one sentence, and propose a narrow rewrite.
- If a spec intentionally trades purity for integration-test cost, say so explicitly instead of forcing the isolated-unit rule.
- If the spec is already in good shape, say that directly.

## Rewrite Patterns

- Split a multi-assertion isolated example into multiple `it` blocks.
- Replace vague example names with user-visible behavior.
- Move setup conditions from `it` descriptions into `context` blocks.
- Split combined context conditions into nested `context` blocks when that makes the Given/When structure clearer.
- Rewrite `it "returns empty array for nil vector"` as `context "with nil vector input"` + `it "returns an empty array"`.
- Replace implementation-level expectations with observable outputs, state changes, responses, jobs, side effects, or raised errors.
- Convert `should` syntax to `expect` or `is_expected`.
- Split mixed setup/action/assertion examples by moving preconditions into `before`/`let`, the action into `let(:result)` or `before`, and leaving only one assertion in the `it` block.

### Spy Expectation Pattern

Bad:

```ruby
it "does not call KeywordSearch" do
  allow(Rag::Search::KeywordSearch).to receive(:call)
  described_class.call(query: "", locale: :en)
  expect(Rag::Search::KeywordSearch).not_to have_received(:call)
end
```

Good:

```ruby
before { allow(Rag::Search::KeywordSearch).to receive(:call) }

let!(:result) { described_class.call(query: "", locale: :en) }

it "does not call KeywordSearch" do
  expect(Rag::Search::KeywordSearch).not_to have_received(:call)
end
```

Do not add `expect(result).to eq(...)` to this example unless the return value is the behavior under review. That would create a second Then.

## Reference

Read `references/better-specs-review-reference.md` when you need the detailed checklist, Better Specs examples, or the exception cases around slow non-isolated specs.
