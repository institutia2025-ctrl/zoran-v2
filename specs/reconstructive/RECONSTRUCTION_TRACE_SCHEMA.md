# Reconstruction trace schema V1

Each run MUST trace:

- ZORAN, bridge and ZMOS SHAs;
- contract, schema, policy and configuration versions;
- `RUN_ID`, `TRACE_ID`, cycle identifiers and engine cycle identifiers;
- retrieved frame IDs/versions, relations, transformations and provenance digests;
- retrieval query digest, eligibility decisions and selection reasons;
- deduplication classifications and visited/reactivated candidates;
- conflict IDs, states and engine evidence;
- candidates presented to ENGINE-01;
- digest and references of context presented to ENGINE-07;
- all engine statuses, vetoes and closure reference;
- budget snapshots before and after each transition;
- stable stop reason;
- ZMOS transaction ID and receipt digest;
- reconstruction verification and effective-reuse oracle result;
- `orchestrator_action_authority=false`, separate from the unmodified ENGINE-10 verdict.

Traces MUST use canonical serialization and content digests, be append-only or immutably versioned, and distinguish `NON_MESURE`, `NOT_ATTEMPTED`, `BLOCKED`, `FAILED`, and `PROVED`. A summary cannot replace referenced evidence.
