"""Tests déterministes de 09_STRUCTURED_DECISION (envelope 00→08 injectée).

Vérifie : admissibilité 08 (verdict==ACCEPT, authorize_09 is True strict), chaîne fingerprint 04/07/08,
revalidation 06/07, provenance, COUVERTURE EXACTE (P1), anti-fuite, objet final PLAT (P-C2),
decision_id + CONTENT_SHA256 via la primitive canonique `_fingerprint` (aucun second hasher),
construction 2 phases, conservation EXACTE des chaînes (NFC/NFD, CRLF/LF, ordre des clés), fail-closed.
"""
import copy
import unicodedata

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
    run_structured_decision,
)

FP = "FP"


def _code(v):
    return (v["blocked_by"] or "").split("@")[0]


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

def test_output_schema_plat_16_cles():
    assert tuple(run_structured_decision(_env()).keys()) == OUTPUT_KEYS
    assert tuple(run_structured_decision(_env(verdict="REJECT")).keys()) == OUTPUT_KEYS  # BLOCKED : même schéma
    assert run_structured_decision(_env())["order_key"] == ORDER_KEY


def test_nominal_accept_emet_decision():
    v = run_structured_decision(_env())
    assert v["status"] == PASS and v["blocked_by"] is None
    assert v["decision_type"] == DECISION_TYPE and v["decision_status"] == DECISION_STATUS
    assert v["decision_id"].startswith("DECISION-") and len(v["decision_id"]) == len("DECISION-") + 64
    assert v["targets"] == [{"object_public_id": "OBJ-0001", "frame": "CODE"}]
    assert v["claims_retained"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "canon": "C"}]
    assert v["claims_rejected"] == []
    assert v["constraints"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "operant": "OP", "applied": True}]
    assert v["referential_fingerprint"] == FP and v["source_response_fingerprint"] == FP
    assert v["justification_refs"]["canon_refs"] == ["C"] and v["justification_refs"]["operant_refs"] == ["OP"]
    assert isinstance(v["CONTENT_SHA256"], str) and len(v["CONTENT_SHA256"]) == 64


def test_content_sha256_exclut_son_propre_champ():
    # CONTENT_SHA256 est calculé sur l'objet final SANS le champ CONTENT_SHA256 (P-C2) : non auto-référent.
    v = run_structured_decision(_env())
    obj_sans = {k: v[k] for k in OUTPUT_KEYS if k != "CONTENT_SHA256"}
    from zoran_v2.structured_decision import _canonical_sha256
    recompute = _canonical_sha256(obj_sans)
    assert v["CONTENT_SHA256"] == recompute


def test_claim_rejete_verbatim():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": False}],
                               "operant_outcomes": [{"operant": "OP", "applied": False, "reason_code": "NOT_APPLICABLE"}]}])
    v = run_structured_decision(_env(response=resp))
    assert v["status"] == PASS
    assert v["claims_rejected"] == [{"object_public_id": "OBJ-0001", "frame": "CODE", "canon": "C"}]
    assert v["claims_retained"] == []
    assert v["constraints"][0]["reason_code"] == "NOT_APPLICABLE"


# ---------- 16 contre-exemples adversariaux (→ BLOCKED) ----------

def test_CE1_verdict_non_accept_bloque():
    for bad in ("REJECT", "QUARANTINE", None, "accept"):
        v = run_structured_decision(_env(verdict=bad))
        assert v["status"] == BLOCKED and _code(v) == NOT_ADMITTED, bad
        assert v["decision_id"] is None


def test_CE2_status_08_non_pass_bloque():
    env = _env()
    env["coherence_2"] = {**env["coherence_2"], "status": "BLOCKED"}
    v = run_structured_decision(env)
    assert v["status"] == BLOCKED and _code(v) == UPSTREAM_NOT_PASS and v["blocked_by"].endswith("@08_COHERENCE_2")


def test_CE3_authorize_09_entier_1_bloque():
    assert _code(run_structured_decision(_env(authorize_09=1))) == NOT_ADMITTED


def test_CE4_authorize_09_str_true_bloque():
    assert _code(run_structured_decision(_env(authorize_09="true"))) == NOT_ADMITTED


def test_CE5_authorize_09_true_mais_verdict_reject_bloque():
    assert _code(run_structured_decision(_env(verdict="REJECT", authorize_09=True))) == NOT_ADMITTED


def test_CE6_fingerprint_08_diverge_de_04_bloque():
    assert _code(run_structured_decision(_env(fp08="FP_A", fp04="FP_B"))) == FINGERPRINT_CHAIN


def test_CE7_fingerprint_reponse_07_diverge_bloque():
    assert _code(run_structured_decision(_env(response=_response(fingerprint="FP_X")))) == RESPONSE_MALFORMED


def test_CE8_reponse_schema_invalide_bloque():
    bad = _response()
    del bad["results"]
    assert _code(run_structured_decision(_env(response=bad))) == RESPONSE_MALFORMED


def test_CE9_canon_hors_attendu_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "INVENTED", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    assert _code(run_structured_decision(_env(response=resp))) == PROVENANCE


