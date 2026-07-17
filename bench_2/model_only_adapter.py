from __future__ import annotations

import json
import sys

from bench_2.anthropic_adapter import MODEL, invoke


def main():
    payload = json.load(sys.stdin); prompt = payload["prompt"]
    response, metrics = invoke(prompt, MODEL)
    print(json.dumps({"response": response, "model_version": MODEL,
                      "engines_active": [], "engines_disabled": [],
                      "criterion_scores": "UNAVAILABLE", "score_justifications": {"status": "UNAVAILABLE"},
                      "veto": "UNAVAILABLE", "errors": [], **metrics}, ensure_ascii=False))


if __name__ == "__main__":
    main()
