# CONTRACT_ENGINE_12_COHERENT_EVOLUTION

## Statut

`SPEC_ONLY — NO_CODE_AUTHORIZED`

## Identité

- Component ID : `12_COHERENT_EVOLUTION`
- Rôle : dernier moteur du pipeline ZORAN V2.
- Position : après `11_TRACE_AND_CLOSE`.
- Fonction : transformer les erreurs confirmées en évolution gouvernée des cadres, invariants, guards et tests afin d’empêcher la récurrence de la même classe d’erreur dans des conditions équivalentes.

## Principe canonique

Une correction n’est cohérente que si elle modifie durablement les conditions de décision qui ont permis l’erreur, sans dégrader la cohérence globale.

`12` ne corrige pas directement le produit. Il produit une proposition d’apprentissage canonique soumise à validation externe.

## Entrées autoritaires minimales

- trace clôturée de `11` ;
- erreur confirmée par preuve ou audit externe ;
- claim falsifié ;
- contre-exemple minimal reproductible ;
- cadres utilisés ;
- cadres manquants ou insuffisants ;
- invariants et guards existants ;
- tests de non-régression ;
- SHA exact et provenance des preuves.

## Objet d’apprentissage

Chaque erreur confirmée `e` produit un objet :

```json
{
  "error_id": "ERR-...",
  "error_class": "...",
  "failed_claim": "...",
  "counterexample": "...",
  "frames_used": [],
  "frames_missing": [],
  "frame_policy_before": "...",
  "frame_policy_after": "...",
  "new_invariant": "...",
  "guard": "...",
  "regression_test": "...",
  "applicability": "...",
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

Un cadre n’est jamais supprimé automatiquement. La transformation peut être :

- `ADD_REQUIRED_FRAME` ;
- `REQUIRE_FRAME_COMBINATION` ;
- `FORBID_FRAME_AS_SOLE_ARBITER` ;
- `CHANGE_FRAME_PRIORITY` ;
- `ADD_CONDITIONAL_VETO` ;
- `REJECT_FRAME_IN_CONTEXT`.

## Définition mathématique

### 1. Applicabilité d’une erreur apprise

Pour une erreur confirmée `e` et un nouvel objet `x`, définir :

```text
A_e(x) ∈ {0,1}
```

`A_e(x)=1` si les conditions d’applicabilité canonisées de la classe d’erreur `e` sont réunies dans `x`.

### 2. Indicateur de récurrence

```text
R_e(x) ∈ {0,1}
```

`R_e(x)=1` si, malgré `A_e(x)=1`, le système reproduit le verdict ou l’action invalidée par le contre-exemple `e`, sans nouvelle preuve ni override gouverné.

Condition de non-récurrence :

```text
∀e canonique, ∀x futur : A_e(x)=1 ⇒ R_e(x)=0
```

Équivalent opérationnel :

```text
A_e(x)=1 ⇒ décision(x) ∉ BAD_VERDICTS(e)
```

ou le système doit émettre un blocage explicite :

```text
A_e(x)=1 ∧ preuve_nouvelle_absente ⇒ GUARD_e(x)=BLOCKED
```

### 3. Transformation de la politique de cadres

Soit `F_t(x)` l’ensemble ordonné et pondéré des cadres mobilisés à l’instant `t`.

Après erreur confirmée `e` :

```text
F_{t+1}(x) = U_e(F_t(x))
```

avec `U_e` une transformation gouvernée pouvant ajouter un cadre, imposer une combinaison, modifier une priorité ou introduire un veto conditionnel.

La transformation est admissible seulement si :

```text
ΔS_global(U_e) ≥ 0
```

et si le contre-exemple est fermé :

```text
R_e(x_e après U_e) = 0
```

### 4. Taux d’apprentissage effectif

Sur l’ensemble `E_t` des classes d’erreurs confirmées jusqu’à `t`, pondérées par leur criticité `w_e > 0` :

```text
L_t = 1 - [Σ_e w_e * recurrence_e] / [Σ_e w_e * applicable_e]
```

avec :

- `applicable_e` : nombre de replays ou cas futurs où `A_e=1` ;
- `recurrence_e` : nombre de cas où `A_e=1` et `R_e=1`.

Bornes :

```text
0 ≤ L_t ≤ 1
```

- `L_t=1` : aucune classe d’erreur canonisée n’a récidivé dans les cas applicables observés ;
- `L_t<1` : régression systémique mesurée.

Si aucun cas applicable n’a encore été rejoué, `L_t` est `INDETERMINATE`, jamais fixé artificiellement à `1`.

### 5. Score de cohérence évolutive

La formule canonique est réutilisée avec des proxies explicites :

```text
S_evolution = (beta * delta_phi_learning) / (1 + T_learning + sigma_learning)
```

V1 : `beta = 1.0`.

Définitions :

- `delta_phi_learning` : proportion pondérée des erreurs confirmées converties en objets d’apprentissage complets, guards actifs, tests de régression et replays réussis ;
- `T_learning` : taux pondéré de récurrences observées, contradictions entre nouvelles règles et violations de gouvernance ;
- `sigma_learning` : coefficient de variation de la couverture des guards entre moteurs, cadres et classes d’erreurs.

Le score n’est calculable que si les unités, poids, corpus d’erreurs et cas de replay sont déclarés.

### 6. Gain d’évolution

```text
ΔS_evolution = S_evolution(t+1) - S_evolution(t)
```

Une promotion canonique est interdite si :

```text
ΔS_evolution < 0
```

ou si elle ferme localement `e` mais introduit une nouvelle récurrence critique dans une autre classe.

## Machine à états

```text
ERROR_CONFIRMED
→ COUNTEREXAMPLE_REPRODUCED
→ FRAME_CAUSE_IDENTIFIED
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
- aucune règle créée uniquement à partir d’une intuition ;
- aucune suppression automatique de cadre ;
- aucune auto-certification par ZORAN ;
- aucune preuve provenant d’un autre SHA ;
- aucun guard sans test de non-régression ;
- aucun apprentissage local si `delta S global < 0` ;
- toute récurrence d’une erreur canonisée impose au minimum `FIX_REQUIRED`.

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
  "learning_rate": null,
  "coherence_evolution": null,
  "authorize_canonical_promotion": false
}
```

`authorize_canonical_promotion=true` uniquement après audit externe, replay réussi, absence de régression globale et validation de la gouvernance.

## Position dans la roadmap

Le pipeline cible devient :

```text
00_RUNTIME_CHECK
...
11_TRACE_AND_CLOSE
12_COHERENT_EVOLUTION
```

`12` est le moteur d’évolution contrôlée de ZORAN. Il ne doit être codé qu’après certification de `00→11` et validation externe du présent contrat.
