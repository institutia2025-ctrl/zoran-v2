"""Régressions — findings Codex Session B sur la frontière 03->04 (baseline 6d3f389).

Reproduit EXACTEMENT les deux contre-exemples publiés par Session B :
- CSB-03-04-P1-001 : 04 acceptait un faux PASS de 03 (payload malformé) -> doit BLOQUER.
- CSB-03-04-P1-002 : object_key / operant.id non hashables -> crash TypeError -> doit être
  déterministe (BLOCKED pour un payload d'enveloppe malformé ; skip déterministe pour une entrée
  de registre malformée, jamais d'exception).
"""
import copy

import pytest

from zoran_v2.operants_operes_analysis import run_operants_operes_analysis
from zoran_v2.canon_determination import run_canon_determination


# ---- CSB-03-04-P1-001 : payload 03 exact de Session B ----

PAYLOAD_01 = {"status": "PASS", "objects": [{"object_key": "k", "kind": "code"}]}
PAYLOAD_02 = {"status": "PASS", "object_frame_map": [{"object_key": "k", "frames": ["CODE"]}]}
MALFORMED_PAYLOAD_03 = {"status": "PASS"}  # ni component, ni analysis, ni unanalyzed, ni order_key
ENVELOPE_001 = {
    "runtime_check": {"status": "PASS"},
    "object_discovery": PAYLOAD_01,
    "frame_selection": PAYLOAD_02,
    "operants_operes": MALFORMED_PAYLOAD_03,
}
CANON_REGISTRY = [{"id": "CANON", "applies_to_frames": ["CODE"],
                   "applies_to_kinds": ["code"], "priority": 1}]


