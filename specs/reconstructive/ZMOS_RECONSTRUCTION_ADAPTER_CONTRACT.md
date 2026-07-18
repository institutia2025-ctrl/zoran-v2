# ZMOS reconstruction adapter contract V1

The external bridge is the sole adapter between orchestrator schemas and transactional ZMOS APIs. Its allowed operations are schema validation, representation conversion, deterministic idempotency material, transaction transmission, receipt verification, requested reconstruction, and explicit error reporting.

It MUST NOT select frames, rank business relevance, resolve conflicts, choose canon, invoke an LLM, control the loop, or authorize action. It MUST accept explicit query bounds and return records with schema versions, immutable frame versions, provenance, transaction references and verification status.

Writes are allowed only for an ENGINE-11-closed cycle and must include idempotency key, input digest, transaction identifier and receipt digest. Reconstruction MUST verify requested RUN/TRACE identity, source SHAs, receipts, record digests and version links. Partial or divergent reconstruction fails closed; it cannot silently return a smaller usable context.

Retry policy belongs to the transactional contract and MUST preserve idempotency. The adapter exposes retry outcomes but does not reinterpret them as business success.
