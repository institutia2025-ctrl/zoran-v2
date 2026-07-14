"""Tests déterministes de 04_CANON_DETERMINATION (registre + objets injectés).

Cas de MALFORMATION du registre (id dupliqué, applies_to non-liste, priority
non-entière, sans id) et de CONFLIT (égalité de priorité) bakés dès le départ
— pré-ship adversarial self-audit (leçon d'engine-02/03).
"""
import copy

import pytest

from zoran_v2.canon_determination import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    _fingerprint,
    run_canon_determination,
)

REG = [
    {"id": "CANON_CONSTRAINT", "applies_to_frames": ["SYSTEM", "CODE"],
     "applies_to_kinds": ["system", "code"], "priority": 40},
    {"id": "CANON_STRUCTURE", "applies_to_frames": ["CODE", "SYSTEM"],
     "applies_to_kinds": ["code", "system"], "priority": 30},
    {"id": "CANON_INTENT", "applies_to_frames": ["TEXT", "UI"],
     "applies_to_kinds": ["text", "ui"], "priority": 20},
]


def _env(objects=None, ofm=None, rc="PASS", od="PASS", fs="PASS", oa="PASS"):
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od, "objects": objects or []},
        "frame_selection": {"status": fs, "object_frame_map": ofm or []},
        "operants_operes": {"status": oa},
    }


def _obj(key, kind):
    return {"object_key": key, "kind": kind}


def _ofm(key, frames):
    return {"object_key": key, "frames": frames}


def test_determination_nominale_priorite_desc():
    # objet code sur cadre CODE : CONSTRAINT(40) puis STRUCTURE(30), trié par priorité desc.
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])]), REG)
    assert v["status"] == PASS and v["blocked_by"] is None
    assert v["canons_selected"] == [{
        "object_key": "k1", "frame": "CODE",
        "canons": ["CANON_CONSTRAINT", "CANON_STRUCTURE"],
    }]
    assert v["conflicts"] == []
    assert v["uncanonized"] == []
    assert v["canon_referential"]["canons"] == ["CANON_CONSTRAINT", "CANON_STRUCTURE"]
    assert v["canon_referential"]["priorities"] == {"CANON_CONSTRAINT": 40, "CANON_STRUCTURE": 30}
    assert v["component"] == COMPONENT_ID and v["version"] == VERSION


def test_output_schema_exact_pass_et_blocked():
    assert tuple(run_canon_determination(_env(), REG).keys()) == OUTPUT_KEYS
    assert tuple(run_canon_determination(_env(rc="FAIL"), REG).keys()) == OUTPUT_KEYS
    assert run_canon_determination(_env(), REG)["order_key"] == ORDER_KEY


