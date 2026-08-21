# ZORAN — CHAT 01 — AUDIT 360° DE CARTOGRAPHIE

**Horodatage : 2026-08-21T13:31:00+02:00**  
**Autorité : Fred**  
**Plan : `ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**  
**Mémoire : `zmos_memory/ZORAN_FINAL_PLAN_V1.zmos.json`**  
**Tracker : `zmos_memory/ZORAN_BUILD_TRACKER_V1.json`**

## État de départ

- Construction : **62 %**
- Delta de construction au début du chat : **+0 point**
- Phase : **BGE-M3 + corpus/index**
- Verrou : `BGE_M3_LOCAL_PERSISTENT_RETRIEVAL_PLUS_INDEX`
- Architecture alternative autorisée : **aucune**

## Audit 360°

### K3

La source K3 v1.1 la plus cohérente identifiée reste :

- dépôt : `institutia2025-ctrl/zoran-v2`
- branche : `audit/frame-algebra-k3-v1`
- SHA : `636f70356083697b665f2af2fde6a46abd7a8633`
- fichier : `experiments/frame_algebra/moteur_algebre_cadres.py`
- blob : `ba851c71d7e8ac1ec8c918d291ab128fc9e2fba0`

Verdict : **PASS — noyau logique conservé**.

### ZMOS

Deux niveaux utiles ont été distingués :

1. dépôt direct ZMOS : `Zoran-IA-Mimetique/zmos-v2-transactional-bench`, `main`, dernier SHA audité `112ee9439a36130b97176bc71f01cd1b8606a0a3` ;
2. composants gouvernés historiques du runtime : `Zoran-IA-Mimetique/zoran-bench-runtime`, branche `codex/judge-calibration-v1`, SHA de base `8329b91ef91c7b456d60b90fb235cd601ae81eec`.

Le dépôt direct ZMOS est retenu comme source prioritaire de mémoire transactionnelle/reconstruction. Les modules `governed_memory_v2`, `zmos_selection_v2` et M7 du bench-runtime restent donneurs précis tant qu'un équivalent plus récent n'est pas prouvé dans le dépôt direct.

Verdict : **PASS — ZMOS récupérable sans reconstruction globale**.

### BGE-M3

Source externe retenue : `BAAI/bge-m3` / `FlagOpen/FlagEmbedding`.

Faits vérifiés sur les sources officielles :

- licence : MIT ;
- dimension dense : 1024 ;
- longueur : jusqu'à 8192 tokens ;
- multilingue : 100+ langues ;
- modes : dense, sparse/lexical, multi-vector.

Règle canonique : BGE-M3 **retourne uniquement des candidats et scores**. Il n'a aucune autorité sur fait, cadre, contradiction, action, refus ou certitude.

Manques :

- révision exacte des poids à geler : `NON_MESURÉ` ;
- runtime Zoran BGE-M3 exact-SHA : `NON_MESURÉ` ;
- index corpus exact-SHA : `NON_MESURÉ`.

Verdict : **famille modèle PASS ; intégration runtime NON_MESURÉE**.

### Dépôts historiques embeddings/corpus

`Zoran-IA-Mimetique/zoran-ia-embeddings` est un ancien dépôt MIT principalement documentaire/packagé et ne constitue pas une implémentation BGE-M3 actuelle auditée.

`Zoran-IA-Mimetique/zoran-datasets` est un petit dépôt documentaire/packagé et ne constitue pas la preuve du corpus Wikipédia/Zoran local massif ni de son index actuel.

Verdict : **REJET comme runtime/corpus final ; conservation comme historique uniquement**.

### NLP.js / ZTRACE

Aucune source runtime actuelle correspondant au NLP.js 4.26.1 et au ZTRACE sémantique décrits dans le plan n'a été identifiée dans les trois dépôts principaux audités (`zoran-v2`, `zoran-bench-runtime`, UI gelée). Le dépôt `Zoran-Trace-Init-Copilot` est une documentation d'empreinte mimétique et n'est pas le moteur ZTRACE.

Verdict : **NON_MESURÉ — source exacte à retrouver, aucune substitution autorisée**.

### SEMANTIC_DECISION

Le remote contient une ancienne candidate dans `codex/audit-semantic-decision-v1`. Le SHA R5 rapporté comme scellé localement `111cec9f306c2256b705f79a5ecdd310d3df10f5` n'est pas retrouvable sur GitHub.

Verdict : **QUARANTAINE de l'ancienne candidate ; récupération R5 requise avant greffe**.

### UI

Référence gelée :

- dépôt : `Zoran-IA-Mimetique/ZORAN-UI-27-07-2026`
- branche : `source/exact-v169`
- SHA : `721df5c21a6598c66dc3fb6b958e4c0171be0323`
- tree : `046932b0f2d6a94ccc7c612d0c9b59cdfa399f23`

Le backend LLM historique n'est pas autorité du cœur final.

Verdict : **PASS comme référence UI ; backend décisionnel historique REJETÉ**.

## Contrôle de dérive

- ancienne chaîne 00→11 remise comme cœur : **NON** ;
- Gemma remis comme raisonneur : **NON** ;
- BGE-M3 promu comme décideur : **NON** ;
- changement d'ordre de construction : **NON** ;
- substitution d'un ancien repo embeddings au BGE-M3 : **NON** ;
- substitution d'un dataset stub au corpus : **NON**.

Verdict dérive : **PASS**.

## Delta réel du chat

Ce chat ferme la **cartographie exacte des sources récupérables** et élimine plusieurs faux candidats, mais ne fournit pas encore un runtime BGE-M3 ni un index corpus exécutable.

Par conséquent :

- delta fonctionnel prouvé : **+0 point** ;
- construction : **62 % → 62 %** ;
- cartographie Chat 1 : **PASS** ;
- prochaine porte : **BGE-M3 local persistant + corpus/index exacts**.

## Inconnus à transporter

1. `LIVE_ZMOS_DATABASE_INGESTION_OF_CANON_OBJECT_NON_MESURE_FROM_THIS_ENVIRONMENT`
2. `BGE_M3_EXACT_MODEL_REVISION_NON_MESURE`
3. `BGE_M3_ZORAN_RUNTIME_SHA_NON_MESURE`
4. `CORPUS_WIKIPEDIA_ZORAN_EXACT_PATH_AND_SHA_NON_MESURE`
5. `SEMANTIC_INDEX_SHA_NON_MESURE`
6. `NLP_JS_CURRENT_RUNTIME_SOURCE_NON_MESURE`
7. `ZTRACE_CURRENT_RUNTIME_SOURCE_NON_MESURE`
8. `SEMANTIC_DECISION_R5_REMOTE_SOURCE_NON_MESURE`
9. `AMYGDALA_EXECUTABLE_SOURCE_CURRENT_LOCATION_NON_MESURE`
10. `UNIFIED_E2E_SHA_NON_MESURE`

## Condition de reprise du prochain chat

Lire dans cet ordre :

1. `ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`
2. `zmos_memory/ZORAN_FINAL_PLAN_V1.zmos.json`
3. `zmos_memory/ZORAN_BUILD_TRACKER_V1.json`
4. `zmos_memory/ZORAN_COMPONENT_REGISTRY_V1.json`
5. ce rapport Chat 01

Puis reprendre **uniquement** sur `BGE_M3_LOCAL_PERSISTENT_RETRIEVAL_PLUS_INDEX`.

**Verdict terminal Chat 01 : PASS_CARTOGRAPHY — CONSTRUCTION 62 % — NO_ARCHITECTURE_DRIFT.**
