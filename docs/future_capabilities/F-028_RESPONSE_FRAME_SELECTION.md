# F-028 — FUTURE_RESPONSE_FRAME_SELECTION — fiche capacité durable

- **Identifiant sémantique** : `FUTURE_RESPONSE_FRAME_SELECTION`
- **Anciens numéros / alias** : F-028 ; **ANCIEN moteur 09** (spec 2026-07-14), déplacé par l'ADR-delta (2026-07-15) en branche présentation non autoritaire.
- **Description fonctionnelle** : sélection du CADRE DE PRÉSENTATION de la réponse (rendu utilisateur), HORS chaîne
  décision/action. Ne modifie ni verdict, ni décision, ni plan ; ne canonise rien.
- **Raison de conservation** : couche présentation UX distincte du `STRUCTURED_DECISION` (09 certifié actuel).
- **Statut** : `FUTURE_DORMANT · NON_CANONICAL · NO_CODE · POST_CERTIFICATION_00_11 · HORS_CHEMIN_CRITIQUE`.
- **Position architecturale** : branche PRÉSENTATION non autoritaire (amont de F-029).
- **Inputs prévus** : sortie décisionnelle (09/10/11) + contexte de rendu utilisateur.
- **Outputs prévus** : cadre de présentation sélectionné (non autoritaire).
- **Dépendances** : sortie de 10/11 ; ADR dédié pour toute activation.
- **Incompatibilités** : ne doit JAMAIS altérer verdict/décision/plan ; strictement non autoritaire.
- **Risques** : confondre présentation et décision (doit rester non autoritaire).
- **Conditions mesurables de réactivation** : décision de construire la couche présentation utilisateur (+ ADR dédié).
- **Interdictions** : aucun code sans GO Fred + ADR dédié ; aucune modification de la chaîne décision/action.
- **GO_CODE actuel** : ❌ non.
- **Sources historiques** : `scratchpad/ADR_DELTA_09_10_PIPELINE.md` (2026-07-15 17:47) ; mémoire F-028. Renumérotation : ancien 09 → F-028.
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : amont de F-029 ; branche présentation (aval de la chaîne décisionnelle, en amont de F-027).
