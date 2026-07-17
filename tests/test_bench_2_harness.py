import json
from pathlib import Path

import pytest

from bench_2.harness import Bench2ValidationError, corpus_sha256, load_corpus, validate_results
from bench_2.runner import ExecutorUnavailable, executor_command

ROOT = Path(__file__).parents[1]
CORPUS = ROOT / "bench_2" / "corpus.jsonl"

def test_corpus_is_exactly_30_ordered_prompts_and_hashable():
    assert len(load_corpus(CORPUS)) == 30
    assert len(corpus_sha256(CORPUS)) == 64

def valid_result():
    fields = json.loads((ROOT / "bench_2" / "preregistration.json").read_text(encoding="utf-8"))["required_fields"]
    row = {field: "x" for field in fields}
    row.update(seed=17, configuration="MODEL_ONLY", response="bounded", tokens_total=2,
               estimated_cost="UNAVAILABLE", score_justifications={"fidelity":"evidence"})
    return row

@pytest.mark.parametrize("field", ["prompt_id", "seed", "tokens_total", "score_justifications"])
def test_missing_required_field_fails(field):
    row = valid_result(); del row[field]
    with pytest.raises(Bench2ValidationError): validate_results([row])

def test_unknown_configuration_fails():
    row = valid_result(); row["configuration"] = "UNKNOWN"
    with pytest.raises(Bench2ValidationError): validate_results([row])

def test_empty_response_fails():
    row = valid_result(); row["response"] = ""
    with pytest.raises(Bench2ValidationError): validate_results([row])

def test_duplicate_run_id_fails():
    row = valid_result()
    with pytest.raises(Bench2ValidationError): validate_results([row, dict(row)])

def test_missing_model_executor_fails_closed(monkeypatch):
    monkeypatch.delenv("BENCH2_MODEL_COMMAND", raising=False)
    with pytest.raises(ExecutorUnavailable, match="BENCH2_MODEL_COMMAND=UNAVAILABLE"):
        executor_command("MODEL_ONLY")

def test_missing_zoran_executor_fails_closed(monkeypatch):
    monkeypatch.delenv("BENCH2_ZORAN_COMMAND", raising=False)
    with pytest.raises(ExecutorUnavailable, match="BENCH2_ZORAN_COMMAND=UNAVAILABLE"):
        executor_command("ZORAN_FULL")
