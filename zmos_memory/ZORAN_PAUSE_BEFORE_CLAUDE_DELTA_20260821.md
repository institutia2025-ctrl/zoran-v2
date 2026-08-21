# ZORAN — PAUSE AVANT DELTA CLAUDE

Statut : PAUSED_WAITING_CLAUDE_DELTA_AUDIT
Autorité : Fred
Branche : codex/zoran-final-canon-v1

## État à préserver
- Construction : 62 %
- Delta fonctionnel du chat : +0 point
- Phase : BGE_M3_LOCAL_PERSISTENT_RETRIEVAL_PLUS_INDEX
- Plan canonique : ZORAN_FINAL_CONSTRUCTION_CANON_V1.md
- Mémoire : zmos_memory/ZORAN_FINAL_PLAN_V1.zmos.json
- Tracker : zmos_memory/ZORAN_BUILD_TRACKER_V1.json
- Registre : zmos_memory/ZORAN_COMPONENT_REGISTRY_V1.json
- État courant : zmos_memory/ZORAN_CURRENT_STATE.md
- Dernier audit : reports/ZORAN_CHAT_01_360_AUDIT_20260821.md

## Invariants
- K3 = noyau logique.
- ZMOS = mémoire persistante.
- BGE-M3 = retrieval uniquement.
- LLM reasoning/decision = 0.
- 00→11 ne redevient pas le cœur sans réaudit + GO explicite.
- aucun pourcentage ne monte sans preuve.

## Travail en cours au moment de la pause
La cartographie GitHub avait été persistée. Une seconde passe File Library venait de retrouver des éléments plus récents à réauditer :
- NLP.js 4.26.1 MIT : build PASS, runtime 17/17, sélection 50/50, français naturel 10/10, hors corpus 50/50 NON_MESURÉ ; modèles SHA-256 documentés.
- ZTRACE_POLYMORPHIC_ENGINE_V1_2026_08_17_19h00_CEST.py : moteur déterministe, manifeste SHA-512, 40/40 tests moteur et 76/76 sur le format computable rapportés.
- Internet borné : documents récents rapportent build PASS, runtime 23/23, SQL 2/2, 50/50 requêtes simulées, anti-SSRF/fail-closed ; exact build/SHA encore à relier.
- Amygdale : prototype historique documenté, code exécutable courant non retrouvé.

## Prochaine action après réception Claude
Comparer brique par brique : Claude vs état canonique/artefacts directs. Réauditer 360°. Choisir le meilleur composant par preuve, pas par préférence d'analyste. Ne rien greffer avant verdict.
