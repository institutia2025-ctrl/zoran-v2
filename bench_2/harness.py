from __future__ import annotations

import hashlib
import json
from pathlib import Path

SEEDS = (17, 51, 75)
CONFIGS = {"MODEL_ONLY", "ZORAN_FULL"}
REQUIRED_RESULT_FIELDS = set(json.loads((Path(__file__).with_name("preregistration.json")).read_text(encoding="utf-8"))["required_fields"])

class Bench2ValidationError(ValueError):
    pass

def load_corpus(path: Path) -> list[dict]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
    if len(rows) != 30 or [r["id"] for r in rows] != [f"B2-P{i:02d}" for i in range(1, 31)]:
        raise Bench2ValidationError("canonical corpus must contain ordered B2-P01..B2-P30")
    if any(set(r) != {"id", "prompt", "expected"} or not r["prompt"] or not r["expected"] for r in rows):
        raise Bench2ValidationError("invalid canonical prompt row")
    return rows

def corpus_sha256(path: Path) -> str:
    load_corpus(path)
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def validate_results(rows: list[dict], expected_configurations=CONFIGS) -> None:
    ids = set()
    for row in rows:
        missing = REQUIRED_RESULT_FIELDS - set(row)
        if missing:
            raise Bench2ValidationError(f"missing result fields: {sorted(missing)}")
        if row["configuration"] not in expected_configurations:
            raise Bench2ValidationError("unknown configuration")
        if row["seed"] not in SEEDS or not row["response"]:
            raise Bench2ValidationError("invalid seed or empty response")
        if row["run_id"] in ids:
            raise Bench2ValidationError("duplicate RUN_ID")
        ids.add(row["run_id"])
        if row["tokens_total"] is None:
            raise Bench2ValidationError("tokens must be measured")
        if row["estimated_cost"] is None:
            raise Bench2ValidationError("cost must be numeric or UNAVAILABLE")
        if not row["score_justifications"]:
            raise Bench2ValidationError("score justification required")

