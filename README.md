# ZORAN V2 — graine propre (Codespaces)

Base de construction du moteur de raisonnement ZORAN V2, **isolée du PC de Fred**.

- **Substrat** : GitHub Codespaces (VM + réseau cloud isolés, éphémère).
- **Aucune donnée réelle, aucun secret** : construite par **allowlist** (default-deny), sans historique de l'ancien dépôt.
- **Python** : 3.13 (satisfait le contrat moteur 00 : `< 3.14`).
- **Données** : synthétiques/représentatives en Codespaces ; les 439K réels ne sont testés qu'en **staging local figé** (copie SQLite gelée), jamais poussés.

## Cycle prouvé d'abord (avant le moteur)
`BASE_SHA propre → repo privé → branche mission → Codespace → micro-change → commit → GitHub Actions (pytest) → audit Codex du diff → destruction du Codespace`

## Glossaire des SHA (non ambigu)
- **SOURCE_SHA** = `e7c33b227` — provenance historique (dépôt de production ZORAN). Cet arbre n'est **pas** publié (données réelles + secrets suspectés dans son historique).
- **SEED_BASE_SHA** = `e9d117fe9b3033dd303a38911e4cee92f5fca569` — commit racine de la graine (base du diff d'audit P0.5).
- **PREVIOUS_CANDIDATE_SHA** = `3cbcaa322eb22570daeb0ec92fc69d2934430f63` — candidat P0.5 précédent (audité par Codex).

## Provenance
- Graine créée le 2026-07-14 **par sélection allowlist** (default-deny) à partir de la connaissance du dépôt de production (SOURCE_SHA), sans copier son historique ni ses données.
- `zoran_v2/_cycle_probe.py` = sonde triviale déterministe (pas de logique moteur). Le moteur se construit ensuite, composant par composant.
