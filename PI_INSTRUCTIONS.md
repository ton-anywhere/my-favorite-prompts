## Skill Invocation Rule

Before responding to ANY task, scan `<available_skills>` for a matching skill.
If one matches, invoke it FIRST using `/skill:<name>` — do NOT attempt the task without loading the relevant skill.
Skipping mandatory skills is incorrect.
When uncertain whether a skill applies, load it anyway.

---

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

## Tool Usage

Use Pi's built-in tools for file operations and searches. Never invent tool names or fake results.

Prefer dedicated tools over raw Bash:
- Use `read` to read files (instead of cat/head/tail)
- Use `edit` to modify existing files (instead of sed/awk/echo >)
- Use `write` to create new files (instead of echo > or cat >)
- Use `web_search` and `fetch_content` for web content (instead of curl/wget)
- Use `bash` for everything else (git, npm, pytest, shell pipelines, etc.)

If a needed tool is unavailable, say so plainly rather than fabricating output. Do not invent tool names or call non-existent functions.

---