def test_blocked_si_00():
    v = run_canon_determination(_env(rc="FAIL"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"


def test_blocked_si_01():
    v = run_canon_determination(_env(od="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "01_OBJECT_DISCOVERY"


def test_blocked_si_02():
    v = run_canon_determination(_env(fs="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "02_ANALYSIS_FRAME_SELECTION"


def test_blocked_si_03():
    v = run_canon_determination(_env(oa="BLOCKED"), REG)
    assert v["status"] == BLOCKED and v["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"


def test_blocked_referential_est_vide_et_stable():
    v = run_canon_determination(_env(oa="BLOCKED"), REG)
    assert v["canon_referential"]["canons"] == [] and v["canon_referential"]["priorities"] == {}
    assert v["resource_estimate"] == {"objects": 0, "frames": 0, "pairs": 0, "canons_applied": 0}


def test_uncanonized_si_aucun_canon():
    # kind "ui" sur cadre "UI" : INTENT matche UI+ui -> canonisé ; kind "ui" sur "CODE" -> aucun.
    v = run_canon_determination(
        _env(objects=[_obj("k1", "ui")], ofm=[_ofm("k1", ["CODE"])]), REG)
    assert v["canons_selected"] == []
    assert v["uncanonized"] == [{"object_key": "k1", "frame": "CODE"}]


def test_non_invention_canons_sous_ensemble_registre():
    known = {c["id"] for c in REG}
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code"), _obj("k2", "text")],
             ofm=[_ofm("k1", ["CODE"]), _ofm("k2", ["TEXT"])]), REG)
    for a in v["canons_selected"]:
        assert set(a["canons"]) <= known
    assert set(v["canon_referential"]["canons"]) <= known


def test_conflit_egalite_priorite_liste_jamais_ecrase():
    # Deux canons applicables de MÊME priorité -> conflit listé, aucun canon perdu.
    reg = [
        {"id": "CANON_B", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 50},
        {"id": "CANON_A", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 50},
    ]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    # ordonné par id (égalité de priorité) — aucun écrasé
    assert v["canons_selected"][0]["canons"] == ["CANON_A", "CANON_B"]
    assert v["conflicts"] == [{
        "object_key": "k", "frame": "CODE", "priority": 50,
        "canons": ["CANON_A", "CANON_B"],
    }]


def test_priorites_differentes_pas_de_conflit():
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), REG)
    assert v["conflicts"] == []  # 40 != 30


def test_dedup_canon_registre_duplique():
    reg = [
        {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
        {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
    ]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"][0]["canons"] == ["CANON_X"]
    assert v["conflicts"] == []  # un seul id après dédup -> pas de conflit


def test_applies_non_liste_ignore():
    reg = [{"id": "CANON_X", "applies_to_frames": "CODE", "applies_to_kinds": "code", "priority": 10}]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"] == []
    assert v["uncanonized"] == [{"object_key": "k", "frame": "CODE"}]


def test_priority_non_entiere_ignore():
    reg = [{"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": "haute"},
           {"id": "CANON_B", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": True}]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"] == []  # priority str et bool -> ignorés
    assert v["uncanonized"] == [{"object_key": "k", "frame": "CODE"}]


def test_canon_sans_id_ignore():
    reg = [{"applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
           {"id": "CANON_OK", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10}]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"][0]["canons"] == ["CANON_OK"]


def test_kind_inconnu_join_absente_uncanonized():
    v = run_canon_determination(_env(objects=[], ofm=[_ofm("kx", ["CODE"])]), REG)
    assert v["uncanonized"] == [{"object_key": "kx", "frame": "CODE"}]


def test_ofm_vide_pass_referentiel_vide():
    v = run_canon_determination(_env(), REG)
    assert v["status"] == PASS and v["canons_selected"] == [] and v["conflicts"] == []
    assert v["canon_referential"]["canons"] == []


def test_fingerprint_deterministe_et_stable():
    e = _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])])
    f1 = run_canon_determination(e, REG)["canon_referential"]["fingerprint"]
    f2 = run_canon_determination(e, REG)["canon_referential"]["fingerprint"]
    assert f1 == f2  # déterministe
    # stable : mêmes canons/priorités -> même hash, indépendant de l'ordre d'insertion
    assert _fingerprint({"CANON_CONSTRAINT": 40, "CANON_STRUCTURE": 30}) == \
           _fingerprint({"CANON_STRUCTURE": 30, "CANON_CONSTRAINT": 40})


def test_fingerprint_change_si_referentiel_change():
    assert _fingerprint({"CANON_STRUCTURE": 30}) != _fingerprint({"CANON_STRUCTURE": 31})
    assert _fingerprint({}) != _fingerprint({"CANON_STRUCTURE": 30})


def test_resource_estimate_compte_sans_budget():
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code"), _obj("k2", "text")],
             ofm=[_ofm("k1", ["CODE", "SYSTEM"]), _ofm("k2", ["TEXT"])]), REG)
    assert v["resource_estimate"] == {"objects": 2, "frames": 3, "pairs": 3, "canons_applied": 3}


def test_deterministe():
    e = _env(objects=[_obj("k1", "code"), _obj("k2", "text")],
             ofm=[_ofm("k1", ["CODE"]), _ofm("k2", ["TEXT"])])
    assert run_canon_determination(e, REG) == run_canon_determination(e, REG)


def test_immutabilite_envelope():
    e = _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])])
    snap = copy.deepcopy(e)
    run_canon_determination(e, REG)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_canon_determination(None, REG)


def test_typeerror_registry_non_liste():
    with pytest.raises(TypeError):
        run_canon_determination(_env(), "pas une liste")


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-04-CANON-DETERMINATION"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_04_CANON_DETERMINATION"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False


def test_load_canon_registry_fail_closed():
    from zoran_v2.canon_determination import _canons_from_yaml_obj
    assert _canons_from_yaml_obj(None) == []           # YAML vide
    assert _canons_from_yaml_obj("scalaire") == []     # scalaire (string)
    assert _canons_from_yaml_obj(42) == []             # scalaire (nombre)
    assert _canons_from_yaml_obj([1, 2]) == []         # liste top-level
    assert _canons_from_yaml_obj({"autre": 1}) == []   # clé absente
    assert _canons_from_yaml_obj({"canons": [{"id": "CANON_X"}]}) == [{"id": "CANON_X"}]


def test_registre_reel_charge_et_applique():
    # Le vrai CANONS.yaml se charge et produit un référentiel cohérent avec V1.
    from zoran_v2.canon_determination import load_canon_registry
    reg = load_canon_registry()
    ids = {c["id"] for c in reg}
    assert {"CANON_STRUCTURE", "CANON_INTENT", "CANON_CONSTRAINT"} <= ids
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])]), reg)
    assert v["status"] == PASS
    assert "CANON_STRUCTURE" in v["canon_referential"]["canons"]
