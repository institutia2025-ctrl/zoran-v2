# Reconstructive orchestrator contracts V1

Status: `DRAFT_PENDING_INDEPENDENT_AUDIT`
Guard metadata: `ZORAN_WRENCH.json` with non-empty `guard_ids` applies to this directory.
Scope: documentary only; no runtime authority; no continuity claim.

The transverse ZORAN reconstructive orchestrator owns the explicit bounded loop. Engines 00-11 remain unchanged; ENGINE-11 remains terminal. The external bridge only validates and converts schemas, performs idempotent ZMOS transactions, verifies receipts, and reconstructs requested records. ZMOS persists versioned data but has no truth, selection, stopping, LLM, canon, or action authority.

Documents:

- `RECONSTRUCTIVE_ARCHITECTURE_DECISION.md`: binding placement and responsibility matrix.
- `RECONSTRUCTIVE_ORCHESTRATOR_CONTRACT.md`: state machine and interfaces.
- `FRAME_CONSTELLATION_SCHEMA.md`: stable versioned data model.
- `RECALL_POLICY_CONTRACT.md`: retrieval-to-reuse pipeline.
- `OBJECT_CANDIDATE_ADAPTER_CONTRACT.md`: deterministic ENGINE-01 boundary.
- `LLM_CONTEXT_ADAPTER_CONTRACT.md`: bounded ENGINE-07 context boundary.
- `ZMOS_RECONSTRUCTION_ADAPTER_CONTRACT.md`: bridge/ZMOS boundary.
- `RECONSTRUCTION_TRACE_SCHEMA.md`: replayable evidence.
- `RECONSTRUCTIVE_STOP_AND_BUDGET_POLICY.md`: injected budgets and stop reasons.
- `RECONSTRUCTIVE_THREAT_MODEL.md`: threats and fail-closed counterexamples.
- `RECONSTRUCTIVE_ACCEPTANCE_CRITERIA.md`: documentary and future proof gates.

Normative words `MUST`, `MUST NOT`, `SHOULD`, and `MAY` are binding within this V1 contract. Unknown or unmeasured properties are `NON_MESURE`.
