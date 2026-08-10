# BOUNDARIES — frontières d'isolation du satellite SOCIAL_RECEIVABILITY

> Objectif : garantir, de façon **testable**, que la sociétabilité (`wO`) ne peut **jamais** toucher le noyau de
> vérité/cohérence/sécurité (S, moteurs 00→11, gates, verdict ressource, décisions 09/10/11).

## Frontière de flux (unidirectionnelle)
```
pipeline 00→11 (déterministe, NO_NETWORK, S verrouillé)
        │  (sorties publiées, en lecture)
        ▼
satellites/social_receivability   ──►  objet wO SÉPARÉ (advisory, is_truth_signal:false)
        ╳ (interdit)
        └─►  jamais de retour vers 05 / S / gates / décisions
```

## Les 4 invariants d'isolation (→ tests)
| Invariant | Garantie | Test |
|---|---|---|
| `NO_ENGINE_IMPORT` | aucun `zoran_v2/*.py` n'importe/réfère le satellite | T2 (GREEN) |
| `ONE_WAY_FLOW` | `contract.py` n'importe aucun `zoran_v2/*` | ONE_WAY (GREEN) |
| `SEPARATE_OUTPUT_OBJECT` | `OUTPUT_KEYS` disjoint des sorties 05/09/10/11 | T9 (GREEN) |
| `NO_S_INFLUENCE` / `NO_GATE_INFLUENCE` | source des moteurs sans `social_receiv`/`wO` ; wO n'entre pas dans S/gate | T3, T4 (GREEN) |

## Anti-confusion adoption/vérité
- `is_truth_signal = false` constant · `counter_evidence` obligatoire · `wO` jamais affiché comme score à côté de S sans avertissement · jamais routé dans une décision · jamais un filtre.

## Risques couverts (verdict FEATURE-AUDIT §4)
- **Biais majoritaire** (populaire ≠ vrai) → T5.
- **Dérive normative** (feedback) → T12 (anti-drift).
- **Confusion adoption/vérité** → is_truth_signal + T9 séparation.

## Statut de construction
`CONTRACT_ONLY` : aucun runtime `wO`. Les tests comportementaux (T1, T5–T12) sont **rouges attendus** (`xfail strict`)
jusqu'au GO Fred de construction. Les tests d'isolation (T2, T3, T4, T9, ONE_WAY) **passent déjà** (verts).
