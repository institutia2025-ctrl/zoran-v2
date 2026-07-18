"""Tests du câblage RÉEL cadre → ENGINE-04/05 → gate (package reconstructif isolé).

Exerce les 5 cas obligatoires via les VRAIS moteurs 04/05, la conservation des sorties
réelles dans la trace, la non-usurpation par label/attestation, et l'invariant
« aucun NON_PERTINENT / REDONDANT produit par 04/05 ».
"""
import copy

import pytest

from zoran_reconstructive.engine_0405_adapter import (
    ENGINE_04_KEY,
    ENGINE_05_KEY,
    derive_verdict_from_engine_outputs,
    evaluate_frame,
    project_frame,
    real_coherence_evaluator,
    run_real_engines,
)
from zoran_reconstructive.frame_coherence_gate import (
    ADMISSIBLE,
    ALLOWED_VERDICT_SOURCE,
    CONDITIONNEL,
    CONFLICTUEL,
    NON_VERIFIABLE,
    VERDICTS,
    evaluate_frame_admissibility,
    stable_engine_digest,
)


def _prov(tag="p"):
    return {
        "source_id": "src-" + tag,
        "source_version": "1",
        "source_digest": "d" * 8,
        "status": "VERIFIED",
    }


def _request(grounding=None, operants=None, relation_type="supports", frame_id="frame-A"):
    frame = {
        "frame_id": frame_id,
        "frame_version": "v1",
        "relation_type": relation_type,
        "provenance": _prov("frame"),
    }
    if grounding is not None:
        frame["grounding"] = grounding
    if operants is not None:
        frame["operants"] = operants
    return {
        "candidate_frame": frame,
        "current_state": {"loop_state": "SELECT"},
        "active_frames": [],
        "established_facts": [],
        "provenance": _prov("req"),
        "version": "FRAME_V1",
        "run_id": "RUN-1",
        "trace_id": "TRACE-1",
        "policy_version": "POLICY_V1",
    }


def _canon(cid, priority):
    return {"id": cid, "priority": priority, "provenance": _prov(cid)}


def _operant(oid):
    return {"id": oid, "provenance": _prov(oid)}


# ----------------------- Cas obligatoires (vrais moteurs) -----------------------


def test_case1_canonized_and_resolved_is_admissible():
    """1. projection valide, canonisée ET résolue (canon + opérant) → ADMISSIBLE."""
    trace = evaluate_frame(_request(
        grounding=[_canon("CANON_A", 10)],
        operants=[_operant("OP_A")],
    ))
    assert trace["verdict"] == ADMISSIBLE
    assert trace["integration"] is True
    assert trace["fail_closed"] is False
    # Sorties moteur RÉELLES conservées dans la trace.
    assert trace["engine_outputs"][ENGINE_04_KEY]["status"] == "PASS"
    assert trace["engine_outputs"][ENGINE_05_KEY]["coherence"]["resolved_pairs"] == 1
    assert trace["engine_outputs"][ENGINE_05_KEY]["coherence"]["total_pairs"] == 1


def test_case2_real_engine04_conflict_is_conflictuel():
    """2. deux canons de MÊME priorité → conflit RÉEL ENGINE-04 → CONFLICTUEL."""
    trace = evaluate_frame(_request(
        grounding=[_canon("CANON_A", 10), _canon("CANON_B", 10)],
        operants=[_operant("OP_A")],
    ))
    assert trace["verdict"] == CONFLICTUEL
    assert len(trace["engine_outputs"][ENGINE_04_KEY]["conflicts"]) >= 1
    assert trace["integration"] is False


def test_case3_uncanonized_is_conditionnel():
    """3. aucun canon applicable (grounding vide) → paire uncanonized → CONDITIONNEL."""
    trace = evaluate_frame(_request(grounding=[], operants=[_operant("OP_A")]))
    assert trace["verdict"] == CONDITIONNEL
    assert len(trace["engine_outputs"][ENGINE_04_KEY]["uncanonized"]) == 1
    assert trace["integration"] is False


def test_case4_canon_present_but_no_evidence_is_non_verifiable():
    """4. canon présent mais AUCUN opérant exploitable → NON_VERIFIABLE (pas NON_PERTINENT)."""
    trace = evaluate_frame(_request(grounding=[_canon("CANON_A", 10)], operants=[]))
    assert trace["verdict"] == NON_VERIFIABLE
    e04 = trace["engine_outputs"][ENGINE_04_KEY]
    assert e04["uncanonized"] == []  # canon bien présent
    assert trace["engine_outputs"][ENGINE_05_KEY]["coherence"]["resolved_pairs"] == 0


def test_case5a_missing_relation_type_fails_closed():
    """5. donnée absente (relation_type) → fail-closed NON_VERIFIABLE (projection avortée)."""
    req = _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")])
    del req["candidate_frame"]["relation_type"]
    trace = evaluate_frame(req)
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True


