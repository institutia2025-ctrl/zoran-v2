"""Canonical BENCH_2 prompt adapter around unchanged ENGINE-00..11.

GUARD_IDS: BENCH_2_CANONICAL_ADAPTER_V1, NO_ENGINE_MUTATION,
PROMPT_IMMUTABILITY, EXPLICIT_REGISTRIES, EXPLICIT_PROJECTION.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from zoran_v2.action_admissibility_and_plan import run_action_admissibility_and_plan
from zoran_v2.canon_determination import load_canon_registry, run_canon_determination
from zoran_v2.coherence_2 import run_coherence_2
from zoran_v2.coherence_engine import run_coherence_engine
from zoran_v2.frame_selection import load_frame_registry, run_frame_selection
from zoran_v2.llm_execution import run_llm_execution
from zoran_v2.llm_request_build import run_llm_request_build
from zoran_v2.object_discovery import run_object_discovery
from zoran_v2.operants_operes_analysis import load_operant_registry, run_operants_operes_analysis
from zoran_v2.runtime_check import collect_facts, run_runtime_check
from zoran_v2.structured_decision import _canonical_sha256, run_structured_decision
from zoran_v2.trace_and_close import run_trace_and_close

ENGINE_ORDER = (
    "00_RUNTIME_CHECK", "01_OBJECT_DISCOVERY", "02_ANALYSIS_FRAME_SELECTION",
    "03_OPERANTS_OPERES_ANALYSIS", "04_CANON_DETERMINATION", "05_COHERENCE_ENGINE",
    "06_LLM_REQUEST_BUILD", "07_LLM_EXECUTION", "08_COHERENCE_2",
    "09_STRUCTURED_DECISION", "10_ACTION_ADMISSIBILITY_AND_PLAN", "11_TRACE_AND_CLOSE",
)
DEPENDENCIES = {ENGINE_ORDER[index]: ENGINE_ORDER[index - 1] for index in range(1, len(ENGINE_ORDER))}


class AdapterError(RuntimeError):
    pass


class AblationNotExecutable(AdapterError):
    pass


class RunIdRegistry:
    def __init__(self):
        self._ids = set()

    def claim(self, run_id: str) -> None:
        if run_id in self._ids:
            raise AdapterError(f"DUPLICATE_RUN_ID:{run_id}")
        self._ids.add(run_id)


def validate_prompt_unchanged(original: str, received: str) -> None:
    if not isinstance(original, str) or not original or received != original:
        raise AdapterError("PROMPT_MODIFIED")


def build_object_candidates(prompt: str) -> list[dict]:
    if not isinstance(prompt, str) or not prompt:
        raise AdapterError("OBJECT_CANDIDATE_ABSENT")
    return [{"kind": "text", "value": prompt,
             "provenance": {"in_text": {"offset": 0, "len": len(prompt)}}}]


def load_registries(root: Path) -> dict:
    paths = {"frames": root / "ANALYSIS_FRAMES.yaml", "operants": root / "OPERANTS.yaml",
             "canons": root / "CANONS.yaml"}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise AdapterError("REGISTRY_MISSING:" + ",".join(missing))
    registries = {"frames": load_frame_registry(paths["frames"]),
                  "operants": load_operant_registry(paths["operants"]),
                  "canons": load_canon_registry(paths["canons"])}
    if any(not value for value in registries.values()):
        raise AdapterError("REGISTRY_MISSING:empty_or_invalid")
    return registries


def validate_ablation(disabled_engine: str, active_engines: list[str], dependent: str | None = None) -> None:
    if disabled_engine in active_engines:
        raise AblationNotExecutable(f"ENGINE_STILL_ACTIVE:{disabled_engine}")
    if dependent is not None:
        dependency = DEPENDENCIES.get(dependent)
        if dependency == disabled_engine:
            raise AblationNotExecutable(
                f"ABLATION_NOT_EXECUTABLE:{dependent} depends_on={disabled_engine}")


def project_natural_response(response: dict) -> str:
    results = response.get("results") if isinstance(response, dict) else None
    if not isinstance(results, list) or not results:
        raise AdapterError("PROJECTION_EMPTY")
    lines = []
    for result in results:
        accepted = [item["canon"] for item in result.get("canon_findings", []) if item.get("admissible") is True]
        rejected = [item["canon"] for item in result.get("canon_findings", []) if item.get("admissible") is False]
        applied = [item["operant"] for item in result.get("operant_outcomes", []) if item.get("applied") is True]
        blocked = [f"{item['operant']}:{item.get('reason_code', 'NOT_APPLIED')}"
                   for item in result.get("operant_outcomes", []) if item.get("applied") is False]
        lines.append(f"{result['object_public_id']} [{result['frame']}] — canons admissibles: "
                     f"{', '.join(accepted) or 'aucun'}; canons refusés: {', '.join(rejected) or 'aucun'}; "
                     f"opérants appliqués: {', '.join(applied) or 'aucun'}; opérants bloqués: {', '.join(blocked) or 'aucun'}.")
    natural = "\n".join(lines).strip()
    if not natural:
        raise AdapterError("PROJECTION_EMPTY")
    return natural


def _empty_authorities():
    human = {"version": "1.0.0", "source": "HUMAN_AUTHORITY_REGISTRY", "identities": []}
    executor = {"version": "1.0.0", "source": "EXECUTOR_AUTHORITY_REGISTRY", "executors": []}
    return (human, _canonical_sha256(human)), (executor, _canonical_sha256(executor))


def _catalog(root: Path) -> dict:
    import yaml
    value = yaml.safe_load((root / "ACTIONS_CATALOG.yaml").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdapterError("REGISTRY_MISSING:ACTIONS_CATALOG.yaml")
    return value


def _runtime_facts() -> dict:
    facts = collect_facts()
    if facts.get("available_memory_bytes") is None and sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
                        ("total_physical", ctypes.c_ulonglong), ("available_physical", ctypes.c_ulonglong),
                        ("total_page_file", ctypes.c_ulonglong), ("available_page_file", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("available_virtual", ctypes.c_ulonglong),
                        ("available_extended_virtual", ctypes.c_ulonglong)]

        status = MemoryStatus(); status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            facts["available_memory_bytes"] = int(status.available_physical)
    return facts


def _structured_client(model_client, model_version, trace):
    def client(request):
        model_input = {
            "task": "Return only JSON matching the requested ZORAN structured response.",
            "required_root": ["response_schema", "instruction_kind", "referential_fingerprint", "results"],
            "request": request,
            "rules": ["one result per target", "copy opaque ids and frame exactly",
                      "one canon_findings item per canon with admissible boolean",
                      "one operant_outcomes item per operant with applied boolean",
                      "when applied is false add reason_code INSUFFICIENT_EVIDENCE"],
        }
        trace["model_input"] = model_input
        raw, metrics = model_client(json.dumps(model_input, ensure_ascii=False), model_version)
        trace["model_metrics"] = metrics
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AdapterError(f"MODEL_RESPONSE_NOT_JSON:{exc.msg}") from exc
        trace["model_output"] = parsed
        return parsed
    return client


def execute_canonical(prompt: str, seed: int, model_version: str, model_client,
                      root: Path | None = None, disabled_engine: str | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    validate_prompt_unchanged(prompt, prompt)
    registries = load_registries(root)
    if disabled_engine:
        dependent = next((engine for engine, dependency in DEPENDENCIES.items()
                          if dependency == disabled_engine), None)
        validate_ablation(disabled_engine, [], dependent=dependent)
    envelope = {"input_text": prompt, "object_candidates": build_object_candidates(prompt)}
    outputs, timings, active, trace = {}, {}, [], {"prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                                                    "prompt": prompt, "seed": seed, "model_version": model_version}

    def step(engine_id, key, call):
        if disabled_engine == engine_id:
            outputs[key] = {"status": "DISABLED", "blocked_by": "BENCH_2_ABLATION"}
            timings[engine_id] = 0
            return outputs[key]
        started = time.perf_counter_ns(); value = call(); timings[engine_id] = time.perf_counter_ns() - started
        outputs[key] = value; envelope[key] = value; active.append(engine_id)
        if value.get("status") != "PASS":
            raise AdapterError(f"ENGINE_NOT_PASS:{engine_id}:{value.get('status')}:{value.get('blocked_by')}")
        return value

    step(ENGINE_ORDER[0], "runtime_check", lambda: run_runtime_check(_runtime_facts()))
    step(ENGINE_ORDER[1], "object_discovery", lambda: run_object_discovery(envelope))
    step(ENGINE_ORDER[2], "frame_selection", lambda: run_frame_selection(envelope, registries["frames"]))
    step(ENGINE_ORDER[3], "operants_operes", lambda: run_operants_operes_analysis(envelope, registries["operants"]))
    step(ENGINE_ORDER[4], "canon_determination", lambda: run_canon_determination(envelope, registries["canons"]))
    step(ENGINE_ORDER[5], "coherence_engine", lambda: run_coherence_engine(envelope, registries["canons"]))
    step(ENGINE_ORDER[6], "llm_request_build", lambda: run_llm_request_build(envelope))
    step(ENGINE_ORDER[7], "llm_execution", lambda: run_llm_execution(
        envelope, _structured_client(model_client, model_version, trace)))
    step(ENGINE_ORDER[8], "coherence_2", lambda: run_coherence_2(envelope))
    step(ENGINE_ORDER[9], "structured_decision", lambda: run_structured_decision(envelope))
    envelope["action_request"] = {"action_id": "ACTION_NONE", "target_refs": []}
    envelope["impact_context"] = {"assessed_target_refs": [], "global_impact": "BENCH_ONLY", "risks": []}
    permissions = {"version": "1.0.0", "granted": []}; envelope["permissions"] = permissions
    catalog = _catalog(root)
    step(ENGINE_ORDER[10], "action_admissibility_and_plan",
         lambda: run_action_admissibility_and_plan(envelope, catalog, permissions))
    human, executor = _empty_authorities()
    step(ENGINE_ORDER[11], "trace_and_close", lambda: run_trace_and_close(
        envelope, catalog, permissions, human, executor, provenance_refs=["bench2://canonical-adapter"],
        ci_refs=["bench2://local"], closed_at_context="BENCH_2_CANARY"))
    natural = project_natural_response(envelope["llm_execution"]["response"])
    validate_ablation(disabled_engine, active) if disabled_engine else None
    return {"response": natural, "model_version": model_version, "engines_active": active,
            "engines_disabled": [disabled_engine] if disabled_engine else [], "engine_timings_ns": timings,
            "engine_statuses": [{"engine_id": engine, "status": outputs[key]["status"],
                                 "blocked_by": outputs[key].get("blocked_by")}
                                for engine, key in zip(ENGINE_ORDER, ("runtime_check", "object_discovery", "frame_selection",
                                "operants_operes", "canon_determination", "coherence_engine", "llm_request_build",
                                "llm_execution", "coherence_2", "structured_decision", "action_admissibility_and_plan",
                                "trace_and_close"))],
            "tokens_input": trace.get("model_metrics", {}).get("tokens_input", "UNAVAILABLE"),
            "tokens_output": trace.get("model_metrics", {}).get("tokens_output", "UNAVAILABLE"),
            "tokens_total": trace.get("model_metrics", {}).get("tokens_total", "UNAVAILABLE"),
            "time_to_first_token_ms": trace.get("model_metrics", {}).get("time_to_first_token_ms", "UNAVAILABLE"),
            "errors": [], "retries": trace.get("model_metrics", {}).get("retries", 0),
            "estimated_cost": trace.get("model_metrics", {}).get("estimated_cost", "UNAVAILABLE"),
            "adapter_trace": trace}
