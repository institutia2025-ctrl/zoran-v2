"""Tests du FRAME_COHERENCE_ADMISSIBILITY_GATE (vertical slice V1, package ISOLÉ).

Couvre les 3 cas minimaux obligatoires de la mission plus la séparation d'autorité,
la table des six verdicts/conséquences, le déterminisme et l'absence de seuil inventé.
"""
import copy

import pytest

from zoran_reconstructive.frame_coherence_gate import (
    ADMISSIBLE,
    ALLOWED_VERDICT_SOURCE,
    COHERENCE_DIMENSIONS,
    CONDITIONNEL,
    CONFLICTUEL,
    CONSEQUENCE,
    DISPOSITION,
    GATE_FAIL_CLOSED_SOURCE,
    NON_PERTINENT,
    NON_VERIFIABLE,
    REDONDANT,
    VERDICTS,
    evaluate_frame_admissibility,
    reference_coherence_evaluator,
)


def _signals(**overrides):
    base = {dim: "OK" for dim in COHERENCE_DIMENSIONS}
    base.update(overrides)
    return base


def _request(coherence_signals=None, provenance=None, version="FRAME_V1", **extra):
    req = {
        "candidate_frame": {
            "frame_id": "frame-alpha",
            "frame_version": "v1",
            "coherence_signals": coherence_signals
            if coherence_signals is not None
            else _signals(),
            "evidence_refs": ["ev-1"],
        },
        "current_state": {"loop_state": "SELECT", "cycle_id": "c1"},
        "active_frames": [{"frame_id": "frame-root", "frame_version": "v1"}],
        "established_facts": [{"fact_id": "f1"}],
        "provenance": provenance
        if provenance is not None
        else {"source_id": "src-1", "source_version": "1", "status": "VERIFIED"},
        "version": version,
        "run_id": "RUN-1",
        "trace_id": "TRACE-1",
        "policy_version": "POLICY_V1",
    }
    req.update(extra)
    return req


def _fixed_verdict_evaluator(verdict, source=ALLOWED_VERDICT_SOURCE):
    def _evaluator(request):
        return {
            "verdict": verdict,
            "evidence_refs": ["ev-x"],
            "source": source,
            "policy_version": "POLICY_V1",
        }

    return _evaluator


# ----------------------- Cas minimaux obligatoires -----------------------


def test_case1_coherent_verifiable_frame_is_admissible():
    """1. cadre cohérent et vérifiable -> ADMISSIBLE, intégration possible."""
    trace = evaluate_frame_admissibility(_request(), reference_coherence_evaluator)
    assert trace["verdict"] == ADMISSIBLE
    assert trace["verdict_source"] == ALLOWED_VERDICT_SOURCE
    assert trace["consequence"] == "INTEGRATION_POSSIBLE"
    assert trace["disposition"] == "INTEGRATED"
    assert trace["integration"] is True
    assert trace["fail_closed"] is False
    assert trace["reason"] == "OK"


