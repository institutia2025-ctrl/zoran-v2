"""Fail-closed BENCH_2 launcher for externally configured model and ZORAN executors."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from bench_2.harness import SEEDS, corpus_sha256, load_corpus
from bench_2.canonical_adapter import RunIdRegistry

class ExecutorUnavailable(RuntimeError):
    pass

def executor_command(configuration: str) -> list[str]:
    name = "BENCH2_MODEL_COMMAND" if configuration == "MODEL_ONLY" else "BENCH2_ZORAN_COMMAND"
    value = os.environ.get(name, "").strip()
    if not value:
        module = "bench_2.model_only_adapter" if configuration == "MODEL_ONLY" else "bench_2.zoran_full_adapter"
        return [sys.executable, "-m", module]
    return shlex.split(value, posix=False)

def execute(command: list[str], prompt: dict, seed: int, configuration: str) -> dict:
    payload = json.dumps({"prompt_id": prompt["id"], "prompt": prompt["prompt"], "seed": seed,
                          "configuration": configuration}, ensure_ascii=False)
    started = time.perf_counter_ns()
    process = subprocess.run(command, input=payload, text=True, capture_output=True, check=False)
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    if process.returncode != 0:
        raise RuntimeError(f"executor failed rc={process.returncode}: {process.stderr.strip()}")
    result = json.loads(process.stdout)
    result.update(run_id="B2-" + uuid.uuid4().hex, prompt_id=prompt["id"], seed=seed,
                  configuration=configuration, latency_total_ms=elapsed_ms)
    result.setdefault("time_to_first_token_ms", "UNAVAILABLE")
    result.setdefault("tokens_input", "UNAVAILABLE"); result.setdefault("tokens_output", "UNAVAILABLE")
    result.setdefault("tokens_total", "UNAVAILABLE"); result.setdefault("estimated_cost", "UNAVAILABLE")
    result.setdefault("errors", []); result.setdefault("retries", 0)
    result.setdefault("criterion_scores", "UNAVAILABLE")
    result.setdefault("score_justifications", {"status": "UNAVAILABLE"})
    result.setdefault("veto", "UNAVAILABLE")
    result["timestamp"] = datetime.now().astimezone().isoformat()
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", choices=("MODEL_ONLY", "ZORAN_FULL"), required=True)
    parser.add_argument("--prompt-id", default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    corpus_path = Path(__file__).with_name("corpus.jsonl")
    corpus = load_corpus(corpus_path)
    if args.prompt_id:
        corpus = [row for row in corpus if row["id"] == args.prompt_id]
        if not corpus:
            raise SystemExit("unknown prompt id")
    command = executor_command(args.configuration)
    registry = RunIdRegistry()
    rows = [execute(command, prompt, seed, args.configuration) for prompt in corpus for seed in SEEDS]
    repo_root = Path(__file__).resolve().parents[1]
    runner_sha = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    frozen_corpus_sha = corpus_sha256(corpus_path)
    for row in rows:
        registry.claim(row["run_id"])
        row["runner_sha"] = runner_sha
        row["corpus_sha"] = frozen_corpus_sha
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"configuration": args.configuration, "runs": len(rows),
                      "corpus_sha256": corpus_sha256(corpus_path), "output": str(args.output)}))

if __name__ == "__main__":
    main()
