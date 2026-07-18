# Reconstructive orchestrator threat model V1

| Counterexample | Precondition/stimulus | Expected result | Required proof | Fail-closed behavior |
|---|---|---|---|---|
| Combinatorial explosion | high-degree constellation | bounded selection | budget trace | stop before excess |
| Infinite loop | cycle repeats state | repetition stop | state digests | `REPETITION_DETECTED` |
| Repeated reactivation | same frame/reason | deduplicated | activation history | reject duplicate |
| Irrelevant recall | unrelated frame | reject/quarantine | policy reasons | no engine context |
| Obsolete frame | superseded version | preserve but exclude unless requested | version chain | no silent overwrite |
| Missing provenance | candidate lacks source | reject | validation trace | no adaptation |
| Conflicting frames | incompatible evidence | preserve parallel and route 04/05/08 | conflict record | blocking stop if unresolved |
| Persistence becomes truth | stored claim selected as canon | refuse inference | engine evidence absence | remain non-canonical |
| LLM ignores recall | output independent of recalled fact | reuse not proved | discriminating oracle | mark failed |
| LLM merely cites recall | copied phrase only | reuse not proved | effect oracle | mark failed |
| Bridge decides relevance | bridge returns ranking | contract violation | API trace | reject response |
| ZMOS becomes canonical | store assigns truth state | contract violation | schema/transaction trace | reject transaction |
| Restart reconstruction incomplete | missing fragment/version | divergence | manifest comparison | no partial context |
| Transaction not replayable | receipt exists, records diverge | failure | fresh-process replay | quarantine run |
| Live cache dependency | store absent but recall succeeds | violation | process isolation | fail run |
| Fixture-specific logic | domain regex determines policy | violation | source/config inspection | reject promotion |
| ENGINE-10 bypass | orchestrator authorizes action | violation | action trace | force false and stop |
| Persistence before ENGINE-11 | open cycle write requested | violation | closure reference | bridge refuses write |

Additional surfaces include schema downgrade, forged provenance, stale policy versions, cross-run identity collision, context injection, receipt substitution, retry duplication and circular ZORAN/ZMOS dependencies. Security controls require least authority, immutable versions, canonical digests, explicit trust boundaries and adversarial replay.

## Trust boundaries

- User/configuration authority supplies the objective and versioned budgets; it cannot forge engine or store evidence.
- The orchestrator trusts engine outputs only after existing engine contract validation and ENGINE-11 closure.
- The bridge trusts neither caller nor store implicitly; it validates schemas, identities, digests and receipts.
- ZMOS is trusted only for transaction semantics proven by verified receipts, never for truth or selection.
- Provenance issuers are explicit registered authorities bound to key/version or equivalent verifiable identity; self-issued runtime provenance is rejected.
- The LLM is untrusted probabilistic input evaluated by engines 08-11 and has no persistence or action authority.
