import pytest
from value_bench.harness import ValueBenchError, blind_pair, reconcile, validate_run, validate_unique

def run(config="MODEL_ONLY", run_id="r1"):
    return {"run_id":run_id,"fixture_id":"F1-v1","prompt_id":"P1","prompt":"Q","seed":17,
            "configuration":config,"model_version":"claude-haiku-4-5","model_parameters":{},
            "system_prompt":"NONE","context":"NONE","response":"answer","latency_total_ms":1,
            "tokens_input":1,"tokens_output":1,"estimated_cost":0.1,"runner_sha":"abc","timestamp":"now"}

def judgment(score=3):
    from value_bench.harness import CRITERIA
    return {"scores":{c:score for c in CRITERIA},"justifications":{c:"why" for c in CRITERIA},
            "textual_evidence":{c:"answer" for c in CRITERIA}}

def test_labels_are_masked_and_system_order_inverts():
    a,b=run(),run("ZORAN_FULL","r2")
    p1,s1=blind_pair(a,b,False); p2,s2=blind_pair(a,b,True)
    assert s1["SYSTEM_A"] != s2["SYSTEM_A"]
    assert "MODEL_ONLY" not in str(p1) and "ZORAN_FULL" not in str(p1)

def test_duplicate_run_id_rejected():
    with pytest.raises(ValueBenchError, match="duplicate"): validate_unique([run(),run("ZORAN_FULL")])

def test_empty_response_rejected():
    r=run(); r["response"]=""
    with pytest.raises(ValueBenchError, match="empty"): validate_run(r)

def test_truncated_response_rejected():
    r=run(); r["truncated"]=True
    with pytest.raises(ValueBenchError, match="truncated"): validate_run(r)

def test_missing_metric_rejected():
    r=run(); del r["tokens_input"]
    with pytest.raises(ValueBenchError, match="missing"): validate_run(r)

def test_contradictory_judges_become_non_mesure():
    result=reconcile(judgment(4),judgment(3))
    assert set(result.values()) == {"NON_MESURE"}
