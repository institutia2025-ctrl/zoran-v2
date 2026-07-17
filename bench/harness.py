"""BENCH_1 validation, aggregation, and JSONL/manifest emission.

GUARD_IDS: BENCH_SCOPE_ONLY, NO_ENGINE_MUTATION, RAW_MEASURES_ONLY
"""
from __future__ import annotations

import json
import math
import os
import platform
import statistics
import sys
import time
import uuid
from pathlib import Path


ENGINE_ORDER = tuple(f"{index:02d}_{name}" for index, name in enumerate((
    "RUNTIME_CHECK", "OBJECT_DISCOVERY", "ANALYSIS_FRAME_SELECTION",
    "OPERANTS_OPERES_ANALYSIS", "CANON_DETERMINATION", "COHERENCE_ENGINE",
    "LLM_REQUEST_BUILD", "LLM_EXECUTION", "COHERENCE_2", "STRUCTURED_DECISION",
    "ACTION_ADMISSIBILITY_AND_PLAN", "TRACE_AND_CLOSE",
)))
REQUIRED_IDS = ("run_id", "fixture_id", "sha", "environment", "iteration_id", "scenario_id")


class HarnessValidationError(ValueError):
    pass


def execution_key(run: dict) -> str:
    return "+".join((run["sha"], run["fixture_id"], run["scenario_id"], str(run["iteration_id"])))


def validate_formula_measurement(measurement: dict) -> dict:
    required = ("beta", "delta_phi", "T", "sigma", "S")
    if any(not isinstance(measurement.get(key), (int, float)) for key in required):
        raise HarnessValidationError("formula measurement missing numeric input")
    expected = round((measurement["beta"] * measurement["delta_phi"]) /
                     (1 + measurement["T"] + measurement["sigma"]), 6)
    if not math.isclose(expected, measurement["S"], rel_tol=0.0, abs_tol=1e-6):
        raise HarnessValidationError("formula mismatch")
    return {**measurement, "expected_S": expected, "matches": True}


def validate_run(run: dict) -> dict:
    for field in REQUIRED_IDS:
        if field not in run or run[field] in (None, ""):
            raise HarnessValidationError(f"missing {field}")
    if not (isinstance(run["sha"], str) and len(run["sha"]) == 40):
        raise HarnessValidationError("invalid SHA")
    statuses = run.get("engine_statuses")
    if not isinstance(statuses, list) or [item.get("engine_id") for item in statuses] != list(ENGINE_ORDER):
        raise HarnessValidationError("engine statuses do not match ENGINE_ORDER")
    for item in statuses:
        duration = item.get("duration_ns")
        if not isinstance(duration, int) or duration < 0:
            raise HarnessValidationError("negative or invalid duration")
    total = run.get("end_to_end_duration_ns")
    if not isinstance(total, int) or total < 0:
        raise HarnessValidationError("negative or invalid end-to-end duration")
    normalized = dict(run)
    expected_key = execution_key(normalized)
    if normalized.get("execution_key") not in ("", expected_key):
        raise HarnessValidationError("execution key mismatch")
    normalized["execution_key"] = expected_key
    return normalized


def _percentile(values: list[int], quantile: float) -> int | str:
    if not values:
        return "NON_MESURE"
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[index]


def _rate(numerator: int, denominator: int, label: str) -> dict:
    return {label: numerator, "total": denominator,
            "rate": round(numerator / denominator, 6) if denominator else "NON_MESURE"}


def aggregate_runs(runs: list[dict]) -> dict:
    if not runs:
        raise HarnessValidationError("no runs")
    checked = [validate_run(run) for run in runs]
    keys = [run["execution_key"] for run in checked]
    if len(keys) != len(set(keys)):
        raise HarnessValidationError("duplicate execution key")
    shas = {run["sha"] for run in checked}
    if len(shas) != 1:
        raise HarnessValidationError("divergent SHA in aggregate")
    engine_latency = {}
    for engine_id in ENGINE_ORDER:
        values = [next(item["duration_ns"] for item in run["engine_statuses"]
                       if item["engine_id"] == engine_id) for run in checked]
        engine_latency[engine_id] = {"p50": _percentile(values, .50), "p95": _percentile(values, .95)}
    end_values = [run["end_to_end_duration_ns"] for run in checked]
    replay_matched = sum(run.get("replay", {}).get("matched") is True for run in checked)
    gate_pass = sum(item["status"] == "PASS" for run in checked for item in run["engine_statuses"])
    gate_total = len(checked) * len(ENGINE_ORDER)
    formula = [run.get("formula_05_08", "NON_MESURE") for run in checked]
    return {
        "schema_version": "BENCH_1_MANIFEST_V1", "sha": checked[0]["sha"],
        "execution_keys": keys, "run_count": len(checked),
        "latency_ns": {"engines": engine_latency,
                       "end_to_end": {"p50": _percentile(end_values, .50), "p95": _percentile(end_values, .95)}},
        "replay_rate": _rate(replay_matched, len(checked), "matched"),
        "gate_rate": _rate(gate_pass, gate_total, "pass"),
        "formula_05_08": formula,
        "axes": {"sota_score": "NON_MESURE", "python_initialization_ns": "NON_MESURE",
                 "pytest_duration_ns": "NON_MESURE"},
    }


def write_outputs(runs: list[dict], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    checked = [validate_run(run) for run in runs]
    jsonl = output_dir / "bench_1_runs.jsonl"
    manifest_path = output_dir / "bench_1_manifest.json"
    jsonl.write_text("".join(json.dumps(run, sort_keys=True) + "\n" for run in checked), encoding="utf-8")
    manifest_path.write_text(json.dumps(aggregate_runs(checked), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl, manifest_path


def environment_record() -> dict:
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "platform": platform.platform(), "executable": sys.executable, "pid": os.getpid()}


def timed_call(callable_):
    start = time.perf_counter_ns()
    output = callable_()
    duration = time.perf_counter_ns() - start
    return output, duration


def new_run_id() -> str:
    return "BENCH1-" + uuid.uuid4().hex

