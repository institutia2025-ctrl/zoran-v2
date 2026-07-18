# Reconstructive orchestrator contract V1

## Authority and invariants

The orchestrator owns explicit reconstructive loop state, injected budgets, transitions, candidate selection, deduplication, stagnation detection, conflict routing, stop evaluation, traces, and bounded bridge calls. It MUST NOT canonize, authorize actions, transact directly with ZMOS, call an LLM outside ENGINE-07, retain implicit process memory, or bypass any engine gate.

## Request

A request MUST contain `contract_version`, objective, initial frame references, explicit budget configuration, ZORAN/bridge/ZMOS SHAs, policy versions, `RUN_ID`, and `TRACE_ID`. Missing or incompatible values fail before retrieval.

## State machine

Initial state is `VALIDATE_REQUEST`; terminal states are `STOPPED`, `COMPLETED`, and `ERROR`. Valid transitions are:

| From | Condition | To |
|---|---|---|
| `VALIDATE_REQUEST` | valid | `RETRIEVE` |
| any non-terminal state | invalid input, bridge/transaction/runtime error | `ERROR` |
| `RETRIEVE` | verified records available | `FILTER` |
| `RETRIEVE` | no record or stop budget reached | `STOPPED` |
| `FILTER` | eligible records exist | `DEDUPLICATE` |
| `FILTER` | none eligible | `STOPPED` |
| `DEDUPLICATE` | novel/reactivatable candidates exist | `SELECT` |
| `DEDUPLICATE` | repetition or no novelty | `STOPPED` |
| `SELECT` | bounded set non-empty | `ADAPT_ENGINE_01` |
| `SELECT` | blocking conflict or empty set | `STOPPED` |
| `ADAPT_ENGINE_01` | deterministic adaptation valid | `RUN_00_11` |
| `RUN_00_11` | engine veto or non-PASS | `STOPPED` |
| `RUN_00_11` | ENGINE-11 closes cycle | `ASSESS` |
| `ASSESS` | objective reached | `PERSIST_CLOSED_CYCLE` then `COMPLETED` |
| `ASSESS` | another cycle useful and within budget | `PERSIST_CLOSED_CYCLE` |
| `ASSESS` | stop condition | `PERSIST_CLOSED_CYCLE` then `STOPPED` |
| `PERSIST_CLOSED_CYCLE` | receipt verified and next cycle authorized | `RETRIEVE` |
| `PERSIST_CLOSED_CYCLE` | receipt verified and terminal decision recorded | `COMPLETED` or `STOPPED` |

No persistence transition exists before ENGINE-11 closure. Every transition MUST record previous state, next state, cause, input digests, output digests and policy version. Any transition absent from the table enters `ERROR` fail-closed.

Every terminal state has a non-null stable `stop_reason`. Deterministic error mapping is:

| Error cause | Terminal state | `stop_reason` |
|---|---|---|
| bridge validation, conversion, receipt or transport error | `ERROR` | `BRIDGE_ERROR` |
| transactional commit or idempotent replay failure | `ERROR` | `TRANSACTION_FAILURE` |
| reconstructed identities, versions, fragments or digests diverge | `ERROR` | `RECONSTRUCTION_DIVERGENCE` |
| invalid runtime, SHA, contract, configuration or authority precondition | `ERROR` | `RUNTIME_PRECONDITION_INVALID` |

If multiple causes occur, the earliest failed transition is authoritative; subsequent symptoms are traced as secondary errors and cannot replace the stable stop reason.

## Candidate and conflict rules

Persisted data is evidence, not truth. Selection MUST be explicit, reproducible for identical inputs/configuration, bounded, and provenance-aware. Conflicts remain parallel until engines 04/05/08 produce applicable evidence. A blocking unresolved conflict stops the loop; the bridge and ZMOS never arbitrate.

## No action authority

The orchestrator MUST set `orchestrator_action_authority=false`. It records but never overwrites the distinct ENGINE-10 admissibility verdict. Any action continues through ENGINE-10 and existing external authorization. Reconstruction success never implies action admissibility.
