# META-PROTOCOL V1 — GRILLE DE SCORING (PROPOSITION PILOTE)

- `scoring_model_version`: **GRID-V1-PILOT-DRAFT-1**
- `audit_protocol_version`: **META-PROTOCOL-V1-PILOT** (issue #20)
- Auteur (proposition, NON application) : `CLAUDE` (auditeur). Conformément à #20 : « évolution
  proposée par les auditeurs, jamais appliquée silencieusement ». À converger avec Codex + ChatGPT
  + arbitrage Fred, puis rétrotest sur 5–10 SHA historiques AVANT tout gate CI.
- Statut : **DRAFT**. Aucun score chiffré n'est produit tant que cette grille n'est pas RATIFIÉE.

## 0. Principes de calcul (déterminisme du scoreur)

- Chaque sous-critère est scoré sur l'échelle discrète **{0.0, 0.5, 1.0}** selon une règle EXPLICITE
  et rejouable (jamais un jugement libre). `0.5` = « partiel, preuve incomplète ».
- Un axe = **somme pondérée** des sous-critères ∈ [0,1]. Poids sommant à 1.0 par axe.
- Arrondi : **4 décimales**, `ROUND_HALF_EVEN` (bankers), appliqué UNIQUEMENT au score final de
  chaque champ (pas aux intermédiaires) pour la reproductibilité inter-auditeurs.
- Le scoreur est **séparé du moteur audité** (aucune dépendance d'import) et déterministe :
  même (SHA, bundle, grille, poids) → mêmes scores. Toute non-reproductibilité ⇒ `NON_REPRODUCIBLE`.

## 1. AXE 1 — C_LOCAL (grille + poids proposés)

| Sous-critère | Poids | Règle 1.0 / 0.5 / 0.0 |
|---|---|---|
| Déterminisme | 0.15 | 1.0 = test « f(x)==f(x) » présent et vert ; 0.5 = déterminisme plausible non testé ; 0.0 = non-déterminisme possible |
| Invariants déclarés | 0.15 | 1.0 = chaque invariant a un test qui ÉCHOUE s'il est violé (falsifiable) ; 0.5 = invariants énoncés, couverture partielle ; 0.0 = invariants non testés |
| Typage / validation d'entrée | 0.15 | 1.0 = schéma+types EXACTS validés (clés exactes, valeurs canoniques) ; 0.5 = clés/listes seulement ; 0.0 = statut amont cru sans revalidation |
| Fail-closed (frontières) | 0.20 | 1.0 = toute entrée malformée/adversariale → BLOCKED déterministe, jamais crash/fail-open ; 0.5 = fail-closed partiel ; 0.0 = fail-open ou exception possible |
| Adversarial / cas limites | 0.15 | 1.0 = classes adversariales couvertes (manquant/en trop/type/vide/doublon/inventé/omission/contradiction/unicode/non-fini/conteneur/mutation) ; 0.5 = sous-ensemble ; 0.0 = happy-path only |
| Contradictions internes | 0.10 | 1.0 = aucune contradiction interne possible (prouvée par test) ; 0.5 = non démontrée ; 0.0 = contradiction connue |
| Couverture branches critiques | 0.10 | 1.0 = toutes les branches BLOCKED/PASS critiques testées ; 0.5 = partiel ; 0.0 = branches critiques non couvertes |

`C_LOCAL = Σ (poids × sous-score)`.

## 2. AXE 2 — C_GLOBAL (grille + poids proposés)

| Sous-critère | Poids | Règle 1.0 / 0.5 / 0.0 |
|---|---|---|
| Contrats amont/aval | 0.20 | 1.0 = entrées revalidées vs amont autoritaire + sortie conforme au contrat aval ; 0.0 = confiance implicite |
| Non-régression globale | 0.15 | 1.0 = suite complète verte (hors échec environnemental documenté) ; 0.0 = régression |
| Compatibilité autres moteurs | 0.10 | 1.0 = aucune interface aval cassée ; 0.5 = à vérifier ; 0.0 = rupture |
| Provenance / traçabilité | 0.15 | 1.0 = chaque valeur trace à une source autoritaire (univers indépendant du résultat évalué) ; 0.0 = univers auto-défini |
| Impact runtime | 0.05 | 1.0 = pas de coût déraisonnable / DoS ; 0.5 = non mesuré ; 0.0 = régression runtime |
| Réversibilité | 0.10 | 1.0 = branche non fusionnée + rollback trivial ; 0.0 = irréversible |
| Dette de cohérence | 0.10 | 1.0 = aucune dette introduite ; 0.5 = dette mineure documentée ; 0.0 = dette structurelle |
| Effets indirects | 0.05 | 1.0 = effets aval analysés (00→N) ; 0.0 = non analysés |
| Chemins de contournement | 0.10 | 1.0 = aucun bypass connu de la frontière ; 0.0 = bypass possible |

`C_GLOBAL = Σ (poids × sous-score)`.

## 3. Axe réflexif + preuve

- **C_FALSIFICATION** ∈ [0,1] = part des classes de contre-exemples ADVERSARIAUX effectivement
  générées ET correctement rejetées par le moteur, sur le total des classes attendues (§AXE1
  « adversarial »). 1.0 = toutes générées et rejetées ; dégrade par classe manquante ou survivante.
- **C_EPISTEMIC** ∈ [0,1] = transparence des angles morts. 5 items (hypothèses explicitées,
  contre-exemples générés, limites de preuve, cadres non couverts, faiblesses connues) : chaque
  item présent = 0.20. **Gate : `C_EPISTEMIC < 0.90 ⇒ statut max PROVISIONAL`.**
- **C_REPRODUCIBILITY** ∈ [0,1] (clarification de l'ambiguïté #20) = reproductibilité de l'AUDIT
  lui-même : 1.0 = scoreur déterministe + grille figée + bundle identique + arrondi défini (rejeu
  bit-identique) ; < 1.0 si une source de variance subsiste. Non listé comme champ de sortie mais
  entre dans `QUALITY_PROOF` — **proposition : l'ajouter aux `scores` du CERTIFICATION_OBJECT**.

## 4. Synthèse (formules #20, inchangées)

```
QUALITY_MOTOR = sqrt(C_LOCAL * C_GLOBAL)
QUALITY_PROOF = C_REPRODUCIBILITY * C_FALSIFICATION * C_EPISTEMIC
CERT_SCORE    = QUALITY_MOTOR * QUALITY_PROOF
```

## 5. Vétos absolus (priment sur tout score)

Aucun `CERTIFIED` si l'un des suivants est présent (statut forcé indiqué) :

| Véto | Statut forcé |
|---|---|
| Finding critique valide | `FIX_REQUIRED` |
| Contradiction interne | `FIX_REQUIRED` |
| Fail-open sur frontière critique | `FIX_REQUIRED` |
| Preuve absente / non rattachée au SHA | `BLOCKED` |
| Protocole différent entre auditeurs | `NON_REPRODUCIBLE` |
| Mutation du SHA pendant l'audit | `NON_REPRODUCIBLE` |
| Bundle de preuves non identique | `NON_REPRODUCIBLE` |
| Score non dérivé d'une grille explicite | `BLOCKED` |

## 6. Mapping statut (proposition de seuils PILOTE — à calibrer par rétrotest)

1. Un véto présent → statut du véto (table §5).
2. Sinon, **indépendance insuffisante** (auditeur = builder du SHA → `SELF_AUDIT`, ou < 2 audits
   indépendants du build) → **max `PROVISIONAL`**.
3. Sinon, `C_EPISTEMIC < 0.90` → **max `PROVISIONAL`**.
4. Sinon, convergence inter-auditeurs hors tolérance (`DELTA_LOCAL>0.010` / `DELTA_GLOBAL>0.010` /
   `DELTA_SCORE>0.005`) → **`NON_REPRODUCIBLE`** (jamais de moyenne).
5. Sinon : `CERT_SCORE ≥ 0.90` → **`CERTIFIED`** ; `0.75 ≤ CERT_SCORE < 0.90` → **`PROVISIONAL`** ;
   `< 0.75` → **`FIX_REQUIRED`**. (Seuils 0.90 / 0.75 = valeurs pilotes à recalibrer.)

## 7. Rétrotest obligatoire avant adoption (plan #20, étapes 4–6)

Rejouer cette grille sur **5–10 SHA historiques** déjà certifiés (`certified/engine-00..07`,
`v2-integration-00-07-hardening`, PR#7/16/19), mesurer la variance inter-auditeurs Codex↔Claude,
analyser faux accords / faux désaccords, **puis** calibrer les seuils. Aucun gate CI avant validation.

## 8. Points ouverts (à trancher en gouvernance)

1. Poids ci-dessus = première proposition, à valider/ajuster par consensus auditeurs.
2. `C_REPRODUCIBILITY` : l'ajouter explicitement aux champs `scores` du JSON.
3. Granularité {0, 0.5, 1} vs échelle plus fine : commencer grossier (moins de faux désaccords),
   affiner après variance mesurée.
4. Séparation build/audit : un moteur construit par Claude doit être audité indépendamment par
   Codex (et inversement) ; le véto de convergence est porté par l'auditeur **non-builder**.
