# Frame → ENGINE-04/05 projection contract V1

Status: `DRAFT_PENDING_INDEPENDENT_AUDIT`
Scope: documentary only; no runtime authority; no engine, ZMOS or bridge change.

Defines the **deterministic projection** that lets the reconstructive frame coherence
gate obtain a verdict from the **real** ZORAN engines 04 and 05, without modifying them
and without inventing coherence. It refines `FRAME_COHERENCE_ADMISSIBILITY_GATE`
(`RECONSTRUCTIVE_ORCHESTRATOR_CONTRACT.md`): the injected `coherence_evaluator` is a
projection adapter whose verdict is **derived from genuine 04/05 outputs**, not from a
plaintext authority label.

```
cadre reconstructif candidat
→ enveloppe valide pour ENGINE-04        (projection déterministe, provenance-préservante)
→ sortie ENGINE-04                       (run_canon_determination, réelle)
→ enveloppe valide pour ENGINE-05        (04 output injecté tel quel)
→ sortie ENGINE-05                       (run_coherence_engine, réelle)
→ dérivation des six verdicts            (depuis les sorties réelles uniquement)
→ verdict utilisable par le gate
```

## Authority and non-invention invariant

The adapter is a **pure, mechanical transform**. It MUST NOT invent canons, conflicts,
fingerprints, commitments or coverage. Every projected value has an explicit source in the
candidate frame or its provenance-backed references. Conflicts and fingerprints are
produced **only by ENGINE-04 itself**; the adapter never fabricates them. `S`, `delta_phi`,
`tension` and the resource verdict are produced **only by ENGINE-05 itself**. The verdict
is therefore attributable to the real engines 04/05, not to the adapter.

## Real engine interfaces (source of truth, unmodified)

- ENGINE-04: `zoran_v2.canon_determination.run_canon_determination(envelope, registry) -> dict`.
- ENGINE-05: `zoran_v2.coherence_engine.run_coherence_engine(envelope, full_registry) -> dict`.
- ENGINE-08: `zoran_v2.coherence_2.run_coherence_2(envelope)` — **post-LLM**, out of this gate (see last section).

## Field correspondence — candidate frame → ENGINE-04 envelope

Every projected pair uses the single candidate identity; the universe is exactly one pair.

| ENGINE-04 envelope field | Projected value | Source (candidate frame) | Forbidden / impossible |
|---|---|---|---|
| `runtime_check.status` | `"PASS"` | constant (projection is 00-clean by construction) | — |
| `object_discovery.objects[0].object_key` | `frame_id` | `candidate_frame.frame_id` | empty / non-string → fail-closed |
| `object_discovery.objects[0].kind` | fixed `"reconstructive_frame"` | constant projected kind | — |
| `object_discovery.status` | `"PASS"` | constant | — |
| `frame_selection.object_frame_map` | `[{object_key: frame_id, frames: [relation_type]}]` | `frame_id`, `candidate_frame.relation_type` | `relation_type` unregistered / empty → fail-closed |
| `frame_selection.status` | `"PASS"` | constant | — |
| `operants_operes.analysis` | `[{object_key: frame_id, frame: relation_type, operants: [op_ids], operes: [...]}]` **iff** the frame carries provenance-backed operant references; else the pair is **absent** from `analysis` | `candidate_frame.operants` (each provenance-backed) | missing provenance on an operant ref → ref **excluded** (never gap-filled) |
| `operants_operes.unanalyzed` | pairs without operant references | derived | — |
| `operants_operes.status` | `"PASS"` | constant | — |
| `registry` (2nd argument) | `[{id, priority, applies_to_frames: [relation_type], applies_to_kinds: ["reconstructive_frame"]}]`, **one entry per declared grounding canon reference** | `candidate_frame.grounding[]` (each provenance-backed canon id + registered priority) | duplicate id, empty id, non-int priority, empty applies-lists → fail-closed; **no canon added that the frame did not declare** |

Provenance rule: a grounding or operant reference is projected **only** if it carries valid
provenance (`source_id`, `source_version`, `source_digest`, `status`). References without
provenance are **excluded**, never replaced by invented data — the pair then legitimately
becomes uncanonized/unanalyzed and the engines, not the adapter, lower the score.

## ENGINE-04 output → ENGINE-05 envelope

The real ENGINE-04 output is injected **verbatim** as `canon_determination`; nothing is edited.

| ENGINE-05 envelope field | Value |
|---|---|
| `runtime_check`, `object_discovery`, `frame_selection`, `operants_operes` | the same nodes projected above |
| `canon_determination` | the **verbatim** ENGINE-04 output (`canons_selected`, `uncanonized`, `conflicts`, `canon_referential{fingerprint, canons}`, `full_registry_commitment`, `resource_estimate`) |
| `full_registry` (2nd argument) | the **same** registry passed to ENGINE-04 |

By construction the 02 universe equals the 04 universe (single pair), satisfying ENGINE-05’s
`CSB-PROV-P1-004` coverage guard. The adapter never edits `fingerprint` or
`full_registry_commitment`; a mismatch can only mean a projection bug and MUST fail-closed.

## Fail-closed behavior on missing or impossible data

