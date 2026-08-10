# SOCIAL_RECEIVABILITY_SATELLITE_V1 — contrat figé

> **Source de vérité** : verdict Claude FEATURE-AUDIT (2026-07-16). **Statut** : `CONTRACT_ONLY — NO_RUNTIME — NO_CODE_WO`.
> **Emplacement** : `satellites/social_receivability/` — **HORS `zoran_v2/`, HORS pipeline 00→11.**

## Rôle
Mesurer la **réceptabilité sociale / adoption contextuelle** (`wO`) d'une proposition dans une population à un
instant. **Adoption ≠ vérité.** N'influence jamais S, les moteurs, les gates, ni aucune décision de vérité/cohérence/sécurité.

## Interface (cf `SCHEMA.yaml`)
- **Entrée** : `proposition_ref (x)`, `t`, `context (c)`, `population {id,size}`, `horizon`, `observed_data[] {value, provenance_ref, timestamp, sample_n}`.
- **Sortie** : `status ∈ {MEASURED, NON_MESURE, BLOCKED}`, `wO ∈ [0,1] | null`, `uncertainty_interval [lo,hi]`,
  `confidence [0,1]`, `provenance_refs[]`, `trend? {dir,slope}`, `counter_evidence[]` (obligatoire),
  `is_truth_signal: false` (constant), `measured_from_sample_n`, `as_of_t`.

## Invariants gravés (testables — mapping dans les tests)
1. `NO_ENGINE_IMPORT` — aucun moteur `zoran_v2/*` (00→11) n'importe ce satellite.
2. `ONE_WAY_FLOW` — flux pipeline → satellite uniquement ; ce module n'importe pas `zoran_v2/*`.
3. `SEPARATE_OUTPUT_OBJECT` — `OUTPUT_KEYS` disjoint des sorties moteurs (05/09/10/11).
4. `NO_S_INFLUENCE` / `NO_GATE_INFLUENCE` — `wO` n'entre jamais dans S ni dans une décision PASS/BLOCKED / verdict ressource.

## Contrat dur
- `NON_MESURE` **fail-closed** sans données observées suffisantes (`sample_n < N_MIN=30`, population indéfinie, horizon hors données, provenance absente/falsifiée, fraîcheur dépassée, contexte non apparié).
- `is_truth_signal = false` **constant**.
- `counter_evidence` **obligatoire**.
- Aucune écriture canonique · aucune action automatique · aucun filtre éliminatoire · aucune influence S / verdict ressource / gates · aucune inférence sans données.

## Verdict d'admissibilité (rappel)
`FIX_REQUIRED` → devient `APPROVED` une fois ce contrat + ces invariants rendus **testables** (T1–T12). Ce PR fige le contrat
et pose les tests rouges ; **aucun runtime `wO` n'est construit**. Construction future = **GO Fred explicite** après audit indépendant du SHA.
