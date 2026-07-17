# SPEC_ENGINE_11_TRACE_AND_CLOSE — contrat figé (ratifié Fred 2026-07-15)

CANONICAL_SPEC = `SPEC_ENGINE_11_TRACE_AND_CLOSE`. ENGINE-11 est la porte **terminale** du pipeline certifié ENGINE-00→11 (aucune porte après). La coherent evolution est une méta-boucle de gouvernance hors pipeline, non-runtime et non numérotée comme gate (cf. `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md`, reclassé `GOV_COHERENT_EVOLUTION`).

## Rôle
Clôturer une transaction de raisonnement/action en produisant **un** objet-clôture unique, immuable, déterministe,
consolidant les preuves 00→10 + l'état final + la décision humaine éventuelle + le résultat d'exécution externe éventuel
+ les anomalies + les conditions de reprise. **N'exécute jamais l'action. Ne re-juge jamais 09/10.**

## Invariants (durs, fail-closed avant toute sortie)
`NO_LLM` · `NO_NETWORK` · `NO_ACTION_EXECUTION` · `NO_HIDDEN_READ` · `NO_INVENTION` · `NO_REJUDGMENT_OF_09_OR_10` ·
`FAIL_CLOSED` · `DETERMINISTIC` · `IMMUTABLE` + hérités : `ANTI_LEAK` récursif · `EXACT_STRING_PRESERVATION` ·
`NON_SCALAR_UNICODE_BLOCKED` · `CANONICAL_PRIMITIVE_REUSED` (`_fingerprint`, via 09, aucun 2ᵉ hasher) ·
`OBJECT_FIRST_CONTENT_SHA256` + nouveaux : `INTEGRITY_REVALIDATION_NOT_REJUDGMENT` · `DETERMINISTIC_REPLAY_09_AND_10` ·
`CLOSURE_COMPLETENESS` · `EXTERNAL_RESULT_INJECTED_AND_VERIFIED` · `HUMAN_GO_SCOPE_BOUNDED_EXACT` · `NO_TIME_INVENTION`.

## Entrées autoritaires (injectées ; revalidées ; NO_HIDDEN_READ)

### État de provisioning des autorités externes

Les autorités historiques sont révoquées. Aucun registre public de remplacement n'est provisionné dans le dépôt.
Les engagements runtime humain et exécuteur restent donc explicitement nuls. Toute `human_decision` ou tout
`execution_result` est `BLOCKED` avant lecture tant qu'un GO séparé n'a pas provisionné de nouvelles clés publiques.
Les flux ne portant aucune preuve externe restent fonctionnels. Les tests cryptographiques utilisent uniquement des
clés éphémères générées en mémoire dans un contexte de test isolé ; ce contexte n'est pas contrôlable par le payload.
La révocation est un invariant indépendant du provisioning : les anciens `key_id` `HUMAN-FRED-RSA-1` et
`EXECUTOR-1-RSA-1`, ainsi que les deux empreintes d'autorité historiquement compromises, appartiennent à des ensembles
immuables de révocation. ENGINE-11 les refuse avec `11_CLOSE_AUTHORITY_REVOKED` avant toute validation de signature,
y compris si un futur engagement runtime est configuré exactement sur une ancienne empreinte ou sur un registre
contenant un ancien `key_id`.

