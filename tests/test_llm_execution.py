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
    NO_CLIENT,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_llm_execution,
)


def _env(authorized=True, request=None, **overrides):
    base = {k: {"status": "PASS"} for k in (
        "runtime_check", "object_discovery", "frame_selection",
        "operants_operes", "canon_determination", "coherence_engine")}
    base["llm_request_build"] = {
        "status": "PASS", "authorized": authorized,
        "llm_request": request if request is not None else {"instruction_kind": "STRUCTURED_ANALYSIS_V1"},
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
    v = run_llm_execution(_env(request={"k": 1}), client)
    assert v["status"] == PASS and v["executed"] is True
    assert v["response"] == {"text": "réponse LLM"} and v["error"] is None
    assert len(calls) == 1 and calls[0] == {"k": 1}  # appel UNIQUE, requête 06 transmise


def test_veto_respecte_aucun_appel():
    calls = []
    v = run_llm_execution(_env(authorized=False), lambda r: calls.append(r))
    assert v["status"] == PASS and v["executed"] is False and v["response"] is None
    assert calls == []  # AUCUN appel LLM quand 05/06 n'autorisent pas


def test_client_manquant_alors_quautorise_bloque():
    v = run_llm_execution(_env(authorized=True), llm_client=None)
    assert v["status"] == BLOCKED and v["blocked_by"] == NO_CLIENT
    assert v["executed"] is False


def test_erreur_client_isolee_fail_closed():
    def boom(req):
        raise RuntimeError("backend down")
    v = run_llm_execution(_env(), boom)
    assert v["status"] == PASS and v["executed"] is False and v["response"] is None
    assert "RuntimeError" in v["error"] and "backend down" in v["error"]


def test_immutabilite_envelope():
    e = _env(request={"k": 1})
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
