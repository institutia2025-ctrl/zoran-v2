# BENCH_1 instrumentation protocol

GUARD_IDS: `BENCH_SCOPE_ONLY`, `NO_ENGINE_MUTATION`, `RAW_MEASURES_ONLY`.

BENCH_1 runs ENGINE-00 through ENGINE-11 in one Python process and times only each
engine call with `time.perf_counter_ns()`. Python initialization and pytest are
outside that interval and remain `NON_MESURE` unless a separate launcher records
them. Every run records `run_id`, versioned `fixture_id`, exact Git SHA,
environment, iteration, scenario, ordered engine status/refusal vector, and the
unique key `SHA + fixture_id + scenario + iteration`.

The aggregator rejects missing IDs, missing/unordered engines, negative durations,
duplicate keys, mixed SHAs, and formula mismatches. It emits JSONL, an aggregate
manifest, P50/P95 per engine and end-to-end, replay and gate rates, and formula
05/08 evidence. Uninstrumented axes are `NON_MESURE`. No SOTA score is produced.

Run from the repository root:

```powershell
python -m bench.runner --iterations 3 --output bench/out
python -m pytest tests/test_bench_harness.py -q
```

Fixtures: nominal, refusal, contradiction, missing measurement, divergent replay,
no action, and external authority without provisioning. The harness is an
observability layer only; it does not mutate ENGINE-00..11, ZMOS, UI, or runtime.