E1 enveloppe complète 00→10 (chaque porte status=PASS ; 09 sous `structured_decision`, 10 sous `action_admissibility_and_plan`).
E2 catalogue canonique + permissions (nécessaires au replay EXACT de 10 — injectés).
E3 résultat d'exécution externe — OPTIONNEL, objet `EXECUTION_RESULT_SCHEMA` injecté + vérifiable.
E4 décision humaine — OPTIONNELLE, objet `HUMAN_DECISION_SCHEMA` injecté.
E5 `provenance_refs` + `ci_refs` de clôture (non vides) + `closed_at_context` (INJECTÉ, jamais d'horloge).

## Ordre impératif (invariant supplémentaire Fred)
1. 00→10 = PASS. 2. anti-fuite/anti-surrogate sur 09/10/catalogue/permissions. 3. **replay `expected_09` depuis 00→08**,
exiger `received_09 == expected_09`. 4. **replay `expected_10` depuis 00→09 + catalogue + permissions + impact_context**,
exiger `received_10 == expected_10`. **Ces comparaisons ont lieu AVANT toute lecture de** `human_decision`,
`execution_result`, `provenance_refs`, `ci_refs`, `closed_at_context`. Toute divergence → `status=BLOCKED`.

## Statuts de clôture (`close_status`, quand `status=PASS`)
`CLOSED_NO_ACTION` · `CLOSED_BLOCKED` · `CLOSED_QUARANTINED` · `CLOSED_PLAN_READY_NOT_EXECUTED` ·
`CLOSED_AWAITING_HUMAN_APPROVAL` · `CLOSED_HUMAN_DECLINED` · `CLOSED_APPROVED_NOT_EXECUTED` ·
`CLOSED_EXECUTED_SUCCESS` · `CLOSED_EXECUTED_FAILED` · `CLOSED_ANOMALY`.
`status=BLOCKED` (fail-closed) est distinct : 11 refuse de produire une clôture autoritative.

### Mapping (déterministe)
- 10=`ACTION_NOT_REQUIRED` → `CLOSED_NO_ACTION` · `ACTION_BLOCKED` → `CLOSED_BLOCKED` · `ACTION_QUARANTINED` → `CLOSED_QUARANTINED`.
- 10=`ACTION_PLAN_READY` : sans exécution → `CLOSED_PLAN_READY_NOT_EXECUTED` ; avec exécution vérifiée → cf exécution.
- 10=`HUMAN_APPROVAL_REQUIRED` : sans décision → `CLOSED_AWAITING_HUMAN_APPROVAL` ; `DECLINED` → `CLOSED_HUMAN_DECLINED` ;
  `APPROVED` sans exécution → `CLOSED_APPROVED_NOT_EXECUTED` ; `APPROVED` + exécution vérifiée → cf exécution.
- Exécution vérifiée : `SUCCESS` sans anomalie → `CLOSED_EXECUTED_SUCCESS` ; `SUCCESS` avec anomalies documentées → `CLOSED_ANOMALY` ;
  `FAILED` → `CLOSED_EXECUTED_FAILED` ; `PARTIAL` → `CLOSED_ANOMALY`.

## Frontière dure (→ BLOCKED) vs douce (→ PASS + close_status)
DURE : schéma invalide · hash invalide · provenance absente/incohérente · replay 09 ou 10 divergent · action_plan_id divergent ·
action_id/target_refs divergents · GO humain hors scope (partiel/élargi/différent) · résultat d'exécution incomplet ·
exécution présente sans plan / sans GO sur mutation sensible / après refus · décision humaine sur chemin non-sensible ·
fuite interne · Unicode non scalaire · statut externe hors énumération · `closed_at_context`/`provenance_refs`/`ci_refs` absents.
DOUCE : exécution valide mais échouée · effet partiel déclaré · rollback requis · résultat valide avec anomalie documentée
· échec de l'exécuteur dans le scope autorisé → clôture PASS avec `close_status` adapté + anomalies enregistrées.

## Replay/revalidation de 09 et 10 (revalider ≠ re-juger)
11 rejoue déterministiquement `run_structured_decision` (09) et `run_action_admissibility_and_plan` (10) et exige l'égalité
EXACTE avec les objets reçus. Il ne recalcule ni ne modifie leurs verdicts (NO_REJUDGMENT). Défense en profondeur :
recompute de `CONTENT_SHA256` inclus dans l'égalité d'objet.

## Décision humaine & périmètre du GO
Appariement EXACT : `action_plan_id`, `action_id`, `target_refs`, `approval_scope` == plan 10. `decision` ∈ {APPROVED, DECLINED}.
`identity_ref`, `decided_at_context`, `provenance_refs` présents. Tout scope partiel/élargi/différent → BLOCKED. Jamais inféré.
Décision humaine valide UNIQUEMENT quand 10=`HUMAN_APPROVAL_REQUIRED`.

## Résultat d'exécution externe falsifié/incomplet
`EXECUTION_RESULT_SCHEMA` exact ; `CONTENT_SHA256` revalidé ; `provenance_refs` explicites ; `action_plan_id`/`action_id`/
`target_refs` == plan 10 ; `executor_id` présent ; `execution_status` ∈ énumération. Falsifié/incomplet/incohérent → BLOCKED.
Valide UNIQUEMENT quand 10=`ACTION_PLAN_READY` ou (`HUMAN_APPROVAL_REQUIRED` avec `APPROVED`). **Aucune clôture ne transforme
un plan en preuve d'exécution.**

## Schéma de sortie (objet PLAT, 21 clés, P-11-4)
`component, version, status, blocked_by, closure_id, close_status, decision_id, action_plan_id, action_status,
pipeline_gate_digest, final_state, human_decision_ref, execution_result_ref, anomalies, resumption_conditions,
rollback_plan_ref, provenance_refs, ci_refs, closed_at_context, CONTENT_SHA256, order_key`.
- `closure_id = "ACTION-CLOSE-" + _canonical_sha256(payload canonique COMPLET sans self-ref)` ; OBJECT_FIRST 2 phases.
- `CONTENT_SHA256` = hash de l'objet final SANS `CONTENT_SHA256` (aucune auto-référence). Primitive canonique réutilisée.
- `closed_at_context` injecté → mêmes entrées ⇒ même objet (déterminisme).

## Rollback & reprise
11 est additif terminal (mute rien). Enregistre `resumption_conditions` (ex. `AWAITING_HUMAN_GO`, `AWAITING_EXECUTOR_RESULT`,
`REVIEW_GLOBAL_IMPACT`) + porte `rollback_plan_ref` de 10 sans l'exécuter. Clôture gelée ; nouveau résultat externe ⇒ nouvel
objet-clôture (nouvel id), jamais mutation d'un objet existant. Rollback moteur = revert branche.

## Impact global 00→11
Nœud terminal additif ; aucune modif 00→10 ; aucun exécuteur intégré au pipeline ; aucune réouverture de 09/10 ; réutilise
`_fingerprint` (04 intact) + gardes 09. Clôt le pipeline. Nouveau tag après certif 11 ; aucun tag existant modifié.

## Fichiers
`zoran_v2/trace_and_close.py` · `tests/test_trace_and_close.py` · `specs/SPEC_ENGINE_11_TRACE_AND_CLOSE.md` ·
`EXECUTION_RESULT_SCHEMA.yaml` · `HUMAN_DECISION_SCHEMA.yaml` · `CANONICAL_SOURCES.yaml`. Aucune modif 00→10.
