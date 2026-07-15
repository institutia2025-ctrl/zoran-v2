"""Tests déterministes de 07_LLM_EXECUTION (client LLM mock injecté).

Vérifie : appel LLM UNIQUE sur requête autorisée, veto respecté (pas d'appel),
fail-closed 00→06, client manquant, erreur client isolée, immuabilité, gouvernance.
"""
import copy

import pytest

from zoran_v2.llm_execution import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    MALFORMED_REQUEST,
    NO_CLIENT,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_llm_execution,
)
from zoran_v2.llm_request_build import run_llm_request_build


def _real_06_request():
    """Requête RÉELLE produite par 06_LLM_REQUEST_BUILD (source de vérité du schéma 06->07).

    Prouve que 07 accepte EXACTEMENT ce que 06 émet (aucun faux blocage), et fournit une base
    valide que les tests de régression dégradent pour vérifier le fail-closed.
    """
    env06 = {
        "runtime_check": {"status": "PASS"},
        "object_discovery": {"status": "PASS", "objects": [{"object_key": "k1", "kind": "code"}]},
        "frame_selection": {"status": "PASS"},
        "operants_operes": {"status": "PASS",
                            "analysis": [{"object_key": "k1", "frame": "CODE", "operants": ["OP_DESCRIBE"]}]},
        "canon_determination": {"status": "PASS",
            "canons_selected": [{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
            "canon_referential": {"fingerprint": "FP", "canons": [], "priorities": {}}},
        "coherence_engine": {"status": "PASS", "coherence": {"S": 1.0},
                            "resource": {"authorize_llm": True, "delta_phi_min": 0.5}},
    }
    out = run_llm_request_build(env06)
    assert out["authorized"] is True and out["llm_request"] is not None
    return out["llm_request"]


_VALID_REQUEST = _real_06_request()


def _env(authorized=True, request=None, **overrides):
    base = {k: {"status": "PASS"} for k in (
        "runtime_check", "object_discovery", "frame_selection",
        "operants_operes", "canon_determination", "coherence_engine")}
    base["llm_request_build"] = {
        "status": "PASS", "authorized": authorized,
        # Défaut = requête VALIDE (schéma 06). Les tests de frontière passent une requête dégradée.
        "llm_request": request if request is not None else dict(_VALID_REQUEST),
    }
    base.update(overrides)
    return base


def test_output_schema_exact():
    assert tuple(run_llm_execution(_env(), lambda r: "ok").keys()) == OUTPUT_KEYS
    blocked_env = _env()
    blocked_env["runtime_check"] = {"status": "FAIL"}
    assert tuple(run_llm_execution(blocked_env).keys()) == OUTPUT_KEYS  # schéma exact en BLOCKED
    assert run_llm_execution(_env())["order_key"] == ORDER_KEY


def test_fail_closed_00_a_06():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"),
                      ("object_discovery", "01_OBJECT_DISCOVERY"),
                      ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
                      ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
                      ("canon_determination", "04_CANON_DETERMINATION"),
                      ("coherence_engine", "05_COHERENCE_ENGINE"),
                      ("llm_request_build", "06_LLM_REQUEST_BUILD")):
        env = _env()
        env[key] = {"status": "BLOCKED"}
        v = run_llm_execution(env, lambda r: "x")
        assert v["status"] == BLOCKED and v["blocked_by"] == comp
        assert v["executed"] is False


def test_appel_unique_sur_requete_autorisee():
    calls = []
    def client(req):
        calls.append(req)
        return {"text": "réponse LLM"}
    v = run_llm_execution(_env(request=dict(_VALID_REQUEST)), client)
    assert v["status"] == PASS and v["executed"] is True
    assert v["response"] == {"text": "réponse LLM"} and v["error"] is None
    assert len(calls) == 1 and calls[0] == _VALID_REQUEST  # appel UNIQUE, requête 06 transmise telle quelle


def test_veto_respecte_aucun_appel():
    calls = []
    v = run_llm_execution(_env(authorized=False), lambda r: calls.append(r))
    assert v["status"] == PASS and v["executed"] is False and v["response"] is None
    assert calls == []  # AUCUN appel LLM quand 05/06 n'autorisent pas


def test_client_manquant_alors_quautorise_bloque():
    v = run_llm_execution(_env(authorized=True), llm_client=None)
    assert v["status"] == BLOCKED and v["blocked_by"] == NO_CLIENT
    assert v["executed"] is False


def test_erreur_client_fail_closed_status_blocked():
    # Audit total P1 : une panne LLM ne doit PAS être présentée comme PASS aux portes suivantes.
    from zoran_v2.llm_execution import CLIENT_ERROR

    def boom(req):
        raise RuntimeError("backend down")
    v = run_llm_execution(_env(), boom)
    assert v["status"] == BLOCKED and v["blocked_by"] == CLIENT_ERROR
    assert v["executed"] is False and v["response"] is None
    assert "RuntimeError" in v["error"] and "backend down" in v["error"]


def test_immutabilite_envelope():
    e = _env(request=dict(_VALID_REQUEST))
    snap = copy.deepcopy(e)
    run_llm_execution(e, lambda r: "ok")
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_llm_execution(None, lambda r: "x")


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-07-LLM-EXECUTION"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_07_LLM_EXECUTION"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
    assert COMPONENT_ID == "07_LLM_EXECUTION" and VERSION == "1.0.0"


# --- RÉGRESSIONS audit ChatGPT global coherence 2026-07-15 : frontière 06->07 fail-closed (P1) ---

def test_requete_reelle_06_acceptee_pas_de_faux_blocage():
    # Invariant frontière : 07 doit accepter EXACTEMENT la requête produite par 06 (pas de faux BLOCKED).
    calls = []
    v = run_llm_execution(_env(request=_real_06_request()), lambda r: calls.append(r) or {"ok": True})
    assert v["status"] == PASS and v["executed"] is True
    assert len(calls) == 1


def test_requete_absente_ou_none_bloque_sans_appel():
    # 06 autorisée mais llm_request=None (enveloppe malformée) -> AUCUN appel LLM, fail-closed.
    calls = []
    v = run_llm_execution(_env(authorized=True, request=None, llm_request_build={
        "status": "PASS", "authorized": True, "llm_request": None}), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST
    assert v["executed"] is False and calls == []


def test_requete_non_dict_bloque_sans_appel():
    calls = []
    v = run_llm_execution(_env(request="pas-un-dict"), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST
    assert calls == []


def test_requete_hors_schema_bloque_sans_appel():
    # Requête à clés incomplètes (schéma 06 non respecté) -> fail-closed.
    calls = []
    v = run_llm_execution(_env(request={"instruction_kind": "STRUCTURED_ANALYSIS_V1"}), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST
    assert calls == []


def test_instruction_kind_inattendu_bloque():
    bad = dict(_VALID_REQUEST, instruction_kind="ARBITRARY_INJECTION")
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST and calls == []


def test_requete_avec_object_key_pii_bloque_sans_appel():
    # Tentative de fuite : une cible porte un object_key (PII dérivée du contenu utilisateur).
    # 07 DOIT bloquer AVANT d'appeler le client (RULE-078 à la frontière 06->07).
    leaky_target = dict(_VALID_REQUEST["targets"][0], object_key="code\x1fjean-dupont-dossier")
    bad = dict(_VALID_REQUEST, targets=[leaky_target])
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST
    assert v["executed"] is False and calls == []  # AUCUNE PII transmise au LLM


def test_object_key_racine_bloque():
    bad = dict(_VALID_REQUEST, object_key="code\x1fpii")
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST and calls == []


def test_target_non_dict_bloque():
    bad = dict(_VALID_REQUEST, targets=["pas-un-dict"])
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


def test_frames_non_str_bloque():
    bad = dict(_VALID_REQUEST, frames=["CODE", 123])
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


def test_fingerprint_vide_bloque():
    bad = dict(_VALID_REQUEST, referential_fingerprint="")
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


# --- RÉGRESSIONS audit ChatGPT GC-D1-001 2026-07-15 : PII dans une VALEUR de champ autorisé (P1) ---

def test_pii_dans_object_public_id_bloque_sans_appel():
    # GC-D1-001 : object_public_id porte la clé dérivée (contient \x1f) au lieu de l'ID opaque.
    # Passait avant (str), doit être BLOQUÉ maintenant : jamais de PII au client.
    leaky = dict(_VALID_REQUEST["targets"][0], object_public_id="code\x1fjean-dupont-dossier")
    bad = dict(_VALID_REQUEST, targets=[leaky])
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST and calls == []


def test_pii_dans_canons_bloque_sans_appel():
    # GC-D1-001 : la même fuite via un autre champ autorisé (canons) doit aussi être bloquée.
    leaky = dict(_VALID_REQUEST["targets"][0], canons=["C", "code\x1fjean-dupont"])
    bad = dict(_VALID_REQUEST, targets=[leaky])
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST and calls == []


def test_pii_dans_kind_bloque_sans_appel():
    leaky = dict(_VALID_REQUEST["targets"][0], kind="code\x1fpii")
    bad = dict(_VALID_REQUEST, targets=[leaky])
    calls = []
    v = run_llm_execution(_env(request=bad), lambda r: calls.append(r))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST and calls == []


def test_object_public_id_format_non_opaque_bloque():
    # object_public_id str mais PAS au format OBJ-nnnn (ex. sans \x1f mais dérivé) -> refus.
    for bad_id in ("code-jean", "OBJ-1", "obj-0001", "OBJ-", "jean-dupont"):
        leaky = dict(_VALID_REQUEST["targets"][0], object_public_id=bad_id)
        bad = dict(_VALID_REQUEST, targets=[leaky])
        v = run_llm_execution(_env(request=bad), lambda r: "x")
        assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST, bad_id


def test_pii_policy_alteree_bloque():
    bad = dict(_VALID_REQUEST, pii_policy="DISABLED")
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


def test_coherence_s_type_invalide_bloque():
    bad = dict(_VALID_REQUEST, coherence_S="beaucoup")
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


def test_canons_non_str_list_bloque():
    leaky = dict(_VALID_REQUEST["targets"][0], canons=[123])
    bad = dict(_VALID_REQUEST, targets=[leaky])
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST


def test_target_cle_manquante_bloque():
    # clés EXACTES par cible : une cible amputée d'un champ (ex. operants) est refusée.
    incomplete = {k: v for k, v in _VALID_REQUEST["targets"][0].items() if k != "operants"}
    bad = dict(_VALID_REQUEST, targets=[incomplete])
    v = run_llm_execution(_env(request=bad), lambda r: "x")
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED_REQUEST
