from pathlib import Path

import pytest

from bench_2.canonical_adapter import (
    AblationNotExecutable,
    AdapterError,
    RunIdRegistry,
    build_object_candidates,
    load_registries,
    project_natural_response,
    validate_ablation,
    validate_prompt_unchanged,
)


def test_absence_candidate_fails_closed():
    with pytest.raises(AdapterError, match="OBJECT_CANDIDATE_ABSENT"):
        build_object_candidates("")


def test_missing_registry_fails_closed(tmp_path):
    with pytest.raises(AdapterError, match="REGISTRY_MISSING"):
        load_registries(tmp_path)


def test_engine_still_active_fails_ablation():
    with pytest.raises(AblationNotExecutable, match="ENGINE_STILL_ACTIVE"):
        validate_ablation("05_COHERENCE_ENGINE", ["05_COHERENCE_ENGINE"])


def test_empty_projection_fails_closed():
    with pytest.raises(AdapterError, match="PROJECTION_EMPTY"):
        project_natural_response({"results": []})


def test_modified_prompt_fails_closed():
    with pytest.raises(AdapterError, match="PROMPT_MODIFIED"):
        validate_prompt_unchanged("original", "original ")


def test_double_run_id_fails():
    registry = RunIdRegistry()
    registry.claim("B2-run-1")
    with pytest.raises(AdapterError, match="DUPLICATE_RUN_ID"):
        registry.claim("B2-run-1")


def test_candidate_is_explicit_and_traceable():
    prompt = "Surface 1 240 m2 contre 1 180 m2."
    candidate = build_object_candidates(prompt)[0]
    assert candidate == {"kind": "text", "value": prompt,
                         "provenance": {"in_text": {"offset": 0, "len": len(prompt)}}}


def test_all_three_registries_load_from_existing_files():
    root = Path(__file__).parents[1]
    registries = load_registries(root)
    assert registries["frames"] and registries["operants"] and registries["canons"]


def test_dependency_exact_when_ablation_cannot_execute():
    with pytest.raises(AblationNotExecutable, match="depends_on=04_CANON_DETERMINATION"):
        validate_ablation("04_CANON_DETERMINATION", [], dependent="05_COHERENCE_ENGINE")
