## Path Aliases

When the user refers to a folder without a full path, resolve using these mappings:

- "agents" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/agents/`
- "prompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/prompts/`
- "metaprompts" => `/home/airtonp/code/ton-anywhere/my-favorite-prompts/metaprompt/`

The user may reference these aliases in either English or Portuguese.

## Agent Feedback

When the user provides feedback about agent performance, **always** append it to the agents feedback log:

- **File:** `/home/airtonp/code/ton-anywhere/my-favorite-prompts/feedbacks/agents_feedback.md`
- **Format:** Add a new row at the bottom of the markdown table with format: `Agent \| Feedback \| No`

## Language

Respond in the same language the user writes in. The user communicates in both English and Portuguese — match whichever they use in each message.
The user might alse references the alias above in both languages.


## Tool Invocation Safety

Use the platform's real tool and skill mechanisms for reads, searches, commands, dispatches, and skill loading. Never type raw tool-call markup, XML tags, function-call blocks, or closing thought tags as assistant text, including `<tool_call>`, `<function=...>`, `<parameter=...>`, or `</think>`.

If a named tool or skill is unavailable, say what is unavailable in plain language and continue with the closest valid workflow. Do not invent tool-call syntax.
