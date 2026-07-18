# Object candidate adapter contract V1

This deterministic adapter converts selected reconstructive candidates into the existing ENGINE-01 `object_candidates` boundary. It MUST NOT retrieve, rank, canonize, call an LLM, persist, or mutate source records.

Each output candidate MUST contain an admissible kind/value representation, structured provenance, stable source frame/version references, relation and transformation references when applicable, and a selection-reason reference. Ordering MUST be canonical and documented. One source identity maps deterministically to one candidate identity for a fixed adapter version.

Malformed, unprovenanced, over-budget, unresolved blocking-conflict, or schema-incompatible candidates are rejected before ENGINE-01 with reason codes. Rejections remain traced. Adapter output is input, never a claim that the candidate is true or canonical.
