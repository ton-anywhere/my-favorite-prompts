## Path Aliases

When the user refers to a folder without a full path, resolve using these mappings:

- "agents" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/agents/`
- "prompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/prompts/`
- "metaprompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/metaprompt/`
- "dotfiles" => `/home/airtonp/code/ton-anywhere/dotfiles`
- "skills" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/skills/`

---

## Tool Usage

Use Pi's built-in tools honestly. Never invent tool names or fake results.

- `read`: inspect existing files, including skill files.
- `bash`: list/search files, run git, tests, package managers, and shell commands. Prefer `rg` for text search.
- `edit`: modify existing files with exact replacements.
- `write`: create new files or intentionally replace a whole file.
- `web_search`: current or external web research.
- `fetch_content`: readable content from URLs, videos, GitHub repos, or local videos.
- `get_search_content`: full stored content from prior search/fetch responses.

If a needed tool is unavailable, say so plainly and choose the closest safe alternative.

---

## Operating System Preferences

- The user uses **Ubuntu Linux**.
- Do not provide guidance for other operating systems unless explicitly requested.
