"""Tests déterministes de 06_LLM_REQUEST_BUILD (envelope injectée).

Vérifie : respect du veto ressource (05), requête structurelle PII-free, fail-closed
00→05, déterminisme, immuabilité, gouvernance/provenance.
"""
import copy

import pytest

from zoran_v2.llm_request_build import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_llm_request_build,
)


def _ce(authorize=True, S=1.0):
    return {
        "status": PASS,
        "coherence": {"S": S},
        "resource": {"authorize_llm": authorize, "delta_phi_min": 0.5},
    }


def _env(objects=None, canons_selected=None, analysis=None, ce=None,
         rc="PASS", od="PASS", fs="PASS", oa="PASS", cd="PASS"):
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od, "objects": objects or []},
        "frame_selection": {"status": fs},
        "operants_operes": {"status": oa, "analysis": analysis or []},
        "canon_determination": {
            "status": cd,
            "canons_selected": canons_selected or [],
            "canon_referential": {"fingerprint": "FP", "canons": [], "priorities": {}},
        },
        "coherence_engine": ce if ce is not None else _ce(),
    }


def test_output_schema_exact_pass_et_blocked():
    assert tuple(run_llm_request_build(_env()).keys()) == OUTPUT_KEYS
    assert tuple(run_llm_request_build(_env(rc="FAIL")).keys()) == OUTPUT_KEYS
    assert run_llm_request_build(_env())["order_key"] == ORDER_KEY


def test_fail_closed_00_a_05():
    for kw, comp in (("rc", "00_RUNTIME_CHECK"), ("od", "01_OBJECT_DISCOVERY"),
                     ("fs", "02_ANALYSIS_FRAME_SELECTION"), ("oa", "03_OPERANTS_OPERES_ANALYSIS"),
                     ("cd", "04_CANON_DETERMINATION")):
        v = run_llm_request_build(_env(**{kw: "BLOCKED"}))
        assert v["status"] == BLOCKED and v["blocked_by"] == comp
        assert v["authorized"] is False and v["llm_request"] is None


def test_fail_closed_si_05_blocked():
    env = _env()
    env["coherence_engine"] = {"status": "BLOCKED"}
    v = run_llm_request_build(env)
    assert v["status"] == BLOCKED and v["blocked_by"] == "05_COHERENCE_ENGINE"


def test_veto_ressource_respecte():
    # 05 refuse l'appel LLM -> pas de requête (07 interdit).
    v = run_llm_request_build(_env(ce=_ce(authorize=False)))
    assert v["status"] == PASS
    assert v["authorized"] is False and v["llm_request"] is None


def test_requete_construite_si_autorise():
    v = run_llm_request_build(_env(
        objects=[{"object_key": "k1", "kind": "code"}],
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["CANON_STRUCTURE"]}],
        analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP_DESCRIBE"], "operes": ["k1"]}],
        ce=_ce(authorize=True, S=0.83),
    ))
    assert v["authorized"] is True
    req = v["llm_request"]
    assert req["instruction_kind"] == "STRUCTURED_ANALYSIS_V1"
    assert req["referential_fingerprint"] == "FP"
    assert req["coherence_S"] == 0.83
    assert req["frames"] == ["CODE"]
    assert req["targets"] == [{
        "object_public_id": "OBJ-0001", "kind": "code", "frame": "CODE",
        "canons": ["CANON_STRUCTURE"], "operants": ["OP_DESCRIBE"],
    }]
    assert v["object_id_map"] == {"OBJ-0001": "k1"}


def test_cibles_uniquement_paires_resolues():
    # paire canonisée SANS opérant + paire avec opérant SANS canon -> aucune cible.
    v = run_llm_request_build(_env(
        objects=[{"object_key": "k1", "kind": "code"}, {"object_key": "k2", "kind": "text"}],
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
        analysis=[{"object_key": "k2", "frame": "TEXT", "operants": ["O"]}],
    ))
    assert v["llm_request"]["targets"] == []


def test_pii_free_policy_presente():
    v = run_llm_request_build(_env(
        objects=[{"object_key": "k1", "kind": "code"}],
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
        analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}],
    ))
    assert v["llm_request"]["pii_policy"] == "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT"


def test_object_key_pii_n_atteint_pas_le_llm():
    # Audit total P0 : object_key = contenu utilisateur normalisé (01 : f"{kind}\x1f{normalized}").
    # Il NE DOIT PAS apparaître dans la requête envoyée au LLM ; seul un id opaque y figure.
    import json
    pii = "code\x1fjean-dupont-dossier-medical"
    v = run_llm_request_build(_env(
        objects=[{"object_key": pii, "kind": "code"}],
        canons_selected=[{"object_key": pii, "frame": "CODE", "canons": ["C"]}],
        analysis=[{"object_key": pii, "frame": "CODE", "operants": ["O"]}],
    ))
    blob = json.dumps(v["llm_request"], ensure_ascii=False)
    assert pii not in blob  # AUCUNE fuite de la clé dérivée dans la requête
    assert v["llm_request"]["targets"][0]["object_public_id"] == "OBJ-0001"
    assert v["object_id_map"] == {"OBJ-0001": pii}  # correspondance LOCALE seulement


def test_deterministe():
    e = _env(
        objects=[{"object_key": "k1", "kind": "code"}],
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
        analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}],
    )
    assert run_llm_request_build(e) == run_llm_request_build(e)


def test_immutabilite_envelope():
    e = _env(
        objects=[{"object_key": "k1", "kind": "code"}],
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
        analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}],
    )
    snap = copy.deepcopy(e)
    run_llm_request_build(e)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_llm_request_build(None)


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-06-LLM-REQUEST-BUILD"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_06_LLM_REQUEST_BUILD"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
    assert COMPONENT_ID == "06_LLM_REQUEST_BUILD" and VERSION == "1.0.0"
