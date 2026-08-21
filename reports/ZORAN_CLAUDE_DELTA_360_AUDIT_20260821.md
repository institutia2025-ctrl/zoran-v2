# ZORAN — DELTA CLAUDE vs CANON / ZMOS — AUDIT 360°

**Date : 2026-08-21 — analyse Claude reçue 13:47 CEST**  
**Autorité produit : Fred**  
**Statut : AUDIT UNIQUEMENT — AUCUN RUNTIME MODIFIÉ**  
**Plan verrouillé : `ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**

## 0. Verdict

**VERDICT = MIX, avec priorité à l'état ZMOS/runtime courant pour l'architecture et aux vérifications GitHub de Claude pour les briques historiques/donneuses.**

Claude corrige utilement plusieurs faits GitHub. En revanche son périmètre A→H ne correspond pas à l'objectif final verrouillé : il omet BGE-M3/corpus large, voix, Internet hébergé E2E, identité K3 canonique, Amygdala réelle et la distinction runtime courant vs chaîne 00→11 historique.

Le chemin final ne devient donc ni « analyse Claude pure » ni « analyse ChatGPT pure ». Il garde l'architecture canonique K3/ZMOS, et incorpore les preuves GitHub de Claude là où elles améliorent l'inventaire.

## 1. Réponse immédiate à la question Amygdala

**Amygdala ≠ GLYPHNET.**

Preuve GitHub : `experiments/glyphnet/README.md` décrit GlyphNet comme un **canal structurel fermé** et précise explicitement qu'il est périphérique, non décisionnel et ne modifie jamais verdict/modalité/chiffre/CLAIM_SET.

Preuve ZMOS/File Library : `ZORAN_BRICKS_SYNC_REGISTRY_V9_2026-08-20.json` identifie séparément `AMYGDALA-V10-PING`, historiquement prouvé (`167/167 Node`, `54/54 Python`) mais non raccordé actuellement, avec source courante / isolation / purge encore NON_MESURÉES.

Conclusion : GlyphNet peut rester un donneur périphérique futur. Il n'entre pas dans le cœur nécessaire à finaliser Zoran.

## 2. Delta brique par brique

| Claim Claude | Audit 360° | Verdict |
|---|---|---|
| K3 Python existe, 12/12 | Confirmé. Branche `audit/frame-algebra-k3-v1`, HEAD `636f703...`, manifeste candidat 12/12 local PASS. | **PASS DONNEUR / IDENTITÉ À RÉCONCILIER** |
| K3 n'est branché nulle part | Vrai pour le candidat Python GitHub ; faux si généralisé au produit : le runtime courant ZMOS documente un K3 TypeScript actif. Trois identités K3 distinctes sont actuellement en conflit. | **CRITIQUE : P0 IDENTITÉ K3** |
| Semantic Decision 263 lignes, 12/12, consommé par 06 | Le composant 05B existe et 7+5 tests couvrent la couture. `run_semantic_request_build()` consomme 05B. Mais `main()` de 06 appelle encore le chemin historique `run_llm_request_build()`. Le 05B GitHub est en outre borné (intents `pourquoi`/`quel*`, causalité NON_MESURÉE). | **PARTIEL / DONNEUR CONTRACTUEL** |
| GLYPHNET = candidat Amygdala | Contredit par README GlyphNet et registre Amygdala V10. | **FAIL** |
| ZMOS très avancé | Confirmé structurellement. Repo direct `zmos-v2-transactional-bench` HEAD `112ee943...` avec transactional/reconstruction/bridge. Les `215/215` sont rapportés par Claude, non rejoués dans cet environnement. | **PASS SOURCE, TEST COUNT = RAPPORTÉ** |
| Pont ZMOS↔Zoran exécute encore 00→11 | Confirmé : `z3/zoran_bridge/bridge.py` exige exactement 00→11 et épingle `ZORAN_SOURCE_SHA=e7113ad...`. | **FAIT HISTORIQUE** |
| Il faut donc réparer Python 3.14 d'abord | Le contrat engine00 impose `<3.14`; donc Python 3.14 échoue SI on choisit ce pont historique. Mais le registre ZMOS courant classe 00→11 `ARCHIVE_INERTE_INTERDITE`, usages autorisés = intégrité/provenance/histoire, imports/exécution/design interdits. | **PAS LE PREMIER VERROU DU ZORAN FINAL** |
| UI 5 prises refuse localhost/IP/HTTP | Confirmé dans `lib/zoran-connector-gate.ts`: HTTPS uniquement, ni localhost/.local/IP, double certificat Claude+Codex et SHA release. | **PASS : VRAI VERROU UI v169** |
| UI ne parle à aucun Zoran | Vrai pour les cinq connecteurs gelés v169. Mais le runtime RC2 courant documente une UI locale déjà raccordée à sémantique→K3→mémoire. | **PARTIEL** |
| Seulement quatre trous | Faux pour l'objectif final : corpus/retrieval BGE-M3, identité K3, ZMOS canonique courant, voix, hosted Internet, Amygdala, semantic decision final et E2E restent ouverts. | **FAIL PÉRIMÈTRE** |
| 90 % sur A+B+C+D+E | La métrique 4 cases TEST/CODE/BRANCHÉ/EXÉC mesure la préparation technique, pas la cohérence avec l'objectif produit. Elle donne par exemple 75 % à GlyphNet alors que la brique n'est pas nécessaire au cœur final. | **NON COMPARABLE** |
| 4 sessions suffisent | Possible pour un assemblage étroit des briques GitHub historiques, pas pour l'objectif final comprendre/répondre/parler offline+online avec corpus large, mémoire, UI et E2E. | **TROP OPTIMISTE** |

## 3. Fait nouveau le plus important : conflit d'identité K3

La mémoire ZMOS la plus récente contient un blocker explicite :

`K3-CANONICAL-IDENTITY-RECONCILIATION-V91 = OPEN_CRITICAL_BLOCKING_THREE_DISTINCT_K3_IDENTITIES_CANONICAL_AUTHORITY_RECEIPT_REQUIRED`

Trois empreintes sont simultanément présentes :

1. candidat Python historique `865e6120…` ;
2. source TypeScript courante `e9d0d7cc…` ;
3. runtime K3 gouverné `8b8839f2…`.

**C'est le premier verrou causal.** Avant de brancher BGE, ZMOS canonique ou UI, il faut déterminer quelle identité K3 est l'autorité réellement exécutée, puis la figer et la relier à un reçu d'autorité. Sinon on peut assembler un système autour du mauvais K3.

Cette porte est une précondition de sécurité ; elle ne change pas l'architecture verrouillée.

## 4. Runtime courant réellement plus avancé que le GitHub historique

Les fichiers ZMOS du 20–21 août documentent un runtime local actuel distinct de la chaîne Python 00→11 :

`CURRENT-SEMANTIC-RUNTIME = RACCORDÉ_ACTIF_BORNÉ`

avec dépôt local `/workspace/sites/zoran-sessions-rc1`, HEAD rapporté `ff64bbb74ccb27e8798f50e062bfd0552f1d2fa1`.

NLP.js 4.26.1 MIT est déjà intégré derrière l'adaptateur borné : build PASS, runtime 17/17, sélection 50/50, formulations naturelles 10/10, hors corpus 50/50 NON_MESURÉ attendu, SQL 2/2. Les modèles intentions/faits sont hashés.

Une campagne plus récente rapporte également un runtime 55/55, SQL 2/2, build/lint PASS et des campagnes de langage déterministes ; ces preuves restent bornées à leurs artefacts et ne valent pas E2E final.

Conclusion : le meilleur point de départ produit n'est pas le pont historique 00→11 ; c'est **le runtime sémantique courant**, après réconciliation de son identité K3 et de son SHA exact.

## 5. BGE-M3 reste nécessaire

Claude ne traite pas BGE-M3. Or l'objectif final exige de dépasser le corpus borné actuel (dix faits dans le build NLP.js documenté).

BGE-M3 reste positionné **uniquement comme retrieval** :

`question → embedding/recherche → candidats ZMOS → K3`.

Il n'obtient jamais l'autorité de valider un fait ou un cadre. Sans une couche de retrieval/corpus large, le système peut comprendre la forme d'une question mais ne peut pas retrouver assez de connaissances hors du petit corpus local.

Donc BGE-M3/corpus/index reste une porte du plan final, mais **après le pré-gate d'identité K3**.

## 6. Internet : plus avancé que notre première cartographie

La mission active documente déjà un repli Internet borné : Wikipédia FR / Crossref / Zenodo, destinations fermées, redirections refusées, timeout 3,5 s, 1 Mo max, 3 sources max. Six cadres K3 sont produits pour connexion/identité/provenance/actualité/droits/contenu.

Preuves rapportées localement : build PASS, runtime 23/23, SQL 2/2, lint PASS, 50/50 requêtes simulées, anti-SSRF PASS, double rejeu déterministe, trois endpoints HTTP 200 depuis l'atelier.

Reste NON_MESURÉ : fetch depuis worker hébergé + conversation authentifiée + provenance visible + D1 reload/restart.

Conclusion : Internet n'est pas à construire de zéro ; il faut fermer son E2E hébergé.

## 7. Amygdala : état réel

État consolidé :

- historique V10 : preuves `167/167 Node PASS`, `54/54 Python PASS` ;
- actuel : non raccordé ; source physique courante / isolation de processus / purge réelle NON_MESURÉES ;
- contrôles plus récents nommés Amygdala V2 existent dans des campagnes bornées, mais ne prouvent pas la totalité du processus V10.

Donc : **récupérer/reconstituer à partir du contrat et des preuves historiques**, pas remplacer par GlyphNet.

## 8. Méthode de score corrigée

Le score de Claude est utile comme `READINESS_TECHNIQUE`, mais pas comme cohérence produit.

Pour le final, garder la mesure verrouillée par portes fonctionnelles :

- comprendre offline ;
- corpus/retrieval ;
- K3+décision ;
- ZMOS persistant ;
- répondre naturellement sans LLM ;
- écouter/parler ;
- Internet gouverné ;
- UI ;
- Amygdala ;
- E2E/QA.

Sur cette même grille, les nouvelles preuves font passer l'**état observé candidat** d'environ **62 % à ~69 % (±5)**, principalement grâce au runtime NLP.js déjà intégré, à l'Internet local borné et à la maturité ZMOS retrouvée.

Ce +7 est un **delta de connaissance/audit**, pas sept points de code écrits aujourd'hui. Le pourcentage canonique ne doit être promu qu'après liaison des artefacts au K3 canonique.

## 9. Chemin le plus pertinent — proposition après audit

Le plan structurel reste inchangé. Ajouter seulement un **pré-gate P0 de réconciliation d'identité**, puis reprendre l'ordre verrouillé :

```text
P0 — RÉCONCILIER K3 CANONIQUE
     TypeScript courant vs candidat Python vs runtime gouverné
     → choisir l'autorité réellement exécutée
     → SHA + reçu + replay

