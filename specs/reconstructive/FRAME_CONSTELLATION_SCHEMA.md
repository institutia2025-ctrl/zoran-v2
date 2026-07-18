# Frame constellation schema V1

## Required records

A constellation contains immutable frame versions and typed edges. Unless marked optional, fields are required and non-null.

| Field | Type/cardinality | Rule |
|---|---|---|
| `frame_id` | non-empty string, 1 | stable logical identity |
| `frame_version` | non-empty string, 1 | immutable version identity |
| `frame_type` | non-empty enum string, 1 | registered type |
| `parent_frame_ids` | array of `{frame_id, frame_version}`, 0..N | sorted, unique references |
| `relation_type` | registered enum string, 1 | relation to activating frame |
| `transformation_id` | non-empty string, 0..1 | optional separately versioned transformation |
| `provenance` | object, 1 | `source_id`, `source_version`, `source_digest`, `status`, `observed_at`; all required |
| `activation_state` | enum string, 1 | `CANDIDATE`, `ACTIVE`, `QUARANTINED`, `INACTIVE`, or `REJECTED` |
| `activation_reason` | stable reason code plus evidence refs, 1 | never free-text only |
| `retrieval_query` | object, 1 | query digest and policy version; raw secrets forbidden |
| `candidate_ids` | unique sorted string array, 0..N | candidates considered this cycle |
| `visited_candidate_ids` | unique sorted string array, 0..N | candidates previously evaluated |
| `deduplication_result` | enum plus matched identity refs, 1 | classification defined below |
| `conflict_ids` | unique sorted string array, 0..N | referenced conflict records |
| `conflict_status` | enum string, 1 | state defined below |
| `cycle_id` | non-empty string, 1 | reconstructive-cycle identity |
| `engine_cycle_ids` | unique ordered string array, 0..N | completed engine cycles |
| `RUN_ID`, `TRACE_ID` | non-empty strings, 1 each | run and trace identities |
| `stop_reason` | stable enum string, 0..1 | null only before terminal state |
| `budget_snapshot` | object of configured/consumed/remaining integers, 1 | all enabled dimensions represented |
| `transaction_id`, `receipt_digest` | non-empty strings, 0..1 each | both absent before persistence or both present after verified receipt |

## Identity and version rules

The deduplication identity is `SHA-256(canonical-JSON([frame_id, frame_version, relation_type, provenance.source_digest]))`, lowercase hexadecimal. Canonical JSON is UTF-8, NFC-normalized strings, arrays preserved in specified canonical order, object keys lexicographically sorted, and no insignificant whitespace. A new version MUST NOT overwrite an older one. Exact duplicates, new versions, different relations, different provenance, derived transformations, already visited candidates, and justified reactivations are distinct classifications.

## Conflict states

Allowed states include `DETECTED`, `UNRESOLVED`, `RESOLVED`, `PARALLEL_PRESERVED`, `INVALIDATED_WITH_EVIDENCE`, `DEFERRED`, and `BLOCKING_STOP`. Resolution records MUST reference engine outputs and evidence; persistence alone cannot change conflict status to resolved.

All records require `schema_version="FRAME_CONSTELLATION_V1"`, the canonical serialization above, a SHA-256 content digest and provenance. Domain identifier namespaces and collision handling require contract tests before runtime authorization; the deterministic identity material and digest algorithm are fixed here.
