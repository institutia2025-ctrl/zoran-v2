from __future__ import annotations

import json, subprocess, sys, time, uuid
from datetime import datetime
from pathlib import Path

import bench_2.anthropic_adapter as anthropic
from bench_2.anthropic_adapter import MODEL, MAX_TOKENS, TEMPERATURE, invoke
from bench_2.harness import corpus_sha256, load_corpus
from bench_2.runner import execute
from value_bench.harness import CRITERIA, blind_pair, reconcile, sha256, summarize, validate_run, validate_unique

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"/"value_bench_v1"

def dump_jsonl(path, rows):
    path.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")

def generate():
    existing=OUT/"runs.jsonl"
    if existing.exists():
        rows=[json.loads(line) for line in existing.read_text(encoding="utf-8").splitlines() if line]
        if len(rows)==60:
            for row in rows: validate_run(row)
            validate_unique(rows)
            return rows
    corpus_path=ROOT/"bench_2"/"corpus.jsonl"; corpus=load_corpus(corpus_path)
    sha=subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    rows=[]
    for prompt in corpus:
        for config,module in (("MODEL_ONLY","bench_2.model_only_adapter"),("ZORAN_FULL","bench_2.zoran_full_adapter")):
            raw=execute([sys.executable,"-m",module],prompt,17,config)
            row={**raw,"fixture_id":prompt["id"]+"-v1","prompt":prompt["prompt"],
                 "model_parameters":{"temperature":TEMPERATURE,"max_tokens":MAX_TOKENS,"seed":"LABEL_ONLY_PROVIDER_UNSUPPORTED"},
                 "system_prompt":"NONE" if config=="MODEL_ONLY" else "BENCH_2_ENGINE_07_CANONICAL_STRUCTURED_PROMPT",
                 "context":"CANONICAL_PROMPT_ONLY" if config=="MODEL_ONLY" else "PROMPT_PLUS_VERSIONED_REGISTRIES",
                 "runner_sha":sha,"corpus_sha":corpus_sha256(corpus_path),"truncated":raw.get("provider_stop_reason")=="max_tokens"}
            validate_run(row); rows.append(row)
            dump_jsonl(OUT/"runs.jsonl",rows)
    validate_unique(rows); return rows

def judge_one(public, judge_id):
    schema={"scores":{c:"integer 0..4" for c in CRITERIA},
            "justifications":{c:"specific concise reason" for c in CRITERIA},
            "textual_evidence":{c:"short exact excerpt or NO_EVIDENCE" for c in CRITERIA}}
    instruction=("You are an independent blind evaluator. Evaluate each system separately against the prompt. "
      "Do not infer system identity. Score 0 worst to 4 best. Concision must not reward length. "
      "Return JSON only with top-level SYSTEM_A and SYSTEM_B, each exactly matching this schema: "+json.dumps(schema)+
      "\nCASE:\n"+json.dumps(public,ensure_ascii=False))
    previous=anthropic.MAX_TOKENS
    anthropic.MAX_TOKENS=4096
    try: text,metrics=invoke(instruction,MODEL)
    finally: anthropic.MAX_TOKENS=previous
    try: parsed=json.loads(text)
    except json.JSONDecodeError:
        start=text.find("{"); end=text.rfind("}")+1; parsed=json.loads(text[start:end])
    return parsed,metrics

def judge(rows):
    by={(r["prompt_id"],r["configuration"]):r for r in rows}; judgments=[]; scored=[]
    for i,pid in enumerate(sorted({r["prompt_id"] for r in rows})):
        a,b=by[(pid,"MODEL_ONLY")],by[(pid,"ZORAN_FULL")]
        per=[]
        for jid,invert in (("JUDGE_1",False),("JUDGE_2",True)):
            public,secret=blind_pair(a,b,invert); parsed,metrics=judge_one(public,jid)
            record={"judgment_id":"VBJ-"+uuid.uuid4().hex,"judge_id":jid,"prompt_id":pid,"blind_order":list(secret),
                    "source_run_ids":{slot: (a["run_id"] if config=="MODEL_ONLY" else b["run_id"]) for slot,config in secret.items()},
                    "scores":parsed,"provider_metrics":metrics,"timestamp":datetime.now().astimezone().isoformat()}
            judgments.append(record); per.append((parsed,secret))
            dump_jsonl(OUT/"judgments.jsonl",judgments)
        for config in ("MODEL_ONLY","ZORAN_FULL"):
            mapped=[]
            for parsed,secret in per:
                slot=next(k for k,v in secret.items() if v==config); mapped.append(parsed[slot])
            scored.append({"prompt_id":pid,"configuration":config,"scores":reconcile(mapped[0],mapped[1])})
    return judgments,scored

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=generate(); judgments,scored=judge(rows); summary=summarize(scored)
    dump_jsonl(OUT/"scored.jsonl",scored)
    report={"status":"BENCH_COMPLETE","quality_gate":summary["quality_gate"],
      "continuity_measurement":"NON_MESURE","model_only_quality":summary["means"]["MODEL_ONLY"],
      "zoran_full_quality":summary["means"]["ZORAN_FULL"],"per_criterion_delta":summary["delta"],
      "blind_judge_agreement":{"judgments":len(judgments),"unresolved_scores":sum(v=="NON_MESURE" for r in scored for v in r["scores"].values())},
      "continuity_metrics":{"status":"NON_MESURE","reason":"REAL_ZMOS_PERSISTENCE_NOT_USED"},
      "resources":{"latency_p50_p95":{"status":"NON_MESURE_QUALITY_GATE_NOT_PASSED"},"tokens":{"status":"NON_MESURE_QUALITY_GATE_NOT_PASSED"},"cost":{"status":"NON_MESURE_QUALITY_GATE_NOT_PASSED"},"cpu_ram_swap":{"status":"NON_MESURE_QUALITY_GATE_NOT_PASSED"}},
      "error_taxonomy":{"generation_errors":0,"judge_errors":0,"unresolved_judge_disagreements":sum(v=="NON_MESURE" for r in scored for v in r["scores"].values())},
      "sota_claim":"NON_MESURE" if summary["quality_gate"]=="NON_MESURE" else ("BELOW_BASELINE" if summary["quality_gate"]=="FAIL" else "SOTA_CANDIDATE"),
      "evidence_sha256":[],"mutations_engines":0,"merge_performed":False}
    report_path=OUT/"BENCH_VALUE_V1_REPORT.json"; report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files=[OUT/"runs.jsonl",OUT/"judgments.jsonl",OUT/"scored.jsonl",report_path]
    report["evidence_sha256"]=[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha256(p)} for p in files[:-1]]
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest={"files":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha256(p)} for p in files]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__": main()
