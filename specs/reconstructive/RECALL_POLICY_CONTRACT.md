# Recall policy contract V1

Recall is a pipeline, not raw semantic search:

1. retrieve requested versioned records through the bridge;
2. validate schemas, receipts, SHAs and provenance;
3. apply structural eligibility filters;
4. deduplicate and classify versions/relations/provenances;
5. rank or select using a named versioned policy;
6. adapt a bounded set for ENGINE-01;
7. optionally expose an independently bounded context through ENGINE-07;
8. prove effective reuse from observable engine/LLM outputs.

Raw concatenation of all reconstructed content is forbidden. Persistence confers no truth, canon, priority or action authority. Each selected and rejected candidate MUST have a stable reason code. Recall outside the objective or active frames is rejected or quarantined with trace evidence.

`RECONSTRUCTED` proves data recovery only. `PRESENTED_TO_ENGINE_01`, `PRESENTED_TO_ENGINE_07`, `USED_IN_OUTPUT`, and `AFFECTED_DECISION_WITH_VALID_EVIDENCE` are separate states. Textual citation without a discriminating oracle is not proof of use.

The policy MUST accept explicit candidate, context, cycle, depth and time/transaction budgets. Identical inputs, store snapshot and policy configuration MUST yield the same structural selection; LLM output is evaluated separately by engines.
