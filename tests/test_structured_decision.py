"""Tests déterministes de 09_STRUCTURED_DECISION (envelope 00→08 injectée).

Vérifie : admissibilité 08 (verdict==ACCEPT, authorize_09 is True strict), chaîne de fingerprint
04/07/08, revalidation 06/07, provenance, COUVERTURE EXACTE (P1), anti-fuite, déterminisme du
decision_id (payload canonique complet), fail-closed, gouvernance. 16 contre-exemples adversariaux.
"""
import copy

import pytest

from zoran_v2.structured_decision import (
    ACCEPT,
    BLOCKED,
    COVERAGE,
    DECISION_STATUS,
    DECISION_TYPE,
    FINGERPRINT_CHAIN,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    LEAK,
    NOT_ADMITTED,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE,
    PROVENANCE_DECL,
    REQUEST_MALFORMED,
    RESPONSE_MALFORMED,
    UPSTREAM_NOT_PASS,
    VERSION,
    run_structured_decision,
)

FP = "FP"


def _targets(tgts=None):
    return tgts if tgts is not None else [
        {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP"]}]


def _results(res=None):
    return res if res is not None else [
        {"object_public_id": "OBJ-0001", "frame": "CODE",
         "canon_findings": [{"canon": "C", "admissible": True}],
         "operant_outcomes": [{"operant": "OP", "applied": True}]}]


def _response(results=None, fingerprint=FP, schema="RESPONSE_STRUCTURED_ANALYSIS_V1",
              instruction_kind="STRUCTURED_ANALYSIS_V1"):
    return {"response_schema": schema, "instruction_kind": instruction_kind,
            "referential_fingerprint": fingerprint, "results": _results(results)}


def _env(verdict=ACCEPT, authorize_09=True, fp08=FP, fp04=FP, request_fp=FP,
         targets=None, response=None, executed=True, **over):
    req = {"referential_fingerprint": request_fp, "targets": _targets(targets)}
    base = {
        "runtime_check": {"status": "PASS"},
        "object_discovery": {"status": "PASS"},
        "frame_selection": {"status": "PASS"},
        "operants_operes": {"status": "PASS"},
        "canon_determination": {"status": "PASS", "canon_referential": {"fingerprint": fp04}},
        "coherence_engine": {"status": "PASS"},
        "llm_request_build": {"status": "PASS", "authorized": True, "llm_request": req},
        "llm_execution": {"status": "PASS", "executed": executed,
                          "response": response if response is not None else _response()},
        "coherence_2": {"status": "PASS", "verdict": verdict, "authorize_09": authorize_09,
                        "referential_fingerprint": fp08},
    }
    base.update(over)
    return base


# ---------- schéma & nominal ----------

def test_output_schema_exact():
    assert tuple(run_structured_decision(_env()).keys()) == OUTPUT_KEYS
    assert run_structured_decision(_env())["order_key"] == ORDER_KEY


def test_nominal_accept_emet_decision():
    v = run_structured_decision(_env())
    assert v["status"] == PASS and v["blocked_by"] is None
    d = v["decision"]
    assert d["decision_type"] == DECISION_TYPE and d["decision_status"] == DECISION_STATUS
    assert d["decision_id"].startswith("DECISION-") and len(d["decision_id"]) == len("DECISION-") + 64
    assert d["targets"] == [{"object_public_id": "OBJ-0001", "frame": "CODE"}]
    assert d["claims_retained"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "canon": "C"}]
    assert d["claims_rejected"] == []
    assert d["constraints"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "operant": "OP", "applied": True}]
    assert d["referential_fingerprint"] == FP and d["source_response_fingerprint"] == FP
    assert d["justification_refs"]["canon_refs"] == ["C"] and d["justification_refs"]["operant_refs"] == ["OP"]


def test_claim_rejete_verbatim():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": False}],
                               "operant_outcomes": [{"operant": "OP", "applied": False, "reason_code": "NOT_APPLICABLE"}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == PASS
    assert v["decision"]["claims_rejected"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "canon": "C"}]
    assert v["decision"]["claims_retained"] == []
    assert v["decision"]["constraints"][0]["reason_code"] == "NOT_APPLICABLE"


# ---------- 16 contre-exemples adversariaux (→ BLOCKED) ----------

def test_CE1_verdict_non_accept_bloque():
    for bad in ("REJECT", "QUARANTINE", None, "accept"):
        v = run_structured_decision(_env(verdict=bad))
        assert v["status"] == BLOCKED and v["blocked_by"] == NOT_ADMITTED, bad
        assert v["decision"] is None


def test_CE2_status_08_non_pass_bloque():
    env = _env()
    env["coherence_2"] = {**env["coherence_2"], "status": "BLOCKED"}
    v = run_structured_decision(env)
    assert v["status"] == BLOCKED and v["blocked_by"] == UPSTREAM_NOT_PASS and v["blocked_source"] == "08_COHERENCE_2"


def test_CE3_authorize_09_entier_1_bloque():
    v = run_structured_decision(_env(authorize_09=1))
    assert v["status"] == BLOCKED and v["blocked_by"] == NOT_ADMITTED


def test_CE4_authorize_09_str_true_bloque():
    v = run_structured_decision(_env(authorize_09="true"))
    assert v["status"] == BLOCKED and v["blocked_by"] == NOT_ADMITTED


