# SEED_MANIFEST — inventaire allowlist (P0.5)

OBJECT_ID: ZORAN-V2-GITHUB-SEED · VERSION: 2.0.0-seed · OWNER: FRED · PROVENANCE: TX_ZORAN_V2_ROUTE_CLEANUP → pivot Codespaces
CRÉÉ: 2026-07-14 06:40 +0200 · PUSH: ❌ INTERDIT sans GO Fred + repo privé + audit Codex

## Principe : default-deny. Rien n'entre sauf la liste ci-dessous.
| Fichier | Rôle | Secret/PII |
|---|---|---|
| `.gitignore` | exclusions renforcées (data/uploads/memory/*.jsonl/.env/*.db) | non |
| `.env.example` | variables **fictives** | non (fictif) |
| `README.md` | provenance + cycle | non |
| `requirements-dev.txt` | pytest | non |
| `.github/workflows/ci.yml` | CI pytest Python 3.13 | non |
| `zoran_v2/__init__.py` | package (version) | non |
| `zoran_v2/_cycle_probe.py` | sonde triviale déterministe (pas de moteur) | non |
| `tests/test_cycle_probe.py` | 2 tests déterministes | non |
| `SEED_MANIFEST.md` | ce fichier | non |

## Exclusions absolues (jamais dans la graine)
`data/` réel · `uploads/` · conversations · préférences user · mémoires · SQLite réel · logs/traces · clés/tokens · ancien `.git` · caches · artefacts générés · fichiers Desktop.

## Contrôles P0.5 (à faire AVANT push)
- [x] Aucun ancien `.git` copié (dossier neuf)
- [x] Aucun fichier `data/` réel présent
- [x] `.env.example` fictif uniquement
- [ ] Scan secrets automatique sur la graine (à rejouer juste avant push)
- [ ] Clôture des dépendances code (quand le moteur entre)
- [ ] **Audit contradictoire Codex du diff/inventaire**
- [ ] Repo GitHub privé créé (action Fred) + push protection activée si dispo
