"""Tests du FRAME_COHERENCE_ADMISSIBILITY_GATE (vertical slice, package ISOLÉ).

Modèle d'autorité (post-fix bypass déclaratif) : une intégration n'est possible QUE via un
verdict DÉRIVÉ par le gate à partir de sorties moteur RÉELLES et ATTESTÉES. Aucun
`evaluation["verdict"]` auto-déclaré, et aucune absence de `verdict_deriver`, ne peut
autoriser `integration=true`.
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
    NON_PERTINENT,
    NON_VERIFIABLE,
    REDONDANT,
    VERDICTS,
    evaluate_frame_admissibility,
    reference_coherence_evaluator,
    stable_engine_digest,
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


# --- Évaluateur attesté minimal (chemin autoritaire) : porte des sorties moteur + digests. ---
def _attested_evaluator(engine_outputs, source=ALLOWED_VERDICT_SOURCE):
    attestations = [
        {
            "component_id": cid,
            "version": out.get("version", "1.0.0"),
            "status": out.get("status"),
            "output_digest": stable_engine_digest(out),
        }
        for cid, out in engine_outputs.items()
    ]

    def _ev(request):
        return {
            "source": source,
            "engine_outputs": engine_outputs,
            "attestations": attestations,
            "evidence_refs": ["ev-x"],
            "policy_version": "POLICY_V1",
        }

    return _ev


def _stub_deriver(verdict):
    return lambda engine_outputs: verdict


_OUTPUTS_OK = {"05_COHERENCE_ENGINE": {"status": "PASS", "version": "1.0.0", "v": 1}}


# ----------------------- CONTRE-TEST : bypass déclaratif Codex -----------------------


def test_codex_bypass_selfdeclared_verdict_without_deriver_is_non_verifiable():
    """Bypass Codex EXACT : verdict ADMISSIBLE auto-déclaré, sans sorties moteur, sans
    verdict_deriver. AVANT le fix -> integration=true. APRÈS -> NON_VERIFIABLE, integration=false."""
    def _liar(request):
        return {"source": ALLOWED_VERDICT_SOURCE, "verdict": ADMISSIBLE}  # aucune sortie moteur

    trace = evaluate_frame_admissibility(_request(), _liar)  # PAS de verdict_deriver
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "VERDICT_DERIVER_REQUIRED"


def test_codex_bypass_selfdeclared_verdict_with_deriver_but_no_outputs():
    """Même label menteur, mais avec un deriver permissif : bloqué car sorties moteur absentes."""
    def _liar(request):
        return {"source": ALLOWED_VERDICT_SOURCE, "verdict": ADMISSIBLE}

    trace = evaluate_frame_admissibility(
        _request(), _liar, verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert "ATTESTATION" in trace["reason"]


def test_selfdeclared_verdict_is_never_read_by_gate():
    """Même avec sorties attestées, un `verdict` auto-déclaré est ignoré : seul le deriver décide."""
    def _ev(request):
        base = _attested_evaluator(_OUTPUTS_OK)(request)
        base["verdict"] = ADMISSIBLE  # label menteur
        return base

    trace = evaluate_frame_admissibility(
        _request(), _ev, verdict_deriver=_stub_deriver(CONDITIONNEL)
    )
    assert trace["verdict"] == CONDITIONNEL  # dérivé, pas le label
    assert trace["integration"] is False


# ----------------------- verdict_deriver requis -----------------------


def test_no_deriver_even_with_attested_outputs_is_non_verifiable():
    """Sans verdict_deriver, aucune intégration : NON_VERIFIABLE même avec sorties attestées."""
    trace = evaluate_frame_admissibility(_request(), _attested_evaluator(_OUTPUTS_OK))
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "VERDICT_DERIVER_REQUIRED"


def test_reference_evaluator_is_non_authoritative():
    """L'évaluateur de référence ne porte pas de sorties moteur -> jamais d'intégration."""
    # sans deriver
    t1 = evaluate_frame_admissibility(_request(), reference_coherence_evaluator)
    assert t1["verdict"] == NON_VERIFIABLE and t1["integration"] is False
    # avec un deriver permissif : bloqué faute d'attestations
    t2 = evaluate_frame_admissibility(
        _request(), reference_coherence_evaluator, verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert t2["verdict"] == NON_VERIFIABLE and t2["integration"] is False


# ----------------------- Entrées fail-closed -----------------------


def test_missing_provenance_fails_closed_before_evaluator():
    calls = {"n": 0}

    def _spy(request):  # pragma: no cover — jamais appelé
        calls["n"] += 1
        return _attested_evaluator(_OUTPUTS_OK)(request)

    trace = evaluate_frame_admissibility(
        _request(provenance={}), _spy, verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert calls["n"] == 0
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "INPUT_PROVENANCE_MISSING"


def test_missing_version_fails_closed():
    trace = evaluate_frame_admissibility(
        _request(version=""), _attested_evaluator(_OUTPUTS_OK),
        verdict_deriver=_stub_deriver(ADMISSIBLE),
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "INPUT_VERSION_MISSING"


# ----------------------- Autorité & intégrité (chemin attesté) -----------------------


@pytest.mark.parametrize("bad_source", ["BRIDGE", "ZMOS", "LLM", None, "ORCHESTRATOR"])
def test_non_engine_source_rejected(bad_source):
    ev = _attested_evaluator(_OUTPUTS_OK, source=bad_source)
    trace = evaluate_frame_admissibility(
        _request(), ev, verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "AUTHORITY_VIOLATION"
    assert trace["integration"] is False


def test_tampered_output_breaks_attestation():
    engine_outputs = {"05_COHERENCE_ENGINE": {"status": "PASS", "version": "1.0.0", "v": 1}}
    ev = _attested_evaluator(engine_outputs)

    def _tamper(request):
        base = ev(request)
        base["engine_outputs"]["05_COHERENCE_ENGINE"]["v"] = 999  # sans refaire le digest
        return base

    trace = evaluate_frame_admissibility(
        _request(), _tamper, verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert "ATTESTATION" in trace["reason"]


def test_derivation_error_fails_closed():
    def _boom(engine_outputs):
        raise RuntimeError("boom")

    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(_OUTPUTS_OK), verdict_deriver=_boom
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "VERDICT_DERIVATION_ERROR"


def test_derived_verdict_out_of_set_fails_closed():
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(_OUTPUTS_OK), verdict_deriver=_stub_deriver("MAYBE")
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "VERDICT_AMBIGUOUS"


# ----------------------- Table des six verdicts / conséquences (via gate attesté) -----------------------


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
def test_mandatory_consequences_per_verdict(verdict, consequence, disposition, integration):
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(_OUTPUTS_OK), verdict_deriver=_stub_deriver(verdict)
    )
    assert trace["verdict"] == verdict
    assert trace["consequence"] == consequence
    assert trace["disposition"] == disposition
    assert trace["integration"] is integration
    assert (trace["integration"] is True) == (verdict == ADMISSIBLE)


def test_verdict_set_and_maps_are_exactly_six():
    assert VERDICTS == {
        ADMISSIBLE, CONDITIONNEL, CONFLICTUEL, REDONDANT, NON_PERTINENT, NON_VERIFIABLE,
    }
    assert set(CONSEQUENCE) == VERDICTS
    assert set(DISPOSITION) == VERDICTS
    # Seul ADMISSIBLE porte l'intégration.
    assert CONSEQUENCE[ADMISSIBLE] == "INTEGRATION_POSSIBLE"


# ----------------------- Évaluateur de référence : mapping ILLUSTRATIF (appel direct) -----------------------


@pytest.mark.parametrize(
    "signals,expected_hint",
    [
        (_signals(), ADMISSIBLE),
        (_signals(contradiction="VIOLATED"), CONFLICTUEL),
        (_signals(relevance="VIOLATED"), NON_PERTINENT),
        (_signals(new_contribution="VIOLATED"), REDONDANT),
        (_signals(compatibility_facts="CONDITIONAL"), CONDITIONNEL),
        (_signals(contradiction="UNKNOWN"), NON_VERIFIABLE),
    ],
)
def test_reference_mapping_is_illustrative_hint_only(signals, expected_hint):
    # Appel DIRECT : on inspecte l'indice, sans passer par le gate (non autoritatif).
    hint = reference_coherence_evaluator(_request(coherence_signals=signals))["verdict"]
    assert hint == expected_hint


# ----------------------- Déterminisme & trace -----------------------


def test_deterministic_same_input_same_trace():
    ev = _attested_evaluator(_OUTPUTS_OK)
    req = _request()
    t1 = evaluate_frame_admissibility(req, ev, verdict_deriver=_stub_deriver(CONDITIONNEL))
    t2 = evaluate_frame_admissibility(
        copy.deepcopy(req), ev, verdict_deriver=_stub_deriver(CONDITIONNEL)
    )
    assert t1 == t2
    assert t1["trace_digest"] == t2["trace_digest"]


def test_trace_is_complete_and_conserves_engine_outputs():
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(_OUTPUTS_OK), verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    for key in (
        "component_id", "run_id", "trace_id", "candidate_frame_ref", "input_digest",
        "verdict", "verdict_source", "consequence", "disposition", "integration",
        "fail_closed", "evidence_refs", "policy_version", "reason", "gate_authority",
        "engine_outputs", "engine_attestations", "trace_digest",
    ):
        assert key in trace
    assert trace["engine_outputs"] == _OUTPUTS_OK  # sorties réelles conservées
    assert trace["engine_attestations"] is not None


def test_fail_closed_trace_has_no_engine_outputs():
    trace = evaluate_frame_admissibility(_request(provenance={}), reference_coherence_evaluator)
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["engine_outputs"] is None
    assert trace["integration"] is False
