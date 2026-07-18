# Reconstructive contract acceptance criteria V1

## Documentary acceptance

- Responsibilities have one explicit owner and prohibited owners.
- Engines 00-11 are unchanged and ENGINE-11 remains terminal.
- The bridge has no business decision, LLM or loop authority.
- ZMOS has no truth, canon, selection, stop or action authority.
- Budgets, stops, deduplication, conflicts and provenance are explicit.
- Reconstruction and effective reuse are distinct states.
- No runtime code, fixture-specific general rule, performance claim or optimal budget is introduced.
- Unknowns are `NON_MESURE`.

## Future proof sequence

Implementation cannot be approved before: unit tests; contract tests; integration tests; transactional persistence; complete process stop; fresh process; verified reconstruction; discriminating LLM reuse oracle; adversarial independent audit on the same SHA.

Required negative controls include every case in `RECONSTRUCTIVE_THREAT_MODEL.md`. Tests must verify no mutation of engine inputs, no persistence before ENGINE-11, no action authorization, deterministic structural selection, bounded termination, replayable traces and exact provenance/version preservation.

## Current status

Runtime implementation: `NOT_AUTHORIZED`. General multicadre continuity, quality, performance, costs and optimal budgets: `NON_MESURE`. Documentary acceptance does not certify runtime behavior.
