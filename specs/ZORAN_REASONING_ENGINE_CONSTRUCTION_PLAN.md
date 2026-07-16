# ZORAN V2 — Plan canonique de construction des moteurs de raisonnement

## Statut

Ce document est la feuille de route canonique de construction du pipeline de raisonnement ZORAN V2.

## Séquence

```text
00_RUNTIME_CHECK
→ 01_OBJECT_DISCOVERY
→ 02_ANALYSIS_FRAME_SELECTION
→ 03_OPERANTS_OPERES_ANALYSIS
→ 04_CANON_DETERMINATION
→ 05_COHERENCE_ENGINE
→ 06_LLM_REQUEST_BUILD
→ 07_LLM_EXECUTION
→ 08_COHERENCE_2
→ 09_RESERVED_BY_CANONICAL_CONTRACT
→ 10_RESERVED_BY_CANONICAL_CONTRACT
→ 11_TRACE_AND_CLOSE
→ 12_COHERENT_EVOLUTION
→ EXTERNAL_INDEPENDENT_CERTIFICATION_BY_CLAUDE
```

Les noms et contrats détaillés de 09 et 10 restent à matérialiser avant leur construction. Aucun agent ne doit les inventer.

## ENGINE-12 — 12_COHERENT_EVOLUTION

### Fonction

Transformer toute erreur confirmée en apprentissage systémique persistant :

- classe d'erreur ;
- contre-exemple minimal ;
- diagnostic des cadres utilisés, manquants ou mal hiérarchisés ;
- invariant ;
- guard ou veto ;
- test de non-régression ;
- replay ;
- proposition de promotion canonique après validation externe.

### Position

ENGINE-12 est le dernier moteur du plan de raisonnement V2. Il intervient après `11_TRACE_AND_CLOSE`.

### Prérequis absolus

- moteurs `00→11` construits ;
- gate d'intégration global `00→11` PASS ;
- contrat `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md` validé extérieurement ;
- aucune auto-certification de ZORAN ;
- aucun code ENGINE-12 avant ces conditions.

### Principe scientifique V1

Aucune équation de cohérence évolutive ne devient canonique tant que chacune de ses variables n'est pas calculable par un tiers à partir de données figées et de règles versionnées.

Le verrou principal est l'identifiabilité de l'applicabilité :

```text
a_e(x ; v_e) -> {0,1}
```

avec :

- `x` : cas observé ;
- `e` : classe d'erreur canonisée ;
- `v_e` : version figée de la règle d'applicabilité ;
- `a_e` : fonction déterministe qui ne lit ni le verdict final, ni le finding à prédire.

La récurrence est définie par :

```text
r_e(x) -> {0,1}
```

`r_e(x)=1` si la décision déjà invalidée est reproduite sur un cas applicable.

### Taux de récurrence observable

V1 exclut les poids libres et toute pénalité paramétrique non calibrée :

```text
rho = [sum_e,x a_e(x;v_e) * r_e(x)] / [sum_e,x a_e(x;v_e)]
```

Bornes :

```text
0 <= rho <= 1
```

Si aucun cas applicable n'est observable :

```text
INDETERMINATE_NO_APPLICABLE_REPLAY
```

Il est interdit de fixer artificiellement `rho=0`.

### Équation V1 candidate

```text
S_evo = S * (1 - rho)
```

soit :

```text
S_evo = [beta * delta_phi * (1 - rho)] / [1 + T + sigma]
```

Cette forme :

- conserve la formule canonique de cohérence ;
- n'applique qu'une seule pénalité de récurrence ;
- n'introduit ni `lambda`, ni exposant libre, ni pondération arbitraire en V1 ;
- retrouve `S` si `rho=0` ;
- donne `0` si `rho=1`.

Les variantes à double pénalité, les poids `w_e`, `lambda` et les formes `(1-rho)^k` restent au backlog expérimental V2 jusqu'à calibration externe.

### Veto critique

Une moyenne ne peut jamais compenser une récurrence critique :

```text
si existe e de sévérité P0 ou P1 et x tel que a_e(x)=1 et r_e(x)=1
alors BLOCKED
```

### Conditions d'identifiabilité avant code

ENGINE-12 ne pourra être implémenté que si les éléments suivants existent :

1. fonctions `applicable(case, rule) -> bool` versionnées ;
2. classes d'erreurs munies de conditions et exclusions exécutables ;
3. dataset de replay figé avec cas positifs et négatifs ;
4. vérité de référence indépendante ;
5. mesures de précision, rappel, accord et stabilité entre versions ;
6. prédiction falsifiable reliant `rho` à un comportement observable ;
7. protection anti-Goodhart : la définition d'applicabilité ne peut pas être resserrée rétroactivement pour améliorer le score.

### Stabilité temporelle

Lorsque plusieurs fenêtres comparables sont disponibles, ENGINE-12 pourra exposer :

```text
mean_rho_W
var_rho_W
```

Ces mesures restent descriptives tant que la taille de fenêtre, les corpus et les règles d'applicabilité ne sont pas figés. Une baisse de `rho` accompagnée d'une variance élevée ne prouve pas une évolution stable.

### Condition de non-récurrence

```text
Pour toute classe d'erreur canonique e et tout cas futur x :
a_e(x;v_e)=1 implique r_e(x)=0.
```

### Règle de construction

ENGINE-12 ne remplace pas les audits externes. Il produit des mesures, guards et propositions d'évolution ; Fred reste l'autorité de GO et les certificateurs externes restent obligatoires.

## Certification indépendante finale par Claude

Après construction, intégration et certification interne de tous les moteurs `00→12`, un paquet autonome, figé et indépendant de GitHub doit être soumis à **Claude Assistant** pour un audit externe final.

### Paquet requis

Le paquet contient au minimum :

- `AGENTS.md` ;
- plan canonique `00→12` ;
- contrats de tous les moteurs ;
- code source exact lié à un SHA figé ;
- tests et résultats CI ;
- traces runtime et benchmarks ;
- manifest et hashes ;
- preuves brutes ;
- findings historiques séparés du corpus aveugle.

### Protocole d'indépendance

Claude reçoit d'abord uniquement le paquet aveugle : contrats, code, tests, preuves et SHA. Il rend un premier verdict indépendant avant d'accéder aux verdicts détaillés de ChatGPT, Codex Session A et Codex Session B.

Puis :

```text
AUDIT_CLAUDE_PRELIMINAIRE
→ ouverture des verdicts historiques
→ analyse des divergences
→ AUDIT_CLAUDE_CONVERGENCE
```

### Autorité et limites

- Claude ne modifie pas le produit pendant cet audit ;
- Claude ne remplace pas les certificateurs internes ;
- un PASS Claude ne compense jamais un FAIL interne ;
- un FAIL Claude déclenche investigation et reproduction ;
- aucune certification finale ZORAN V2 sans traitement explicite des divergences ;
- Fred reste seul autorisé à déclarer la certification finale et à promouvoir la baseline.

## Gouvernance

- Aucun moteur suivant ne démarre sans contrat matérialisé.
- Chaque candidat est figé sur un SHA unique.
- Aucun merge sans convergence des certificateurs requis.
- Une amélioration locale est interdite si `delta_S_global < 0`.
- Toute erreur confirmée doit enrichir la règle de non-récurrence cohérente.
- Aucune formule n'est canonique sur la seule base de sa cohérence algébrique.
- Après certification interne de `00→12`, la certification indépendante finale par Claude est obligatoire avant promotion finale de ZORAN V2.
