"""Tests déterministes de 08_COHERENCE_2 (2e passe de cohérence post-LLM, réponses mock).

Vérifie le contrat FIGÉ : validation stricte de RESPONSE_STRUCTURED_ANALYSIS_V1, provenance
04/06, fingerprint, anti-fuite récursive, split BLOCKED/REJECT/QUARANTINE/ACCEPT, formule
canonique post-LLM, cinématique, déterminisme, immuabilité, gouvernance.
"""
import copy

import pytest

from zoran_v2.coherence_2 import (
    ACCEPT,
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    QUARANTINE,
    REJECT,
    RESPONSE_SCHEMA_ID,
    VERSION,
    run_coherence_2,
)


def _req_06(tgts, fingerprint="FP", s_pre=0.5, **over):
    """Requête AUTORITAIRE 06 COMPLÈTE et valide (schéma exact). `over` pour dégrader un champ."""
    frames = sorted({t["frame"] for t in tgts if isinstance(t, dict) and isinstance(t.get("frame"), str)})
    req = {
        "instruction_kind": "STRUCTURED_ANALYSIS_V1",
        "referential_fingerprint": fingerprint,
        "coherence_S": s_pre,
        "frames": frames,
        "targets": tgts,
        "pii_policy": "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT",
    }
    req.update(over)
    return req


def _env(response=None, s_pre=0.5, targets=None, executed=True, fingerprint="FP",
         request=None, **status_overrides):
    tgts = targets if targets is not None else [
        {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP_A"]}]
    req = request if request is not None else _req_06(tgts, fingerprint=fingerprint, s_pre=s_pre)
    base = {
        "runtime_check": {"status": "PASS"},
        "object_discovery": {"status": "PASS"},
        "frame_selection": {"status": "PASS"},
        "operants_operes": {"status": "PASS"},
        "canon_determination": {"status": "PASS",
                                "canon_referential": {"fingerprint": fingerprint, "canons": []}},
        "coherence_engine": {"status": "PASS", "coherence": {"S": s_pre}},
        "llm_request_build": {"status": "PASS", "authorized": True, "llm_request": req},
        "llm_execution": {"status": "PASS", "executed": executed,
                          "response": response if response is not None else _resp()},
    }
    base.update(status_overrides)
    return base


def _resp(results=None, fingerprint="FP", schema=RESPONSE_SCHEMA_ID,
          instruction_kind="STRUCTURED_ANALYSIS_V1"):
    if results is None:
        results = [{"object_public_id": "OBJ-0001", "frame": "CODE",
                    "canon_findings": [{"canon": "C", "admissible": True}],
                    "operant_outcomes": [{"operant": "OP_A", "applied": True}]}]
    return {"response_schema": schema, "instruction_kind": instruction_kind,
            "referential_fingerprint": fingerprint, "results": results}


# ---------- schéma de sortie ----------

def test_output_schema_exact_pass_et_blocked():
    assert tuple(run_coherence_2(_env()).keys()) == OUTPUT_KEYS
    assert tuple(run_coherence_2(_env(runtime_check={"status": "FAIL"})).keys()) == OUTPUT_KEYS
    assert run_coherence_2(_env())["order_key"] == ORDER_KEY


# ---------- BLOCKED (prérequis pipeline) ----------

def test_blocked_fail_closed_00_a_07():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"),
                      ("object_discovery", "01_OBJECT_DISCOVERY"),
                      ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
                      ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
                      ("canon_determination", "04_CANON_DETERMINATION"),
                      ("coherence_engine", "05_COHERENCE_ENGINE"),
                      ("llm_request_build", "06_LLM_REQUEST_BUILD"),
                      ("llm_execution", "07_LLM_EXECUTION")):
        v = run_coherence_2(_env(**{key: {"status": "BLOCKED"}}))
        assert v["status"] == BLOCKED and v["blocked_by"] == comp
        assert v["verdict"] is None and v["coherence_post"] is None and v["authorize_09"] is False


def test_blocked_07_non_execute():
    from zoran_v2.coherence_2 import NOT_EXECUTED
    v = run_coherence_2(_env(executed=False))
    assert v["status"] == BLOCKED and v["blocked_by"] == NOT_EXECUTED


def test_blocked_fingerprint_04_absent():
    from zoran_v2.coherence_2 import FINGERPRINT_MISSING
    env = _env()
    env["canon_determination"]["canon_referential"] = {"fingerprint": "", "canons": []}
    v = run_coherence_2(env)
    assert v["status"] == BLOCKED and v["blocked_by"] == FINGERPRINT_MISSING


def test_blocked_enveloppe_malformee_requete_absente():
    from zoran_v2.coherence_2 import ENVELOPE_MALFORMED
    env = _env()
    env["llm_request_build"]["llm_request"] = {"targets": []}  # aucune cible
    v = run_coherence_2(env)
    assert v["status"] == BLOCKED and v["blocked_by"] == ENVELOPE_MALFORMED


def test_blocked_s_pre_absent():
    from zoran_v2.coherence_2 import ENVELOPE_MALFORMED
    env = _env()
    env["coherence_engine"]["coherence"] = {"S": None}
    v = run_coherence_2(env)
    assert v["status"] == BLOCKED and v["blocked_by"] == ENVELOPE_MALFORMED


# --- Frontière 06->08 : re-validation STRICTE de la requête autoritaire (GC-08-001/002/003) ---

def _assert_blocked_malformed(request):
    from zoran_v2.coherence_2 import ENVELOPE_MALFORMED
    v = run_coherence_2(_env(request=request))
    assert v["status"] == BLOCKED and v["blocked_by"] == ENVELOPE_MALFORMED and v["authorize_09"] is False


def test_blocked_06_schema_racine_incomplet():
    _assert_blocked_malformed({"targets": [
        {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP_A"]}]})  # clés racine manquantes


def test_blocked_06_instruction_kind_faux():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts, instruction_kind="AUTRE"))


def test_blocked_06_pii_policy_faux():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts, pii_policy="DISABLED"))


def test_blocked_06_fingerprint_divergent_du_04():
    # Contre-exemple ChatGPT GC-08-001 : requête 06 avec un fingerprint != 04 gelé -> BLOCKED,
    # même si la réponse 07 utilisait le vrai fingerprint 04.
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts, referential_fingerprint="FAUX"))


