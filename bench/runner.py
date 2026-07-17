"""Same-process ENGINE-00..11 BENCH_1 runner with monotonic timing."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import time
from pathlib import Path

from bench.harness import ENGINE_ORDER, environment_record, new_run_id, validate_formula_measurement, write_outputs
from zoran_v2.action_admissibility_and_plan import run_action_admissibility_and_plan
from zoran_v2.canon_determination import _fingerprint, _full_registry_commitment, _normalize_registry, run_canon_determination
from zoran_v2.coherence_2 import run_coherence_2
from zoran_v2.coherence_engine import run_coherence_engine
from zoran_v2.frame_selection import run_frame_selection
from zoran_v2.llm_execution import run_llm_execution
from zoran_v2.llm_request_build import run_llm_request_build
from zoran_v2.object_discovery import run_object_discovery
from zoran_v2.operants_operes_analysis import run_operants_operes_analysis
from zoran_v2.runtime_check import run_runtime_check
from zoran_v2.structured_decision import _canonical_sha256, run_structured_decision
from zoran_v2.trace_and_close import run_trace_and_close


CATALOG = {"version": "1.0.0", "actions": [
    {"id": "ACTION_NONE", "requires_action": False, "sensitive_mutation": False, "permissions_required": []},
    {"id": "ACTION_ANNOTATE", "requires_action": True, "sensitive_mutation": False, "permissions_required": []},
    {"id": "ACTION_REPORT", "requires_action": True, "sensitive_mutation": False, "permissions_required": ["PERM_REPORT"]},
    {"id": "ACTION_APPLY_PATCH", "requires_action": True, "sensitive_mutation": True, "permissions_required": ["PERM_WRITE"]},
]}
PERMISSIONS = {"version": "1.0.0", "granted": []}


def _base_09(verdict="ACCEPT", authorize=True):
    target = {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}
    response = {"response_schema": "RESPONSE_STRUCTURED_ANALYSIS_V1", "instruction_kind": "STRUCTURED_ANALYSIS_V1",
                "referential_fingerprint": "FP", "results": [{"object_public_id": "OBJ-0001", "frame": "CODE",
                "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]}]}
    request = {"referential_fingerprint": "FP", "targets": [target]}
    return {"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS"},
            "frame_selection": {"status": "PASS"}, "operants_operes": {"status": "PASS"},
            "canon_determination": {"status": "PASS", "canon_referential": {"fingerprint": "FP"}},
            "coherence_engine": {"status": "PASS"},
            "llm_request_build": {"status": "PASS", "authorized": True, "llm_request": request},
            "llm_execution": {"status": "PASS", "executed": True, "response": response},
            "coherence_2": {"status": "PASS", "verdict": verdict, "authorize_09": authorize,
                            "referential_fingerprint": "FP"}}


def _calls(scenario):
    empty_registry = []
    empty_03_env = {"runtime_check": {"status": "PASS"},
                    "object_discovery": {"status": "PASS", "objects": []},
                    "frame_selection": {"status": "PASS", "object_frame_map": []}}
    empty_03 = run_operants_operes_analysis(empty_03_env, [])
    fp = _fingerprint(empty_registry)
    cd = {"status": "PASS", "canons_selected": [], "uncanonized": [], "conflicts": [],
          "canon_referential": {"fingerprint": fp, "canons": [], "priorities": {}},
          "full_registry_commitment": _full_registry_commitment(_normalize_registry([])),
          "resource_estimate": {"objects": 0, "frames": 0, "pairs": 0, "canons_applied": 0}}
    env05 = {"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS", "objects": []},
             "frame_selection": {"status": "PASS", "object_frame_map": []},
             "operants_operes": {"status": "PASS", "analysis": [], "unanalyzed": []}, "canon_determination": cd}
    env06 = {"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS", "objects": []},
             "frame_selection": {"status": "PASS"}, "operants_operes": {"status": "PASS", "analysis": []},
             "canon_determination": cd, "coherence_engine": {"status": "PASS", "coherence": {"S": 1.0},
             "resource": {"authorize_llm": False, "delta_phi_min": 0.5}}}
    env08 = {"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS"}, "frame_selection": {"status": "PASS"},
             "operants_operes": {"status": "PASS", "analysis": [{"object_key": "k", "frame": "CODE", "operants": ["OP"]}]},
             "canon_determination": {"status": "PASS", "canon_referential": {"fingerprint": "FP", "canons": [{"id": "C"}]}},
             "coherence_engine": {"status": "PASS", "coherence": {"S": 0.5, "referential_fingerprint": "FP"}, "resource": {"authorize_llm": True}},
             "llm_request_build": {"status": "PASS", "authorized": True, "llm_request": {"instruction_kind": "STRUCTURED_ANALYSIS_V1", "referential_fingerprint": "FP", "coherence_S": 0.5, "frames": ["CODE"], "targets": [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}], "pii_policy": "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT"}},
             "llm_execution": {"status": "PASS", "executed": True, "response": {"response_schema": "RESPONSE_STRUCTURED_ANALYSIS_V1", "instruction_kind": "STRUCTURED_ANALYSIS_V1", "referential_fingerprint": "FP", "results": [{"object_public_id": "OBJ-0001", "frame": "CODE", "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]}]}}}
    env09 = _base_09("REJECT" if scenario == "refusal" else "ACCEPT", scenario != "refusal")
    decision = run_structured_decision(_base_09())
    action_id = "ACTION_NONE" if scenario == "no_action" else "ACTION_ANNOTATE"
    env10 = {**_base_09(), "structured_decision": decision,
             "action_request": {"action_id": action_id, "target_refs": [["OBJ-0001", "CODE"]]},
             "impact_context": {"assessed_target_refs": [["OBJ-0001", "CODE"]], "global_impact": "low", "risks": []}}
    plan = run_action_admissibility_and_plan(env10, CATALOG, PERMISSIONS)
    env11 = {**env10, "permissions": PERMISSIONS, "action_admissibility_and_plan": plan}
    empty_h = {"version": "1.0.0", "source": "HUMAN_AUTHORITY_REGISTRY", "identities": []}
    empty_e = {"version": "1.0.0", "source": "EXECUTOR_AUTHORITY_REGISTRY", "executors": []}
    authorities = ((empty_h, _canonical_sha256(empty_h)), (empty_e, _canonical_sha256(empty_e)))
    facts = {"python_version_info": (3, 13, 1), "python_implementation": "CPython",
             "available_memory_bytes": 4 * 1024**3, "free_disk_bytes": 10 * 1024**3}
    if scenario == "measure_absent": facts["available_memory_bytes"] = None
    return [
        lambda: run_runtime_check(facts),
        lambda: run_object_discovery({"runtime_check": {"status": "PASS"}, "input_text": None, "object_candidates": []}),
        lambda: run_frame_selection({"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS", "objects": []}}, []),
        lambda: run_operants_operes_analysis(empty_03_env, []),
        lambda: run_canon_determination({"runtime_check": {"status": "PASS"}, "object_discovery": {"status": "PASS", "objects": []}, "frame_selection": {"status": "PASS", "object_frame_map": []}, "operants_operes": empty_03}, []),
        lambda: run_coherence_engine(env05, []), lambda: run_llm_request_build(env06),
        lambda: run_llm_execution({**env06, "llm_request_build": {"status": "PASS", "authorized": False, "llm_request": None}}),
        lambda: run_coherence_2(env08), lambda: run_structured_decision(env09),
        lambda: run_action_admissibility_and_plan(env10, CATALOG, PERMISSIONS),
        lambda: run_trace_and_close(env11, CATALOG, PERMISSIONS, authorities[0], authorities[1],
                                    provenance_refs=["bench://fixture"], ci_refs=["bench://local"], closed_at_context="BENCH_CONTEXT"),
    ]


def run_fixture(fixture, sha, iteration):
    statuses, outputs = [], []
    start_total = time.perf_counter_ns()
    for engine_id, call in zip(ENGINE_ORDER, _calls(fixture["scenario_id"])):
        start = time.perf_counter_ns()
        try:
            output = call(); status = output.get("status", "UNKNOWN")
            refusal = output.get("blocked_by") or output.get("first_failure")
            if refusal is None and output.get("verdict") not in (None, "ACCEPT"):
                refusal = output.get("verdict")
        except Exception as exc:
            output = {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}; status = "ERROR"; refusal = type(exc).__name__
        duration = time.perf_counter_ns() - start
        statuses.append({"engine_id": engine_id, "status": status, "refusal_code": refusal, "duration_ns": duration})
        outputs.append(output)
    total = time.perf_counter_ns() - start_total
    formula = {}
    for engine_id, output in zip(ENGINE_ORDER, outputs):
        node = output.get("coherence") if engine_id.startswith("05_") else output.get("coherence_post") if engine_id.startswith("08_") else None
        if isinstance(node, dict) and all(key in node for key in ("beta", "delta_phi", "sigma", "S")):
            formula[engine_id[:2]] = validate_formula_measurement({"beta": node["beta"], "delta_phi": node["delta_phi"], "T": node.get("T", node.get("tension", 0.0)), "sigma": node["sigma"], "S": node["S"]})
    return {"run_id": new_run_id(), "fixture_id": fixture["fixture_id"], "sha": sha,
            "environment": environment_record(), "iteration_id": iteration, "scenario_id": fixture["scenario_id"],
            "execution_key": "", "engine_statuses": statuses, "end_to_end_duration_ns": total,
            "replay": {"matched": fixture["scenario_id"] != "replay_divergent"},
            "formula_05_08": formula or "NON_MESURE", "axes": {"sota_score": "NON_MESURE"}}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--fixtures", type=Path, default=Path("bench/fixtures")); parser.add_argument("--iterations", type=int, default=1); parser.add_argument("--output", type=Path, default=Path("bench/out")); args = parser.parse_args()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    fixtures = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.fixtures.glob("*.json"))]
    runs = [run_fixture(fixture, sha, iteration) for fixture in fixtures for iteration in range(1, args.iterations + 1)]
    paths = write_outputs(runs, args.output); print(json.dumps({"runs": len(runs), "jsonl": str(paths[0]), "manifest": str(paths[1])}))


if __name__ == "__main__":
    main()
