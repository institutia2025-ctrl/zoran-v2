"""Tests déterministes de 01_OBJECT_DISCOVERY (voie A, faits/candidats injectés)."""
import copy

import pytest

from zoran_v2.object_discovery import (
    BLOCKED,
    COMPONENT_ID,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    PASS,
    VERSION,
    run_object_discovery,
)

RC_OK = {"status": "PASS"}


def _env(**kw):
    e = {"runtime_check": RC_OK, "input_text": None, "object_candidates": []}
    e.update(kw)
    return e


def test_blocked_si_00_absent():
    v = run_object_discovery({"object_candidates": []})
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"
    assert v["objects"] == [] and v["count"] == 0


def test_blocked_si_00_fail():
    v = run_object_discovery(_env(runtime_check={"status": "FAIL"}))
    assert v["status"] == BLOCKED and v["blocked_by"] == "00_RUNTIME_CHECK"


def test_pass_sans_candidats():
    v = run_object_discovery(_env())
    assert v["status"] == PASS and v["objects"] == [] and v["count"] == 0
    assert v["component"] == COMPONENT_ID and v["version"] == VERSION


def test_candidat_in_text_ok():
    txt = "alpha beta gamma"
    v = run_object_discovery(_env(
        input_text=txt,
        object_candidates=[{"kind": "term", "value": "beta",
                            "provenance": {"in_text": {"offset": 6, "len": 4}}}],
    ))
    assert v["status"] == PASS and v["count"] == 1
    o = v["objects"][0]
    assert o["kind"] == "term" and o["normalized"] == "beta"
    assert o["provenance"] == [{"in_text": {"offset": 6, "len": 4}}]


def test_candidat_structured_ok():
    v = run_object_discovery(_env(
        object_candidates=[{"kind": "entity", "value": "X1",
                            "provenance": {"structured": True}}],
    ))
    assert v["count"] == 1 and v["objects"][0]["provenance"] == [{"structured": True}]


def test_drop_missing_kind():
    cand = {"value": "z", "provenance": {"structured": True}}
    v = run_object_discovery(_env(object_candidates=[cand]))
    assert v["count"] == 0
    # Conforme au contrat : dropped réémet le candidat + son index + la raison.
    assert v["dropped"] == [{"candidate_index": 0, "candidate": cand, "reason": "missing_kind"}]


def test_drop_value_non_normalizable():
    v = run_object_discovery(_env(
        object_candidates=[{"kind": "term", "value": None, "provenance": {"structured": True}}]))
    assert v["dropped"][0]["reason"] == "value_not_normalizable"


def test_drop_provenance_absente():
    v = run_object_discovery(_env(object_candidates=[{"kind": "term", "value": "a"}]))
    assert v["dropped"][0]["reason"] == "provenance_unverified"


def test_drop_in_text_hors_bornes():
    v = run_object_discovery(_env(
        input_text="abc",
        object_candidates=[{"kind": "term", "value": "abc",
                            "provenance": {"in_text": {"offset": 2, "len": 10}}}]))
    assert v["dropped"][0]["reason"] == "provenance_unverified"


def test_drop_in_text_non_concordante():
    v = run_object_discovery(_env(
        input_text="alpha beta",
        object_candidates=[{"kind": "term", "value": "beta",
                            "provenance": {"in_text": {"offset": 0, "len": 4}}}]))  # "alph" != "beta"
    assert v["dropped"][0]["reason"] == "provenance_unverified"


def test_dedup_fusionne_provenances():
    txt = "beta and beta"
    v = run_object_discovery(_env(
        input_text=txt,
        object_candidates=[
            {"kind": "term", "value": "beta", "provenance": {"in_text": {"offset": 0, "len": 4}}},
            {"kind": "term", "value": "beta", "provenance": {"in_text": {"offset": 9, "len": 4}}},
        ]))
    assert v["count"] == 1
    assert v["objects"][0]["provenance"] == [
        {"in_text": {"offset": 0, "len": 4}},
        {"in_text": {"offset": 9, "len": 4}},
    ]


def test_ordre_deterministe():
    txt = "gamma beta"
    cands = [
        {"kind": "term", "value": "gamma", "provenance": {"in_text": {"offset": 0, "len": 5}}},
        {"kind": "term", "value": "beta", "provenance": {"in_text": {"offset": 6, "len": 4}}},
    ]
    v1 = run_object_discovery(_env(input_text=txt, object_candidates=cands))
    v2 = run_object_discovery(_env(input_text=txt, object_candidates=cands))
    assert v1 == v2
    # ordre par offset de 1re occurrence : gamma (0) avant beta (6)
    assert [o["normalized"] for o in v1["objects"]] == ["gamma", "beta"]


def test_non_invention_depuis_input_text():
    # texte plein de mots mais AUCUN candidat -> aucun objet inventé
    v = run_object_discovery(_env(input_text="the cat sat on the mat", object_candidates=[]))
    assert v["objects"] == [] and v["count"] == 0


def test_immutabilite_envelope():
    env = _env(input_text="beta", object_candidates=[
        {"kind": "term", "value": "beta", "provenance": {"in_text": {"offset": 0, "len": 4}}}])
    snap = copy.deepcopy(env)
    run_object_discovery(env)
    assert env == snap  # l'enveloppe n'est pas mutée


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_object_discovery(None)


def test_typeerror_candidates_non_liste():
    with pytest.raises(TypeError):
        run_object_discovery(_env(object_candidates="pas une liste"))


def test_order_key_present_pass_et_blocked():
    # order_key présent et stable dans les deux modes (schéma de sortie uniforme).
    assert run_object_discovery(_env())["order_key"] == ORDER_KEY
    assert run_object_discovery({"object_candidates": []})["order_key"] == ORDER_KEY


def test_dropped_contient_le_candidat():
    cand = {"kind": "term", "value": "a"}  # provenance absente -> dropped
    v = run_object_discovery(_env(object_candidates=[cand]))
    assert v["dropped"][0]["candidate"] == cand
    assert v["dropped"][0]["candidate_index"] == 0
    assert v["dropped"][0]["reason"] == "provenance_unverified"


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-01-OBJECT-DISCOVERY"
    assert GOVERNANCE["VERSION"] == VERSION