def test_blocked_06_object_public_id_non_opaque():
    for bad_id in ("code-jean", "OBJ-1", "obj-0001", "jean"):
        tgts = [{"object_public_id": bad_id, "kind_public": "code", "frame": "CODE",
                 "canons": ["C"], "operants": ["OP_A"]}]
        _assert_blocked_malformed(_req_06(tgts))


def test_blocked_06_canons_conteneur_malforme():
    # GC-08-003 : conteneur falsy/partiellement malformé ne doit PAS être normalisé silencieusement.
    for bad in ({}, "", [12, None, "C"], "CANON"):
        tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
                 "canons": bad, "operants": ["OP_A"]}]
        _assert_blocked_malformed(_req_06(tgts))


def test_blocked_06_doublon_cible_opid_frame():
    # GC-08-002 : deux cibles (object_public_id, frame) identiques -> BLOCKED (pas d'écrasement).
    t = {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP_A"]}
    _assert_blocked_malformed(_req_06([t, dict(t)]))


def test_blocked_06_doublon_canon_dans_cible():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C", "C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts))


def test_blocked_06_cle_interne_fuite():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts, object_id_map={"OBJ-0001": "k1"}))  # clé interne interdite


def test_blocked_06_target_cle_en_trop():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"], "object_key": "pii"}]
    _assert_blocked_malformed(_req_06(tgts))


def test_blocked_06_kind_public_x1f_fuite():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code\x1fpii", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts))


def test_blocked_06_frames_racine_incoherentes_avec_cibles():
    # frames racine != ensemble des frames des cibles -> requête 06 incohérente -> BLOCKED.
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    _assert_blocked_malformed(_req_06(tgts, frames=["CODE", "FRONTEND"]))


# ---------- ACCEPT ----------

def test_accept_reponse_complete_conforme():
    v = run_coherence_2(_env(s_pre=0.5))
    assert v["status"] == PASS and v["verdict"] == ACCEPT
    assert v["coherence_post"]["delta_phi"] == 1.0
    assert v["cinematic"]["S_post"] >= v["cinematic"]["S_pre"]
    assert v["authorize_09"] is True
    assert v["violations"] == [] and v["conflicts"] == [] and v["missing_targets"] == []


