# F-027 — FUTURE_RELEVANCE_AND_NOISE_FILTER — fiche capacité durable

- **Identifiant sémantique** : `FUTURE_RELEVANCE_AND_NOISE_FILTER`
- **Anciens numéros / alias** : F-027 ; aucun numéro ENGINE.
- **Description fonctionnelle** : filtre de SORTIE (dernier nœud avant l'utilisateur) : retire tout élément (cadre, réserve,
  destinataire, option, information) qui ne modifie NI la compréhension NI la décision NI l'action immédiate → réponse
  MINIMALE SUFFISANTE. **Fail-safe INVERSÉ** : au DOUTE → PRÉSERVER (le sur-filtrage est le risque n°1).
- **Raison de conservation** : formalise la loi ZORAN « token economy / minimal suffisant » comme nœud tracé et réversible.
- **Statut** : `FUTURE_DORMANT · NON_CANONICAL · NO_CODE · POST_CERTIFICATION_00_11 · HORS_CHEMIN_CRITIQUE`.
- **Position architecturale** : branche PRÉSENTATION, nœud terminal (n'altère jamais le CONTENU décisionnel, seulement le bruit).
- **Inputs prévus** : réponse candidate + objectif immédiat + destinataire réel.
- **Outputs prévus** : réponse minimale suffisante (statuts `NOISE_REDUCED / MINIMAL_SUFFICIENT / CRITICAL_CONTEXT_PRESERVED / OVERFILTERING_RISK`).
- **Dépendances** : couche présentation (F-028/F-029) ou indépendante.
- **Incompatibilités** : ne RÉSUME pas / ne reformule pas le fond (retire le superflu, pas la substance).
- **Risques** : SUR-FILTRAGE (supprimer un élément critique) → doit lever `OVERFILTERING_RISK`, jamais silencieux.
- **Liste blanche JAMAIS supprimée** : sécurité, gouvernance, alerte bloquante, mentions légales/consentement, provenance/traçabilité, demande explicite de l'utilisateur.
- **Conditions mesurables de réactivation** : sorties trop verbeuses mesurées / coût token présentation mesuré.
- **Interdictions** : aucun code sans GO Fred ; jamais supprimer un élément de liste blanche ; toute suppression tracée et réversible.
- **GO_CODE actuel** : ❌ non.
- **Sources historiques** : `scratchpad/FUTURE_RELEVANCE_AND_NOISE_FILTER.md` (2026-07-15 15:42) ; mémoire F-027.
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : nœud terminal de la branche PRÉSENTATION (aval de F-028/F-029).
