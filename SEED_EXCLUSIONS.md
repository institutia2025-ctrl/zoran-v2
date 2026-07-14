# SEED_EXCLUSIONS — ce qui est banni de la graine (default-deny)

Mission : TX_ZORAN_GITHUB_SEED_P0_V2. Principe : rien n'entre sauf `SEED_ALLOWLIST.json`.

## Exclusions absolues (jamais dans la graine, jamais commit)
- Données réelles : `data/`, `uploads/`, `memory/`, conversations, préférences utilisateur.
- Bases : tout SQLite réel (`*.db`, `*.sqlite`, `*.sqlite3`), tout `*.jsonl` de données.
- Secrets : `.env` réel, `*.pem`, `*.key`, `secret*.txt`, clés/tokens fournisseur.
- Historique : aucun ancien dossier `.git`, aucun historique importé.
- Chantier : ancien dépôt de production, moteur historique complet, clone local `zoran_v2_sandbox`.
- Système : logs/traces réels, caches, artefacts générés, fichiers du Bureau, chemins absolus vers le PC.

## Mécanisme
- `.gitignore` défensif bloque les ajouts FUTURS de ces catégories (protection prospective, PAS une purge d'historique — l'historique est neuf).
- Ajout Git **explicite par allowlist** uniquement ; jamais `git add .`.

## Portée
Travail confiné à la graine. Le dépôt de production, le produit en service et les ports ne sont pas mutés par cette mission.
