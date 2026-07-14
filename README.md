# ZORAN V2 — graine propre (Codespaces)

Base de construction du moteur de raisonnement ZORAN V2, **isolée du PC de Fred**.

- **Substrat** : GitHub Codespaces (VM + réseau cloud isolés, éphémère).
- **Aucune donnée réelle, aucun secret** : construite par **allowlist** (default-deny), sans historique de l'ancien dépôt.
- **Python** : 3.13 (satisfait le contrat moteur 00 : `< 3.14`).
- **Données** : synthétiques/représentatives en Codespaces ; les 439K réels ne sont testés qu'en **staging local figé** (copie SQLite gelée), jamais poussés.

## Cycle prouvé d'abord (avant le moteur)
`BASE_SHA propre → repo privé → branche mission → Codespace → micro-change → commit → GitHub Actions (pytest) → audit Codex du diff → destruction du Codespace`

## Provenance
- Créée le 2026-07-14 depuis le dépôt local ZORAN (BASE_SHA de référence : `e7c33b227`), **par sélection allowlist** — l'arbre `e7c33b227` lui-même n'est **pas** publié (données réelles + secrets suspectés dans son historique).
- `zoran_v2/_cycle_probe.py` = sonde triviale déterministe (pas de logique moteur). Le moteur se construit ensuite, composant par composant.
