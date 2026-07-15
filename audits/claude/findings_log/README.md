# FINDINGS_LOG — journal des findings certificateurs par moteur (DOCS_ONLY)

But : transformer la « courbe des erreurs par moteur » d'une **reconstruction de mémoire de session**
en **preuve vivante** journalisée. Aucun impact moteur (00→11). Additif, append-only.

## Schéma (1 ligne JSON par finding)
| champ | sens |
|---|---|
| `engine` / `engine_key` | numéro de porte + clé snake_case (ex. `09` / `structured_decision`) |
| `code` (+ `alias`) | identifiant du finding tel que soulevé par le certificateur |
| `class` | **classe** de défaut (c'est la classe qu'on ferme, pas l'exemple — REX #15) |
| `summary` | 1 ligne |
| `fix_sha` | SHA de la correction (best-effort ; voir provenance) |
| `fixer` | acteur ayant corrigé (défaut = CODEX_FIXER) |
| `reused_downstream` | **true si le garde issu de ce fix est réutilisé en aval** (+ `reused_note`) — c'est le moteur de l'amélioration |
| `provenance` | `reconstructed` (reconstruit de mémoire, SHAs non re-vérifiés) \| `live` (journalisé en temps réel) |
| `session` | session de construction |

## Règle d'or (loi anti-régression instrumentée)
Un finding dont `reused_downstream=true` = une **classe fermée** dont le garde protège les moteurs suivants
par construction. La courbe descendante 05→10 s'EXPLIQUE par le cumul de ces gardes réutilisés — pas par chance.

## État actuel (2026-07-15)
- 10 lignes, **toutes `provenance:reconstructed`** (findings de cette session, SHAs best-effort NON re-vérifiés contre `git log`).
- Comptes par moteur : **05=6 · 08=2 · 09=2 · 10=0** (10 en réaudit, 0 PROVISOIRE).
- Gardes réutilisés en aval (`reused_downstream:true`) : 6 findings → dont surrogate + primitive canonique + contexte-complet-id → **importés tels quels par 10**.

## Limites (honnêteté)
1. `reconstructed` ≠ vérifié : les `fix_sha` sont de mémoire de session, à re-certifier contre `git log` avant tout usage probant.
2. 10=0 est PROVISOIRE (réaudit ChatGPT + Codex A + Codex B non lancé).
3. 05=6 gonflé par le coût d'apprentissage initial (saga E11), pas une fragilité intrinsèque.

## Régénérer la courbe
`python audits/claude/findings_log/render_curve.py` → recompte par moteur + ratio `reused_downstream`.
Toute nouvelle certification AJOUTE une ligne `provenance:live` ici (jamais réécrire l'historique).
