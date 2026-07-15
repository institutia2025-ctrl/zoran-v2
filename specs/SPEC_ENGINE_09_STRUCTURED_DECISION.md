# SPEC_ENGINE_09_STRUCTURED_DECISION (FIGÉ — Fred 2026-07-15)

Porte 9 du pipeline de raisonnement ZORAN V2. Position : `08 ADMISSIBILITY → 09 STRUCTURED_DECISION
→ 10 ACTION_ADMISSIBILITY_AND_PLAN → exécuteur externe (GO humain) → 11 TRACE_AND_CLOSE`.

## Fonction
Transformer EXCLUSIVEMENT une réponse ADMISE par 08 (ACCEPT) en un OBJET-DÉCISION déterministe,
typé, traçable, SANS nouvelle génération. 09 ne juge pas (08 l'a fait), ne résume pas librement,
ne complète pas, n'invente pas, ne choisit ni n'exécute aucune action (→ 10).

## Invariants
`NO_LLM` · `NO_NETWORK` · `NO_NEW_INFORMATION` · `NO_ACTION_EXECUTION` · `FAIL_CLOSED` ·
`ANTI_LEAK` (récursif : clés internes interdites + séparateur `\x1f`) · `IMMUTABLE` · `DETERMINISTIC`.

## Entrées autoritaires (revalidées, 4 niveaux, jamais confiance au statut)
- `status` 00→08 == PASS (chaque moteur).
- `coherence_2` (08) : `verdict == "ACCEPT"` ; `authorize_09 is True` (identité STRICTE) ; `referential_fingerprint` str non vide.
- `canon_determination` (04) : `canon_referential.fingerprint` str non vide ET == 08.referential_fingerprint (chaîne).
- `llm_request_build` (06) : `authorized is True` ; `llm_request.targets` = liste non vide au schéma exact
  ({object_public_id `OBJ-\d{4,}`, kind_public, frame, canons:[str], operants:[str]}), unicité (opid,frame), canons/operants str.
- `llm_execution` (07) : `executed is True` ; `response` = RESPONSE_STRUCTURED_ANALYSIS_V1 (schéma exact) ;
  `response.referential_fingerprint == 04` ; chaque result (opid,frame)/canon/opérant ⊆ attendus 06 ; unicité.
- Concordance : `verdict==ACCEPT ⇔ authorize_09 is True` ; fingerprints 08/07 == 04.
- **COUVERTURE (P1)** : l'ensemble des (opid,frame) de la réponse == l'ensemble des cibles 06. Toute omission,
  cible inconnue ou couverture partielle → BLOCKED.

## Sortie
Enveloppe : `component, version, status, blocked_by, blocked_source, decision, order_key`.
- BLOCKED (fail-closed) : `status="BLOCKED"`, `blocked_by` = code 09 dédié, `blocked_source` = référence structurée
  vers le moteur/frontière source, `decision=None`.
- PASS : `decision` = objet-décision :
  `decision_id, decision_type, decision_status, targets, claims_retained, claims_rejected, constraints,
   justification_refs, referential_fingerprint, source_response_fingerprint`.

## Sémantique de décision (déterministe, ZÉRO information nouvelle)
- `decision_type = "STRUCTURED_ANALYSIS_DECISION_V1"`. `decision_status = "DECIDED_ON_ACCEPT"`.
- `targets` = [(object_public_id, frame)] triés = cibles 06.
- `claims_retained` = canon_findings `admissible==true` (verbatim, triés). `claims_rejected` = `admissible==false`.
- `constraints` = operant_outcomes (operant, applied, reason_code?) (verbatim, triés).
- `justification_refs` = `{canon_refs, operant_refs, target_refs, response_fingerprint, referential_fingerprint}` — références STRUCTURÉES uniquement, aucun texte libre / paraphrase.
- `referential_fingerprint` == 04 ; `source_response_fingerprint` == 07.response.referential_fingerprint (== 04).

## decision_id (Q3 figé)
`decision_id = "DECISION-" + sha256(canonical_json(PAYLOAD))`, PAYLOAD (clés triées) =
`{decision_type, verdict, referential_fingerprint, targets_06_normalisées, response_07_complète_normalisée,
  claims_retained, claims_rejected, constraints, justification_refs}`.
Règles : JSON canonique, clés triées, ordre des listes explicitement défini (tri), UTF-8, séparateurs déterministes,
AUCUNE donnée volatile / date / UUID aléatoire. → mêmes entrées = même id ; contenu différent (même fingerprint) = id différent.

## codes blocked_by (09 dédiés)
`09_STRUCTURED_DECISION_UPSTREAM_NOT_PASS` · `_NOT_ADMITTED` · `_FINGERPRINT_CHAIN` · `_REQUEST_MALFORMED` ·
`_RESPONSE_MALFORMED` · `_PROVENANCE` · `_COVERAGE` · `_LEAK`. Chacun accompagné de `blocked_source`.

## NON-goals
Résumé libre · complétion · génération/LLM · réseau · choix/exécution d'action · invention · re-jugement · modification du référentiel.
