---
name: verify-specs
description: Use when reviewing, refactoring, or writing RSpec test files and you need to verify Better Specs compliance, especially around one behavior per example, meaningful example names, describe/context structure, behavior-over-implementation assertions, `expect` syntax, or spec readability and maintainability problems.
---

# Verify Specs

## Overview

Review RSpec code against Better Specs and return concrete, file-specific findings. Focus on issues that make specs misleading, brittle, hard to debug, or unnecessarily hard to read.

## Review Mode

Treat this as a spec review, not a generic style pass. Prioritize problems that affect failure isolation, behavior coverage, and maintainability before reporting cosmetic cleanup.

## Workflow

1. Identify the spec type: isolated unit spec, request spec, integration/system spec, or another slow end-to-end flow.
2. Apply the high-signal checklist first.
3. Apply the secondary checklist only when it improves clarity without forcing churn.
4. Report findings as narrow rewrites tied to the current file.

## High-Signal Checklist

- Check that each isolated example tests one behavior. Flag multiple expectations in a single unit-style `it` block when they represent separate behaviors.
- Allow exceptions for non-isolated specs with expensive setup, such as database-heavy flows, external service integration, or end-to-end behavior. In those cases, flag only true multi-behavior examples, not multiple checks for the same flow outcome.
- Require meaningful example names. Flag vague names like `works`, `returns the value`, or descriptions that document implementation steps instead of behavior.
- Prefer behavior over implementation. Flag tests that pin private methods, callback order, framework internals, SQL shape, or incidental collaborator calls unless those interactions are the public contract.
- Check structure. Use `describe` for the unit under test and `context` for conditions. Prefer method-style names like `.call` and `#valid?`.
- Keep descriptions short. If an example name becomes long or conditional, move the condition into a `context`.

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
- Move setup conditions into `context` blocks.
- Replace implementation-level expectations with observable outputs, state changes, responses, jobs, side effects, or raised errors.
- Convert `should` syntax to `expect` or `is_expected`.

## Reference

Read `references/better-specs-review-reference.md` when you need the detailed checklist, Better Specs examples, or the exception cases around slow non-isolated specs.
