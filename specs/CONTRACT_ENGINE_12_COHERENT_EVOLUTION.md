# CONTRACT_ENGINE_12_COHERENT_EVOLUTION

## Statut

`SPEC_ONLY — NO_CODE_AUTHORIZED`

## Identité

- Component ID : `12_COHERENT_EVOLUTION`
- Rôle : dernier moteur du pipeline ZORAN V2.
- Position : après `11_TRACE_AND_CLOSE`.
- Fonction : transformer les erreurs confirmées en évolution gouvernée des cadres, invariants, guards et tests afin d'empêcher la récurrence de la même classe d'erreur dans des conditions équivalentes.

## Principe canonique

Une correction n'est cohérente que si elle modifie durablement les conditions de décision qui ont permis l'erreur, sans dégrader la cohérence globale.

`12` ne corrige pas directement le produit. Il produit une proposition d'apprentissage canonique soumise à validation externe.

Aucune équation de cohérence évolutive ne devient canonique tant que chacune de ses variables n'est pas calculable par un tiers à partir de données figées et de règles versionnées.

## Entrées autoritaires minimales

- trace clôturée de `11` ;
- erreur confirmée par preuve ou audit externe ;
- claim falsifié ;
- contre-exemple minimal reproductible ;
- cadres utilisés ;
- cadres manquants ou insuffisants ;
- invariants et guards existants ;
- tests de non-régression ;
- SHA exact et provenance des preuves ;
- règle d'applicabilité exécutable et versionnée ;
- dataset de replay figé.

## Objet d'apprentissage

```json
{
  "error_id": "ERR-...",
  "error_class": "...",
  "severity": "P0 | P1 | P2 | P3",
  "failed_claim": "...",
  "counterexample": "...",
  "frames_used": [],
  "frames_missing": [],
  "frame_policy_before": "...",
  "frame_policy_after": "...",
  "new_invariant": "...",
  "guard": "...",
  "regression_test": "...",
  "applicability_rule_id": "...",
  "applicability_version": "...",
  "applicability_dataset": "...",
  "global_impact": "...",
  "evidence_sha": "...",
  "status": "PROPOSED | QUARANTINED | CANONICAL | REJECTED"
}
```

## Distinction obligatoire sur les cadres

Pour chaque erreur, `12` doit distinguer :

1. cadre faux ;
2. cadre pertinent mais incomplet ;
3. cadre valide utilisé seul à tort ;
4. cadre mal pondéré ;
5. cadre manquant ;
6. conflit entre cadres ;
7. hiérarchie de cadres incorrecte.

Un cadre n'est jamais supprimé automatiquement. Transformations autorisées :

- `ADD_REQUIRED_FRAME` ;
- `REQUIRE_FRAME_COMBINATION` ;
- `FORBID_FRAME_AS_SOLE_ARBITER` ;
- `CHANGE_FRAME_PRIORITY` ;
- `ADD_CONDITIONAL_VETO` ;
- `REJECT_FRAME_IN_CONTEXT`.

## Définition mathématique V1

### 1. Applicabilité identifiable

Pour une erreur confirmée `e`, un cas `x` et une version de règle `v_e` :

```text
a_e(x ; v_e) ∈ {0,1}
```

`a_e` doit être une fonction déterministe, versionnée et testable.

Interdictions absolues :

- lire le verdict final à prédire ;
- lire le finding produit sur le cas ;
- modifier rétroactivement la règle d'applicabilité pour améliorer le score ;
- décider l'applicabilité par prose ou jugement non traçable.

Signature cible :

```python
def applicable(case: dict, rule: dict) -> bool:
    """Décision déterministe indépendante du verdict à prédire."""
```

### 2. Indicateur de récurrence

```text
r_e(x) ∈ {0,1}
```

`r_e(x)=1` si, malgré `a_e(x;v_e)=1`, le système reproduit le verdict ou l'action invalidée par le contre-exemple `e`, sans nouvelle preuve ni override gouverné.

Condition de non-récurrence :

```text
∀e canonique, ∀x futur : a_e(x;v_e)=1 ⇒ r_e(x)=0
```

### 3. Taux de récurrence observable

V1 exclut tout poids libre :

```text
rho = [Σ_e,x a_e(x;v_e) * r_e(x)] / [Σ_e,x a_e(x;v_e)]
```

Bornes :

```text
0 <= rho <= 1
```

Si le dénominateur est nul :

```text
INDETERMINATE_NO_APPLICABLE_REPLAY
```

Il est interdit d'inférer `rho=0` de l'absence de replay.

### 4. Score V1 candidat

Soit le score canonique courant :

```text
S = [beta * delta_phi] / [1 + T + sigma]
```

La forme V1 candidate est :

```text
S_evo = S * (1 - rho)
```

