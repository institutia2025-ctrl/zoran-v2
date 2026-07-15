"""Régression — finding Codex Session B CSB-META-P1-003 (baseline 01).

01 ne normalisait pas Unicode (NFC) : deux chaînes canoniquement ÉQUIVALENTES (forme précomposée
vs décomposée) produisaient deux `object_key` différentes -> deux identités pour un seul objet
canonique. Politique retenue : NFC (REX #15).
"""
import unicodedata

from zoran_v2.object_discovery import run_object_discovery, _normalize

RC_OK = {"status": "PASS"}


def _env(candidates):
    return {"runtime_check": RC_OK, "input_text": None, "object_candidates": candidates}


# café : forme PRÉCOMPOSÉE (U+00E9) vs DÉCOMPOSÉE (U+0065 U+0301) — canoniquement équivalentes.
PRECOMPOSEE = "café"
DECOMPOSEE = "café"


def test_normalize_nfc_rend_les_formes_equivalentes_egales():
    a = _normalize(PRECOMPOSEE)
    b = _normalize(DECOMPOSEE)
    assert a == b, "les formes canoniquement équivalentes doivent normaliser identiquement"
    assert a == unicodedata.normalize("NFC", a), "sortie en forme NFC"


def test_object_key_unicode_equivalence_dedup():
    # Deux candidats équivalents -> MÊME object_key -> dédup en 1 objet.
    v = run_object_discovery(_env([
        {"kind": "term", "value": PRECOMPOSEE, "provenance": {"structured": True}},
        {"kind": "term", "value": DECOMPOSEE, "provenance": {"structured": True}},
    ]))
    assert v["status"] == "PASS"
    assert v["count"] == 1, "les formes équivalentes doivent déduper en 1 objet"
    assert len({o["object_key"] for o in v["objects"]}) == 1


def test_non_regression_ascii():
    # Une valeur ASCII normale n'est pas altérée.
    v = run_object_discovery(_env([
        {"kind": "term", "value": "beta", "provenance": {"structured": True}}]))
    assert v["count"] == 1 and v["objects"][0]["normalized"] == "beta"


def test_formes_distinctes_restent_distinctes():
    # NFC ne doit pas fusionner des objets réellement différents.
    v = run_object_discovery(_env([
        {"kind": "term", "value": "alpha", "provenance": {"structured": True}},
        {"kind": "term", "value": "beta", "provenance": {"structured": True}},
    ]))
    assert v["count"] == 2


def test_nfc_ne_fusionne_pas_les_compatibilites_nfkc():
    # Politique NFC (pas NFKC) : un caractere de COMPATIBILITE que casefold NE replie PAS (chiffre
    # pleine chasse U+FF12) n'est PAS reduit -> "２" et "2" restent DISTINCTS. NFKC les fusionnerait.
    v = run_object_discovery(_env([
        {"kind": "term", "value": "２", "provenance": {"structured": True}},   # ２ (fullwidth)
        {"kind": "term", "value": "2", "provenance": {"structured": True}},
    ]))
    assert v["count"] == 2
