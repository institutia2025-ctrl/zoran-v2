"""Tests déterministes de 04_CANON_DETERMINATION (registre + objets injectés).

Cas de MALFORMATION du registre (id dupliqué, applies_to non-liste, priority
non-entière, sans id), CONFLIT (égalité de priorité), et RÉGRESSIONS de l'audit
indépendant 2026-07-14 : dédup id ordre-indépendant, YAML fail-closed,
fingerprint complet (couvre applies_to).
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
    _normalize_registry,
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


def _ids(v):
    return [c["id"] for c in v["canon_referential"]["canons"]]


def _env(objects=None, ofm=None, rc="PASS", od="PASS", fs="PASS", oa="PASS"):
    # 03 fournit un VRAI résultat (contrat complet) : 04 revalide désormais le payload 03, pas
    # seulement son status (CSB-03-04-P1-001). `oa` fixe le status pour les tests fail-closed.
    # 03 fournit un VRAI resultat COHERENT avec 01/02 : chaque couple (object_key, frame) de 02
    # est classifie (ici en unanalyzed, le contenu operant n'etant pas consomme par 04). 04 revalide
    # desormais la structure ET la provenance du payload 03 (CSB-03-04-P1-001 / GC-PR16-001).
    _ofm = ofm or []
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od, "objects": objects or []},
        "frame_selection": {"status": fs, "object_frame_map": _ofm},
        "operants_operes": {"component": "03_OPERANTS_OPERES_ANALYSIS", "version": "1.0.0",
                            "status": oa, "blocked_by": None, "analysis": [],
                            "unanalyzed": [{"frame": f, "object_key": e["object_key"]}
                                           for e in _ofm for f in e["frames"]],
                            "order_key": "object_frame_map_order_puis_operant_id_alphabetique"},
    }


def _obj(key, kind):
    return {"object_key": key, "kind": kind}


def _ofm(key, frames):
    return {"object_key": key, "frames": frames}


def test_determination_nominale_priorite_desc():
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])]), REG)
    assert v["status"] == PASS and v["blocked_by"] is None
    assert v["canons_selected"] == [{
        "object_key": "k1", "frame": "CODE",
        "canons": ["CANON_CONSTRAINT", "CANON_STRUCTURE"],
    }]
    assert v["conflicts"] == []
    assert v["uncanonized"] == []
    assert _ids(v) == ["CANON_CONSTRAINT", "CANON_STRUCTURE"]
    assert v["canon_referential"]["priorities"] == {"CANON_CONSTRAINT": 40, "CANON_STRUCTURE": 30}
    assert v["full_registry_commitment"] == {
        "full_registry_fingerprint": _fingerprint(_normalize_registry(REG)),
        "registry_version": "1.0.0",
        "registry_source": "CANONS.yaml",
        "normalization": {
            "id": "zoran_v2.canon_determination._normalize_registry",
            "version": "1.0.0",
        },
    }
    assert len(v["canon_referential"]["canons"]) == 2
    assert len(REG) == 3  # sous-ensemble applique et engagement complet restent distincts
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
    assert set(_ids(v)) <= known


def test_conflit_egalite_priorite_liste_jamais_ecrase():
    reg = [
        {"id": "CANON_B", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 50},
        {"id": "CANON_A", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 50},
    ]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"][0]["canons"] == ["CANON_A", "CANON_B"]
    assert v["conflicts"] == [{
        "object_key": "k", "frame": "CODE", "priority": 50,
        "canons": ["CANON_A", "CANON_B"],
    }]


def test_priorites_differentes_pas_de_conflit():
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), REG)
    assert v["conflicts"] == []


def test_dedup_canon_registre_duplique():
    reg = [
        {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
        {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
    ]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)
    assert v["canons_selected"][0]["canons"] == ["CANON_X"]
    assert v["conflicts"] == []


def test_dup_id_priorites_differentes_DETERMINISTE_ordre_independant():
    # RÉGRESSION (audit Codex 2026-07-14, constat 2) : doublon d'id à priorités
    # différentes NE DOIT PLUS dépendre de l'ordre du registre.
    a = {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10}
    b = {"id": "CANON_X", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 20}
    env = _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])])
    v1 = run_canon_determination(env, [a, b])
    v2 = run_canon_determination(env, [b, a])
    assert v1 == v2  # ordre-indépendant
    # priorité max déterministe conservée (20)
    assert v1["canon_referential"]["priorities"]["CANON_X"] == 20


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
    assert v["canons_selected"] == []
    assert v["uncanonized"] == [{"object_key": "k", "frame": "CODE"}]


def test_id_non_str_ignore_pas_de_crash():
    # Audit total P2 : id non-str (liste/dict) -> rejeté (pas de TypeError comme clé).
    reg = [{"id": ["X"], "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
           {"id": {"k": 1}, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10},
           {"id": "CANON_OK", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10}]
    v = run_canon_determination(
        _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])]), reg)  # ne doit PAS crasher
    assert v["canons_selected"][0]["canons"] == ["CANON_OK"]


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
    assert f1 == f2
    rec = lambda i, p: {"id": i, "priority": p, "applies_to_frames": [], "applies_to_kinds": []}
    # stable : ordre d'insertion indifférent (le fingerprint trie par id)
    assert _fingerprint([rec("A", 1), rec("B", 2)]) == _fingerprint([rec("B", 2), rec("A", 1)])


def test_fingerprint_change_si_priorite_change():
    rec = lambda i, p, k=(): {"id": i, "priority": p, "applies_to_frames": [], "applies_to_kinds": list(k)}
    assert _fingerprint([rec("S", 30)]) != _fingerprint([rec("S", 31)])
    assert _fingerprint([]) != _fingerprint([rec("S", 30)])


def test_fingerprint_couvre_applies_to_COMPLET():
    # RÉGRESSION (audit Codex 2026-07-14, constat 3) : le fingerprint doit couvrir
    # les applies_to, pas seulement id+priorité. Même sélection, applies_to différents
    # -> référentiel gelé différent -> fingerprint différent.
    env = _env(objects=[_obj("k", "code")], ofm=[_ofm("k", ["CODE"])])
    reg1 = [{"id": "C", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"], "priority": 10}]
    reg2 = [{"id": "C", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code", "text"], "priority": 10}]
    v1 = run_canon_determination(env, reg1)
    v2 = run_canon_determination(env, reg2)
    assert _ids(v1) == _ids(v2) == ["C"]  # même canon sélectionné
    assert v1["canon_referential"]["fingerprint"] != v2["canon_referential"]["fingerprint"]


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
    assert _canons_from_yaml_obj(None) == []
    assert _canons_from_yaml_obj("scalaire") == []
    assert _canons_from_yaml_obj(42) == []
    assert _canons_from_yaml_obj([1, 2]) == []
    assert _canons_from_yaml_obj({"autre": 1}) == []
    assert _canons_from_yaml_obj({"canons": [{"id": "CANON_X"}]}) == [{"id": "CANON_X"}]


def test_load_canon_registry_yaml_invalide_fail_closed(tmp_path):
    # RÉGRESSION (audit Codex 2026-07-14, constat 1) : YAML invalide -> [] (pas de crash).
    from zoran_v2.canon_determination import load_canon_registry
    bad = tmp_path / "bad.yaml"
    bad.write_text("canons: [unclosed\n  - id: X\n :::not yaml", encoding="utf-8")
    assert load_canon_registry(str(bad)) == []
    missing = tmp_path / "nope.yaml"
    assert load_canon_registry(str(missing)) == []  # fichier absent -> []


def test_registre_reel_charge_et_applique():
    from zoran_v2.canon_determination import load_canon_registry
    reg = load_canon_registry()
    ids = {c["id"] for c in reg}
    assert {"CANON_STRUCTURE", "CANON_INTENT", "CANON_CONSTRAINT"} <= ids
    v = run_canon_determination(
        _env(objects=[_obj("k1", "code")], ofm=[_ofm("k1", ["CODE"])]), reg)
    assert v["status"] == PASS
    assert "CANON_STRUCTURE" in _ids(v)
