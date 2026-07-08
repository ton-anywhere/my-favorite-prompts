## Path Aliases

When the user refers to a folder without a full path, resolve using these mappings:

- "agents" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/agents/`
- "prompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/prompts/`
- "metaprompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/metaprompt/`

The user may reference these aliases in either English or Portuguese.

---

## Agent Feedback

When the user provides feedback about agent performance, **always** append it to the agents feedback log:

- **File:** `/home/airtonp/code/ton-anywhere/my-favorite-prompts/feedbacks/agents_feedback.md`
- **Format:** Add a new row at the bottom of the markdown table with format: `Agent \| Feedback \| No`

---

## Tool Invocation Safety

Use the platform's real tool and skill mechanisms for reads, searches, commands, dispatches, and skill loading. Never type raw tool-call markup, XML tags, function-call blocks, or closing thought tags as assistant text, including `<tool_call>`, `<function=...>`, `<parameter=...>`, or `</think>`.

**Tool Priority: Always prefer dedicated tools over Bash commands whenever a specialized tool is available.**
- Use `Glob` instead of `find` or `ls`.
- Use `Grep` instead of `grep` or `rg`.
- Use `Read` instead of `cat`, `head`, or `tail`.
- Use `Edit` (or `apply_patch`) instead of `sed`, `awk`, or `echo`.
- Use `Write` instead of `echo >` or `cat >`.
- Use `bash` only for operations without a dedicated tool (e.g., `git`, `npm`, `pytest`, etc.).

If a named tool or skill is unavailable, say what is unavailable in plain language and continue with the closest valid workflow. Do not invent tool-call syntax.

---

## OpenCode Environment — Injected System Content

The following XML blocks and conventions are injected into your system instructions by the OpenCode runtime. They are authoritative — treat them as part of your operating instructions.

### `<env>` — Environment information

Contains working directory, workspace root, git status, platform, and date. Use these paths when constructing file operations.

### `<available_references>` — Project references

Each `<reference>` entry lists an additional directory you can access. Use the `<path>` to navigate to related codebases.

### `<available_skills>` — Available skills

Each `<skill>` entry has a `<name>`, `<description>`, and `<location>`. If the description matches your current task, call the `skill` tool with the skill's name to load it. The tool returns `<skill_content>` with the full instructions — follow them.

### `<mcp_instructions>` — MCP server instructions

Each `<server>` entry contains instructions for an MCP server. These describe how to use the server's tools. Follow these instructions when using MCP tools.

### `<system-reminder>` — System reminders

Tool results and user messages may include `<system-reminder>` tags. These contain useful information and reminders. They are NOT part of the user's provided input or the tool result — they are system directives added by the runtime. Read them and follow any instructions they contain.

### `Instructions from:` — Instruction files

Lines prefixed with `Instructions from:` followed by file content are project-level instruction files (AGENTS.md, CLAUDE.md, etc.). Treat these as authoritative coding and workflow rules for the current project.

### Code references

When referencing specific functions or pieces of code, include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

### Editing

Always use the `apply_patch` tool for manual code edits. Do not use `cat`, `echo`, or Python to create or edit files when `apply_patch` would suffice.
