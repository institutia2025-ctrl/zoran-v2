# ZORAN Value Bench V1

The frozen 30-case `bench_2/corpus.jsonl` is executed once per configuration with seed label 17. Both use `claude-haiku-4-5`, temperature 0 and max tokens 512. The provider does not expose deterministic seeds, so the seed is a trace label only.

Each pair is presented anonymously as SYSTEM_A/SYSTEM_B. Judge 2 receives the reverse order. Both judges score all eight criteria from 0 to 4 with a justification and textual evidence. A score disagreement is `NON_MESURE`; no averaging resolves it. The quality gate passes only when ZORAN_FULL is non-inferior on every critical criterion aggregate.

Resource comparisons are suppressed unless the quality gate passes. Raw provider metrics remain in the traces. Continuity is `NON_MESURE` because this adapter does not use demonstrated real ZMOS persistence. No simulated memory is permitted.
