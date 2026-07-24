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

## État actuel (2026-07-16) — pipeline 00→11 COMPLET (12 dormant)
- FINDINGS : 15 lignes. 05/08/09 = `reconstructed` (10 lignes) ; **10 et 11 = `live`** (5 lignes, journalisées à la certif+merge).
- Courbe findings (ordre construction) : **05=6 · 08=2 · 09=2 · 10=3 · 11=2**. Gardes réutilisés en aval : **9/15**.
- METRICS (mesurés, SHA certifiés) : LOC **486→510→392→363→534**, tests(fn) **68→63→32→31→64** (11 = 150 cas via paramétrage).
- severite : CRASH 1 (09) · SECURITY 2 (11 : auth preuve externe + usurpation identité) · LOGIC 8 · PROVENANCE 3 · SCHEMA 1.
- dette (Minimum-Debt V1) : D_LOGIC 9 · D_SYSTEM 3 · D_CODE 2 · D_METRIC 1 (PROOF_SHA_LAG).
- caught_by : 15/15 `external_certifier` ; self_precorrections (pré-ship) montent **1→2→2→3→4** (ENGINE_METRICS).
- 11 (terminal) : findings de type SÉCURITÉ (ne plus faire confiance à une preuve externe auto-attestée / une identité usurpable) — reused_downstream=0 (aucun moteur actif en aval).

## Limites (honnêteté)
1. `reconstructed` ≠ vérifié : `fix_sha`, `rounds_to_green`, `self_precorrections_approx`, `fixer_mix` sont de mémoire de session.
2. 10=0 findings est PROVISOIRE (réaudit ChatGPT + Codex A + Codex B non lancé).
3. 05=6 gonflé par le coût d'apprentissage initial (saga E11), pas une fragilité intrinsèque.
4. `self_precorrections_approx` = ordre de grandeur (les self-catches n'étaient pas journalisés en temps réel) → à passer en `live` désormais.

## Régénérer la courbe
`python audits/claude/findings_log/render_curve.py` → recompte par moteur + ratio `reused_downstream`.
Toute nouvelle certification AJOUTE une ligne `provenance:live` ici (jamais réécrire l'historique).
