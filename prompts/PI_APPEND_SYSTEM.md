## Path Aliases

When the user refers to a folder without a full path, resolve using these mappings:

- "agents" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/agents/`
- "prompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/prompts/`
- "metaprompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/metaprompt/`
- "dotfiles" => `/home/airtonp/code/ton-anywhere/dotfiles`
- "skills" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/skills/`

---

## Operating System Preferences

- The user uses **Ubuntu Linux**.
- Do not provide guidance for other operating systems unless explicitly requested.

---

# ai-memory

## Memory Recall

Before implementing, designing, or debugging in an existing project, call `memory_query` with the task's specific terms (module, tool, error text).
Read any `_rules/`, `procedures/` and `gotchas/` hits in full and follow them. Query again when you start a new subtask or hit an error.

## Memory Handoffs

- Every `memory_handoff_*` and `memory_write_page` call passes `workspace` **and** `project` explicitly. No session id reaches the MCP server, so an unscoped call lands in whichever project published the active-project pointer last.
- `cwd` on `memory_handoff_begin` is metadata only: it never scopes the handoff, and a manual handoff is project-wide once written.
