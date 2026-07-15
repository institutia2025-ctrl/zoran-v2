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
→ 13_HISTORICAL_DIFFERENTIAL_INFERENCE
→ 14_EXTERNAL_EVIDENCE_AND_FALSIFICATION
→ EXTERNAL_INDEPENDENT_CERTIFICATION_BY_CLAUDE
```

Les noms et contrats détaillés de 09 et 10 restent à matérialiser avant leur construction. Aucun agent ne doit les inventer.

## Documents contractuels

- `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md`
- `specs/CONTRACT_ENGINE_13_HISTORICAL_DIFFERENTIAL_INFERENCE.md`
- `specs/CONTRACT_ENGINE_14_EXTERNAL_EVIDENCE_AND_FALSIFICATION.md`
- `specs/ZORAN_REASONING_ENGINE_CONSTRUCTION_PLAN_ENGINE_14_ADDENDUM.md`

L'addendum ENGINE-14 fait partie du présent plan et porte la description détaillée de l'extension `00→14`.

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

ENGINE-12 intervient après `11_TRACE_AND_CLOSE` et avant `13_HISTORICAL_DIFFERENTIAL_INFERENCE`.

### Prérequis absolus

- moteurs `00→11` construits ;
- gate d'intégration global `00→11` PASS ;
- contrat ENGINE-12 validé extérieurement ;
- aucune auto-certification de ZORAN ;
- aucun code ENGINE-12 avant ces conditions.

### Principe scientifique V1

```text
a_e(x ; v_e) -> {0,1}
r_e(x) -> {0,1}
rho = [sum_e,x a_e(x;v_e) * r_e(x)] / [sum_e,x a_e(x;v_e)]
S_evo = S * (1 - rho)
```

Si aucun cas applicable n'est observable :

```text
INDETERMINATE_NO_APPLICABLE_REPLAY
```

Une récurrence applicable P0 ou P1 déclenche `BLOCKED`.

ENGINE-12 ne remplace pas les audits externes. Il produit des mesures, guards et propositions d'évolution ; Fred reste l'autorité de GO.

## ENGINE-13 — 13_HISTORICAL_DIFFERENTIAL_INFERENCE

### Fonction

Produire une réponse différentielle historiquement augmentée. ENGINE-13 identifie un cadre historique autoritaire comparable, vérifie les invariants, calcule le delta du cadre présent, réutilise uniquement les conclusions encore valides et raisonne seulement sur ce qui a changé.

### Formule canonique ASCII

```text
R_t = R_previous_valid + F(delta_C) - I(delta_C)
delta_C = (A_plus, A_minus, A_modified, X_contradictions)
```

- `A_plus` : éléments ajoutés ;
- `A_minus` : éléments supprimés ;
- `A_modified` : éléments modifiés ;
- `X_contradictions` : contradictions nouvelles ;
- `F` : opérateur d'augmentation ;
- `I` : opérateur d'invalidation.

### Verdicts

```text
HISTORICAL_REPLAY_NO_DELTA
HISTORICAL_FRAME_AUGMENTED
HISTORICAL_FRAME_BREAK
HISTORICAL_SURFACE_SIMILARITY
HISTORICAL_INDETERMINATE
BLOCKED
```

### Architecture

- index sémantique ou vectoriel pour proposer des candidats uniquement ;
- graphe ou magasin d'objets comme source autoritaire ;
- journal chronologique immuable ;
- validation déterministe des invariants, de la provenance et du delta.

Aucun score de similarité n'a de pouvoir de verdict.

### Prérequis

- moteurs `00→12` construits et certifiés ;
- gate global `00→12` PASS ;
- contrat ENGINE-13 validé extérieurement ;
- schémas historiques et politiques d'invariants figés ;
- dataset indépendant ;
- aucun code avant GO explicite de Fred.

## ENGINE-14 — 14_EXTERNAL_EVIDENCE_AND_FALSIFICATION

### Fonction

Quand ENGINE-13 identifie un delta matériel que le corpus interne ne permet pas de trancher, ENGINE-14 déclenche automatiquement une recherche externe, collecte des preuves favorables et défavorables et tente activement de falsifier les hypothèses concurrentes.

L'utilisateur n'a pas à demander séparément la recherche Internet. La recherche externe ordinaire est automatique par défaut.

### Déclenchement

```text
historical_frame_identified = true
delta_C_non_empty = true
internal_authoritative_evidence_sufficient = false
delta_material_for_answer = true
→ external_search_automatic = true
```

### Chaîne

```text
hypothèses
→ critères de réfutation définis avant recherche
→ recherche externe automatique
→ qualification des sources
→ preuves favorables
→ contre-preuves
→ tentative de falsification
→ verdict borné
→ quarantaine avant toute proposition canonique
```

### Principe

Une recherche confirmatoire seule est interdite. L'automatisation de la recherche ne vaut jamais automatisation de la certitude.

### Intégration au corpus

```text
EXTERNAL_CANDIDATE
→ PROVENANCE_VERIFIED
→ FALSIFICATION_ATTEMPTED
→ QUARANTINE
→ REPLAY
→ EXTERNAL_AUDIT
→ CANON_PROPOSAL
```

### Prérequis

- moteurs `00→13` construits et certifiés ;
- gate global `00→13` PASS ;
- contrat ENGINE-14 validé extérieurement ;
- politiques de sources et de falsification versionnées ;
- corpus de tests externes figé ;
- aucun code avant GO explicite de Fred.

## Certification indépendante finale par Claude

Après construction, intégration et certification interne de tous les moteurs `00→14`, un paquet autonome, figé et indépendant de GitHub doit être soumis à Claude Assistant pour un audit externe final.

Claude reçoit d'abord un paquet aveugle. Il rend un verdict indépendant avant d'accéder aux verdicts détaillés de ChatGPT et des sessions Codex.

Un PASS Claude ne compense jamais un FAIL interne. Fred reste seul autorisé à déclarer la certification finale et à promouvoir la baseline.

## Gouvernance

- Aucun moteur suivant ne démarre sans contrat matérialisé.
- Chaque candidat est figé sur un SHA unique.
- Aucun merge sans convergence des certificateurs requis.
- Une amélioration locale est interdite si `delta_S_global < 0`.
- Toute erreur confirmée doit enrichir la règle de non-récurrence cohérente.
- Aucune formule n'est canonique sur la seule base de sa cohérence algébrique.
- ENGINE-13 et ENGINE-14 restent `SPEC_ONLY` tant que leurs prérequis ne sont pas satisfaits.
- Après certification interne de `00→14`, la certification indépendante finale par Claude est obligatoire avant promotion finale de ZORAN V2.