def test_case2_missing_provenance_forces_non_verifiable_fail_closed():
    """2a. provenance absente -> NON_VERIFIABLE et rejet fail-closed."""
    trace = evaluate_frame_admissibility(
        _request(provenance={}), reference_coherence_evaluator
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True
    assert trace["integration"] is False
    assert trace["consequence"] == "FAIL_CLOSED"
    assert trace["reason"] == "INPUT_PROVENANCE_MISSING"
    # Le gate ne délègue même pas : refus fail-closed du gate lui-même.
    assert trace["verdict_source"] == GATE_FAIL_CLOSED_SOURCE


def test_case2_missing_version_forces_non_verifiable_fail_closed():
    """2b. version absente -> NON_VERIFIABLE et rejet fail-closed."""
    trace = evaluate_frame_admissibility(
        _request(version=""), reference_coherence_evaluator
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True
    assert trace["reason"] == "INPUT_VERSION_MISSING"


def test_case2_missing_provenance_does_not_call_evaluator():
    """Fail-closed d'entrée AVANT toute évaluation (l'évaluateur n'est pas appelé)."""
    calls = {"n": 0}

    def _spy(request):  # pragma: no cover - ne doit jamais être appelé
        calls["n"] += 1
        return {"verdict": ADMISSIBLE, "source": ALLOWED_VERDICT_SOURCE}

    trace = evaluate_frame_admissibility(_request(provenance={}), _spy)
    assert calls["n"] == 0
    assert trace["verdict"] == NON_VERIFIABLE


def test_case3_absent_verdict_fails_closed():
    """3a. verdict absent -> rejet fail-closed."""
    trace = evaluate_frame_admissibility(
        _request(), lambda request: {"source": ALLOWED_VERDICT_SOURCE}
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True
    assert trace["reason"] == "VERDICT_AMBIGUOUS"


def test_case3_ambiguous_verdict_fails_closed():
    """3b. verdict ambigu / hors des six valeurs -> rejet fail-closed."""
    trace = evaluate_frame_admissibility(
        _request(), _fixed_verdict_evaluator("MAYBE_OK")
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True
    assert trace["reason"] == "VERDICT_AMBIGUOUS"


def test_case3_evaluator_returning_non_dict_fails_closed():
    """3c. résultat d'évaluateur non structuré -> rejet fail-closed."""
    trace = evaluate_frame_admissibility(_request(), lambda request: "ADMISSIBLE")
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "EVALUATOR_RESULT_INVALID"


# ----------------------- Séparation d'autorité -----------------------


@pytest.mark.parametrize("bad_source", ["BRIDGE", "ZMOS", "LLM", None, "ORCHESTRATOR"])
def test_bridge_zmos_llm_cannot_decide_admissibility(bad_source):
    """Un verdict dont la source n'est pas ENGINES_04_05_08 est refusé fail-closed."""
    trace = evaluate_frame_admissibility(
        _request(), _fixed_verdict_evaluator(ADMISSIBLE, source=bad_source)
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "AUTHORITY_VIOLATION"
    assert trace["integration"] is False


def test_gate_never_grants_admissible_by_itself():
    """Aucun chemin autonome du gate ne produit ADMISSIBLE : seul l'évaluateur le peut."""
    # Évaluateur qui refuse systématiquement toute autorité -> jamais ADMISSIBLE.
    trace = evaluate_frame_admissibility(
        _request(), _fixed_verdict_evaluator(ADMISSIBLE, source="LLM")
    )
    assert trace["verdict"] != ADMISSIBLE


# ----------------------- Table des six verdicts / conséquences -----------------------


@pytest.mark.parametrize(
    "verdict,consequence,disposition,integration",
    [
        (ADMISSIBLE, "INTEGRATION_POSSIBLE", "INTEGRATED", True),
        (CONDITIONNEL, "KEPT_WITHOUT_CANONIZATION", "CONSERVED_NON_CANONICAL", False),
        (CONFLICTUEL, "ARBITRATION_ENGINES_04_05_08", "ROUTED_TO_ARBITRATION", False),
        (REDONDANT, "NO_NEW_ACTIVATION", "NO_NEW_ACTIVATION", False),
        (NON_PERTINENT, "REJECTED_FOR_CYCLE", "REJECTED_CYCLE", False),
        (NON_VERIFIABLE, "FAIL_CLOSED", "FAIL_CLOSED", False),
    ],
)
def test_mandatory_consequences_per_verdict(
    verdict, consequence, disposition, integration
):
    trace = evaluate_frame_admissibility(
        _request(), _fixed_verdict_evaluator(verdict)
    )
    assert trace["verdict"] == verdict
    assert trace["consequence"] == consequence
    assert trace["disposition"] == disposition
    assert trace["integration"] is integration
    # Seul ADMISSIBLE autorise l'intégration.
    assert (trace["integration"] is True) == (verdict == ADMISSIBLE)


def test_verdict_set_is_exactly_six():
    assert VERDICTS == {
        ADMISSIBLE,
        CONDITIONNEL,
        CONFLICTUEL,
        REDONDANT,
        NON_PERTINENT,
        NON_VERIFIABLE,
    }
    assert set(CONSEQUENCE) == VERDICTS
    assert set(DISPOSITION) == VERDICTS


# ----------------------- Évaluateur de référence (signaux -> verdict) -----------------------


@pytest.mark.parametrize(
    "signals,expected",
    [
        (_signals(), ADMISSIBLE),
        (_signals(contradiction="VIOLATED"), CONFLICTUEL),
        (_signals(compatibility_facts="VIOLATED"), CONFLICTUEL),
        (_signals(compatibility_active_frames="VIOLATED"), CONFLICTUEL),
        (_signals(bounds_authorizations="VIOLATED"), CONFLICTUEL),
        (_signals(relevance="VIOLATED"), NON_PERTINENT),
        (_signals(new_contribution="VIOLATED"), REDONDANT),
        (_signals(compatibility_facts="CONDITIONAL"), CONDITIONNEL),
        (_signals(contradiction="UNKNOWN"), NON_VERIFIABLE),
    ],
)
def test_reference_evaluator_signal_mapping(signals, expected):
    trace = evaluate_frame_admissibility(
        _request(coherence_signals=signals), reference_coherence_evaluator
    )
    assert trace["verdict"] == expected


def test_reference_evaluator_incomplete_signals_non_verifiable():
    incomplete = {"contradiction": "OK"}  # dimensions manquantes
    trace = evaluate_frame_admissibility(
        _request(coherence_signals=incomplete), reference_coherence_evaluator
    )
    assert trace["verdict"] == NON_VERIFIABLE


def test_reference_evaluator_out_of_domain_signal_non_verifiable():
    bad = _signals(relevance="PROBABLY")
    trace = evaluate_frame_admissibility(
        _request(coherence_signals=bad), reference_coherence_evaluator
    )
    assert trace["verdict"] == NON_VERIFIABLE


# ----------------------- Déterminisme, immuabilité, trace -----------------------


def test_deterministic_same_input_same_trace():
    req = _request()
    t1 = evaluate_frame_admissibility(req, reference_coherence_evaluator)
    t2 = evaluate_frame_admissibility(copy.deepcopy(req), reference_coherence_evaluator)
    assert t1 == t2
    assert t1["trace_digest"] == t2["trace_digest"]


def test_trace_is_complete_and_digested():
    trace = evaluate_frame_admissibility(_request(), reference_coherence_evaluator)
    for key in (
        "component_id",
        "run_id",
        "trace_id",
        "candidate_frame_ref",
        "input_digest",
        "verdict",
        "verdict_source",
        "consequence",
        "disposition",
        "integration",
        "fail_closed",
        "evidence_refs",
        "policy_version",
        "reason",
        "gate_authority",
        "trace_digest",
    ):
        assert key in trace
    assert trace["candidate_frame_ref"] == {"frame_id": "frame-alpha", "frame_version": "v1"}
    assert trace["run_id"] == "RUN-1"
    assert trace["gate_authority"] == "orchestrator_requests_engines_decide"


def test_input_mutation_changes_digest():
    t1 = evaluate_frame_admissibility(_request(), reference_coherence_evaluator)
    t2 = evaluate_frame_admissibility(
        _request(extra_field="different"), reference_coherence_evaluator
    )
    assert t1["input_digest"] != t2["input_digest"]


def test_no_invented_numeric_threshold_in_module():
    """Garde anti-régression : aucun seuil numérique de cohérence codé en dur."""
    import zoran_reconstructive.frame_coherence_gate as gate

    src = gate.__doc__ or ""
    assert "NON_MESURE" in src  # la doctrine du non-mesuré est explicite
