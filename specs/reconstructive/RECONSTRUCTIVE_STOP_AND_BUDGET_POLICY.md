# Stop and budget policy V1

All budgets are explicit request inputs or versioned configuration. Required dimensions are maximum cycles, candidates per cycle, depth, LLM context volume, unresolved conflicts, repetitions, and optional time and transaction limits. This contract declares no optimal numeric value; defaults, if later proposed, are unmeasured startup hypotheses.

Stable stop reasons include:

- `OBJECTIVE_REACHED`;
- `ENGINE_VETO`;
- `NO_NEW_ADMISSIBLE_CANDIDATE`;
- `NO_NEW_INFORMATION`;
- `STAGNATION`;
- `REPETITION_DETECTED`;
- `UNRESOLVED_BLOCKING_CONFLICT`;
- `CYCLE_BUDGET_EXHAUSTED`;
- `DEPTH_BUDGET_EXHAUSTED`;
- `CANDIDATE_BUDGET_EXHAUSTED`;
- `CONTEXT_BUDGET_EXHAUSTED`;
- `UNRESOLVED_CONFLICT_BUDGET_EXHAUSTED`;
- `TIME_BUDGET_EXHAUSTED`;
- `TRANSACTION_BUDGET_EXHAUSTED`;
- `BRIDGE_ERROR`;
- `TRANSACTION_FAILURE`;
- `RECONSTRUCTION_DIVERGENCE`;
- `RUNTIME_PRECONDITION_INVALID`.

Budget exhaustion stops before the prohibited operation. A disabled optional budget is represented explicitly as `DISABLED`, never omitted. Stagnation means no admissible new frame, relation, transformation, resolved conflict or reduced debt across the configured observation window. Repetition compares stable candidate and transition identities, not only text. Every stop records the triggering evidence and final budget snapshot.
