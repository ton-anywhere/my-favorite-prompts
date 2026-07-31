---
name: mitmproxy-web
description: Inspect and debug local mitmweb/mitmproxy HTTP flows, especially OpenAI-compatible or llama.cpp request/response captures, authenticated mitmweb URLs, SSE streams, request payloads, response field shapes, headers, and missing reasoning/thinking fields. Use when the user gives a mitmweb URL, flow ID, mitmproxy web token, or asks to debug proxied API requests/responses.
---

# Mitmproxy Web

## Required Token

Before calling mitmweb, ensure you have the mitmweb token/password.

- If the user supplied a URL with `?token=...`, use that token.
- If the user supplied only a flow URL or flow ID, ask for the token before trying authenticated endpoints.
- Do not guess or scrape unrelated terminal history for the token unless the user asks you to inspect the local process/logs.

## Workflow

1. Identify the mitmweb base URL, usually `http://127.0.0.1:8084`.
2. Authenticate with the token to obtain the `mitmproxy-auth-*` cookie.
3. Fetch `/flows`, then select the requested flow ID client-side; mitmweb may return `405` for direct `GET /flows/<id>`.
4. Fetch request/response bodies with:
   - `/flows/<id>/request/content.data`
   - `/flows/<id>/response/content.data`
5. Summarize structure first. Avoid dumping raw response content unless the user explicitly asks.

Use `scripts/inspect_flow.py` for steps 2-5.

```bash
python3 /path/to/mitmproxy-web/scripts/inspect_flow.py \
  --base http://127.0.0.1:8084 \
  --token TOKEN \
  --flow FLOW_ID
```

## Request Debugging

For OpenAI-compatible/llama.cpp captures, report:

- request model, stream flag, sampling fields, tools count, and message count;
- whether `chat_template_kwargs`, `reasoning_effort`, or `thinking` were sent;
- response status, content type, and SSE event counts;
- whether response deltas contain `content`, `reasoning_content`, `reasoning`, or `reasoning_text`.

If `chat_template_kwargs.enable_thinking` was sent but the SSE stream has no reasoning fields, conclude that the server did not expose separate thinking blocks to the client.

## Safety

- Redact authorization headers, API keys, cookies, and tokens in summaries.
- Do not paste full prompts, completions, or SSE content into the answer by default.
- For model-template or special-token debugging, combine this skill with model-template-safety and avoid printing raw control tokens.
