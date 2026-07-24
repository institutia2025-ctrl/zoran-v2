TIMESTAMP: 2026-07-24T20:59:31+02:00

# SEMANTIC_DECISION_V1 — preuve d'implémentation

ID: ZORAN-SEMANTIC-DECISION-V1-IMPLEMENTATION-PROOF
META_ID: META-ZORAN-SEMANTIC-DECISION-V1-IMPLEMENTATION-PROOF
GUARD_IDS: EXACT_SHA, NO_LLM_REASONING, FAIL_CLOSED_NON_MESURE, LOCAL_AND_GENERAL_COHERENCE_REQUIRED, ROLLBACK_BY_GIT_REVERT

## Identité

- Dépôt : `institutia2025-ctrl/zoran-v2`
- Branche : `codex/semantic-decision-v1`
- Base gelée : `e7113ad2202e57b325350e7ca6a13b7b10433c0f`
- Commit d'implémentation scellé : `23f1b51c0ee538f39c28273035a99b304b8a6ed1`
- Architecture autoritaire : `Zoran-IA-Mimetique/zoran-bench-runtime@86a541a087b25b5fa8b30078ad29c736078ecae4`
- Rollback : revert du commit dédié, sans toucher au worktree négatif conservé.

## Premier point de rupture

Avant correction, `tests/test_semantic_decision_v1.py` échoue à la collecte :
`ModuleNotFoundError: No module named 'zoran_v2.semantic_decision'`.

## Correction bornée

- Ajout d'une capacité pure `05B_SEMANTIC_DECISION_V1`.
- Aucun changement des moteurs 03, 04 ou 05.
- Ajout dans 06 d'une entrée séparée `run_semantic_request_build`; le contrat historique `run_llm_request_build` reste inchangé.
- La mémoire consommée est exclusivement `governed_memory_state` amont.
- Donnée absente ou insuffisante : `NON_MESURE`, autorisation 06 refusée.
- La décision, les claims, modalités, ordre et hash sont produits avant tout verbaliseur.
- Le verbaliseur de référence fonctionne sans LLM.
- Un faux verbaliseur modifiant une modalité ou le texte est rejeté sans juge LLM.

## Résultats

- Test rouge initial : 1 erreur attendue, capacité absente.
- Tests ciblés et contrat historique 06 : `27 passed`.
- Ciblés + provenance/anti-legacy : `39 passed`.
- Non-régression hors sonde de version Python : `607 passed`.
- Suite complète : `607 passed, 2 failed`.
  - Échec introduit initial de provenance : corrigé puis retesté PASS.
  - Échec restant : `test_cycle_probe.py`, environnement Python 3.14 alors que le contrat exige Python <3.14. Ce défaut est environnemental et préexistant au patch.
- `git diff --check` : aucune erreur ; avertissement autocrlf seulement.

## Question discriminante unique

Question : `Quel matériau faut-il éviter ?`

Entrée gouvernée active : `Le matériau X est interdit.`

Décision pré-verbalisation :

- intention : `ASK_FACT`
- finalité : `INFORM`
- conclusion : `Le matériau X est interdit.`
- modalité : `PROUVE`
- cohérence locale : `PASS`
- cohérence générale : `PASS`
- autorisation 06 : `true`

Réponse du verbaliseur déterministe : `Le matériau X est interdit.`

Le faux verbaliseur remplaçant `interdit` par `recommandé` est rejeté.

## Verdict

`IMPLEMENTED_AND_LOCALLY_PROVEN`

Le code est scellé par le commit local ci-dessus. Aucun push, merge, déploiement, appel modèle ou benchmark 10/30 n'a été effectué.
