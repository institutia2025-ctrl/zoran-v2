# CONTRAT — ENGINE-13 HISTORICAL_DIFFERENTIAL_INFERENCE

## Statut

`SPEC_ONLY` — aucun code moteur n'est autorisé avant certification de `00→12`, validation externe du contrat et GO explicite de Fred.

## Finalité

ENGINE-13 construit la réponse présente à partir de l'histoire recevable du système. Il ne répond pas comme si chaque requête était nouvelle : il identifie un cadre historique comparable, vérifie ses invariants, calcule le delta du cadre présent et réutilise seulement les conclusions encore valides.

## Formule canonique

```text
R_t = R_previous_valid + F(delta_C) - I(delta_C)
```

Avec :

```text
delta_C = (A_plus, A_minus, A_modified, X_contradictions)
```

- `A_plus` : éléments ajoutés ;
- `A_minus` : éléments supprimés ;
- `A_modified` : éléments modifiés ;
- `X_contradictions` : contradictions nouvelles ;
- `F` : opérateur d'augmentation, limité aux nouvelles inférences permises par le delta ;
- `I` : opérateur d'invalidation, limité aux conclusions historiques touchées par le delta.

Cette notation ASCII est canonique dans le dépôt afin d'éviter les caractères mathématiques illisibles ou corrompus.

## Principe PRACH

PRACH signifie `PRINCIPE_DE_REPONSE_AUGMENTEE_PAR_COHERENCE_HISTORIQUE`.

La réponse est une fonction du cadre présent et de son histoire autoritaire. Toute réutilisation historique doit être traçable et conditionnée au maintien des invariants applicables.

## Verdicts principaux

### HISTORICAL_REPLAY_NO_DELTA

Conditions :

- cadre historique autoritaire identifié ;
- invariants critiques intacts ;
- delta vide.

Action :

- réutiliser la réponse précédente valide ;
- ne pas répéter le raisonnement ;
- demander l'action nouvelle attendue.

### HISTORICAL_FRAME_AUGMENTED

Conditions :

- invariants critiques intacts ;
- delta non vide ;
- aucune rupture globale.

Action :

- conserver les conclusions non affectées ;
- raisonner uniquement sur le delta ;
- exposer ce que le nouveau cadre permet désormais.

### HISTORICAL_FRAME_BREAK

Conditions :

- au moins un invariant critique est modifié ;
- ou une contradiction nouvelle invalide une conclusion historique.

Action :

- invalider localement ou globalement selon la politique de l'invariant ;
- reconstruire uniquement la partie nécessaire ;
- signaler explicitement la rupture.

### HISTORICAL_SURFACE_SIMILARITY

Similarité lexicale ou vectorielle sans équivalence structurelle démontrée. Aucune conclusion historique ne peut être réutilisée comme autorité.

### HISTORICAL_INDETERMINATE

Historique, provenance, temporalité ou politique d'invariants insuffisants. Aucune réutilisation silencieuse.

### BLOCKED

Historique malformé, provenance falsifiée, versions incomparables non déclarées ou contradiction interne non résolue.

## Architecture de mémoire

Architecture hybride obligatoire :

1. index sémantique ou vectoriel pour proposer des candidats uniquement ;
2. graphe ou magasin d'objets comme source autoritaire ;
3. journal chronologique immuable pour reconstruire ce qui était connu au moment de la réponse ;
4. validation déterministe des invariants, de la provenance et du delta.

Un score de similarité ne rend jamais un verdict.

## Invariants

Chaque invariant porte :

- un identifiant ;
- une version ;
- un type : `GLOBAL`, `LOCAL`, `TEMPORAL`, `PROVENANCE` ou `CONDITIONAL` ;
- une politique : `MUST_MATCH`, `MAY_DIFFER`, `REQUIRES_RECHECK`, `INVALIDATES_SUBSET` ou `INVALIDATES_ALL`.

Invariants par défaut :

- identité de l'objet ;
- finalité de la demande ;
- périmètre fonctionnel ;
- cadres actifs ;
- version du contrat ;
- provenance ;
- temporalité ;
- statut de validation de la réponse historique.

Invariants conditionnels possibles : SHA, version de schéma, version de loi, environnement, dépendances et périmètre d'audit.

## Entrées autoritaires minimales

- `CURRENT_FRAME_OBJECT` ;
- `HISTORICAL_FRAME_OBJECT[]` ;
- `HISTORICAL_RESPONSE_OBJECT[]` ;
- `INVARIANT_POLICY_OBJECT` ;
- `PROVENANCE_OBJECT[]` ;
- `TEMPORAL_STATE_OBJECT`.

Une ancienne sortie textuelle non structurée ne peut pas être la seule source autoritaire.

## Sortie canonique minimale

```json
{
  "component": "13_HISTORICAL_DIFFERENTIAL_INFERENCE",
  "status": "PASS",
  "verdict": "HISTORICAL_FRAME_AUGMENTED",
  "historical_reference": {
    "frame_id": "FRAME-HIST-001",
    "response_id": "RESP-HIST-001",
    "timestamp": "2026-07-15T10:00:00+02:00"
  },
  "delta": {
    "added": [],
    "removed": [],
    "modified": [],
    "contradictions": []
  },
  "invariants": {
    "preserved": [],
    "changed_local": [],
    "changed_global": [],
    "requires_recheck": []
  },
  "reuse": {
    "preserved_conclusions": [],
    "invalidated_conclusions": [],
    "recompute_required": []
  },
  "augmentation": {
    "new_inferences": [],
    "new_actions_enabled": []
  },
  "answer_mode": "DELTA_ONLY"
}
```

## Règles fail-closed

- aucun antécédent sans provenance ;
- aucun score global ne neutralise un invariant critique ;
- aucune conclusion ne peut être réutilisée si son périmètre est inconnu ;
- aucune absence de delta ne peut être conclue si les versions sont incomparables ;
- aucune invalidation globale ne supprime les conclusions indépendantes ;
- aucune réponse historique n'est réécrite rétroactivement ;
- aucune recherche vectorielle n'a de pouvoir de verdict.

## Tests adversariaux minimaux

- même texte, SHA différent ;
- même SHA, périmètre différent ;
- cadre identique sans delta ;
- ajout non critique ;
- ajout critique ;
- suppression d'une contrainte ;
- contradiction avec une décision historique ;
- historique sans provenance ;
- forte similarité sémantique avec invariants différents ;
- faible similarité lexicale avec structure identique ;
- réponse historique partiellement valide ;
- timestamp expiré ;
- plusieurs antécédents concurrents ;
- boucle de réutilisation récursive ;
- historique postérieur présenté comme antérieur.

## Prérequis avant code

- moteurs `00→12` construits et certifiés ;
- gate global `00→12` PASS ;
- schémas des objets historiques figés ;
- politiques d'invariants versionnées ;
- dataset de cas identiques, augmentés, rompus et faux-similaires ;
- vérité de référence indépendante ;
- mesures de précision, rappel, faux réemploi et faux rejet ;
- audit anti-boucle et anti-réécriture du passé ;
- certification externe du contrat ;
- GO explicite de Fred.

## Gouvernance

ENGINE-13 ne remplace ni la mémoire, ni ENGINE-12, ni les audits externes. ENGINE-12 transforme les erreurs en apprentissages persistants. ENGINE-13 exploite l'histoire autoritaire pour produire une réponse différentielle. Fred reste l'autorité de GO et de promotion canonique.