def test_CE5_authorize_09_true_mais_verdict_reject_bloque():
    v = run_structured_decision(_env(verdict="REJECT", authorize_09=True))
    assert v["status"] == BLOCKED and v["blocked_by"] == NOT_ADMITTED


def test_CE6_fingerprint_08_diverge_de_04_bloque():
    v = run_structured_decision(_env(fp08="FP_A", fp04="FP_B"))
    assert v["status"] == BLOCKED and v["blocked_by"] == FINGERPRINT_CHAIN


def test_CE7_fingerprint_reponse_07_diverge_bloque():
    v = run_structured_decision(_env(response=_response(fingerprint="FP_X")))
    assert v["status"] == BLOCKED and v["blocked_by"] == RESPONSE_MALFORMED


def test_CE8_reponse_schema_invalide_bloque():
    bad = _response()
    del bad["results"]  # clé racine manquante
    v = run_structured_decision(_env(response=bad))
    assert v["status"] == BLOCKED and v["blocked_by"] == RESPONSE_MALFORMED


def test_CE9_canon_hors_attendu_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "INVENTED", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == BLOCKED and v["blocked_by"] == PROVENANCE


def test_CE10_operant_hors_attendu_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "INVENTED", "applied": True}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == BLOCKED and v["blocked_by"] == PROVENANCE


def test_CE11_opid_hors_cibles_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-9999", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == BLOCKED and v["blocked_by"] == PROVENANCE


def test_CE12_fuite_x1f_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C\x1fLEAK", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == BLOCKED and v["blocked_by"] == LEAK


def test_CE13_upstream_00_a_07_non_pass_bloque():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"), ("coherence_engine", "05_COHERENCE_ENGINE"),
                      ("llm_request_build", "06_LLM_REQUEST_BUILD"), ("llm_execution", "07_LLM_EXECUTION")):
        env = _env()
        env[key] = {**env[key], "status": "BLOCKED"}
        v = run_structured_decision(env)
        assert v["status"] == BLOCKED and v["blocked_by"] == UPSTREAM_NOT_PASS and v["blocked_source"] == comp, comp


def test_CE14_targets_06_malformees_bloque():
    for bad in ([{"object_public_id": "BAD", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}],
                [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"]}],  # clé manquante
                []):  # aucune cible
        v = run_structured_decision(_env(targets=bad))
        assert v["status"] == BLOCKED and v["blocked_by"] == REQUEST_MALFORMED, bad


def test_CE15_decision_id_deterministe():
    e = _env()
    a = run_structured_decision(e)["decision"]["decision_id"]
    b = run_structured_decision(_env())["decision"]["decision_id"]
    assert a == b  # mêmes entrées -> même id


def test_CE16_meme_fingerprint_contenu_different_id_different():
    # même referential_fingerprint FP mais contenu de réponse DIFFÉRENT (admissible True vs False) -> id DIFFÉRENT.
    r_true = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                                 "canon_findings": [{"canon": "C", "admissible": True}],
                                 "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    r_false = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                                  "canon_findings": [{"canon": "C", "admissible": False}],
                                  "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    id_t = run_structured_decision(_env(response=r_true))["decision"]["decision_id"]
    id_f = run_structured_decision(_env(response=r_false))["decision"]["decision_id"]
    assert id_t != id_f


# ---------- COUVERTURE EXACTE (P1) ----------

def test_couverture_partielle_bloque():
    # 06 attend 2 cibles ; la réponse n'en couvre qu'une -> BLOCKED(COVERAGE).
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}]
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    v = run_structured_decision(_env(targets=tgts, response=resp))
    assert v["status"] == BLOCKED and v["blocked_by"] == COVERAGE


def test_couverture_exacte_deux_cibles_passe():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}]
    res = [{"object_public_id": "OBJ-0001", "frame": "CODE",
            "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]},
           {"object_public_id": "OBJ-0002", "frame": "CODE",
            "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]}]
    v = run_structured_decision(_env(targets=tgts, response=_response(results=res)))
    assert v["status"] == PASS and len(v["decision"]["targets"]) == 2


# ---------- invariants divers ----------

def test_immutabilite_envelope():
    e = _env()
    snap = copy.deepcopy(e)
    run_structured_decision(e)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_structured_decision(None)


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], k
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-09-STRUCTURED-DECISION"
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_09_STRUCTURED_DECISION"


def test_garde_enumerante_preuves_consommees():
    """Chaque preuve consommée × un invariant violé -> BLOCKED (jamais PASS ni crash)."""
    cases = [
        ("08.verdict", _env(verdict="REJECT"), NOT_ADMITTED),
        ("08.authorize_09 strict", _env(authorize_09=1), NOT_ADMITTED),
        ("chain 04/08", _env(fp08="A", fp04="B"), FINGERPRINT_CHAIN),
        ("07.response fp", _env(response=_response(fingerprint="Z")), RESPONSE_MALFORMED),
        ("06.targets", _env(targets=[]), REQUEST_MALFORMED),
        ("06.request fp", _env(request_fp="Z"), REQUEST_MALFORMED),
        ("provenance canon", _env(response=_response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
            "canon_findings": [{"canon": "X", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]}])), PROVENANCE),
    ]
    for label, env, expected in cases:
        v = run_structured_decision(env)
        assert v["status"] == BLOCKED and v["blocked_by"] == expected, (label, v.get("blocked_by"))
