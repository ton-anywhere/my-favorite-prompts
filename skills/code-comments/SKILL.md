---
name: code-comments
description: "Use when writing or reviewing code and about to add a comment, when a diff or review adds comments, or when deciding whether an existing comment, doc comment, TODO, or workaround note should stay. Also use when the user invokes it with the search-n-destroy argument for a codebase-wide comment sweep."
argument-hint: "search-n-destroy"
license: MIT
metadata:
  author: Airton Ponce @ton-anywhere
---

# Code Comments Standard

Comments are forbidden in source code. Every fact has a better home than a comment: a name, an extracted method, a test, an issue, a document, or an ADR, and this skill's job is to route each fact there.

## Comments are forbidden — route the fact

Never write a comment in source code, and delete the ones on lines your change adds or edits — a comment you are about to write is a signal that names the artifact that is missing. Comments on lines the change does not touch are left for the search-n-destroy sweep. Route the fact; the table below is the decision procedure, not a suggestion:

| The comment you were about to write | Do this instead |
|---|---|
| Restates what the code visibly does | Nothing. The code is the statement. |
| Explains what a poorly named thing does | Rename the variable or function, or extract a method whose name carries it |
| Explains a deployment or environment value | Move the value into a config file, where its comment may stay |
| Excuses a hacky implementation ("workaround for…", "temporary") | File an issue or task for the real fix; leave the code uncommented |
| States an invariant or expected behavior | A test that asserts it |
| Records a non-obvious decision | An ADR |
| Documents how to use a module or API | A document — the module README or the project's usage guide |

Examples: `// One function per transition` → `transition(…)`; `// Conventional Commits type prefixes` → `CONVENTIONAL_COMMIT_TYPES`; `// T is unconstrained; an async callback runs writes outside this commit` → an ADR — the constraint cannot live in a name.

Worked before/after examples for every destination are in [references/routing-examples.md](references/routing-examples.md); templates for the documents a comment becomes — ADR, fix task, module doc — are in [references/artifact-templates.md](references/artifact-templates.md).

Rename only when the new name carries a fact a removed comment held. Never rename an exported symbol or type for a fact a doc already states.

## The ban's scope

- **Source code is in scope** — application code, libraries, migrations, tests, scripts: no comment may exist. If the fact is a number, an ordering, or an invariant, it belongs in a name, an assertion, or a test.
- **Config files are out of scope** — files whose job is configuration: initializers, environment configs, seeds, dependency manifests (Gemfile, Podfile), YAML, TOML, INI-family (`.ini`, `.cfg`, `.conf`, `.properties`), JSONC and comment-bearing JSON (`*.jsonc`, `tsconfig.json`, editor settings), Dockerfiles, env files, Makefiles, Terraform, CI and deploy manifests. Leave their comments as they are.
- **Machine-read comments are not prose** — shebangs, encoding and magic comments (`# frozen_string_literal:`), tool pragmas and directives (`# rubocop:`, `eslint-disable`, `// @ts-expect-error`, `# type: ignore`, `//go:build`), license headers, and `Usage:` headers on human-facing scripts. Leave them.
- **Doc comments are convention-gated** — see the next section.

## Doc comments

Doc comments (rustdoc, javadoc, godoc, docstrings, YARD) are a third kind: neither line comments nor configuration. They are undesirable by default — never introduce them to a project that does not use them.

Where the project's convention carries doc comments, adapt to it: an item of a kind that already carries them gets them in the project's format and tags, written with facts the signature cannot express — units, errors, side effects, invariants, examples — never a restatement of the signature. Such a doc comment is left alone in review; in a project with no such convention it is an ordinary comment and the ban applies.

## Contracts: own vs external

- **External contract** — another team's API, library behavior, CLI exit codes, wire format, database, protocol: record it at the boundary in the project's docs; the reader cannot check it from this repository.
- **Internal contract** — an interface or type whose every implementer and caller live in this repository: no per-member doc comments. A behavior callers depend on that the signature cannot express (a never-reject guarantee, a call-order rule, an ordering invariant) goes in the interface's doc, or in a test that pins it.
- Before deleting a doc comment, search for references to it (`docs/`, `tasks/`, `AGENTS.md`, `README`). A pointer such as "`Notifier` in `interfaces.ts` carries this constraint" goes stale silently.

## Quick Decision Test

Before touching a comment, ask in order:

1. **Is the file configuration?** → leave the comment alone.
2. **Is it machine-read** (pragma, shebang, license header)? → leave it alone.
3. **Is it a doc comment in a format the project already uses?** → keep it, per *Doc comments*.
4. **Otherwise** → the comment goes, and its fact routes per the table.

## Modes

- **Writing or reviewing code** (default): everything above applies, ending with the mandatory diff audit below.
- **search-n-destroy**: the full-codebase comment sweep. Runs only when the user invokes this skill by hand with the `search-n-destroy` argument. A plain request to "remove all comments" never starts it: answer from the rules above, and say the sweep is manual — the user invokes the skill with the `search-n-destroy` argument to run it. When the argument is present, read [references/search-n-destroy.md](references/search-n-destroy.md) and follow it. The scope above is the only exemption list; the mode file never overrides it.

## Audit your own diff

Before presenting a code change, inventory the comments it added. Skip this audit = incomplete change.

1. Run against the branch's base, including uncommitted edits (`git add -N <file>` first for new untracked files):

   ```bash
   git diff --merge-base origin/HEAD | grep -nE '^\+(\s*(#|//|/\*|\*)|.*\s(#|//)\s)'
   ```

   Replace `origin/HEAD` with the base branch when the remote has no default branch set.
2. Classify each hit with the Quick Decision Test. A hit that survives all four questions is deleted or rerouted to the artifact the table names.
