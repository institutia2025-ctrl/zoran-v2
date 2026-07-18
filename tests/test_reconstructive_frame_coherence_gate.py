"""Tests du FRAME_COHERENCE_ADMISSIBILITY_GATE (vertical slice, package ISOLÉ).

Modèle d'autorité (post-fix) : une intégration n'est possible QUE via un verdict DÉRIVÉ par
le gate à partir des sorties CONJOINTES, IDENTIFIÉES et ATTESTÉES des moteurs EXACTEMENT
requis (04 ET 05). Aucun `evaluation["verdict"]` auto-déclaré, aucune absence de
`verdict_deriver`, aucun ensemble de moteurs incomplet/étranger ne peut autoriser
`integration=true`.
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

_ENGINE_04 = "04_CANON_DETERMINATION"
_ENGINE_05 = "05_COHERENCE_ENGINE"
_REQUIRED = [
    {"component_id": _ENGINE_04, "version": "1.0.0"},
    {"component_id": _ENGINE_05, "version": "1.0.0"},
]
_OUTPUTS_OK = {
    _ENGINE_04: {"component": _ENGINE_04, "version": "1.0.0", "status": "PASS", "x": 1},
    _ENGINE_05: {"component": _ENGINE_05, "version": "1.0.0", "status": "PASS", "y": 2},
}


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


def _attestations(engine_outputs):
    return [
        {
            "component_id": cid,
            "version": out.get("version"),
            "status": out.get("status"),
            "output_digest": stable_engine_digest(out),
        }
        for cid, out in engine_outputs.items()
    ]


def _attested_evaluator(engine_outputs=None, source=ALLOWED_VERDICT_SOURCE, extra=None):
    outputs = _OUTPUTS_OK if engine_outputs is None else engine_outputs

    def _ev(request):
        ev = {
            "source": source,
            "engine_outputs": outputs,
            "attestations": _attestations(outputs),
            "evidence_refs": ["ev-x"],
            "policy_version": "POLICY_V1",
        }
        if extra:
            ev.update(extra)
        return ev

    return _ev


def _stub_deriver(verdict):
    return lambda engine_outputs: verdict


def _authorized(request, verdict, evaluator=None):
    return evaluate_frame_admissibility(
        request,
        evaluator if evaluator is not None else _attested_evaluator(),
        verdict_deriver=_stub_deriver(verdict),
        required_engines=_REQUIRED,
    )


# ----------------------- CONTRE-TEST : bypass déclaratif -----------------------


def test_selfdeclared_verdict_without_deriver_is_non_verifiable():
    """Verdict ADMISSIBLE auto-déclaré, sans sorties moteur, sans deriver -> NON_VERIFIABLE."""
    def _liar(request):
        return {"source": ALLOWED_VERDICT_SOURCE, "verdict": ADMISSIBLE}

    trace = evaluate_frame_admissibility(_request(), _liar)  # PAS de verdict_deriver
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "VERDICT_DERIVER_REQUIRED"


def test_selfdeclared_verdict_is_never_read_by_gate():
    """Un `verdict` auto-déclaré est ignoré même avec sorties attestées : seul le deriver décide."""
    trace = _authorized(
        _request(), CONDITIONNEL,
        evaluator=_attested_evaluator(extra={"verdict": ADMISSIBLE}),
    )
    assert trace["verdict"] == CONDITIONNEL
    assert trace["integration"] is False


# ----------------------- verdict_deriver & required_engines requis -----------------------


def test_no_deriver_even_with_attested_outputs_is_non_verifiable():
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(), required_engines=_REQUIRED
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "VERDICT_DERIVER_REQUIRED"


def test_required_engines_absent_uses_frozen_canonical_set():
    """Post-fix: l'ensemble des moteurs est FIGÉ dans le gate. Un appelant qui n'envoie
    aucun `required_engines` n'invalide plus rien : le gate applique son contrat canonique
    interne (04+05) et dérive un verdict à partir des sorties réelles attestées."""
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(), verdict_deriver=_stub_deriver(ADMISSIBLE)
    )
    assert trace["verdict"] == ADMISSIBLE
    assert trace["integration"] is True


def test_caller_supplied_required_engines_cannot_substitute_authority():
    """CONTRE-TEST MISSION (ZORAN_0405_GATE_CANONICAL_ENGINE_IDENTITY_FIX_V1).

    required_engines = [ATTACKER@9], sortie ATTACKER auto-attestée, deriver permissif.
    Attendu : NON_VERIFIABLE, integration=false, deriver_calls=0.
    """
    deriver_calls = {"n": 0}

    def _permissive(engine_outputs):  # deriver permissif : accorderait ADMISSIBLE
        deriver_calls["n"] += 1
        return ADMISSIBLE

    attacker_outputs = {
        "ATTACKER": {"component": "ATTACKER", "version": "9", "status": "PASS", "z": 1}
    }
    trace = evaluate_frame_admissibility(
        _request(),
        _attested_evaluator(engine_outputs=attacker_outputs),  # ATTACKER auto-attesté
        verdict_deriver=_permissive,
        required_engines=[{"component_id": "ATTACKER", "version": "9"}],
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "REQUIRED_ENGINES_NOT_CANONICAL"
    assert deriver_calls["n"] == 0


def test_rogue_evaluator_outputs_rejected_against_canonical_set():
    """Défense en profondeur : même sans substitution de `required_engines`, un évaluateur
    qui émet des sorties de moteur NON canoniques est rejeté (ensemble != 04+05), sans
    appeler le deriver."""
    deriver_calls = {"n": 0}

    def _permissive(engine_outputs):
        deriver_calls["n"] += 1
        return ADMISSIBLE

    attacker_outputs = {
        "ATTACKER": {"component": "ATTACKER", "version": "9", "status": "PASS", "z": 1}
    }
    trace = evaluate_frame_admissibility(
        _request(),
        _attested_evaluator(engine_outputs=attacker_outputs),
        verdict_deriver=_permissive,  # aucun required_engines fourni
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "ENGINE_ATTESTATION_ENGINE_SET_MISMATCH"
    assert deriver_calls["n"] == 0


def test_wrong_engine_version_is_rejected_against_frozen_canonical():
    """Un ensemble 04+05 mais à une VERSION incorrecte (ex. 04@9.9.9) est une substitution
    non canonique -> fail-closed avant tout appel deriver."""
    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(), verdict_deriver=_stub_deriver(ADMISSIBLE),
        required_engines=[
            {"component_id": _ENGINE_04, "version": "9.9.9"},
            {"component_id": _ENGINE_05, "version": "1.0.0"},
        ],
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["integration"] is False
    assert trace["reason"] == "REQUIRED_ENGINES_NOT_CANONICAL"


def test_reference_evaluator_is_non_authoritative():
    t1 = evaluate_frame_admissibility(_request(), reference_coherence_evaluator)
    assert t1["verdict"] == NON_VERIFIABLE and t1["integration"] is False
    t2 = evaluate_frame_admissibility(
        _request(), reference_coherence_evaluator,
        verdict_deriver=_stub_deriver(ADMISSIBLE), required_engines=_REQUIRED,
    )
    assert t2["verdict"] == NON_VERIFIABLE and t2["integration"] is False


# ----------------------- Entrées fail-closed -----------------------


def test_missing_provenance_fails_closed_before_evaluator():
    calls = {"n": 0}

    def _spy(request):  # pragma: no cover — jamais appelé
        calls["n"] += 1
        return _attested_evaluator()(request)

    trace = evaluate_frame_admissibility(
        _request(provenance={}), _spy,
        verdict_deriver=_stub_deriver(ADMISSIBLE), required_engines=_REQUIRED,
    )
    assert calls["n"] == 0
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "INPUT_PROVENANCE_MISSING"


def test_missing_version_fails_closed():
    trace = _authorized(_request(version=""), ADMISSIBLE)
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "INPUT_VERSION_MISSING"


# ----------------------- Autorité & intégrité -----------------------


@pytest.mark.parametrize("bad_source", ["BRIDGE", "ZMOS", "LLM", None, "ORCHESTRATOR"])
def test_non_engine_source_rejected(bad_source):
    trace = _authorized(
        _request(), ADMISSIBLE, evaluator=_attested_evaluator(source=bad_source)
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "AUTHORITY_VIOLATION"
    assert trace["integration"] is False


def test_derivation_error_fails_closed():
    def _boom(engine_outputs):
        raise RuntimeError("boom")

    trace = evaluate_frame_admissibility(
        _request(), _attested_evaluator(), verdict_deriver=_boom, required_engines=_REQUIRED
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "VERDICT_DERIVATION_ERROR"


def test_derived_verdict_out_of_set_fails_closed():
    trace = _authorized(_request(), "MAYBE")
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "VERDICT_AMBIGUOUS"


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
def test_mandatory_consequences_per_verdict(verdict, consequence, disposition, integration):
    trace = _authorized(_request(), verdict)
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
    hint = reference_coherence_evaluator(_request(coherence_signals=signals))["verdict"]
    assert hint == expected_hint


# ----------------------- Déterminisme & trace -----------------------


def test_deterministic_same_input_same_trace():
    req = _request()
    t1 = _authorized(req, CONDITIONNEL)
    t2 = _authorized(copy.deepcopy(req), CONDITIONNEL)
    assert t1 == t2
    assert t1["trace_digest"] == t2["trace_digest"]


def test_trace_is_complete_and_conserves_engine_outputs():
    trace = _authorized(_request(), ADMISSIBLE)
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
