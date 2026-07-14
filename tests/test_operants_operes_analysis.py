"""Tests déterministes de 03_OPERANTS_OPERES_ANALYSIS (registre + objets injectés).

Inclut dès le départ les cas de MALFORMATION du registre (id dupliqué,
applies_to non-liste) — leçon d'engine-02.
"""
import copy

import pytest

from zoran_v2.operants_operes_analysis import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_operants_operes_analysis,
)

REG = [
    {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE", "TEXT"], "applies_to_kinds": ["code", "text"]},
    {"id": "OP_CLASSIFY", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
    {"id": "OP_CONSTRAIN", "applies_to_frames": ["SYSTEM"], "applies_to_kinds": ["system"]},
]


def _env(objects=None, ofm=None, rc="PASS", od="PASS", fs="PASS"):
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od, "objects": objects or []},
        "frame_selection": {"status": fs, "object_frame_map": ofm or []},
    }


def _obj(key, kind):
    return {"object_key": key, "kind": kind}


def _ofm(key, frames):
    return {"object_key": key, "frames": frames}


def test_analyse_nominale():
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])]), REG)
    assert v["status"] == PASS and v["blocked_by"] is None
    assert v["analysis"] == [{
        "frame": "CODE", "object_key": "k1",
        "operants": ["OP_CLASSIFY", "OP_DESCRIBE"],  # dédup + trié
        "operes": ["k1"],                            # opéré = l'objet
    }]
    assert v["unanalyzed"] == []
    assert v["component"] == COMPONENT_ID and v["version"] == VERSION


def test_output_schema_exact_pass_et_blocked():
    assert tuple(run_operants_operes_analysis(_env(), REG).keys()) == OUTPUT_KEYS
    assert tuple(run_operants_operes_analysis(_env(rc="FAIL"), REG).keys()) == OUTPUT_KEYS
    assert run_operants_operes_analysis(_env(), REG)["order_key"] == ORDER_KEY


def test_blocked_si_00():
    v = run_operants_operes_analysis(_env(rc="FAIL"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"


def test_blocked_si_01():
    v = run_operants_operes_analysis(_env(od="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "01_OBJECT_DISCOVERY"


def test_blocked_si_02():
    v = run_operants_operes_analysis(_env(fs="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "02_ANALYSIS_FRAME_SELECTION"


def test_unanalyzed_si_aucun_operant():
    # kind "ui" sur cadre "UI" : aucun opérant du REG ne matche.
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k1", "ui")], ofm=[_ofm("k1", ["UI"])]), REG)
    assert v["analysis"] == []
    assert v["unanalyzed"] == [{"frame": "UI", "object_key": "k1"}]


def test_non_invention_operants_sous_ensemble_registre():
    known = {op["id"] for op in REG}
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE", "TEXT"])]), REG)
    for a in v["analysis"]:
        assert set(a["operants"]) <= known


def test_dedup_operant_registre_duplique():
    reg = [
        {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
        {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
    ]
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["analysis"][0]["operants"] == ["OP_DESCRIBE"]


def test_applies_non_liste_ignore():
    reg = [{"id": "OP_X", "applies_to_frames": "CODE", "applies_to_kinds": "code"}]
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["analysis"] == []
    assert v["unanalyzed"] == [{"frame": "CODE", "object_key": "k"}]


def test_operant_sans_id_ignore():
    reg = [{"applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
           {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    v = run_operants_operes_analysis(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["analysis"][0]["operants"] == ["OP_DESCRIBE"]


def test_kind_inconnu_join_absente_unanalyzed():
    # object_key du frame_map absent des objets de 01 -> kind None -> aucun opérant.
    v = run_operants_operes_analysis(_env(objects=[], ofm=[_ofm("kx", ["CODE"])]), REG)
    assert v["unanalyzed"] == [{"frame": "CODE", "object_key": "kx"}]


def test_ofm_vide_analyse_vide_pass():
    v = run_operants_operes_analysis(_env(), REG)
    assert v["status"] == PASS and v["analysis"] == [] and v["unanalyzed"] == []


def test_deterministe():
    e = _env(objects=[_obj("k1", "code"), _obj("k2", "system")],
             ofm=[_ofm("k1", ["CODE"]), _ofm("k2", ["SYSTEM"])])
    assert run_operants_operes_analysis(e, REG) == run_operants_operes_analysis(e, REG)


def test_immutabilite_envelope():
    e = _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])])
    snap = copy.deepcopy(e)
    run_operants_operes_analysis(e, REG)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_operants_operes_analysis(None, REG)


def test_typeerror_registry_non_liste():
    with pytest.raises(TypeError):
        run_operants_operes_analysis(_env(), "pas une liste")


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-03-OPERANTS-OPERES-ANALYSIS"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_03_OPERANTS_OPERES_ANALYSIS"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
