# EXTERNAL_EVIDENCE_AND_FALSIFICATION — fiche capacité durable

- **Identifiant sémantique** : `EXTERNAL_EVIDENCE_AND_FALSIFICATION`
- **Anciens numéros / alias** : ENGINE-14 ; `14_EXTERNAL_EVIDENCE_AND_FALSIFICATION`. **C'est la « fonction Internet »**
  du souvenir « 17 » de Fred (partie recherche externe uniquement).
- **Description fonctionnelle** : quand le corpus interne ne permet pas de trancher un delta matériel — déclencher une
  recherche externe (Internet) automatique, collecter preuves favorables ET défavorables, définir les critères de
  réfutation AVANT la recherche, tenter activement de falsifier, conclure avec le niveau réel de preuve.
- **Raison de conservation** : capacité auxiliaire importante pour dépasser les limites du corpus interne (escalade + falsification).
- **Statut** : `IMPORTANT_AUXILIARY_SERVICE / IMPLEMENTATION_DEFERRED`.
- **Position architecturale** : **service externe ISOLÉ**, jamais dans le cœur déterministe. Résultats obligatoirement
  FIGÉS, HASHÉS, SOURCÉS, mis en QUARANTAINE et AUDITÉS avant usage ; promotion canon = GO Fred. AVAL de F-025.
- **Inputs prévus** : `HISTORICAL_DIFFERENTIAL_RESULT` (de 13), `CURRENT_FRAME_OBJECT`, `DELTA_OBJECT`,
  `INTERNAL_EVIDENCE_STATUS_OBJECT`, `EXTERNAL_SOURCE_POLICY_OBJECT` versionné, `FALSIFICATION_POLICY_OBJECT` versionné.
- **Outputs prévus** : verdict externe (`EXTERNALLY_SUPPORTED` / `EXTERNALLY_REFUTED` / `PARTIALLY_SUPPORTED` /
  `CONFLICTING_EXTERNAL_EVIDENCE` / `NO_RELIABLE_EXTERNAL_EVIDENCE` / `FALSIFICATION_PASSED/FAILED` / `INDETERMINATE` /
  `BLOCKED`) + évaluation de sources (provenance, date, hash) + `corpus_action: PROPOSE_QUARANTINE_OBJECT`.
- **Dépendances** : **F-025** (COMPLEMENTARY_FRAME_DISCOVERY) en AMONT — sans le bon espace de questions, la recherche
  externe chercherait dans le mauvais espace ; politiques de sources/falsification versionnées ; frontière de quarantaine/ingestion.
- **Incompatibilités** : **incompatible avec le cœur déterministe** — introduit réseau + non-déterminisme. **Aucun accès
  Internet direct depuis le pipeline 00→11** (invariant `NO_NETWORK`). Le service doit être physiquement isolé.
- **Risques** : authenticité/spoofing des sources externes (classe `SELF_ASSERTED_PROOF` amplifiée), citation circulaire,
  duplication présentée comme multiple, non-reproductibilité du live web (mitigée par corpus figé + hash + timestamps).
- **Conditions mesurables de réactivation** : cas de production RÉCURRENTS de corpus interne insuffisant **et** design
  d'un service externe isolé prouvé (retrieval isolé, replay sur corpus figé) **et** F-025 disponible **et** GO Fred.
  (Ex. de seuil : signalé sur ~18 % des transactions de recherche avec ~80 % de confirmations humaines → besoin mesuré.)
- **Interdictions** : aucun réseau dans 00→11 ; aucune donnée externe directement au canon ; aucun verdict positif sans
  tentative documentée de contre-preuve ; aucune réécriture rétroactive des critères de falsification.
- **GO_CODE actuel** : ❌ non (après F-025 + définition quarantaine + GO Fred).
- **Sources historiques** : `specs/CONTRACT_ENGINE_14_EXTERNAL_EVIDENCE_AND_FALSIFICATION.md` (branche `governance/add-engine-13-historical-differential`, `b273b7f`).
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : AVAL de F-025 ; AMONT de la quarantaine puis de `GOV_COHERENT_EVOLUTION` (12)
  si une correction en découle. Fonctionnellement APRÈS le « 15 » informel (F-025), d'où la confusion de la numérotation.
