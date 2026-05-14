---
name: stateful-lifecycle-audit
description: Use when creating, modifying, or reviewing code with singleton state, memoization, lazy loading, caches, registries, mutexes, unload/reset paths, or long-lived external resources
---

# Stateful Lifecycle Audit

## Overview

Stateful code is not correct because it has a familiar shape. Trace ownership and execution. The guard, resource, reset, and tests must all agree about the same state.

## When to Use

Use for code involving:
- singleton instances, class variables, class instance variables, or module globals
- memoization, caches, registries, warmup, lazy loading, unload, or reset paths
- mutexes, thread-local/request-local state, background lifecycle jobs, or long-lived resources
- expensive constructors such as model/session/client/tokenizer/database connection loaders

Do not use for stateless pure functions with no persistent resource or lifecycle behavior.

## Audit Steps

1. Identify every persistent state variable and classify its owner: class object/singleton class, singleton instance, ordinary instance, module/global, thread-local, or request-local.
2. Trace every read and write of each variable. Do not infer correctness from names like `ready`, `loaded`, `cache`, or from the presence of a mutex.
3. Verify guards and resources share the same owner, or the guard derives directly from the resource state.
4. Trace two sequential public calls: first call loads/creates the resource; second call must reuse it without rerunning expensive constructors.
5. Trace reset/unload paths: they must clear resource references and readiness/registry state together.
6. Require behavioral coverage for lifecycle invariants. Structural tests like "has a mutex" are not enough.

## Review Heuristics

| Risk | What to Check |
|---|---|
| Split ownership | A guard is read from one object and written to another, e.g. instance `@ready` vs class `@ready` |
| Pattern-only approval | Reviewer says "singleton/mutex exists" without tracing two public calls |
| Stale state | Reset clears `@instance` but leaves ready flags, registry state, or external resources inconsistent |
| Duplicate loads | Expensive constructors can run twice in one process/request lifecycle |
| Test masking | Specs reset state so aggressively that production reuse is never exercised |

## Required Evidence

Implementation/build work should include or preserve a behavioral test proving repeated public calls reuse the resource when reuse is required.

Review work should report the ownership trace for stateful services, or explicitly state that no persistent lifecycle state is present.

## Common Mistakes

- Treating class instance variables and instance variables as the same state.
- Checking a readiness flag instead of the actual resource references.
- Testing mutex existence but not the lifecycle behavior protected by the mutex.
- Resetting only one side of coupled state, such as clearing an instance without clearing loaded/ready metadata.
