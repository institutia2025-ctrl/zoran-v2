from __future__ import annotations

import json
import sys

from bench_2.canonical_adapter import execute_canonical
from bench_2.anthropic_adapter import MODEL, invoke


def main():
    payload = json.load(sys.stdin)
    result = execute_canonical(payload["prompt"], payload["seed"], MODEL, invoke,
                               disabled_engine=payload.get("disabled_engine"))
    result.update(criterion_scores="UNAVAILABLE", score_justifications={"status": "UNAVAILABLE"},
                  veto="UNAVAILABLE")
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