def test_case5b_engine_blocked_fails_closed():
    """5. moteur BLOCKED (id de canon dupliqué → registre invalide) → NON_VERIFIABLE."""
    trace = evaluate_frame(_request(
        grounding=[_canon("CANON_DUP", 10), _canon("CANON_DUP", 20)],
        operants=[_operant("OP_A")],
    ))
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True


def test_case5c_missing_provenance_input_fails_closed():
    """5. provenance de requête absente → NON_VERIFIABLE (garde d'entrée du gate)."""
    req = _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")])
    req["provenance"] = {}
    trace = evaluate_frame(req)
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["fail_closed"] is True


# ----------------------- Non-invention / provenance -----------------------


def test_grounding_without_provenance_is_excluded_not_invented():
    """Un canon sans provenance est EXCLU → la paire devient uncanonized (moteur décide)."""
    trace = evaluate_frame(_request(
        grounding=[{"id": "CANON_NOPROV", "priority": 10}],  # pas de provenance
        operants=[_operant("OP_A")],
    ))
    # Exclu du registre → aucun canon appliqué → uncanonized → CONDITIONNEL.
    assert trace["verdict"] == CONDITIONNEL
    assert trace["engine_outputs"][ENGINE_04_KEY]["canons_selected"] == []


def test_adapter_never_yields_non_pertinent_or_redondant():
    """Balayage : l'adaptateur ne produit jamais NON_PERTINENT ni REDONDANT."""
    cases = [
        _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")]),
        _request(grounding=[_canon("A", 10), _canon("B", 10)], operants=[_operant("OP_A")]),
        _request(grounding=[], operants=[_operant("OP_A")]),
        _request(grounding=[_canon("CANON_A", 10)], operants=[]),
    ]
    for req in cases:
        v = evaluate_frame(req)["verdict"]
        assert v in VERDICTS
        assert v not in ("NON_PERTINENT", "REDONDANT")


# ----------------------- Autorité non usurpable (attestations) -----------------------


def test_verdict_derived_by_gate_not_from_label():
    """Un label `verdict` auto-déclaré est IGNORÉ : le gate dérive des sorties réelles."""
    def _liar(request):
        ev = real_coherence_evaluator(request)  # vraies sorties (case 3 → CONDITIONNEL)
        ev["verdict"] = ADMISSIBLE  # label menteur
        return ev

    trace = evaluate_frame_admissibility(
        _request(grounding=[], operants=[_operant("OP_A")]),
        _liar,
        verdict_deriver=derive_verdict_from_engine_outputs,
    )
    assert trace["verdict"] == CONDITIONNEL  # dérivé, pas le label ADMISSIBLE


def test_tampered_engine_output_breaks_attestation():
    """Modifier une sortie moteur sans refaire le digest → attestation invalide → NON_VERIFIABLE."""
    def _tamper(request):
        ev = real_coherence_evaluator(request)
        # Falsifie la sortie 04 sans mettre à jour output_digest.
        ev["engine_outputs"][ENGINE_04_KEY]["conflicts"] = []
        ev["engine_outputs"][ENGINE_04_KEY]["uncanonized"] = []
        return ev

    trace = evaluate_frame_admissibility(
        _request(grounding=[_canon("A", 10), _canon("B", 10)], operants=[_operant("OP_A")]),
        _tamper,
        verdict_deriver=derive_verdict_from_engine_outputs,
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert "ATTESTATION" in trace["reason"]


def test_fake_source_from_bridge_rejected():
    """Une évaluation dont la source n'est pas ENGINES_04_05_08 est refusée."""
    def _bridge(request):
        ev = real_coherence_evaluator(request)
        ev["source"] = "BRIDGE"
        return ev

    trace = evaluate_frame_admissibility(
        _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")]),
        _bridge,
        verdict_deriver=derive_verdict_from_engine_outputs,
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert trace["reason"] == "AUTHORITY_VIOLATION"


def test_empty_engine_outputs_fail_closed():
    """Sorties moteur absentes (projection avortée) → attestations vides → NON_VERIFIABLE."""
    def _empty(request):
        return {"source": ALLOWED_VERDICT_SOURCE, "engine_outputs": {}, "attestations": []}

    trace = evaluate_frame_admissibility(
        _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")]),
        _empty,
        verdict_deriver=derive_verdict_from_engine_outputs,
    )
    assert trace["verdict"] == NON_VERIFIABLE
    assert "ATTESTATION" in trace["reason"]


# ----------------------- Déterminisme -----------------------


def test_deterministic_same_request_same_trace():
    req = _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")])
    t1 = evaluate_frame(req)
    t2 = evaluate_frame(copy.deepcopy(req))
    assert t1 == t2
    assert t1["trace_digest"] == t2["trace_digest"]


def test_attestation_digest_matches_embedded_output():
    """Le digest attesté correspond bien à la sortie moteur embarquée."""
    engine_outputs, attestations = run_real_engines(
        _request(grounding=[_canon("CANON_A", 10)], operants=[_operant("OP_A")])
    )
    for att in attestations:
        cid = att["component_id"]
        assert att["output_digest"] == stable_engine_digest(engine_outputs[cid])