def test_CE10_operant_hors_attendu_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "INVENTED", "applied": True}]}])
    assert _code(run_structured_decision(_env(response=resp))) == PROVENANCE


def test_CE11_opid_hors_cibles_06_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-9999", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    assert _code(run_structured_decision(_env(response=resp))) == PROVENANCE


def test_CE12_fuite_x1f_bloque():
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C\x1fLEAK", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    assert _code(run_structured_decision(_env(response=resp))) == LEAK


def test_CE13_upstream_non_pass_bloque():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"), ("coherence_engine", "05_COHERENCE_ENGINE"),
                      ("llm_request_build", "06_LLM_REQUEST_BUILD"), ("llm_execution", "07_LLM_EXECUTION")):
        env = _env()
        env[key] = {**env[key], "status": "BLOCKED"}
        v = run_structured_decision(env)
        assert v["status"] == BLOCKED and _code(v) == UPSTREAM_NOT_PASS and v["blocked_by"].endswith("@" + comp), comp


def test_CE14_targets_06_malformees_bloque():
    for bad in ([{"object_public_id": "BAD", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}],
                [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"]}],
                []):
        assert _code(run_structured_decision(_env(targets=bad))) == REQUEST_MALFORMED, bad


def test_CE15_decision_id_et_content_deterministes():
    a = run_structured_decision(_env())
    b = run_structured_decision(_env())
    assert a["decision_id"] == b["decision_id"] and a["CONTENT_SHA256"] == b["CONTENT_SHA256"]


def test_CE16_meme_fingerprint_contenu_different_id_different():
    r_true = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                                 "canon_findings": [{"canon": "C", "admissible": True}],
                                 "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    r_false = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                                  "canon_findings": [{"canon": "C", "admissible": False}],
                                  "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    id_t = run_structured_decision(_env(response=r_true))["decision_id"]
    id_f = run_structured_decision(_env(response=r_false))["decision_id"]
    assert id_t != id_f


# ---------- T-2 : conservation EXACTE des chaînes (point 2 Fred) ----------

def _env_for_canon(canon):
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": [canon], "operants": ["OP"]}]
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": canon, "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    return _env(targets=tgts, response=resp)


def test_T2_nfc_vs_nfd_ids_differents():
    base = "café"  # é = U+00E9
    nfc = run_structured_decision(_env_for_canon(unicodedata.normalize("NFC", base)))
    nfd = run_structured_decision(_env_for_canon(unicodedata.normalize("NFD", base)))
    assert nfc["status"] == PASS and nfd["status"] == PASS
    assert nfc["decision_id"] != nfd["decision_id"]                # conservation exacte -> ids différents


def test_T2_crlf_vs_lf_ids_differents():
    crlf = run_structured_decision(_env_for_canon("A\r\nB"))
    lf = run_structured_decision(_env_for_canon("A\nB"))
    assert crlf["status"] == PASS and lf["status"] == PASS
    assert crlf["decision_id"] != lf["decision_id"]


def test_T2_ordre_des_cles_json_id_identique():
    # même contenu logique, ordre d'INSERTION des clés différent (résultat + cible) -> MÊME decision_id.
    r1 = {"object_public_id": "OBJ-0001", "frame": "CODE",
          "canon_findings": [{"canon": "C", "admissible": True}],
          "operant_outcomes": [{"operant": "OP", "applied": True}]}
    r2 = {"operant_outcomes": [{"applied": True, "operant": "OP"}],
          "canon_findings": [{"admissible": True, "canon": "C"}],
          "frame": "CODE", "object_public_id": "OBJ-0001"}
    t1 = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}]
    t2 = [{"operants": ["OP"], "canons": ["C"], "frame": "CODE", "kind_public": "code", "object_public_id": "OBJ-0001"}]
    a = run_structured_decision(_env(targets=t1, response=_response(results=[r1])))
    b = run_structured_decision(_env(targets=t2, response=_response(results=[r2])))
    assert a["status"] == PASS and b["status"] == PASS
    assert a["decision_id"] == b["decision_id"]


# ---------- COUVERTURE EXACTE (P1) ----------

def test_couverture_partielle_bloque():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}]
    resp = _response(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                               "canon_findings": [{"canon": "C", "admissible": True}],
                               "operant_outcomes": [{"operant": "OP", "applied": True}]}])
    assert _code(run_structured_decision(_env(targets=tgts, response=resp))) == COVERAGE


def test_couverture_exacte_deux_cibles_passe():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE", "canons": ["C"], "operants": ["OP"]}]
    res = [{"object_public_id": "OBJ-0001", "frame": "CODE",
            "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]},
           {"object_public_id": "OBJ-0002", "frame": "CODE",
            "canon_findings": [{"canon": "C", "admissible": True}], "operant_outcomes": [{"operant": "OP", "applied": True}]}]
    v = run_structured_decision(_env(targets=tgts, response=_response(results=res)))
    assert v["status"] == PASS and len(v["targets"]) == 2


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
        assert v["status"] == BLOCKED and _code(v) == expected, (label, v.get("blocked_by"))
