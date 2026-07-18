# LLM context adapter contract V1

Only the client injected into ENGINE-07 may consume LLM context. The adapter receives an already selected, bounded and provenance-validated context; it does not retrieve or rank.

The adapter MUST enforce the context budget, preserve frame/version/provenance references, separate observed facts from hypotheses, identify conflicts, avoid secrets and forbidden data, and emit a digest of the exact context presented. It MUST fail closed on unresolved identities, digest divergence, excess context or absent provenance.

The LLM MAY propose, reformulate, interpret and return an authorized schema. It MUST NOT persist, canonize, authorize action, alter frames, set budgets, control the loop or claim continuity. Effective reuse requires a case-specific oracle demonstrating an output dependency on recalled information; mentioning recalled text is insufficient.
