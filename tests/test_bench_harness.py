import copy

import pytest

from bench.harness import (
    ENGINE_ORDER,
    HarnessValidationError,
    aggregate_runs,
    validate_formula_measurement,
    validate_run,
)


def valid_run():
    statuses = [
        {"engine_id": engine_id, "status": "PASS", "refusal_code": None,
         "duration_ns": index + 1}
        for index, engine_id in enumerate(ENGINE_ORDER)
    ]
    return {
        "run_id": "run-1", "fixture_id": "nominal-v1", "sha": "a" * 40,
        "environment": {"python": "3.13.1", "implementation": "CPython", "platform": "test"},
        "iteration_id": 1, "scenario_id": "nominal", "execution_key": "",
        "engine_statuses": statuses, "end_to_end_duration_ns": sum(x["duration_ns"] for x in statuses),
        "replay": {"matched": True}, "formula_05_08": {"status": "MESURE", "matches": True},
        "axes": {"sota_score": "NON_MESURE"},
    }


def test_rejects_missing_id():
    run = valid_run(); del run["run_id"]
    with pytest.raises(HarnessValidationError, match="run_id"):
        validate_run(run)


def test_rejects_missing_engine():
    run = valid_run(); run["engine_statuses"].pop()
    with pytest.raises(HarnessValidationError, match="ENGINE_ORDER"):
        validate_run(run)


def test_rejects_negative_duration():
    run = valid_run(); run["engine_statuses"][3]["duration_ns"] = -1
    with pytest.raises(HarnessValidationError, match="duration"):
        validate_run(run)


def test_rejects_duplicate_execution_key():
    one = validate_run(valid_run())
    two = copy.deepcopy(one); two["run_id"] = "run-2"
    with pytest.raises(HarnessValidationError, match="duplicate"):
        aggregate_runs([one, two])


def test_rejects_divergent_sha():
    one = validate_run(valid_run())
    two = valid_run(); two["iteration_id"] = 2; two["sha"] = "b" * 40
    two = validate_run(two)
    with pytest.raises(HarnessValidationError, match="SHA"):
        aggregate_runs([one, two])


def test_rejects_unordered_statuses():
    run = valid_run(); run["engine_statuses"][0], run["engine_statuses"][1] = run["engine_statuses"][1], run["engine_statuses"][0]
    with pytest.raises(HarnessValidationError, match="ENGINE_ORDER"):
        validate_run(run)


def test_rejects_incorrect_formula():
    measurement = {"beta": 1.0, "delta_phi": 1.0, "T": 0.0, "sigma": 0.0, "S": 0.5}
    with pytest.raises(HarnessValidationError, match="formula"):
        validate_formula_measurement(measurement)


def test_aggregate_emits_percentiles_rates_and_non_mesure():
    manifest = aggregate_runs([validate_run(valid_run())])
    assert manifest["latency_ns"]["end_to_end"]["p50"] > 0
    assert manifest["latency_ns"]["engines"]["00_RUNTIME_CHECK"]["p95"] == 1
    assert manifest["replay_rate"] == {"matched": 1, "total": 1, "rate": 1.0}
    assert manifest["gate_rate"] == {"pass": 12, "total": 12, "rate": 1.0}
    assert manifest["axes"]["sota_score"] == "NON_MESURE"
