# GOV_COHERENT_EVOLUTION — fiche capacité durable

- **Identifiant sémantique** : `GOV_COHERENT_EVOLUTION`
- **Anciens numéros / alias** : ENGINE-12 ; `12_COHERENT_EVOLUTION` (retiré)
- **Description fonctionnelle** : prendre une erreur confirmée → identifier sa classe générale → ajouter/renforcer un
  invariant → produire un guard → produire un test de non-récurrence → vérifier l'impact global → soumettre à audit →
  empêcher que la même classe d'erreur réapparaisse. Non-récurrence + correction gouvernée.
- **Raison de conservation** : mécanisme qui a réellement fermé les findings des moteurs (ex. les 2 findings d'usurpation
  d'ENGINE-11 : `SELF_ASSERTED_EXTERNAL_PROOF` + `IDENTITY_IMPERSONATION`).
- **Statut** : `ACTIVE_MANUAL_GOVERNANCE` — fonction déjà opérante comme PROCESSUS (registre findings, tests adversariaux,
  guards, CI, audits indépendants, quarantaine, décision Fred). Pas un moteur.
- **Position architecturale** : gouvernance HORS pipeline (méta-boucle, multi-transactions, post-confirmation d'erreur).
- **Inputs prévus** : erreur confirmée + contre-exemple minimal reproductible + cadres utilisés/manquants + invariants/guards
  existants + tests de non-régression + SHA/provenance des preuves.
- **Outputs prévus** : objet d'apprentissage (proposition de guard/invariant/test + impact global) soumis à audit ; jamais
  une modification directe du produit.
- **Dépendances** : registre de findings (`audits/claude/findings_log/FINDINGS_LOG.jsonl`), CI, audits indépendants.
- **Incompatibilités** : ne doit pas s'exécuter par transaction (chaque réponse déclencherait une tentative d'évolution).
- **Risques** : automatiser prématurément → auto-apprentissage / promotion incorrecte depuis une mauvaise interprétation
  d'un finding. Forme future obligatoire = CONSULTATIVE (propose ; ne modifie jamais le code ; ne promeut jamais ; ne merge
  jamais ; GO Fred final).
- **Conditions mesurables de réactivation (automatisation)** : trop de findings pour traitement manuel ; **récidive d'une
  classe déclarée fermée** (détectable via `FINDINGS_LOG.jsonl` `reused_downstream`) ; oubli fréquent de guards/tests ;
  délai d'audit bloquant ; contradictions entre registres.
- **Interdictions** : aucune promotion sans contre-exemple reproduit ; aucune règle depuis une intuition seule ; aucune
  auto-certification ; aucune preuve d'un autre SHA ; aucun guard sans test de non-régression.
- **GO_CODE actuel** : ❌ non (ENGINE-12 runtime = DO_NOT_BUILD).
- **Sources historiques** : `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md` (canonique, reclassé) ; reframe PR #41 mergé `5923252` ; `AGENTS.md` (règle de non-récurrence).
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : reçoit (à terme) les signaux de récidive du `DEFERRED_CAPABILITY_RELEVANCE_GUARD` ;
  aval fonctionnel de la boucle « erreur → correction » (dernière étape de l'ordre fonctionnel 13→F-025→14→quarantaine→**12**).
