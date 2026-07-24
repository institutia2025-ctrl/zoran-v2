# CODEX SIGNATURE BLOCK
# MISSION_ID: ENGINE_05_06_SEMANTIC_DECISION_ARCHITECTURE_V1
# DATE: 2026-07-24
# PREVIOUS_AUTHOR: NONE
# CHANGE_REASON: red-first contract for the bounded deterministic semantic decision capability
# IMPACT: TEST_ONLY
# GUARD_IDS: TEST_RED_BEFORE_FIX, NO_LLM_REASONING, LOCAL_AND_GLOBAL_COHERENCE_REQUIRED

import copy

from zoran_v2.semantic_decision import (
    BLOCKED,
    NON_MESURE,
    PASS,
    deterministic_verbalizer,
    run_semantic_decision,
    verify_closed_render,
)


def _env(question="Quel matériau faut-il éviter ?", memory=True):
    env = {
        "runtime_check": {"status": PASS},
        "object_discovery": {
            "status": PASS,
            "objects": [{
                "object_key": "text\u001fquel matériau faut-il éviter ?",
                "kind": "text",
                "normalized": question.casefold(),
                "provenance": [{"structured": True}],
            }],
        },
        "frame_selection": {
            "status": PASS,
            "object_frame_map": [{
                "object_key": "text\u001fquel matériau faut-il éviter ?",
                "frames": ["TEXT"],
            }],
        },
        "operants_operes": {"status": PASS, "analysis": []},
        "canon_determination": {
            "status": PASS,
            "canon_referential": {"fingerprint": "FP"},
            "canons_selected": [],
        },
        "coherence_engine": {
            "status": PASS,
            "coherence": {"S": 1.0},
            "resource": {"authorize_llm": True},
        },
    }
    if memory:
        env["governed_memory_state"] = {
            "status": PASS,
            "state_id": "MEM-STATE-1",
            "active": [{
                "fact_id": "FACT-1",
                "subject": "matériau",
                "predicate": "restriction",
                "value": "X interdit",
                "text": "Le matériau X est interdit.",
                "frame": "TEXT",
                "modality": "PROUVE",
            }],
            "superseded": [],
        }
    return env


def test_positive_fact_decision_is_complete_and_sealed():
    result = run_semantic_decision(_env())
    assert result["status"] == PASS
    decision = result["semantic_decision"]
    assert decision["question_intent"] == "ASK_FACT"
    assert decision["purpose"] == "INFORM"
    assert decision["conclusions"][0]["text"] == "Le matériau X est interdit."
    assert decision["coherence"]["local"] == PASS
    assert decision["coherence"]["general"] == PASS
    assert decision["decision_id"].startswith("SEMANTIC-DECISION-")


def test_missing_governed_memory_is_non_mesure_and_fail_closed():
    result = run_semantic_decision(_env(memory=False))
    assert result["status"] == PASS
    assert result["semantic_decision"]["status"] == NON_MESURE
    assert result["authorize_06"] is False


def test_local_truth_but_wrong_purpose_fails_general_coherence():
    result = run_semantic_decision(_env(question="Pourquoi le matériau est-il interdit ?"))
    decision = result["semantic_decision"]
    assert decision["coherence"]["local"] == PASS
    assert decision["coherence"]["general"] == NON_MESURE
    assert result["authorize_06"] is False


def test_deterministic_and_input_immutable():
    env = _env()
    snapshot = copy.deepcopy(env)
    assert run_semantic_decision(env) == run_semantic_decision(env)
    assert env == snapshot


def test_reference_verbalizer_and_closed_render_verifier():
    decision = run_semantic_decision(_env())["semantic_decision"]
    rendered = deterministic_verbalizer(decision)
    assert rendered == {
        "decision_id": decision["decision_id"],
        "claims": [{
            "claim_id": decision["conclusions"][0]["claim_id"],
            "rendered_text": "Le matériau X est interdit.",
            "modality": "PROUVE",
        }],
    }
    assert verify_closed_render(decision, rendered) is True


def test_hostile_gemma_cannot_add_change_or_reorder_meaning():
    decision = run_semantic_decision(_env())["semantic_decision"]
    hostile = deterministic_verbalizer(decision)
    hostile["claims"][0]["rendered_text"] = "Le matériau X est recommandé."
    assert verify_closed_render(decision, hostile) is False


def test_blocked_if_any_01_to_05_stage_is_not_pass():
    env = _env()
    env["coherence_engine"]["status"] = BLOCKED
    result = run_semantic_decision(env)
    assert result["status"] == BLOCKED
    assert result["authorize_06"] is False
