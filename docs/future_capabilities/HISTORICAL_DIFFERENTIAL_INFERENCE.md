# HISTORICAL_DIFFERENTIAL_INFERENCE — fiche capacité durable

- **Identifiant sémantique** : `HISTORICAL_DIFFERENTIAL_INFERENCE` (forme cible : `HISTORICAL_DIFFERENTIAL_CONTEXT_SERVICE`)
- **Anciens numéros / alias** : ENGINE-13 ; `13_HISTORICAL_DIFFERENTIAL_INFERENCE`
- **Description fonctionnelle** : ne pas repartir de zéro — retrouver une situation historique comparable, vérifier sa
  provenance recevable, comparer cadres anciens/actuels, conserver uniquement les conclusions encore valides, identifier
  le delta, recalculer seulement ce qui a changé, BLOQUER si versions/preuves incomparables. `R_t = R_previous_valid + F(delta_C) - I(delta_C)`.
- **Raison de conservation** : mémoire longue, continuité inter-session, reconstruction, réduction du recalcul, cohérence
  dans le temps, exploitation réelle de l'histoire.
- **Statut** : `NECESSARY_FOR_TARGET_PRODUCT / IMPLEMENTATION_DEFERRED`. *Réserve d'audit* : nécessité pour la cible
  ASSERTÉE, non encore MESURÉE (aucun benchmark de coût de recalcul).
- **Position architecturale** : **service auxiliaire AVANT pipeline** (`ZMOS historique → service différentiel → contexte
  historique figé → pipeline 00→11`). Jamais une porte après 11.
- **Inputs prévus** : `CURRENT_FRAME_OBJECT`, `HISTORICAL_FRAME_OBJECT[]`, `HISTORICAL_RESPONSE_OBJECT[]`,
  `INVARIANT_POLICY_OBJECT`, `PROVENANCE_OBJECT[]`, `TEMPORAL_STATE_OBJECT`.
- **Outputs prévus** : verdict différentiel (`HISTORICAL_REPLAY_NO_DELTA` / `FRAME_AUGMENTED` / `FRAME_BREAK` /
  `SURFACE_SIMILARITY` / `INDETERMINATE` / `BLOCKED`) + conclusions réutilisées/invalidées + delta.
- **Dépendances** : interface historique **ZMOS autoritaire** (objets versionnés, transactions closes, cadres engagés,
  provenance, hashes, temporalité, relations d'états, politique de sélection historique).
- **Incompatibilités** : ne doit pas modifier rétroactivement une transaction close ; les replays utilisent la VERSION
  HISTORIQUE ENGAGÉE (jamais une politique postérieure).
- **Risques** : réutiliser une conclusion non valable / une version postérieure / un historique falsifié.
- **Conditions mesurables de réactivation** : interface ZMOS autoritaire DISPONIBLE **et** coût de recalcul mesuré justifiant le service.
- **Interdictions** : aucun code avant interface ZMOS ; ne pas geler le point de contact ZMOS tant qu'il n'existe pas
  (gel contre producteur fantôme = dette) → viser `READY_EXCEPT_ZMOS_BINDING` ; ne pas en faire une porte numérotée après 11.
- **GO_CODE actuel** : ❌ non (bloqué sur interface ZMOS + nouveau GO Fred).
- **Sources historiques** : `specs/CONTRACT_ENGINE_13_HISTORICAL_DIFFERENTIAL_INFERENCE.md` (branche `governance/add-engine-13-historical-differential`, `47e5e0a`).
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : **AMONT** de F-025 puis 14 dans l'ordre fonctionnel ; alimente le
  `FUTURE_MODE_ROUTER` (F-024). Ne remplace ni la mémoire, ni GOV_COHERENT_EVOLUTION.
