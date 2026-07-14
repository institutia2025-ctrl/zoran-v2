"""Tests déterministes de 02_ANALYSIS_FRAME_SELECTION (registre + objets injectés)."""
import copy

import pytest

from zoran_v2.frame_selection import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_frame_selection,
)

REG = [
    {"id": "CODE", "applies_to_kinds": ["code", "identifier"]},
    {"id": "TEXT", "applies_to_kinds": ["text", "term"]},
    {"id": "UI", "applies_to_kinds": ["ui", "component"]},
    {"id": "SYSTEM", "applies_to_kinds": ["system", "service"]},
]


def _env(objects=None, rc="PASS", od="PASS"):
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od, "objects": objects or []},
    }


def _obj(key, kind):
    return {"object_key": key, "kind": kind}


def test_pass_selection_nominale():
    v = run_frame_selection(_env([_obj("k1", "code"), _obj("k2", "text")]), REG)
    assert v["status"] == PASS and v["blocked_by"] is None
    assert v["frames_selected"] == ["CODE", "TEXT"]
    assert v["object_frame_map"] == [
        {"object_key": "k1", "frames": ["CODE"]},
        {"object_key": "k2", "frames": ["TEXT"]},
    ]
    assert v["unmatched_objects"] == []
    assert v["component"] == COMPONENT_ID and v["version"] == VERSION


def test_output_schema_exact_pass_et_blocked():
    # Contrôle de conformité au contrat : clés EXACTES dans les deux modes.
    assert tuple(run_frame_selection(_env(), REG).keys()) == OUTPUT_KEYS
    assert tuple(run_frame_selection(_env(rc="FAIL"), REG).keys()) == OUTPUT_KEYS
    assert run_frame_selection(_env(), REG)["order_key"] == ORDER_KEY


def test_blocked_si_00_pas_pass():
    v = run_frame_selection(_env(rc="FAIL"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"
    assert v["frames_selected"] == []


def test_blocked_si_00_absent():
    v = run_frame_selection({"object_discovery": {"status": "PASS", "objects": []}}, REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"


def test_blocked_si_01_pas_pass():
    v = run_frame_selection(_env(od="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "01_OBJECT_DISCOVERY"


def test_unmatched_objet_sans_cadre():
    v = run_frame_selection(_env([_obj("k1", "code"), _obj("k3", "inconnu")]), REG)
    assert v["status"] == PASS
    assert v["frames_selected"] == ["CODE"]
    assert v["unmatched_objects"] == [{"object_key": "k3", "kind": "inconnu"}]


def test_non_invention_frames_sous_ensemble_du_registre():
    known = {f["id"] for f in REG}
    v = run_frame_selection(_env([_obj("k1", "code"), _obj("k2", "text"),
                                  _obj("k3", "inconnu")]), REG)
    assert set(v["frames_selected"]) <= known
    assert v["frames_selected"] == ["CODE", "TEXT"]


def test_objet_multi_cadres_recoit_tous_tries():
    reg = [
        {"id": "SYSTEM", "applies_to_kinds": ["shared"]},
        {"id": "CODE", "applies_to_kinds": ["shared"]},
    ]
    v = run_frame_selection(_env([_obj("k1", "shared")]), reg)
    assert v["object_frame_map"][0]["frames"] == ["CODE", "SYSTEM"]  # trié
    assert v["frames_selected"] == ["CODE", "SYSTEM"]


def test_objets_vides_selection_vide_pass():
    v = run_frame_selection(_env([]), REG)
    assert v["status"] == PASS
    assert v["frames_selected"] == [] and v["object_frame_map"] == [] and v["unmatched_objects"] == []


def test_deterministe():
    e = _env([_obj("k1", "code"), _obj("k2", "text")])
    assert run_frame_selection(e, REG) == run_frame_selection(e, REG)


def test_immutabilite_envelope():
    e = _env([_obj("k1", "code")])
    snap = copy.deepcopy(e)
    run_frame_selection(e, REG)
    assert e == snap


def test_registre_entree_malformee_ignoree():
    reg = [{"applies_to_kinds": ["code"]}, {"id": "CODE", "applies_to_kinds": ["code"]}]
    v = run_frame_selection(_env([_obj("k1", "code")]), reg)
    assert v["frames_selected"] == ["CODE"]


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_frame_selection(None, REG)


def test_typeerror_registry_non_liste():
    with pytest.raises(TypeError):
        run_frame_selection(_env(), "pas une liste")


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-02-ANALYSIS-FRAME-SELECTION"


def test_provenance_decl_present_et_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_02_ANALYSIS_FRAME_SELECTION"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
