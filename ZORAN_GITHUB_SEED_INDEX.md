# ZORAN_GITHUB_SEED_INDEX — tableau de bord double-contrôle

Mission : **TX_ZORAN_GITHUB_SEED_P0_V2** · Statut : `SEED_CANDIDATE_LOCAL_CREATED` · `CODEX_AUDIT_REQUIRED` · `PUSH_NOT_AUTHORIZED`

**⚠️ IMMUABILITÉ** — Ce fichier est la **déclaration Claude** figée dans le commit seed. Codex **ne remplit PAS** ses colonnes ICI : les modifier changerait le SHA audité (boucle infinie). Le **double-contrôle** (coche Claude + coche Codex) est tenu dans le **registre externe** `ZORAN_V2_CONSTRUCTION/SEED_DOUBLE_INDEX.md`, clé `AUDITED_CANDIDATE_SHA`. Les colonnes Codex ci-dessous restent `[ ]` par convention ; l'autorité du verdict = registre externe. Toute modif du code/doc → nouveau `CANDIDATE_SHA` + nouvel audit externe.

`BASE_SHA` = `e9d117fe9b3033dd303a38911e4cee92f5fca569` → `CANDIDATE_SHA` = nouveau SHA (produit post-commit ; non figé ici car ce fichier est inclus dans le commit — voir preuves brutes de session). Source canonique d'inventaire = `SEED_ALLOWLIST.json` (`SEED_MANIFEST.md` supprimé pour éviter deux inventaires).

| ID | Contrôle | Claude | Preuve Claude | Codex | Verdict Codex | Preuve Codex |
|----|----------|:------:|---------------|:-----:|---------------|--------------|
| P0-001 | Dossier distinct du dépôt historique | [x] | graine hors arbre du dépôt de prod (répertoire séparé) | [ ] | | |
| P0-002 | Aucun ancien `.git` copié | [x] | historique neuf = **2 commits propres** (racine + candidat) ; racine `rev-list --parents` = 0 parent ; aucun `.git` de production importé | [ ] | | |
| P0-003 | Allowlist == fichiers présents | [x] | `git ls-tree -r HEAD` == entrées `SEED_ALLOWLIST.json` | [ ] | | |
| P0-004 | Aucune donnée utilisateur réelle | [x] | 0 `data/`/`memory/`/conversations tracké ; scan raw joint | [ ] | | |
| P0-005 | Aucun SQLite réel | [x] | 0 `*.db`/`*.sqlite*` (find, raw joint) | [ ] | | |
| P0-006 | Aucun chemin absolu vers le PC | [x] | grep `C:\\Users` sur fichiers trackés = 0 (raw joint) | [ ] | | |
| P0-007 | Aucun secret fournisseur reconnu | [x] | « aucun motif reconnu détecté par le scan utilisé » (raw joint) | [ ] | | |
| P0-008 | Config via variables d'environnement | [x] | `.env.example` = variables ; aucune valeur en dur | [ ] | | |
| P0-009 | `.env.example` = valeurs fictives | [x] | `your-anthropic-key-here`, `your-openai-key-here` | [ ] | | |
| P0-010 | Workflow Actions sous Python 3.13 | [x] | `.github/workflows/ci.yml` → `python-version: "3.13"` | [ ] | | |
| P0-011 | Test Python < 3.14 falsifiable | [x] | `assert probe()["py_lt_314"] is True` | [ ] | | |
| P0-012 | Test échoue en 3.14 local (raison attendue) | [x] | `pytest` → 1 failed (`py_lt_314` False en 3.14) ; raw joint | [ ] | | |
| P0-013 | Commit = uniquement fichiers allowlist | [x] | `git ls-tree -r HEAD` == allowlist | [ ] | | |
| P0-014 | Working-tree propre après commit | [x] | `git status --short` vide (raw joint) | [ ] | | |
| P0-015 | Aucun remote configuré | [x] | `git remote -v` vide (raw joint) | [ ] | | |
| P0-016 | Aucun push réalisé | [x] | aucun remote → aucun push possible | [ ] | | |
| P0-017 | Dépôt historique non modifié par cette mission | [x] | travail confiné à la graine ; aucun geste sur le dépôt de prod | [ ] | | |
| P0-018 | Produit non arrêté/redémarré par cette mission | [x] | aucun restart backend dans cette mission | [ ] | | |
| P0-019 | Index = 2 colonnes Claude/Codex distinctes | [x] | ce fichier (colonnes séparées) | [ ] | | |
| P0-020 | Aucune coche Codex renseignée par Claude | [x] | colonnes Codex toutes `[ ]` | [ ] | | |

*Sortie autorisée : SEED_CANDIDATE_LOCAL_CREATED / CODEX_AUDIT_REQUIRED / PUSH_NOT_AUTHORIZED. Arrêt après commit + preuves ; attente audit Codex + GO Fred.*