soit :

```text
S_evo = [beta * delta_phi * (1 - rho)] / [1 + T + sigma]
```

Cette forme n'applique qu'une seule pénalité de récurrence et n'introduit aucun paramètre libre.

Les éléments suivants sont interdits en V1 et placés au backlog expérimental V2 :

- double pénalité numérateur + dénominateur ;
- `lambda` ;
- poids libres `w_e` ;
- exposant libre `k` dans `(1-rho)^k` ;
- calibration rétroactive.

### 5. Veto critique

Une récurrence critique n'est jamais compensable par une moyenne :

```text
si ∃e de sévérité P0 ou P1, ∃x : a_e(x;v_e)=1 ∧ r_e(x)=1
alors BLOCKED
```

### 6. Transformation de la politique de cadres

```text
F_{t+1}(x) = U_e(F_t(x))
```

La transformation est admissible seulement si :

```text
ΔS_global(U_e) >= 0
```

et si le contre-exemple est fermé :

```text
r_e(x_e après U_e)=0
```

### 7. Stabilité temporelle

Lorsque plusieurs fenêtres comparables existent :

```text
mean_rho_W
var_rho_W
```

Ces métriques sont descriptives tant que la fenêtre, le corpus et les versions d'applicabilité ne sont pas figés.

Une baisse de `rho` accompagnée d'une variance élevée ne prouve pas une évolution stable.

## Conditions expérimentales obligatoires avant code

ENGINE-12 ne peut pas être codé tant que les preuves suivantes n'existent pas :

1. au moins 3 classes d'erreurs réelles ;
2. une fonction `applicable()` versionnée par classe ;
3. un dataset figé d'au moins 50 cas positifs et négatifs ;
4. une vérité de référence indépendante ;
5. précision, rappel et accord inter-évaluateurs mesurés ;
6. stabilité des règles entre versions ;
7. au moins une prédiction falsifiable reliant `rho` à un comportement observable ;
8. audit explicite de résistance à Goodhart.

## Prédiction falsifiable minimale

Une hypothèse expérimentale doit être préenregistrée, par exemple :

```text
si rho_t augmente sur une fenêtre comparable,
alors le nombre de régressions confirmées au cycle suivant augmente.
```

Elle doit être testée sans modifier rétroactivement les règles d'applicabilité.

## Machine à états

```text
ERROR_CONFIRMED
→ COUNTEREXAMPLE_REPRODUCED
→ FRAME_CAUSE_IDENTIFIED
→ APPLICABILITY_RULE_VERSIONED
→ DATASET_VALIDATED
→ LEARNING_OBJECT_PROPOSED
→ GLOBAL_IMPACT_EVALUATED
→ EXTERNAL_AUDIT
→ QUARANTINE
→ REPLAY_VALIDATED
→ CANONICAL_PROMOTION
```

États de sortie :

- `LEARNING_CANONICAL`
- `LEARNING_FIX_REQUIRED`
- `LEARNING_QUARANTINE`
- `LEARNING_INDETERMINATE`

## Guards absolus

- aucune promotion sans contre-exemple reproduit ;
- aucune règle créée uniquement à partir d'une intuition ;
- aucune suppression automatique de cadre ;
- aucune auto-certification par ZORAN ;
- aucune preuve provenant d'un autre SHA ;
- aucun guard sans test de non-régression ;
- aucun apprentissage local si `delta S global < 0` ;
- toute récurrence P0/P1 impose `BLOCKED` ;
- toute variable non identifiable impose `INDETERMINATE` ;
- toute optimisation du dénominateur d'applicabilité impose `FIX_REQUIRED`.

## Sortie minimale

```json
{
  "component": "12_COHERENT_EVOLUTION",
  "status": "PASS | BLOCKED",
  "verdict": "LEARNING_CANONICAL | LEARNING_FIX_REQUIRED | LEARNING_QUARANTINE | LEARNING_INDETERMINATE",
  "learning_object": {},
  "frame_transformation": {},
  "counterexample_closed": false,
  "global_delta_S": null,
  "rho": null,
  "rho_observability": "IDENTIFIED | INDETERMINATE",
  "coherence_evolution": null,
  "authorize_canonical_promotion": false
}
```

`authorize_canonical_promotion=true` uniquement après audit externe, replay réussi, absence de régression globale, identifiabilité démontrée et validation de la gouvernance.

## Position dans la roadmap

```text
00_RUNTIME_CHECK
...
11_TRACE_AND_CLOSE
12_COHERENT_EVOLUTION
```

`12` est le moteur d'évolution contrôlée de ZORAN. Il ne doit être codé qu'après certification de `00→11`, validation externe du présent contrat et satisfaction des conditions expérimentales ci-dessus.
