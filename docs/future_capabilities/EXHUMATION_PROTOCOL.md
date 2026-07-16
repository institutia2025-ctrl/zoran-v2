# EXHUMATION_PROTOCOL — protocole d'exhumation obligatoire des capacités différées

> Registre central : [`FUTURE_CAPABILITIES_REGISTRY.md`](FUTURE_CAPABILITIES_REGISTRY.md).
> Objectif : garantir qu'aucune capacité différée n'est ré-inventée, oubliée ou dupliquée, et que l'existant prime.

## Déclencheurs (avant toute mission touchant à…)
mémoire ou histoire · cadres manquants · sélection ou déplacement de cadres · recherche Internet · preuve externe ·
falsification · futur probable · créativité · présentation de réponse · bruit ou pertinence · évolution ou correction des règles.

## Procédure obligatoire
1. Lire `FUTURE_CAPABILITIES_REGISTRY.md`.
2. Identifier les fiches potentiellement concernées.
3. Lire INTÉGRALEMENT ces fiches.
4. Vérifier leurs dépendances et leurs anciens verdicts.
5. Produire le bloc `FUTURE_CAPABILITY_CHECK` (ci-dessous).
6. Privilégier **EXISTING_FIRST**.
7. Interdire toute reconstruction concurrente d'une capacité déjà enregistrée.
8. Ne jamais activer ni coder une capacité sans décision explicite de Fred.

## Bloc à produire
```
FUTURE_CAPABILITY_CHECK:
- capabilities_exhumed:        # ids sémantiques des fiches lues
- sources_read:               # chemins exacts des fiches + sources historiques
- existing_function_reused:   # oui/non + laquelle
- duplication_risk:           # aucun / décrit
- architecture_impact:        # coeur 00->11 / gouvernance / service auxiliaire / branche future
- reactivation_condition_met: # oui/non + preuve mesurable
- go_code:                    # toujours false sans GO Fred explicite
```

## EXISTING_FIRST (règle dure)
Avant de proposer une nouvelle capacité ou un nouveau moteur, vérifier qu'aucune fiche existante ne couvre déjà la
fonction. Une capacité enregistrée ne se reconstruit pas sous un autre nom / un autre numéro. Les identifiants
sémantiques priment sur les anciens numéros.

## §Guard — DEFERRED_CAPABILITY_RELEVANCE_GUARD (conception ; NON construit)
Forme AUTOMATISÉE future du présent protocole. **Conçu, non implémenté, GO_CODE = non.**

- **But** : à partir des traces closes 00→11, signaler (consultativement) quand les preuves d'une transaction
  correspondent aux conditions de réactivation d'une capacité différée. Ne construit rien, n'active rien, n'accède pas
  au réseau, ne mute rien.
- **Architecture** : composant CENTRAL hors pipeline, alimenté par les traces d'ENGINE-11 + le registre. Déterministe,
  rejouable, versionné, auditable. Les moteurs 00→11 restent PURS : ils ne connaissent pas les capacités futures.
- **Anti-couplage (décision Fred)** : NE PAS implanter de règle spécifique (« ENGINE-14 aurait servi ici ») dans les
  moteurs certifiés — cela créerait couplage, recertification globale, duplication, faux positifs. Les moteurs émettent
  seulement des SIGNAUX NEUTRES observables ; le guard central applique des règles versionnées.
- **Signaux neutres (exemples, à émettre par 00→11 SANS connaître les capacités)** :
  `frame_coverage: INSUFFICIENT` · `internal_evidence: INCONCLUSIVE` · `historical_context_available/used` ·
  `creative_mode_requested` · `response_noise_level` · `unresolved_anomalies: [...]`.
- **Sortie guard (exemple)** :
  ```json
  {"capability_signal": "EXTERNAL_EVIDENCE_AND_FALSIFICATION",
   "reason_codes": ["INTERNAL_EVIDENCE_INCONCLUSIVE", "MATERIAL_UNRESOLVED_CLAIM"],
   "confidence": 0.86, "automatic_activation": false, "go_code": false}
  ```
- **Correspondances signal → capacité** : cadres internes insuffisants → F-025 · corpus interne ne tranche pas une
  hypothèse importante → ENGINE-14 · situation historique comparable non exploitée → ENGINE-13 · demande créative/divergente
  → F-026 · réponse trop bruitée/mal hiérarchisée → F-027 · récidive d'une classe d'erreur connue → GOV_COHERENT_EVOLUTION ·
  cadre de présentation inadéquat → F-028 · construction finale déficiente → F-029.
- **Décision de construire une capacité = falsifiable** : le guard accumule (nb déclenchements, taux de faux positifs,
  types de demandes, impact estimé, répétition du besoin). Exemple de seuil : « ENGINE-14 signalé sur 18 % des
  transactions de recherche, 80 % de confirmations humaines → besoin MESURÉ, contrat réactivable ». Transforme une
  intuition en décision mesurée.
- **Ordre de travail (décision Fred, aucun code maintenant)** : (1) finaliser le registre ; (2) recenser les signaux
  neutres DÉJÀ présents en sortie 00→11 ; (3) identifier les signaux réellement manquants ; (4) concevoir le guard central ;
  (5) le simuler sur des traces historiques ; (6) mesurer les faux positifs ; (7) seulement ensuite décider si quelques
  moteurs doivent émettre un champ supplémentaire. Le composant reste : consultatif · sans réseau · sans mutation · sans
  activation automatique · versionné · rejouable · auditable. Fred = unique autorité d'activation.

## Interdictions transverses
Ne jamais : activer/coder sans GO Fred · introduire du réseau dans le cœur 00→11 · muter un moteur certifié pour un
signal de capacité future · créer un nouveau numéro ENGINE · supprimer une source historique · déclarer une capacité
caduque sans audit + décision Fred.
