# Better Specs Review Reference

Use this file when the review needs the detailed Better Specs checklist instead of only the workflow in `SKILL.md`.

## Highest-Priority Rules

### One behavior per isolated example

- Prefer one expectation per isolated unit example.
- Treat multiple expectations in one isolated example as a smell because they often hide multiple behaviors.
- Exception: Better Specs explicitly allows multiple related expectations in slow non-isolated specs when repeating setup would be expensive. Request specs, DB-heavy integration specs, external service flows, and end-to-end specs may reasonably check more than one observable result from the same scenario.

### Meaningful example names

- Prefer names that read like documentation.
- Flag vague names such as `works`, `behaves correctly`, `returns data`, or `does the thing`.
- Prefer behavior names over implementation names. Good names describe what changes, what is returned, what is rendered, or what error is raised.

### Behavior over implementation

- Prefer public behavior and observable outcomes.
- Flag tests that are mostly about private methods, callbacks in a specific order, framework plumbing, SQL shape, or internal helper calls unless that interaction is the contract.

## Structure Rules

### Describe the right unit

- Prefer method-style `describe` names such as `.call`, `#valid?`, or `GET /path`.
- Avoid vague describe labels that hide what is under test.

### Use `context` for conditions

- Use `context` for setup conditions and branches.
- Prefer context names that begin with `when`, `with`, or `without`.
- If an example name grows long because it includes setup conditions, move the condition into a `context`.

### Keep descriptions short

- Better Specs recommends short example descriptions.
- If an example name is long, split the setup into a `context` and leave the example focused on the behavior.

## Syntax and Setup Rules

### Prefer `expect` and `is_expected`

- Prefer `expect(...).to`.
- For one-line implicit-subject examples, prefer `it { is_expected.to ... }`.
- Flag `should` syntax unless the codebase is explicitly locked to an old convention.

### Prefer `let` to instance variables in setup

- Prefer `let` for reusable named setup.
- Use `let!` only when eager setup is required.
- Avoid instance variables in `before` blocks when `let` would make the setup clearer.

### Keep test data minimal

- Create only the data needed for the example.
- Prefer factories over fixtures when the project already uses FactoryBot or an equivalent factory library.
- Flag oversized setup that obscures the behavior under test.

## Coverage and Duplication

### Cover success, invalid, and edge paths

- If the code branches, check whether the spec covers valid, invalid, and edge cases.
- Missing unhappy-path coverage is often a more important finding than a style issue.

### Use shared examples carefully

- Repeated behavior across multiple files or contexts can justify shared examples.
- Do not force shared examples for one-off duplication that is still easy to read locally.

## Review Heuristics

- Prefer reporting a few strong findings over a long list of low-value nits.
- Do not enforce isolated-unit rules mechanically on request or system specs.
- If a current spec is a reasonable tradeoff for performance or clarity, say so.
- When proposing a rewrite, preserve the existing test intent and scope.

## Sources Used To Build This Skill

- Local reference: `docs/better_specs_reference.md`
- Official Better Specs: <https://www.betterspecs.org/>
