# ADR — transverse reconstructive orchestrator

Decision status: `DRAFT_PENDING_INDEPENDENT_AUDIT`
Base ZORAN SHA: `e7113ad2202e57b325350e7ca6a13b7b10433c0f`

## Decision

Place continuity/reconstruction ownership in a transverse ZORAN orchestrator outside engines 00-11. The architecture is:

`ZORAN reconstructive orchestrator -> unchanged engines 00-11 -> external adaptation bridge -> transactional ZMOS`.

No ENGINE-12 is created. ENGINE-11 stays terminal. The orchestrator cannot bypass engine vetoes or ENGINE-10 action admissibility.

## Responsibility matrix

| Capability | Orchestrator | Engines | Bridge | ZMOS | LLM |
|---|---:|---:|---:|---:|---:|
| Loop state, budgets, stopping | owns | veto inputs | no | no | no |
| Candidate selection | owns policy | evaluate | no | no | propose only |
| Canon/coherence/conflicts | preserve/route | 04/05/08 own decisions | no | no | propose only |
| Action admissibility | no | ENGINE-10 | no | no | no |
| Cycle closure | no | ENGINE-11 | validate closed input | persist | no |
| Schema conversion/idempotence | request | no | owns | executes contract | no |
| Transactions and durable versions | no | no | transmit/verify | owns | no |
| LLM generation | no | ENGINE-07 invokes | no | no | injected dependency |

## Rejected placements

- Existing engine: violates purity through external state and duplicates established gates.
- New canonical engine: conflicts with the terminal 00-11 chain.
- Bridge ownership: creates an unaudited hidden engine.
- ZMOS ownership: gives persistence truth and decision authority.
- LLM ownership: makes a probabilistic dependency control budgets, state, or action.

## Prototype PR #10 matrix

| Prototype element | Classification | Contract decision |
|---|---|---|
| External `run_public_cycle` caller | reusable conceptually | relocate ownership to ZORAN orchestration |
| Engine-07 injected client | reusable conceptually | preserve ENGINE-07-only invocation |
| ZMOS-verified resolver | adapt | generalize to typed/versioned frames and policy input |
| `z3/zoran_bridge` validation/transaction/reconstruction | reusable conceptually | keep as bridge-only responsibility |
| Tour A/Tour B process separation | test later | future continuity proof pattern |
| Forbidden-material regex/token | fixture-specific | reject from general contract |
| Concatenation of the reconstructed table | reject | structural filtering and bounded selection required |
| Gemma/Ollama operational tuning | misplaced for this contract | exclude |
| Two-call canary limit | fixture-specific | do not promote as an optimal budget |
| Recall assertion | adapt | require observable evidence, not token citation alone |

## Consequences

The first implementation, if separately authorized, belongs in a new ZORAN orchestration package. Bridge/schema extensions require a distinct scoped decision. Performance, optimal budgets, and generalized continuity remain `NON_MESURE`.
