# ZORAN V2 — Instructions obligatoires pour tout agent

## Lecture préalable obligatoire

Avant toute analyse, modification, audit, review, merge, benchmark ou décision concernant ZORAN V2, l’agent doit relire et intégrer la page canonique suivante :

- Notion : https://app.notion.com/p/39ec578e95578124a3bad0d64bab486f

Si Notion n’est pas accessible depuis l’environnement de l’agent, utiliser directement les cinq références prioritaires ci-dessous.

## Corpus canonique prioritaire

1. Loi de cohérence phénoménale — contrainte universelle d’admissibilité dans le temps  
   https://zenodo.org/records/18516353
2. Démonstration complète par applications  
   https://zenodo.org/records/18526755
3. Falsification assistée par LLM  
   https://zenodo.org/records/18497598
4. Opérationnaliser la cohérence — mesure locale, falsifiabilité, application  
   https://zenodo.org/records/18457447
5. Cohérence relative aux cadres d’admissibilité  
   https://zenodo.org/records/18466127

## Formule canonique verrouillée

```text
S = (beta * delta_phi) / (1 + T + sigma)
```

- `beta` : direction explicite du système ou de l’argument.
- `delta_phi` : continuité interne / taux de résolution selon les proxies définis.
- `T` : contradictions, tensions ou violations détectées.
- `sigma` : bruit, ambiguïtés ou dispersion selon le cadre.

Aucun score n’est admissible sans définition préalable des cadres, proxies, unités, bornes et preuves utilisées.

## Contrat minimal de tout audit

Tout audit doit comporter :

1. ÉTAT RÉEL observé directement ;
2. COHÉRENCE calculée avec cadres, critères, preuves et pondérations ;
3. CINÉMATIQUE : `S(t)`, `delta S`, `dS/dt`, `d2S/dt2` lorsque comparable ;
4. FUTUR PROBABLE conditionnel ;
5. VERROU PRINCIPAL ;
6. RISQUE PRINCIPAL ;
7. PROCHAINE ACTION ;
8. verdict explicite : `CERTIFIED_10_10`, `FIX_REQUIRED`, `QUARANTINE` ou `INDETERMINATE`.

## Règle de non-récurrence cohérente

Toute erreur confirmée, reproduite ou admise par un agent doit produire un apprentissage persistant. Un correctif local seul est insuffisant.

Pour chaque erreur confirmée, l’agent doit identifier et tracer :

1. le claim rendu faux ;
2. le contre-exemple minimal ;
3. les cadres utilisés lors de la décision erronée ;
4. les cadres manquants, insuffisants ou mal hiérarchisés ;
5. la classe générale d’erreur ;
6. l’invariant nouveau ;
7. le guard ou veto associé ;
8. le test de non-régression ;
9. les conditions d’applicabilité ;
10. l’impact global avant promotion canonique.

Il est interdit de supprimer automatiquement un cadre parce qu’il a participé à une erreur. Il faut déterminer s’il était faux, incomplet, utilisé seul à tort ou mal pondéré. La correction peut imposer :

- un cadre supplémentaire obligatoire ;
- une combinaison minimale de cadres ;
- l’interdiction pour un cadre de décider seul ;
- un veto dans certaines conditions ;
- une nouvelle hiérarchie entre cadres.

Aucun contre-exemple confirmé ni aucune classe d’erreur canonisée ne peut recevoir à nouveau le même verdict dans des conditions équivalentes sans blocage explicite, nouvelle preuve ou override gouverné et traçable.

Cette règle s’applique à tous les agents. Avant toute nouvelle décision, chaque agent doit vérifier le registre d’erreurs canonisées et les guards associés. Une erreur déjà apprise mais reproduite constitue une régression systémique et impose au minimum `FIX_REQUIRED`.

Boucle de gouvernance associée (HORS pipeline, non-runtime, non numérotée comme gate) : `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md` (identifiant interne `GOV_COHERENT_EVOLUTION`). Le pipeline de raisonnement reste borné à ENGINE-00→11 ; ENGINE-11 est la porte terminale. La règle de non-récurrence ci-dessus reste autoritaire.

## Registre autoritaire des capacités différées

Source de vérité des capacités mises de côté (différées, dormantes, hors pipeline, bloquées) : **[`docs/FUTURE_CAPABILITIES_REGISTRY.md`](docs/FUTURE_CAPABILITIES_REGISTRY.md)**.

**RÈGLE (Fred 2026-07-16).** Toute capacité différée, dormante, hors pipeline ou bloquée DOIT être enregistrée dans `docs/FUTURE_CAPABILITIES_REGISTRY.md` AVANT clôture de sa mission. L'absence d'implémentation ne signifie JAMAIS abandon. Aucune capacité enregistrée ne peut être supprimée, renommée ou déclarée caduque sans preuve, audit d'impact global et décision explicite de Fred.

## Règles d’exécution

- Observer le dépôt, le SHA, le diff et la CI avant de conclure.
- Ne jamais certifier à partir d’un résumé tiers si la source directe est accessible.
- Une amélioration locale ne peut être acceptée si `delta S global < 0`.
- Toute preuve d’un autre SHA est invalide.
- Les déclarations, commentaires et docstrings ne remplacent pas une preuve runtime.
- Toute contradiction impose reconstruction ou `FIX_REQUIRED`, jamais une rationalisation.
- Aucun ajout de gouvernance abstraite sans incident réel démontré pendant la construction des moteurs.

## Portée

Ce fichier s’applique à tous les sous-répertoires du dépôt et à tous les agents humains ou IA intervenant sur ZORAN V2.