| Condition | Result |
|---|---|
| candidate `frame_id`, `frame_version`, `relation_type` or `provenance` missing/empty | projection aborts **before** calling any engine → `NON_VERIFIABLE` |
| any structurally invalid projected value (non-string key, empty id, non-int priority, duplicate canon id, both-canonized-and-uncanonized pair) | engine returns `BLOCKED` (`MALFORMED`/`CD04`) → `NON_VERIFIABLE` |
| ENGINE-04 `status != PASS` | `NON_VERIFIABLE` |
| ENGINE-05 `status != PASS` | `NON_VERIFIABLE` |
| engine raises | caught, treated as `BLOCKED` → `NON_VERIFIABLE` |

Missing data is never guessed. The adapter degrades to `NON_VERIFIABLE` or lets the real
engines lower `delta_phi`; it never manufactures coverage to force a positive verdict.

## Verdict derivation from real 04/05 outputs

Let `e04 = run_canon_determination(...)` and `e05 = run_coherence_engine(...)`. The verdict
is a pure function of their genuine outputs. **Structural ENGINE-04 facts are evaluated before
ENGINE-05 resolution facts**, in this fixed normative order (first match wins):

| # | Condition (real engine output only) | Verdict | Rationale |
|---|---|---|---|
| 1 | projection aborted, `e04.status != PASS`, `e05.status != PASS`, or `e05.coherence.total_pairs == 0` (nothing evaluable) | `NON_VERIFIABLE` | data absent / incoherent / invalid or empty engine output |
| 2 | `len(e04.conflicts) > 0` **or** `e05.coherence.tension > 0` | `CONFLICTUEL` | explicit ENGINE-04 canon conflict / conflictual tension → arbitration by 04/05/08 |
| 3 | `len(e04.uncanonized) > 0` | `CONDITIONNEL` | compatible but partially ungrounded → kept without canonization |
| 4 | `uncanonized` empty **but** `e05.coherence.resolved_pairs == 0` | `NON_VERIFIABLE` | canon present yet no resolution / no exploitable operant evidence |
| 5 | otherwise (`resolved_pairs == total_pairs`, no conflict) | `ADMISSIBLE` | resolved without conflict → integration possible |

This order fixes the two prior defects: no rule maps ENGINE-05’s resource veto to a relevance
verdict, and the `uncanonized` (ENGINE-04) branch is reached before any resolution test, so
`CONDITIONNEL` is reachable and the canon-present-but-unresolved case degrades to
`NON_VERIFIABLE` rather than being mislabelled.

### Verdicts that ENGINE-04/05 do NOT produce

- **`NON_PERTINENT` belongs to the upstream relevance / eligibility filter** (recall policy
  structural eligibility), **not** to coherence. ENGINE-04/05 emit no relevance measure, so
  this projection MUST NOT emit `NON_PERTINENT`.
- **`REDONDANT` belongs to the upstream deduplication stage**
  (`FRAME_CONSTELLATION_SCHEMA.md` `deduplication_result`), **not** to coherence. This
  projection MUST NOT emit `REDONDANT`.
- Both verdicts are supplied by their owning stage **before** the coherence request; deriving
  either here would be an invented coherence signal.

### Non-interpretation of resolution signals

`delta_phi`, `S`, and `resource.authorize_llm` are **resolution / resource** signals only.
`authorize_llm` is ENGINE-05’s LLM-budget veto (`delta_phi >= delta_phi_min`) and is **not
used** in this derivation. None of `delta_phi`, `S`, or `authorize_llm` may **ever** be
interpreted as a relevance/pertinence signal. They may accompany a verdict as an opaque
confidence annotation, never as a verdict cause.

The five reachable verdicts carry their contract consequences unchanged
(`FRAME_COHERENCE_ADMISSIBILITY_GATE` table). No numeric threshold is introduced by the
adapter: the only threshold that exists is ENGINE-05’s own `delta_phi_min`, owned by
ENGINE-05; any other threshold remains `NON_MESURE`.

## ENGINE-08 — `DEFERRED_POST_LLM`

ENGINE-08 (`run_coherence_2`) hard-requires the full 00→07 chain **including a real executed
LLM** (`llm_execution.executed is True`). It cannot contribute to a pre-integration,
no-LLM frame gate. In this contract ENGINE-08 is explicitly `DEFERRED_POST_LLM`: it is
**out of this gate**, its pre-LLM contribution is `NON_MESURE`, and it is never invoked to
justify a frame verdict here. A future post-LLM path (separate lot) may add ENGINE-08; until
then no verdict depends on it.

## Acceptance (documentary)

- Every ENGINE-04/05 envelope field has one explicit projected source; none is invented.
- Conflicts and fingerprints come only from ENGINE-04; `S`/`delta_phi`/`tension`/resource only from ENGINE-05.
- Missing/impossible data is fail-closed to `NON_VERIFIABLE`, never gap-filled.
- The verdict derivation uses only real engine outputs; `NON_PERTINENT` (relevance filter) and `REDONDANT` (dedup stage) are out; resolution signals are never read as relevance.
- ENGINE-08 is `DEFERRED_POST_LLM`. Runtime implementation of this projection is `NOT_AUTHORIZED` until independently audited.