def test_accept_operant_non_applicable_justifie_compte_comme_couvert():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A", "OP_B"]}]
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [
                               {"operant": "OP_A", "applied": True},
                               {"operant": "OP_B", "applied": False, "reason_code": "NOT_APPLICABLE"}]}])
    v = run_coherence_2(_env(response=resp, targets=tgts, s_pre=0.3))
    assert v["verdict"] == ACCEPT and v["coherence_post"]["delta_phi"] == 1.0


# ---------- REJECT ----------

def test_reject_reponse_non_dict():
    from zoran_v2.coherence_2 import V_SCHEMA_INVALID
    for bad in ("ok", None, [], 42, {"text": "..."}):
        env = _env()
        env["llm_execution"]["response"] = bad  # injection EXPLICITE (dont None)
        v = run_coherence_2(env)
        assert v["status"] == PASS and v["verdict"] == REJECT
        assert V_SCHEMA_INVALID in v["violations"] and v["authorize_09"] is False


def test_reject_fingerprint_reponse_different():
    from zoran_v2.coherence_2 import V_FINGERPRINT_MISMATCH
    v = run_coherence_2(_env(response=_resp(fingerprint="AUTRE")))
    assert v["verdict"] == REJECT and V_FINGERPRINT_MISMATCH in v["violations"]


def test_reject_cible_inventee():
    resp = _resp(results=[{"object_public_id": "OBJ-9999", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT and v["unknown_targets"] == ["OBJ-9999:CODE"]


def test_reject_frame_inventee():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "FRONTEND",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_canon_hors_attendu():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "CANON_INVENTE", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_operant_hors_analyse():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_INVENTE", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_contradiction_meme_element():
    # OBJ-0001 apparaît sur deux frames avec le même canon admissible opposé -> contradiction.
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]},
            {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "TEXT",
             "canons": ["C"], "operants": ["OP_A"]}]
    resp = _resp(results=[
        {"object_public_id": "OBJ-0001", "frame": "CODE",
         "canon_findings": [{"canon": "C", "admissible": True}],
         "operant_outcomes": [{"operant": "OP_A", "applied": True}]},
        {"object_public_id": "OBJ-0001", "frame": "TEXT",
         "canon_findings": [{"canon": "C", "admissible": False}],
         "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp, targets=tgts))
    assert v["verdict"] == REJECT and v["conflicts"] and v["conflicts"][0]["canon"] == "C"


def test_reject_resultats_vides():
    from zoran_v2.coherence_2 import V_EMPTY_RESULTS
    v = run_coherence_2(_env(response=_resp(results=[])))
    assert v["verdict"] == REJECT and V_EMPTY_RESULTS in v["violations"]
    assert v["coherence_post"]["delta_phi"] == 0.0
    assert len(v["missing_targets"]) == 1


def test_reject_fuite_cle_interne_recursive():
    from zoran_v2.coherence_2 import V_PII_LEAK
    for leak in (
        {"object_key": "x"},
        {"content": "..."},
        {"provenance": {}},
        {"object_id_map": {}},
    ):
        resp = _resp()
        resp["results"][0].update(leak)  # clé interdite injectée profond
        v = run_coherence_2(_env(response=resp))
        assert v["verdict"] == REJECT and V_PII_LEAK in v["violations"], leak


def test_reject_fuite_separateur_x1f_dans_valeur():
    from zoran_v2.coherence_2 import V_PII_LEAK
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "code\x1fjean-dupont", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT and V_PII_LEAK in v["violations"]


# ---------- schéma strict / unicité / enum ----------

def test_reject_cle_racine_en_trop():
    resp = _resp()
    resp["extra"] = 1
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_result_cle_manquante():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}]}])  # operant_outcomes manquant
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_doublon_result_meme_opid_frame():
    r = {"object_public_id": "OBJ-0001", "frame": "CODE",
         "canon_findings": [{"canon": "C", "admissible": True}],
         "operant_outcomes": [{"operant": "OP_A", "applied": True}]}
    v = run_coherence_2(_env(response=_resp(results=[r, copy.deepcopy(r)])))
    assert v["verdict"] == REJECT  # doublon (opid, frame) non conforme, pas dédupliqué


