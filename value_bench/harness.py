from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path

CRITERIA = ("answers_request", "factual_accuracy", "useful_completeness",
            "constraint_compliance", "provenance_fact_hypothesis",
            "no_invention", "justified_refusal", "useful_concision")
CRITICAL = ("factual_accuracy", "useful_completeness", "constraint_compliance",
            "provenance_fact_hypothesis", "no_invention", "justified_refusal")

class ValueBenchError(ValueError):
    pass

def blind_pair(run_a: dict, run_b: dict, invert: bool) -> tuple[dict, dict]:
    if run_a["prompt_id"] != run_b["prompt_id"] or run_a["seed"] != run_b["seed"]:
        raise ValueBenchError("non-comparable pair")
    ordered = (run_b, run_a) if invert else (run_a, run_b)
    public = {"prompt_id": run_a["prompt_id"], "prompt": run_a["prompt"],
              "responses": {"SYSTEM_A": ordered[0]["response"], "SYSTEM_B": ordered[1]["response"]}}
    secret = {"SYSTEM_A": ordered[0]["configuration"], "SYSTEM_B": ordered[1]["configuration"]}
    encoded = json.dumps(public, ensure_ascii=False)
    if "MODEL_ONLY" in encoded or "ZORAN_FULL" in encoded:
        raise ValueBenchError("configuration label leaked to judge")
    return public, secret

def validate_run(row: dict) -> None:
    required = {"run_id", "fixture_id", "prompt_id", "prompt", "seed", "configuration",
                "model_version", "model_parameters", "system_prompt", "context", "response",
                "latency_total_ms", "tokens_input", "tokens_output", "estimated_cost", "runner_sha", "timestamp"}
    missing = required - set(row)
    if missing: raise ValueBenchError(f"missing metrics/identity: {sorted(missing)}")
    if not row["response"].strip(): raise ValueBenchError("empty response")
    if row.get("truncated") is True: raise ValueBenchError("truncated response")

def validate_unique(rows: list[dict]) -> None:
    ids = [r["run_id"] for r in rows]
    if len(ids) != len(set(ids)): raise ValueBenchError("duplicate run_id")

def validate_judgment(row: dict) -> None:
    if set(row.get("scores", {})) != set(CRITERIA): raise ValueBenchError("incomplete judge scores")
    if set(row.get("justifications", {})) != set(CRITERIA): raise ValueBenchError("incomplete judge justifications")
    if set(row.get("textual_evidence", {})) != set(CRITERIA): raise ValueBenchError("incomplete textual evidence")
    if any(not isinstance(v, int) or v < 0 or v > 4 for v in row["scores"].values()):
        raise ValueBenchError("invalid score")

def reconcile(j1: dict, j2: dict) -> dict:
    validate_judgment(j1); validate_judgment(j2)
    out = {}
    for criterion in CRITERIA:
        a, b = j1["scores"][criterion], j2["scores"][criterion]
        out[criterion] = a if a == b else "NON_MESURE"
    return out

def summarize(scored: list[dict]) -> dict:
    configs = ("MODEL_ONLY", "ZORAN_FULL")
    means = {c: {} for c in configs}
    for config in configs:
        for criterion in CRITERIA:
            vals = [r["scores"][criterion] for r in scored if r["configuration"] == config and isinstance(r["scores"][criterion], int)]
            means[config][criterion] = round(statistics.fmean(vals), 4) if vals else "NON_MESURE"
    delta = {}
    for criterion in CRITERIA:
        a, b = means["MODEL_ONLY"][criterion], means["ZORAN_FULL"][criterion]
        delta[criterion] = round(b-a, 4) if isinstance(a, float) and isinstance(b, float) else "NON_MESURE"
    critical = [delta[c] for c in CRITICAL]
    gate = "NON_MESURE" if any(x == "NON_MESURE" for x in critical) else ("PASS" if all(x >= 0 for x in critical) else "FAIL")
    return {"quality_gate": gate, "means": means, "delta": delta}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()
