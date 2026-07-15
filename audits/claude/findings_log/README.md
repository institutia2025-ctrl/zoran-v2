# INSTRUMENTATION ZORAN V2 — findings + métriques par moteur (DOCS_ONLY)

But : transformer la « courbe des erreurs par moteur » d'une **reconstruction de mémoire de session**
en **preuve vivante** journalisée, et l'élargir aux paramètres pertinents. Aucun impact moteur (00→11). Additif, append-only.

Deux fichiers : `FINDINGS_LOG.jsonl` (1 ligne / finding certificateur) · `ENGINE_METRICS.jsonl` (1 ligne / moteur, agrégats).

## Schéma FINDINGS_LOG (1 ligne JSON par finding)
| champ | sens |
|---|---|
| `engine` / `engine_key` | numéro de porte + clé snake_case (ex. `09` / `structured_decision`) |
| `code` (+ `alias`) | identifiant du finding tel que soulevé par le certificateur |
| `class` | **classe** de défaut (c'est la classe qu'on ferme, pas l'exemple — REX #15) |
| `severity` | `CRASH` > `LOGIC` > `PROVENANCE` > `SCHEMA` (gravité décroissante) |
| `debt_class` | dette Minimum-Debt V1 : `D_CODE` / `D_LOGIC` / `D_SYSTEM` / `D_GOV` / `D_METRIC` |
| `caught_by` | `external_certifier` (ChatGPT/Codex) \| `self` (self-audit pré-ship) |
| `summary` | 1 ligne |
| `fix_sha` | SHA de la correction (best-effort ; voir provenance) |
| `fixer` | acteur ayant corrigé (défaut = CODEX_FIXER) |
| `reused_downstream` | **true si le garde issu de ce fix est réutilisé en aval** (+ `reused_note`) — c'est le moteur de l'amélioration |
| `provenance` | `reconstructed` (reconstruit de mémoire, SHAs non re-vérifiés) \| `live` (journalisé en temps réel) |
| `session` | session de construction |

## Schéma ENGINE_METRICS (1 ligne JSON par moteur)
`loc` · `tests` · `ci` · `merged` — **measured** (dépôt) · `findings` · `reused_downstream` — **derived** (du log) ·
`rounds_to_green` (nb SHA de fix) · `self_precorrections_approx` (self-audit pré-ship attrapé avant certif) ·
`fixer_mix` (Claude/Codex) — **reconstructed**. Chaque ligne porte un objet `provenance` classant ses champs.

## Paramètres ÉCARTÉS (S multicadres — non mesurables honnêtement, non inventés)
latence/temps par moteur (pas d'horodatage fiable) · tokens par moteur (non journalisé côté build) ·
couverture % (coverage.py non exécuté) · LOC-comme-dette seul (signal faible, gardé mais non interprété qualité).

## Règle d'or (loi anti-régression instrumentée)
Un finding dont `reused_downstream=true` = une **classe fermée** dont le garde protège les moteurs suivants
par construction. La courbe descendante 05→10 s'EXPLIQUE par le cumul de ces gardes réutilisés — pas par chance.

## État actuel (2026-07-15)
- FINDINGS : 10 lignes `provenance:reconstructed` (SHAs best-effort NON re-vérifiés). Courbe **05=6 · 08=2 · 09=2 · 10=0** (10 réaudit, provisoire).
- Gardes réutilisés en aval : 6 (surrogate + primitive canonique + contexte-complet-id → **importés par 10**).
- METRICS (mesurés) : LOC **486→510→392→330**, tests **68→63→32→27** → **consolidation** (moteurs tardifs plus légers en faisant plus).
- severite : CRASH 1 (09), le reste LOGIC/PROVENANCE/SCHEMA → plus de crash-class en aval (garde surrogate).
- caught_by : les 10 findings loggés = `external_certifier` ; les self-precorrections (pré-ship) sont comptés dans ENGINE_METRICS (`self_precorrections_approx` : 1→2→2→3, en hausse).

## Limites (honnêteté)
1. `reconstructed` ≠ vérifié : `fix_sha`, `rounds_to_green`, `self_precorrections_approx`, `fixer_mix` sont de mémoire de session.
2. 10=0 findings est PROVISOIRE (réaudit ChatGPT + Codex A + Codex B non lancé).
3. 05=6 gonflé par le coût d'apprentissage initial (saga E11), pas une fragilité intrinsèque.
4. `self_precorrections_approx` = ordre de grandeur (les self-catches n'étaient pas journalisés en temps réel) → à passer en `live` désormais.

## Régénérer la courbe
`python audits/claude/findings_log/render_curve.py` → recompte par moteur + ratio `reused_downstream`.
Toute nouvelle certification AJOUTE une ligne `provenance:live` ici (jamais réécrire l'historique).
