"""Décision sémantique déterministe bornée entre les moteurs 05 et 06.

Ce composant ne formule pas librement une réponse. Il transforme uniquement
des sorties 01→05 validées et un état mémoire gouverné amont en décision
canonique scellée. Toute information insuffisante échoue en NON_MESURE.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

COMPONENT_ID = "05B_SEMANTIC_DECISION_V1"
VERSION = "1.0.0"

PASS = "PASS"
BLOCKED = "BLOCKED"
NON_MESURE = "NON_MESURE"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-05B-SEMANTIC-DECISION-V1",
    "META_ID": "META-ZORAN-V2-COMPONENT-05B",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "SEMANTIC_DECISION_V1 architecture exact SHA 86a541a087b25b5fa8b30078ad29c736078ecae4",
    "GUARD_IDS": [
        "NO_LLM_REASONING",
        "UPSTREAM_GOVERNED_MEMORY_ONLY",
        "LOCAL_AND_GENERAL_COHERENCE_REQUIRED",
        "FAIL_CLOSED_NON_MESURE",
        "SEALED_CANONICAL_DECISION",
        "IMMUTABLE_INPUT",
        "DETERMINISTIC",
    ],
    "ROLLBACK": "git revert du commit dédié sur branche codex/semantic-decision-v1",
}

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_CAPABILITY_05B_SEMANTIC_DECISION_V1",
    "SOURCE_SHA": "86a541a087b25b5fa8b30078ad29c736078ecae4",
    "RETAINED_BEHAVIOR": "capacité bornée 05B produisant une décision sémantique déterministe scellée avant 06",
    "REJECTED_BEHAVIOR": "raisonnement LLM, décision laissée au verbaliseur, mémoire aval, action ou autorité finale",
    "LEGACY_CHECK": "aucun comportement historique interdit réintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

_STEPS = (
    ("runtime_check", "00_RUNTIME_CHECK"),
    ("object_discovery", "01_OBJECT_DISCOVERY"),
    ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
    ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
    ("canon_determination", "04_CANON_DETERMINATION"),
    ("coherence_engine", "05_COHERENCE_ENGINE"),
)
_FACT_KEYS = {
    "fact_id", "subject", "predicate", "value", "text", "frame", "modality",
}
_TOKEN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)
_STOP = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "est", "il",
    "elle", "faut", "quel", "quelle", "quels", "quelles", "pourquoi",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _tokens(text: str) -> set[str]:
    return {
        token.casefold()
        for token in _TOKEN.findall(text)
        if len(token) > 1 and token.casefold() not in _STOP
    }


def _intent(question: str) -> tuple[str, str]:
    normalized = question.strip().casefold()
    if normalized.startswith("pourquoi"):
        return "ASK_CAUSE", "EXPLAIN_CAUSE"
    if normalized.startswith(("quel", "quelle", "quels", "quelles")):
        return "ASK_FACT", "INFORM"
    return "UNKNOWN_INTENT", "UNKNOWN_PURPOSE"


def _base_decision(input_fingerprint: str, intent: str, purpose: str) -> dict:
    return {
        "version": VERSION,
        "input_fingerprint": input_fingerprint,
        "policy_fingerprint": _digest({
            "version": VERSION,
            "rules": ["R001", "R002", "R003", "R005", "R006", "R007", "R013"],
        }),
        "status": NON_MESURE,
        "question_intent": intent,
        "purpose": purpose,
        "facts": {"active": [], "superseded": [], "unknown": []},
        "conclusions": [],
        "relations": [],
        "temporal_model": [],
        "causal_model": [],
        "reservations": [],
        "unknowns": [],
        "proposed_action": None,
        "pre_refusal": None,
        "omissions": [],
        "ordering": [],
        "coherence": {"local": NON_MESURE, "general": NON_MESURE},
    }


def _seal(decision: dict) -> dict:
    payload = copy.deepcopy(decision)
    payload.pop("decision_id", None)
    payload.pop("seal", None)
    digest = _digest(payload)
    decision["decision_id"] = f"SEMANTIC-DECISION-{digest[:24].upper()}"
    decision["seal"] = {
        "algorithm": "SHA-256",
        "canonicalization": "JSON_UTF8_SORTED_KEYS_NO_WHITESPACE_NO_NAN",
        "hash": digest,
    }
    return decision


def _result(decision: dict, authorize: bool) -> dict:
    return {
        "component": COMPONENT_ID,
        "version": VERSION,
        "status": PASS,
        "blocked_by": None,
        "authorize_06": authorize,
        "semantic_decision": _seal(decision),
    }


def run_semantic_decision(envelope: dict) -> dict:
    """Produit une décision scellée sans mutation, réseau, mémoire ni LLM."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    for key, component in _STEPS:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return {
                "component": COMPONENT_ID,
                "version": VERSION,
                "status": BLOCKED,
                "blocked_by": component,
                "authorize_06": False,
                "semantic_decision": None,
            }

    frozen_input = copy.deepcopy(envelope)
    objects = frozen_input["object_discovery"].get("objects") or []
    questions = [
        obj.get("normalized")
        for obj in objects
        if isinstance(obj, dict) and isinstance(obj.get("normalized"), str)
    ]
    question = questions[0] if len(questions) == 1 else ""
    intent, purpose = _intent(question)
    decision = _base_decision(_digest(frozen_input), intent, purpose)

    memory = frozen_input.get("governed_memory_state")
    if not isinstance(memory, dict):
        decision["unknowns"].append("governed_memory_state")
        decision["reservations"].append("Mémoire gouvernée amont indisponible.")
        return _result(decision, False)
    if memory.get("status") != PASS or not isinstance(memory.get("state_id"), str):
        decision["unknowns"].append("valid_governed_memory_state")
        decision["reservations"].append("État mémoire amont invalide.")
        return _result(decision, False)

    active = memory.get("active")
    superseded = memory.get("superseded")
    if not isinstance(active, list) or not isinstance(superseded, list):
        decision["unknowns"].append("closed_memory_lists")
        return _result(decision, False)

    all_facts = active + superseded
    if any(not isinstance(fact, dict) or set(fact) != _FACT_KEYS for fact in all_facts):
        decision["unknowns"].append("closed_fact_schema")
        return _result(decision, False)
    ids = [fact["fact_id"] for fact in all_facts]
    if any(not isinstance(fid, str) or not fid for fid in ids) or len(ids) != len(set(ids)):
        decision["unknowns"].append("unique_fact_ids")
        return _result(decision, False)

    qtokens = _tokens(question)
    relevant = [
        fact for fact in active
        if qtokens & _tokens(f"{fact['subject']} {fact['predicate']} {fact['value']} {fact['text']}")
    ]
    decision["facts"]["active"] = copy.deepcopy(relevant)
    decision["facts"]["superseded"] = copy.deepcopy(superseded)

    if not question or intent == "UNKNOWN_INTENT" or not relevant:
        decision["unknowns"].append("answerable_question_or_relevant_active_fact")
        return _result(decision, False)

    decision["coherence"]["local"] = PASS
    if intent == "ASK_CAUSE":
        decision["unknowns"].append("bounded_causal_mechanism")
        decision["reservations"].append(
            "Le fait actif est établi, mais aucune causalité gouvernée ne permet de répondre pourquoi."
        )
        return _result(decision, False)

    conclusions = [
        {
            "claim_id": f"CLAIM-{index:04d}",
            "source_fact_ids": [fact["fact_id"]],
            "text": fact["text"],
            "modality": fact["modality"],
        }
        for index, fact in enumerate(relevant, start=1)
    ]
    decision["conclusions"] = conclusions
    decision["ordering"] = [claim["claim_id"] for claim in conclusions]
    decision["coherence"]["general"] = PASS
    decision["status"] = PASS
    return _result(decision, True)


def deterministic_verbalizer(decision: dict) -> dict:
    """Verbaliseur de référence : copie fermée des claims déjà décidés."""
    if not isinstance(decision, dict) or decision.get("status") != PASS:
        raise ValueError("décision PASS requise")
    return {
        "decision_id": decision["decision_id"],
        "claims": [
            {
                "claim_id": claim["claim_id"],
                "rendered_text": claim["text"],
                "modality": claim["modality"],
            }
            for claim in decision["conclusions"]
        ],
    }


def verify_closed_render(decision: dict, rendered: dict) -> bool:
    """Vérifie sans analyse sémantique libre l'identité de chaque claim rendu."""
    try:
        if set(rendered) != {"decision_id", "claims"}:
            return False
        if rendered["decision_id"] != decision["decision_id"]:
            return False
        expected = deterministic_verbalizer(decision)
        return _canonical(rendered) == _canonical(expected)
    except (KeyError, TypeError, ValueError):
        return False
