## General folder references

`/tmp/` for throwaway temporary code. Not the project root or .agents
`.agents/` for ai-resources like plans, specs and handoffs.

## Path Aliases

When the user refers to a folder without a full path, resolve using these mappings:

- "agents" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/agents/`
- "prompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/prompts/`
- "metaprompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/metaprompt/`
- "dotfiles" => `/home/airtonp/code/ton-anywhere/dotfiles`
- "skills" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/skills/`

---

## Operating System Preferences

- The user uses **Ubuntu Linux** with X11 Desktop.
- Do not provide guidance for other operating systems unless explicitly requested.

---

## Communication Rules

- Be concise. Provide supporting details when asked.

---

## Documentation

- One canonical doc per fact; every other doc keeps a one-line summary and a pointer, never a copy.

---

## ai-memory

- Every `memory_handoff_*` and `memory_write_page` call passes `workspace` **and** `project` explicitly. No session id reaches the MCP server, so an unscoped call lands in whichever project published the active-project pointer last.
- `cwd` on `memory_handoff_begin` is metadata only: it never scopes the handoff, and a manual handoff is project-wide once written.
