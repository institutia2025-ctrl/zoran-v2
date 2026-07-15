# SPEC_ENGINE_10_ACTION_ADMISSIBILITY_AND_PLAN (FIGÉ — Fred 2026-07-15)

Porte 10. Position : `09_STRUCTURED_DECISION → 10_ACTION_ADMISSIBILITY_AND_PLAN → exécuteur externe (GO humain) → 11_TRACE_AND_CLOSE`.

## Fonction
Évaluer si la décision structurée de 09 peut devenir une action, puis produire un plan BORNÉ et vérifiable.
**AUCUNE exécution.** Ne déduit AUCUNE action implicite ; l'action est explicitement demandée (action_request)
et doit appartenir au catalogue gelé. Aucune invention, aucune mutation.

## Invariants
`NO_LLM` · `NO_NETWORK` · `NO_ACTION_EXECUTION` · `NO_ACTION_INVENTION` · `CATALOG_ONLY` ·
`GLOBAL_IMPACT_BEFORE_PLAN` · `FAIL_CLOSED` · `DETERMINISTIC` · `IMMUTABLE` · `HUMAN_GO_REQUIRED_FOR_SENSITIVE_MUTATION`
· `ANTI_LEAK` (récursif) · `EXACT_STRING_PRESERVATION` · `NON_SCALAR_UNICODE_BLOCKED` · `CANONICAL_PRIMITIVE_REUSED`
· `OBJECT_FIRST_CONTENT_SHA256` · `ACTION_PLAN_ID_COVERS_COMPLETE_CONTEXT` · `NO_HIDDEN_READ_IN_PURE_FN`.

## Entrées autoritaires (revalidées 4 niveaux ; catalogue+permissions INJECTÉS, aucune lecture cachée)
- **09** (`envelope["structured_decision"]`) : objet-décision plat, `status==PASS`, `decision_id` valide,
  **intégrité** : recompute `CONTENT_SHA256(objet 09 SANS CONTENT_SHA256) == 09.CONTENT_SHA256` (décision non altérée), complète.
- **action_request** (`envelope["action_request"]`) : `{action_id, target_refs}` (P-10-1, explicite). target_refs ⊆ cibles de 09.
- **catalogue** (argument injecté, ACTIONS_CATALOG.yaml gelé) : `{version, actions:[{id, requires_action, sensitive_mutation, permissions_required}]}` ; ids uniques ; `catalog_fingerprint` recalculé.
- **permissions** (argument injecté, versionné) : `{version, granted:[...]}`.
- **impact_context** (`envelope["impact_context"]`) : `{assessed_target_refs, global_impact}`.

## Gate d'entrée (fail-closed → status=BLOCKED)
`09.status==PASS` (et 00→09 PASS) · `decision_id` valide · `CONTENT_SHA256` 09 recalculé == · décision complète/non altérée ·
`action_request` bien formé · action_id ∈ catalogue (sinon BLOCKED, jamais d'invention) · catalogue versionné valide ·
permissions structure valide · target_refs ⊆ cibles 09 · anti-fuite · anti-surrogate.

## Sorties (action_status, status=PASS)
- `ACTION_NOT_REQUIRED` : action catalogue `requires_action=false`.
- `ACTION_BLOCKED` : permissions VALIDES mais refus explicite (`permissions_required ⊄ granted`).
- `ACTION_QUARANTINED` : impact global INCOMPLET (assessed_target_refs ne couvre pas les cibles) → pas de plan.
- `ACTION_PLAN_READY` : action admissible, permissions OK, impact global complet, NON sensible → plan borné + rollback.
- `HUMAN_APPROVAL_REQUIRED` : `sensitive_mutation=true` → approval_required=true, approval_scope, AUCUN plan_ready sans GO humain.
`status=BLOCKED` (fail-closed) est distinct de ces verdicts. P-10-4 : permissions absentes/malformées → BLOCKED ; refus valide → ACTION_BLOCKED.

## Sortie (objet PLAT, P-10-3) — 19 champs
`component, version, status, blocked_by, action_plan_id, action_status, decision_id, action_id, target_refs,
prerequisites, permissions_required, risks, global_impact, rollback_plan, approval_required, approval_scope,
justification_refs, CONTENT_SHA256, order_key`. (blocked_by = "<code 10 dédié>@<frontière source>".)

## action_plan_id + CONTENT_SHA256 (P-10-6)
- `action_plan_id = "ACTION-PLAN-" + _canonical_sha256(payload canonique COMPLET)`, réutilise `_fingerprint` (aucun 2ᵉ hasher ; 04 intact).
- Payload complet (contexte, sans self-ref) : `decision_id, CONTENT_SHA256 de 09, action_id, target_refs, catalog_version,
  catalog_fingerprint, permissions, prerequisites, risks, global_impact, rollback_plan, approval_scope`.
- `CONTENT_SHA256` = hash SÉPARÉ de l'objet final SANS CONTENT_SHA256. Aucune auto-référence.
- Garde surrogate (U+D800–U+DFFF) sur le payload AVANT hash → BLOCKED(NON_SCALAR_UNICODE) ; unicode scalaire préservé (aucun NFC/NFD/trim/CRLF).

## NON-goals
exécution · invention hors catalogue · génération/LLM · réseau · mutation référentiel/catalogue · re-jugement 09 ·
PLAN_READY sans impact global · PLAN_READY sensible sans approbation humaine · lecture cachée dans la fonction pure.
