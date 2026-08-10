"""Minimal secret-safe Anthropic Messages API client for BENCH_2."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from bench_2.canonical_adapter import AdapterError

MODEL = "claude-haiku-4-5"
TEMPERATURE = 0.0
MAX_TOKENS = 512
INPUT_USD_PER_MTOK = 1.0
OUTPUT_USD_PER_MTOK = 5.0


def provider_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def invoke(text: str, model_version: str = MODEL):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AdapterError("ANTHROPIC_PROVIDER_UNAVAILABLE")
    payload = json.dumps({"model": model_version, "max_tokens": MAX_TOKENS,
                          "temperature": TEMPERATURE,
                          "messages": [{"role": "user", "content": text}]},
                         ensure_ascii=False).encode("utf-8")
    retries = 0
    started = time.perf_counter_ns()
    while True:
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=payload, method="POST",
            headers={"content-type": "application/json", "anthropic-version": "2023-06-01",
                     "x-api-key": api_key})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or retries >= 2:
                raise AdapterError(f"ANTHROPIC_HTTP_ERROR:{exc.code}") from None
            retries += 1
            time.sleep(2 ** retries)
        except (urllib.error.URLError, TimeoutError) as exc:
            if retries >= 2:
                raise AdapterError(f"ANTHROPIC_NETWORK_ERROR:{type(exc).__name__}") from None
            retries += 1
            time.sleep(2 ** retries)
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    content = body.get("content") or []
    text_blocks = [block.get("text", "") for block in content if block.get("type") == "text"]
    output = "".join(text_blocks).strip()
    if not output:
        raise AdapterError("ANTHROPIC_EMPTY_RESPONSE")
    usage = body.get("usage") or {}
    tokens_input = usage.get("input_tokens", "UNAVAILABLE")
    tokens_output = usage.get("output_tokens", "UNAVAILABLE")
    if isinstance(tokens_input, int) and isinstance(tokens_output, int):
        tokens_total = tokens_input + tokens_output
        estimated_cost = round(tokens_input * INPUT_USD_PER_MTOK / 1_000_000 +
                               tokens_output * OUTPUT_USD_PER_MTOK / 1_000_000, 9)
    else:
        tokens_total = estimated_cost = "UNAVAILABLE"
    return output, {"tokens_input": tokens_input, "tokens_output": tokens_output,
                    "tokens_total": tokens_total, "time_to_first_token_ms": "UNAVAILABLE",
                    "estimated_cost": estimated_cost, "retries": retries,
                    "latency_model_ms": elapsed_ms, "provider_request_id": body.get("id", "UNAVAILABLE"),
                    "provider_stop_reason": body.get("stop_reason", "UNAVAILABLE"),
                    "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
                    "seed_support": "UNAVAILABLE_PROVIDER_SEED_LABEL_ONLY"}
