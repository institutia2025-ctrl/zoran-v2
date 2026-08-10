TIMESTAMP: 2026-07-17T14:18:33.8627821+02:00

# BENCH_1 execution-ready report

GUARD_IDS: `BENCH_SCOPE_ONLY`, `NO_ENGINE_MUTATION`, `RAW_MEASURES_ONLY`.

- SPEC_ID: `BENCH_1_INSTRUMENTATION_V1`
- frozen base SHA: `ce69742ea45cf515b545b98acaf741ff52ed5883`
- scope: benchmark harness, versioned fixtures, harness tests, protocol docs
- engine/runtime product files changed: `0`
- merge authority: `false`

## Red to green evidence

- RED: `python -m pytest tests/test_bench_harness.py -q` failed collection with
  `ModuleNotFoundError: No module named 'bench.harness'`.
- GREEN: the same command completed with `8 passed`.
- Non-regression: `603 passed` with `tests/test_cycle_probe.py` excluded.
- Environment limitation: `tests/test_cycle_probe.py` produced `1 passed, 1 failed`
  because this workstation runs Python 3.14 while ENGINE-00 requires Python <3.14.
  The failure is unchanged product behavior and is not hidden or converted to PASS.

## Example campaign

Command: `python -m bench.runner --iterations 3 --output bench/out`

- 21 unique executions: 7 fixtures x 3 iterations
- ordered ENGINE-00..11 vectors: 21/21 present
- nominal vector: 12/12 `PASS`
- end-to-end raw P50: 4,686,600 ns
- end-to-end raw P95: 7,725,500 ns
- replay match rate: 18/21 = 0.857143 (divergent fixture is intentionally false)
- gate pass rate: 246/252 = 0.976190 across all scenario-engine observations
- formula 05/08: recomputed from raw beta, delta_phi, T, sigma and checked per run
- Python initialization, pytest timing, and SOTA score: `NON_MESURE`

Artifacts:

- `bench/out/bench_1_runs.jsonl` SHA-256
  `DF9C436586D0AE7F65DB3A85885B86863549771179596F8D81B8A31134A3DD54`
- `bench/out/bench_1_manifest.json` SHA-256
  `00DFFF7BB51D99DB6D811021AC2873D52A16DC0195D57722BD9C4CB454FEBBDD`

No SOTA score is emitted. These numbers are raw measurements from this local
campaign and are not a product-performance certification.
