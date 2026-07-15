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
    # Registre avec operant.id non-str : REJET DÉTERMINISTE (skip, comme les autres entrées
    # de registre malformées déjà certifiées) -> pas de crash, résultat déterministe.
    reg = [{"id": [], "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]},
           {"id": "OP_DESCRIBE", "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    env = _env_03([{"object_key": "k", "kind": "code"}], [{"object_key": "k", "frames": ["CODE"]}])
    v = run_operants_operes_analysis(env, reg)  # ne doit PAS lever
    assert v["status"] == "PASS"
    assert v["analysis"][0]["operants"] == ["OP_DESCRIBE"]  # l'entrée malformée est ignorée