P1 — Geler le runtime courant RC2/NLP.js
     → SHA exact + artefacts + tests

P2 — BGE-M3 + corpus/index
     → retrieval uniquement
     → modèle/tokenizer/index SHA
     → tie-break déterministe + latence

P3 — ZMOS canonique
     → greffer transactional/reconstruction au runtime courant
     → NE PAS réactiver le pont 00→11 comme architecture

P4 — Sémantique structurée
     NLP.js + ZTRACE donneurs
     → cadres/relations
     → K3
     → Semantic Decision scellée
     → verbaliseur fermé

P5 — UI locale + voix
     → contourner/remplacer de manière auditée le contrat de connecteurs v169 inadapté au loopback
     → STT/TTS sans autorité sémantique

P6 — Internet hébergé E2E
     → authentification + fetch + provenance + mémoire/reload/restart

P7 — Amygdala
     → retrouver source/contrat historique ou reconstruction contrôlée
     → veto/freeze/rollback/purge

P8 — E2E final
     → offline + online + voix + mémoire + restart/rollback + questions humaines libres
     → gel SHA
```

### Ce qui est explicitement rejeté

- `Python 3.13 → old bridge 00→11` comme première route produit ;
- GlyphNet comme Amygdala ;
- Semantic Decision GitHub 05B comme moteur linguistique général ;
- BGE-M3 comme décideur ;
- score 90 % Claude comme taux d'achèvement du Zoran final ;
- quatre sessions comme garantie de fin.

## 10. Estimation sessions après réaudit

**Candidat révisé : 7 chats centraux, fourchette 6–9**, si les artefacts courants sont récupérables sans reconstruction lourde.

La réduction vs 10 chats vient de la redécouverte de travail déjà réalisé (NLP.js, runtime RC2, Internet local, ZMOS), pas d'une réduction du périmètre final.

## 11. Delta de ce chat

- Construction canonique avant promotion : **62 %**.
- Construction observée après réaudit : **~69 % ±5**.
- Delta d'observation : **+7 points**.
- Delta de code produit par ce chat : **+0 point**.
- Runtime modifié : **NON**.
- Plan structurel modifié : **NON**.
- Nouveau verrou prioritaire proposé : `K3_CANONICAL_IDENTITY_RECONCILIATION`.

## 12. Verdict terminal

`PASS_DELTA_AUDIT_WITH_CRITICAL_K3_IDENTITY_GATE`

Le chemin optimal est un **MIX** : conserver l'architecture ZMOS courante K3/NLP.js et le plan final verrouillé ; prendre les vérifications GitHub de Claude comme preuves/donneurs ; rejeter ses conclusions qui ramènent le système vers 00→11, GlyphNet-Amygdala ou un score 90 % hors périmètre.
