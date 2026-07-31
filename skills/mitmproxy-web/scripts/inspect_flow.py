#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "api-key"}
REASONING_FIELDS = ("reasoning_content", "reasoning", "reasoning_text")


def request_json(opener, url):
    with opener.open(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(opener, url):
    with opener.open(url, timeout=10) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def redact_headers(headers):
    redacted = []
    for name, value in headers or []:
        if name.lower() in SENSITIVE_HEADERS:
            value = "[REDACTED]"
        redacted.append([name, value])
    return redacted


def find_flow(flows, flow_id):
    for flow in flows:
        if flow.get("id") == flow_id:
            return flow
    return None


def parse_json_body(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def summarize_request(body):
    obj = parse_json_body(body)
    if not isinstance(obj, dict):
        return {"parseable_json": False, "bytes": len(body)}

    return {
        "parseable_json": True,
        "bytes": len(body),
        "model": obj.get("model"),
        "stream": obj.get("stream"),
        "max_tokens": obj.get("max_tokens"),
        "temperature": obj.get("temperature"),
        "top_p": obj.get("top_p"),
        "top_k": obj.get("top_k"),
        "min_p": obj.get("min_p"),
        "repeat_penalty": obj.get("repeat_penalty"),
        "repeat_last_n": obj.get("repeat_last_n"),
        "has_chat_template_kwargs": "chat_template_kwargs" in obj,
        "chat_template_kwargs": obj.get("chat_template_kwargs"),
        "has_reasoning_effort": "reasoning_effort" in obj,
        "has_thinking": "thinking" in obj,
        "message_count": len(obj.get("messages", [])) if isinstance(obj.get("messages"), list) else None,
        "tool_count": len(obj.get("tools", [])) if isinstance(obj.get("tools"), list) else None,
    }


def summarize_sse(body):
    top_keys = {}
    choice_keys = {}
    events = 0
    json_events = 0
    content_events = 0
    content_chars = 0
    reasoning_events = 0
    reasoning_chars = 0
    finish_reasons = {}

    for line in body.splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload.strip() == "[DONE]":
            continue
        events += 1
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            continue
        json_events += 1
        for key in obj:
            top_keys[key] = top_keys.get(key, 0) + 1
        choices = obj.get("choices")
        choice = choices[0] if isinstance(choices, list) and choices else None
        if not isinstance(choice, dict):
            continue
        for key in choice:
            choice_keys[key] = choice_keys.get(key, 0) + 1
        finish = choice.get("finish_reason")
        if finish is not None:
            finish_reasons[str(finish)] = finish_reasons.get(str(finish), 0) + 1
        delta = choice.get("delta")
        if not isinstance(delta, dict):
            continue
        content = delta.get("content")
        if isinstance(content, str) and content:
            content_events += 1
            content_chars += len(content)
        for field in REASONING_FIELDS:
            value = delta.get(field)
            if isinstance(value, str) and value:
                reasoning_events += 1
                reasoning_chars += len(value)

    return {
        "bytes": len(body),
        "events": events,
        "json_events": json_events,
        "top_level_keys": top_keys,
        "choice_keys": choice_keys,
        "finish_reasons": finish_reasons,
        "content_events": content_events,
        "content_chars": content_chars,
        "reasoning_events": reasoning_events,
        "reasoning_chars": reasoning_chars,
        "has_reasoning": reasoning_events > 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect an authenticated mitmweb flow without dumping raw bodies.")
    parser.add_argument("--base", default="http://127.0.0.1:8084", help="mitmweb base URL")
    parser.add_argument("--token", required=True, help="mitmweb auth token/password")
    parser.add_argument("--flow", required=True, help="flow ID")
    parser.add_argument("--raw", action="store_true", help="include raw request/response bodies")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    auth_url = f"{base}/?token={urllib.parse.quote(args.token)}"
    try:
        opener.open(auth_url, timeout=10).read()
        flows = request_json(opener, f"{base}/flows")
    except urllib.error.HTTPError as exc:
        print(json.dumps({"error": f"HTTP {exc.code}", "url": exc.geturl()}, indent=2))
        return 1
    except OSError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1

    flow = find_flow(flows, args.flow)
    if not flow:
        print(json.dumps({"error": "flow not found", "flow": args.flow, "flow_count": len(flows)}, indent=2))
        return 1

    request_status, request_body = request_text(opener, f"{base}/flows/{args.flow}/request/content.data")
    response_status, response_body = request_text(opener, f"{base}/flows/{args.flow}/response/content.data")

    response_headers = flow.get("response", {}).get("headers", [])
    content_type = None
    for name, value in response_headers:
        if name.lower() == "content-type":
            content_type = value
            break

    result = {
        "flow": {
            "id": flow.get("id"),
            "type": flow.get("type"),
            "request": {
                "method": flow.get("request", {}).get("method"),
                "url": flow.get("request", {}).get("pretty_url"),
                "headers": redact_headers(flow.get("request", {}).get("headers")),
            },
            "response": {
                "status_code": flow.get("response", {}).get("status_code"),
                "headers": redact_headers(response_headers),
                "content_length": flow.get("response", {}).get("contentLength"),
            },
        },
        "request_body": {
            "http_status": request_status,
            "summary": summarize_request(request_body),
        },
        "response_body": {
            "http_status": response_status,
            "summary": summarize_sse(response_body) if content_type == "text/event-stream" else {"bytes": len(response_body)},
        },
    }

    if args.raw:
        result["request_body"]["raw"] = request_body
        result["response_body"]["raw"] = response_body

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