def test_reject_doublon_canon_dans_cible():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True},
                                              {"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_doublon_operant_dans_cible():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True},
                                                {"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_reason_code_present_quand_applied_true():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True,
                                                 "reason_code": "NOT_APPLICABLE"}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT  # reason_code interdit si applied=true


def test_reject_reason_code_absent_quand_applied_false():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": False}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT  # reason_code obligatoire si applied=false


def test_reject_reason_code_hors_enum():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": False,
                                                 "reason_code": "PARCE_QUE"}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


def test_reject_admissible_non_bool():
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": "yes"}],
                           "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp))
    assert v["verdict"] == REJECT


# ---------- QUARANTINE ----------

def test_quarantine_cible_legitime_manquante():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A"]}]
    # réponse ne couvre que OBJ-0001 -> OBJ-0002 manquante, aucune invention.
    v = run_coherence_2(_env(response=_resp(), targets=tgts, s_pre=0.1))
    assert v["verdict"] == QUARANTINE and v["authorize_09"] is False
    assert v["missing_targets"] == ["OBJ-0002:CODE"]
    assert 0.0 < v["coherence_post"]["delta_phi"] < 1.0


def test_quarantine_operant_insufficient_evidence():
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C"], "operants": ["OP_A", "OP_B"]}]
    resp = _resp(results=[{"object_public_id": "OBJ-0001", "frame": "CODE",
                           "canon_findings": [{"canon": "C", "admissible": True}],
                           "operant_outcomes": [
                               {"operant": "OP_A", "applied": True},
                               {"operant": "OP_B", "applied": False, "reason_code": "INSUFFICIENT_EVIDENCE"}]}])
    v = run_coherence_2(_env(response=resp, targets=tgts, s_pre=0.1))
    assert v["verdict"] == QUARANTINE and v["coherence_post"]["delta_phi"] < 1.0


def test_quarantine_complet_mais_s_post_inferieur_s_pre():
    # 2 cibles COMPLÈTES mais dispersion σ (2 vs 1 canon_findings) -> S_post<1 ; S_pre=1 -> delta_S<0.
    # delta_phi=1 mais S_post<S_pre -> QUARANTINE (pas ACCEPT), authorize_09=False.
    tgts = [{"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
             "canons": ["C1", "C2"], "operants": ["OP_A"]},
            {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE",
             "canons": ["C1"], "operants": ["OP_A"]}]
    resp = _resp(results=[
        {"object_public_id": "OBJ-0001", "frame": "CODE",
         "canon_findings": [{"canon": "C1", "admissible": True}, {"canon": "C2", "admissible": True}],
         "operant_outcomes": [{"operant": "OP_A", "applied": True}]},
        {"object_public_id": "OBJ-0002", "frame": "CODE",
         "canon_findings": [{"canon": "C1", "admissible": True}],
         "operant_outcomes": [{"operant": "OP_A", "applied": True}]}])
    v = run_coherence_2(_env(response=resp, targets=tgts, s_pre=1.0))
    assert v["coherence_post"]["delta_phi"] == 1.0
    assert v["coherence_post"]["sigma"] > 0 and v["cinematic"]["delta_S"] < 0
    assert v["verdict"] == QUARANTINE and v["authorize_09"] is False


def test_accept_borne_s_post_egal_s_pre():
    v = run_coherence_2(_env(s_pre=1.0))
    assert v["verdict"] == ACCEPT and v["cinematic"]["delta_S"] == 0.0


# ---------- cinématique / authorize_09 ----------

def test_authorize_09_uniquement_accept():
    assert run_coherence_2(_env())["authorize_09"] is True
    assert run_coherence_2(_env(response=_resp(results=[])))["authorize_09"] is False
    assert run_coherence_2(_env(response="ok"))["authorize_09"] is False


def test_cinematique_trend():
    assert run_coherence_2(_env(s_pre=0.5))["cinematic"]["trend"] == "IMPROVING"
    assert run_coherence_2(_env(s_pre=1.0))["cinematic"]["trend"] == "STABLE"


# ---------- déterminisme / immuabilité / TypeError ----------

def test_deterministe():
    e = _env()
    assert run_coherence_2(e) == run_coherence_2(copy.deepcopy(e))


def test_immutabilite_envelope():
    e = _env()
    snap = copy.deepcopy(e)
    run_coherence_2(e)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_coherence_2(None)


# ---------- gouvernance / provenance ----------

def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-08-COHERENCE-2"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_08_COHERENCE_2"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
    assert COMPONENT_ID == "08_COHERENCE_2" and VERSION == "1.0.0"
