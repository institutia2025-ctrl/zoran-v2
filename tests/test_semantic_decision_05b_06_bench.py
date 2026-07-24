# CODEX SIGNATURE BLOCK
# MISSION_ID: ENGINE_05_06_SEMANTIC_DECISION_ARCHITECTURE_V1
# DATE: 2026-07-24
# CHANGE_REASON: progressive bench for the bounded 05B→06 seam
# IMPACT: TEST_ONLY
# GUARD_IDS: CHAIN_BENCH, LOCAL_AND_GLOBAL_COHERENCE_REQUIRED, NO_LLM_REASONING

from test_semantic_decision_v1 import _env

from zoran_v2.llm_request_build import run_semantic_request_build
from zoran_v2.semantic_decision import (
    PASS,
    deterministic_verbalizer,
    run_semantic_decision,
    verify_closed_render,
)


def _chain(question="Quel matériau faut-il éviter ?"):
    envelope = _env(question=question)
    semantic = run_semantic_decision(envelope)
    envelope["semantic_decision"] = semantic
    request = run_semantic_request_build(envelope)
    return envelope, semantic, request


def test_progressive_00_05_then_05b_then_06():
    envelope, semantic, request = _chain()
    assert all(envelope[key]["status"] == PASS for key in (
        "runtime_check", "object_discovery", "frame_selection",
        "operants_operes", "canon_determination", "coherence_engine",
    ))
    assert semantic["status"] == PASS
    assert semantic["authorize_06"] is True
    assert request["status"] == PASS
    assert request["authorized"] is True
    assert request["semantic_request"]["decision_id"] == (
        semantic["semantic_decision"]["decision_id"]
    )


def test_semantic_request_contains_no_raw_question_or_memory_state():
    envelope, _semantic, request = _chain()
    blob = repr(request)
    question = envelope["object_discovery"]["objects"][0]["normalized"]
    assert question not in blob
    assert "governed_memory_state" not in blob
    assert "FACT-1" not in blob


def test_deterministic_ablation_and_hostile_verbalizer():
    _envelope, semantic, request = _chain()
    decision = semantic["semantic_decision"]
    reference = deterministic_verbalizer(decision)
    assert request["semantic_request"]["claims"] == reference["claims"]
    assert verify_closed_render(decision, reference)

    hostile = {
        "decision_id": reference["decision_id"],
        "claims": [dict(reference["claims"][0], modality="HYPOTHESE")],
    }
    assert not verify_closed_render(decision, hostile)


def test_local_pass_general_non_mesure_never_reaches_06():
    _envelope, semantic, request = _chain(
        question="Pourquoi le matériau est-il interdit ?"
    )
    assert semantic["semantic_decision"]["coherence"]["local"] == PASS
    assert semantic["semantic_decision"]["coherence"]["general"] == "NON_MESURE"
    assert semantic["authorize_06"] is False
    assert request["authorized"] is False
    assert request["semantic_request"] is None


def test_discriminant_question_answer_is_decided_before_any_verbalizer():
    _envelope, semantic, request = _chain()
    decision = semantic["semantic_decision"]
    assert decision["question_intent"] == "ASK_FACT"
    assert decision["purpose"] == "INFORM"
    assert decision["conclusions"] == [{
        "claim_id": "CLAIM-0001",
        "source_fact_ids": ["FACT-1"],
        "text": "Le matériau X est interdit.",
        "modality": "PROUVE",
    }]
    assert request["semantic_request"]["claims"][0]["rendered_text"] == (
        "Le matériau X est interdit."
    )
