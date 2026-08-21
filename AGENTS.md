# ZORAN — Instructions obligatoires pour tout agent

## PRIORITÉ ABSOLUE — PLAN FINAL VERROUILLÉ

Pour la branche `codex/zoran-final-canon-v1`, toute mission Zoran doit d'abord lire et appliquer ces trois autorités persistantes :

1. Plan canonique final :  
   https://github.com/institutia2025-ctrl/zoran-v2/blob/codex/zoran-final-canon-v1/ZORAN_FINAL_CONSTRUCTION_CANON_V1.md
2. Objet mémoire ZMOS du plan :  
   https://github.com/institutia2025-ctrl/zoran-v2/blob/codex/zoran-final-canon-v1/zmos_memory/ZORAN_FINAL_PLAN_V1.zmos.json
3. Tracker persistant de construction :  
   https://github.com/institutia2025-ctrl/zoran-v2/blob/codex/zoran-final-canon-v1/zmos_memory/ZORAN_BUILD_TRACKER_V1.json

Ces trois fichiers priment sur toute ancienne architecture de construction. L'ancienne chaîne ENGINE-00→11 est **historique et donneuse de briques uniquement** ; elle ne constitue plus le pipeline final autorisé. Aucun agent ne doit la réactiver en bloc.

Le pipeline final autorisé est celui du canon : `NLP.js + ZTRACE + BGE-M3 retrieval → corpus/index ZMOS → cadres → K3 → cohérence multicadre → semantic decision → Amygdale/veto → verbaliseur déterministe → texte/voix/UI → ZMOS`.

Aucune architecture alternative, aucun changement d'ordre de construction et aucune décision probabiliste ne sont autorisés sans GO explicite de Fred.

## Mémoire persistante obligatoire

Le contexte conversationnel n'est qu'un cache. La mémoire de construction autoritaire est ZMOS/canon/tracker ci-dessus.

Au début de chaque chat ou mission :
- relire les trois autorités ;
- effectuer un audit 360° ;
- annoncer pourcentage courant, phase, dernier delta prouvé, verrou, NON_MESURÉ et prochaine action.

À la fin de chaque chat ou mission :
- consigner le delta réel ;
- mettre à jour le pourcentage uniquement avec preuve ;
- consigner PASS / FAIL / NON_MESURÉ ;
- inscrire dépôt / branche / SHA / tests / artefacts ;
- consigner le verrou suivant ;
- refaire un audit 360° ;
- ne jamais modifier le plan silencieusement.

## Lecture scientifique préalable obligatoire

Avant toute analyse, modification, audit, review, merge, benchmark ou décision concernant ZORAN, relire et intégrer la page canonique suivante :

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

La boucle de gouvernance historique `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md` peut rester une référence locale de non-récurrence, mais elle ne redéfinit pas le pipeline final verrouillé ci-dessus.

## Règles d’exécution

- Observer le dépôt, le SHA, le diff et la CI avant de conclure.
- Ne jamais certifier à partir d’un résumé tiers si la source directe est accessible.
- Une amélioration locale ne peut être acceptée si `delta S global < 0`.
- Toute preuve d’un autre SHA est invalide.
- Les déclarations, commentaires et docstrings ne remplacent pas une preuve runtime.
- Toute contradiction impose reconstruction ou `FIX_REQUIRED`, jamais une rationalisation.
- Aucun ajout de gouvernance abstraite sans incident réel démontré pendant la construction.

## Portée

Ce fichier s’applique à tous les sous-répertoires de cette branche canonique et à tous les agents humains ou IA intervenant sur la finalisation de ZORAN.
