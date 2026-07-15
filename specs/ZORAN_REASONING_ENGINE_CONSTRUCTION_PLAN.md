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

### Équation d'évolution

```text
S_evo = [beta * delta_phi * (1 - rho)] / [1 + T + sigma + lambda * rho]
```

avec :

```text
rho = recurrent_errors_weighted / applicable_cases_weighted
```

Cas sans observation applicable : `INDETERMINATE_NO_APPLICABLE_REPLAY`, jamais `rho=0` inventé.

### Condition de non-récurrence

```text
Pour toute classe d'erreur canonique e et tout cas futur x :
A_e(x)=1 implique R_e(x)=0.
```

### Règle de construction

ENGINE-12 ne remplace pas les audits externes. Il produit des mesures, guards et propositions d'évolution ; Fred reste l'autorité de GO et les certificateurs externes restent obligatoires.

## Gouvernance

- Aucun moteur suivant ne démarre sans contrat matérialisé.
- Chaque candidat est figé sur un SHA unique.
- Aucun merge sans convergence des certificateurs requis.
- Une amélioration locale est interdite si `delta_S_global < 0`.
- Toute erreur confirmée doit enrichir la règle de non-récurrence cohérente.
