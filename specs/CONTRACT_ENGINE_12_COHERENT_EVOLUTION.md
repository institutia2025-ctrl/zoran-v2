# CONTRACT_ENGINE_12_COHERENT_EVOLUTION

## Statut

`GOVERNANCE_META_LOOP — OUT_OF_PIPELINE — NO_RUNTIME_ENGINE — NO_GATE_12 — SPEC_ONLY — NO_CODE_AUTHORIZED`

> **Reclassement (Fred 2026-07-16).** ENGINE-11 est la porte terminale du pipeline certifié ENGINE-00→11.
> La coherent evolution est une méta-boucle de gouvernance hors pipeline, non-runtime et non numérotée comme gate.
> Ce document ne décrit donc **pas** une porte runtime : il décrit une boucle de gouvernance qui observe
> plusieurs transactions et findings. Identifiant interne : `GOV_COHERENT_EVOLUTION` (l'ancien
> `12_COHERENT_EVOLUTION` est retiré). Le nom de fichier est conservé pour la traçabilité historique.

## Identité

- Governance-object ID : `GOV_COHERENT_EVOLUTION`
- Rôle : méta-boucle de gouvernance HORS pipeline (ni moteur ni gate).
- Position : HORS pipeline ; observe les traces closes de `11_TRACE_AND_CLOSE` et le corpus de findings à travers PLUSIEURS transactions (jamais une porte par-transaction).
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

## Sortie minimale (objet de gouvernance illustratif — NON-RUNTIME)

```json
{
  "governance_object": "GOV_COHERENT_EVOLUTION",
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

## Position (hors pipeline)

Le pipeline de raisonnement certifié est **complet et borné à ENGINE-00→11** ; `11_TRACE_AND_CLOSE` en est la **porte terminale**.

```text
00_RUNTIME_CHECK
...
11_TRACE_AND_CLOSE          <- porte terminale du pipeline certifié ENGINE-00→11
--------------------------------------------------------------
GOV_COHERENT_EVOLUTION      <- HORS pipeline : méta-boucle de gouvernance (non-runtime, non numérotée comme gate)
```

`GOV_COHERENT_EVOLUTION` est une **boucle de gouvernance hors pipeline**, pas un moteur ni une porte runtime. Invariants du reclassement :

1. `ENGINE-00→11` constitue le pipeline de raisonnement complet et certifié.
2. `ENGINE-11` est terminal ; aucune porte n'est ajoutée après lui.
3. La coherent evolution **observe plusieurs transactions et findings** (jamais une étape par transaction).
4. Elle **fonctionne hors pipeline** (non-runtime dans le chemin de raisonnement).
5. Elle **ne modifie jamais rétroactivement** une transaction close.
6. Toute politique évoluée doit être **versionnée**.
7. Les **replays futurs utilisent la version historique engagée** dans la transaction (jamais une politique postérieure).
8. Toute promotion de règle, guard ou politique exige **preuve + test de non-récurrence + audit externe + décision de Fred**.
9. Le **processus manuel actuel reste autoritaire** tant qu'aucune défaillance d'échelle n'est observée.

Aucun code runtime n'est autorisé : ce contrat reste `SPEC_ONLY`.
