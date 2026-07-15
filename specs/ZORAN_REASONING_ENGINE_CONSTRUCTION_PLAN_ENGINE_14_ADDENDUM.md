# ADDENDUM CANONIQUE — EXTENSION DU PLAN ZORAN V2 JUSQU'A ENGINE-14

## Statut

Cet addendum fait partie du plan canonique de construction et complète `specs/ZORAN_REASONING_ENGINE_CONSTRUCTION_PLAN.md` sur la branche de gouvernance de la PR #18.

Il remplace toute formulation antérieure présentant ENGINE-13 comme dernier moteur.

## Séquence canonique étendue

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

## ENGINE-13 — fonction dans la chaîne

ENGINE-13 reconnaît un cadre historique déjà traité, vérifie les invariants et calcule uniquement le delta du cadre présent.

Formule ASCII canonique :

```text
R_t = R_previous_valid + F(delta_C) - I(delta_C)
delta_C = (A_plus, A_minus, A_modified, X_contradictions)
```

## ENGINE-14 — fonction dans la chaîne

ENGINE-14 est déclenché automatiquement lorsqu'ENGINE-13 identifie un delta matériel que le corpus interne ne permet pas de valider ou de réfuter.

Il :

1. formule les hypothèses concurrentes ;
2. définit les critères de réfutation avant recherche ;
3. lance automatiquement la recherche externe ;
4. collecte des preuves favorables et défavorables ;
5. tente activement de falsifier les hypothèses ;
6. produit un verdict borné par le niveau réel de preuve ;
7. propose les nouveaux objets externes en quarantaine, jamais directement au canon.

## Principe de déclenchement

```text
historical_frame_identified = true
delta_C_non_empty = true
internal_authoritative_evidence_sufficient = false
delta_material_for_answer = true
→ external_search_automatic = true
```

Aucune demande préalable de recherche Internet n'est exigée de l'utilisateur pour une recherche externe ordinaire. L'automatisation de la recherche ne vaut jamais automatisation de la certitude.

## Contrat

Le contrat autoritaire est :

`specs/CONTRACT_ENGINE_14_EXTERNAL_EVIDENCE_AND_FALSIFICATION.md`

## Prérequis absolus

- moteurs `00→13` construits et certifiés ;
- gate global `00→13` PASS ;
- contrat ENGINE-14 validé extérieurement ;
- politiques de sources et de falsification versionnées ;
- corpus de tests externes figé ;
- aucun code ENGINE-14 avant GO explicite de Fred.

## Certification finale

La certification externe finale intervient après construction, intégration et certification interne de tous les moteurs `00→14`.

## Gouvernance

- ENGINE-14 reste `SPEC_ONLY` ;
- aucune recherche confirmatoire seule ;
- critères de falsification définis avant les résultats ;
- aucune source externe intégrée directement au canon ;
- aucun merge de cette extension avant résolution de la dépendance de gouvernance PR #14 et convergence des certificateurs requis.