def test_04_blocks_malformed_pass_payload_from_03():
    # Test rouge de Session B : doit BLOQUER (pas PASS+CANON).
    observed = run_canon_determination(ENVELOPE_001, CANON_REGISTRY)
    assert observed["status"] == "BLOCKED"
    assert observed["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"
    assert observed["canons_selected"] == []


def test_04_blocks_wrong_component_03():
    env = copy.deepcopy(ENVELOPE_001)
    env["operants_operes"] = {"status": "PASS", "component": "PAS_03", "version": "1.0.0",
                              "analysis": [], "unanalyzed": [], "order_key": "x"}
    v = run_canon_determination(env, CANON_REGISTRY)
    assert v["status"] == "BLOCKED" and v["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"


# ---- CSB-03-04-P1-002 : identifiants non hashables ----

def _env_03(objects, ofm):
    return {"runtime_check": {"status": "PASS"},
            "object_discovery": {"status": "PASS", "objects": objects},
            "frame_selection": {"status": "PASS", "object_frame_map": ofm}}


def _env_04(objects, ofm):
    e = _env_03(objects, ofm)
    e["operants_operes"] = {"component": "03_OPERANTS_OPERES_ANALYSIS", "version": "1.0.0",
                            "status": "PASS", "blocked_by": None, "analysis": [],
                            "unanalyzed": [], "order_key": "x"}
    return e


def test_03_object_key_non_hashable_bloque_sans_crash():
    env = _env_03([{"object_key": [], "kind": "code"}], [{"object_key": [], "frames": ["CODE"]}])
    v = run_operants_operes_analysis(env, CANON_REGISTRY)  # ne doit PAS lever
    assert v["status"] == "BLOCKED"


def test_04_object_key_non_hashable_bloque_sans_crash():
    env = _env_04([{"object_key": [], "kind": "code"}], [{"object_key": [], "frames": ["CODE"]}])
    v = run_canon_determination(env, CANON_REGISTRY)  # ne doit PAS lever
    assert v["status"] == "BLOCKED"


def test_03_operant_id_non_hashable_pas_de_crash():
    # Registre (CONFIG, pas enveloppe) avec operant.id non-str : REJET DÉTERMINISTE par skip,
    # comme les entrées de registre malformées DÉJÀ CERTIFIÉES (test_operant_sans_id_ignore,
    # test_applies_non_liste_ignore) -> pas de crash, résultat déterministe. Finding 002 autorise
    # explicitement « rejet déterministe OU BLOCKED ».
    reg = [{"id": [], "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
           {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    env = _env_03([{"object_key": "k", "kind": "code"}], [{"object_key": "k", "frames": ["CODE"]}])
    v = run_operants_operes_analysis(env, reg)  # ne doit PAS lever
    assert v["status"] == "PASS"
    assert v["analysis"][0]["operants"] == ["OP_DESCRIBE"]  # l'entrée malformée est ignorée


# ---- variantes exactes exigées (Session A req 7) : object_key non canonique ----

_BAD_KEYS = [[], {}, None, "", 42, ("t",)]


@pytest.mark.parametrize("bad", _BAD_KEYS)
def test_03_object_key_non_canonique_bloque(bad):
    env = _env_03([{"object_key": bad, "kind": "code"}], [{"object_key": bad, "frames": ["CODE"]}])
    v = run_operants_operes_analysis(env, CANON_REGISTRY)  # ne doit PAS lever
    assert v["status"] == "BLOCKED", bad


@pytest.mark.parametrize("bad", _BAD_KEYS)
def test_04_object_key_non_canonique_bloque(bad):
    env = _env_04([{"object_key": bad, "kind": "code"}], [{"object_key": bad, "frames": ["CODE"]}])
    v = run_canon_determination(env, CANON_REGISTRY)  # ne doit PAS lever
    assert v["status"] == "BLOCKED", bad


def test_04_kind_non_str_bloque():
    env = _env_04([{"object_key": "k", "kind": ["code"]}], [{"object_key": "k", "frames": ["CODE"]}])
    v = run_canon_determination(env, CANON_REGISTRY)
    assert v["status"] == "BLOCKED"


def test_04_frames_non_str_bloque():
    env = _env_04([{"object_key": "k", "kind": "code"}], [{"object_key": "k", "frames": [42]}])
    v = run_canon_determination(env, CANON_REGISTRY)
    assert v["status"] == "BLOCKED"


def test_immutabilite_enveloppe_sur_payload_malforme():
    # req 8 : l'enveloppe ne doit pas être mutée, même sur une entrée malformée.
    env = _env_04([{"object_key": [], "kind": "code"}], [{"object_key": [], "frames": ["CODE"]}])
    snap = copy.deepcopy(env)
    run_canon_determination(env, CANON_REGISTRY)
    assert env == snap


def test_04_blocks_03_extra_key():
    # clés EXACTES du contrat 03 : un champ en trop dans le payload 03 -> BLOCKED.
    env = copy.deepcopy(ENVELOPE_001)
    env["operants_operes"] = {"component": "03_OPERANTS_OPERES_ANALYSIS", "version": "1.0.0",
                              "status": "PASS", "blocked_by": None, "analysis": [],
                              "unanalyzed": [{"frame": "CODE", "object_key": "k"}],
                              "order_key": "object_frame_map_order_puis_operant_id_alphabetique",
                              "EXTRA": 1}
    v = run_canon_determination(env, CANON_REGISTRY)
    assert v["status"] == "BLOCKED" and v["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"


# ---- GC-PR16-001 : validation contractuelle COMPLETE du payload 03 (ChatGPT) ----

_OA_ORDER = "object_frame_map_order_puis_operant_id_alphabetique"


def _env_04_03(oa_node):
    # objets/carte valides (1 couple (k, CODE)) ; noeud 03 personnalisable.
    return {"runtime_check": {"status": "PASS"},
            "object_discovery": {"status": "PASS", "objects": [{"object_key": "k", "kind": "code"}]},
            "frame_selection": {"status": "PASS",
                                "object_frame_map": [{"object_key": "k", "frames": ["CODE"]}]},
            "operants_operes": oa_node}


def _oa(**over):
    node = {"component": "03_OPERANTS_OPERES_ANALYSIS", "version": "1.0.0", "status": "PASS",
            "blocked_by": None, "analysis": [], "order_key": _OA_ORDER,
            "unanalyzed": [{"frame": "CODE", "object_key": "k"}]}
    node.update(over)
    return node


def test_04_accepte_payload_03_coherent_analysis():
    # cas positif : entrée analysis bien formée qui couvre exactement le couple de 02 -> PASS.
    oa = _oa(analysis=[{"frame": "CODE", "object_key": "k", "operants": ["OP"], "operes": ["k"]}],
             unanalyzed=[])
    v = run_canon_determination(_env_04_03(oa), CANON_REGISTRY)
    assert v["status"] == "PASS"


@pytest.mark.parametrize("oa_node", [
    _oa(analysis=[{}]),                                                   # entrée analysis vide
    _oa(unanalyzed=[None]),                                               # entrée unanalyzed non-dict
    _oa(version="9.9.9"),                                                 # mauvaise version
    _oa(order_key="n'importe quoi"),                                      # faux order_key
    _oa(analysis=[{"frame": "CODE", "object_key": "k", "operants": [42], "operes": ["k"]}],
        unanalyzed=[]),                                                   # opérant non textuel
    _oa(analysis=[{"frame": "CODE", "object_key": "k", "operants": [], "operes": ["AUTRE"]}],
        unanalyzed=[]),                                                   # operes != [object_key]
    _oa(unanalyzed=[{"frame": "FRONTEND", "object_key": "k"}]),           # couple inventé (absent de 02)
    _oa(analysis=[{"frame": "CODE", "object_key": "ZZZ", "operants": [], "operes": ["ZZZ"]}],
        unanalyzed=[]),                                                   # object_key absent de 01
    _oa(analysis=[], unanalyzed=[]),                                      # couple attendu manquant (couverture)
    _oa(analysis=[{"frame": "CODE", "object_key": "k", "operants": [], "operes": ["k"]}]),  # couple dans analysis ET unanalyzed
])
def test_04_bloque_payload_03_non_contractuel(oa_node):
    v = run_canon_determination(_env_04_03(oa_node), CANON_REGISTRY)
    assert v["status"] == "BLOCKED" and v["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"


def test_04_bloque_contre_exemple_exact_chatgpt_gc_pr16_001():
    # Contre-exemple VERBATIM de ChatGPT (GC-PR16-001) : version fausse + analysis/unanalyzed
    # non contractuels + faux order_key. Doit BLOQUER (ne plus traverser la frontiere 03->04).
    oa = {"component": "03_OPERANTS_OPERES_ANALYSIS", "version": "FAUSSE", "status": "PASS",
          "blocked_by": None, "analysis": [{"garbage": 1}], "unanalyzed": [42],
          "order_key": "inventée"}
    v = run_canon_determination(_env_04_03(oa), CANON_REGISTRY)
    assert v["status"] == "BLOCKED" and v["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"
