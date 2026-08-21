# ZORAN — ÉTAT COURANT PERSISTANT

**Horodatage autoritaire : 2026-08-21T14:04:00+02:00**  
**Autorité : Fred**  
**Plan unique : `../ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**  
**Objet ZMOS : `ZORAN_FINAL_PLAN_V1.zmos.json`**  
**Tracker : `ZORAN_BUILD_TRACKER_V1.json`**  
**Registre briques : `ZORAN_COMPONENT_REGISTRY_V1.json`**  
**Pause : `ZORAN_PAUSE_BEFORE_CLAUDE_DELTA_20260821.md`**  
**Dernier audit 360° : `../reports/ZORAN_CLAUDE2_DELTA_360_AUDIT_20260821.md`**

## État pour reprise

- Construction canonique promue : **62 %**
- Construction observée après audits Claude + ZMOS : **~69 % ±5**
- Delta d'observation total depuis le verrouillage : **+7 points**
- Delta supplémentaire Claude 2 : **+0 point promouvable**
- Delta de code pendant ce chat : **+0 point**
- Plan structurel modifié : **NON**
- Runtime modifié : **NON**
- Verdict : `PASS_CLAUDE2_DELTA_WITH_NO_ARCHITECTURE_CHANGE_AND_BGE_DEPLOY_CLAIM_NON_MESURE`

## Conclusion Claude 1 + Claude 2 vs audit

**Chemin retenu = MIX sélectif, architecture canonique inchangée.**

À conserver de Claude : fraîcheur GitHub, K3 candidat 12/12, ZMOS direct très avancé, couture 05B→06 existante, piège réel du connector gate UI, contrainte Python <3.14 du pipeline historique, confirmation Amygdala != GlyphNet et confirmation UI de référence.

À rejeter / ne pas promouvoir : 00→11 comme route produit, Python 3.13 comme premier verrou du Zoran final, score 90 % comme achèvement produit, garantie de fin en quatre sessions, `GLYPHNET = Amygdala`, et claim `71993b2 BGE-M3 prêt` tant que repo/branche/SHA/tests ne sont pas reliés dans l'espace GitHub accessible.

## Verrou prioritaire

`K3_CANONICAL_IDENTITY_RECONCILIATION`

La mémoire ZMOS récente signale trois identités K3 distinctes :

1. candidat Python historique `865e6120…` ;
2. source TypeScript courante `e9d0d7cc…` ;
3. runtime K3 gouverné `8b8839f2…`.

Avant toute greffe fonctionnelle, il faut déterminer l'identité réellement exécutée et lier SHA + autorité + replay. Ceci est un pré-gate de cohérence, pas un changement d'architecture.

## Architecture toujours verrouillée

`NLP.js/ZTRACE → BGE-M3 retrieval → corpus/ZMOS → cadres → K3 → cohérence → Semantic Decision → Amygdala → verbaliseur → voix/UI → ZMOS`

BGE-M3 reste retrieval uniquement. LLM reasoning/decision reste zéro. 00→11 reste historique/donneur uniquement.

## États importants

### NLP.js

NLP.js 4.26.1 MIT est déjà prouvé localement de façon bornée : build PASS, runtime 17/17, sélection 50/50, français naturel 10/10, hors corpus 50/50 NON_MESURÉ, SQL 2/2. Le build documenté reste limité à dix faits gouvernés + mémoire.

### Runtime courant

Le registre ZMOS V9 classe `CURRENT-SEMANTIC-RUNTIME` comme `RACCORDÉ_ACTIF_BORNÉ`, repo local `/workspace/sites/zoran-sessions-rc1`, head rapporté `ff64bbb74ccb27e8798f50e062bfd0552f1d2fa1`.

### ZMOS

Repo direct prioritaire : `Zoran-IA-Mimetique/zmos-v2-transactional-bench@112ee9439a36130b97176bc71f01cd1b8606a0a3`.

Le pont historique qui exige 00→11 existe, mais le registre ZMOS courant classe `HISTORICAL-ENGINES-00-11` en `ARCHIVE_INERTE_INTERDITE` avec import/exécution/design interdits.

### Semantic Decision

Le 05B GitHub existe et possède une couture testée vers 06, mais le `main()` de 06 reste historique et le composant est linguistiquement borné. Il est donneur de contrat/scellement, pas moteur sémantique général final.

### Internet

Le chemin local borné Wikipédia FR / Crossref / Zenodo est déjà avancé. Hosted authenticated E2E reste NON_MESURÉ.

### UI

La référence canonique reste `Zoran-IA-Mimetique/ZORAN-UI-27-07-2026@721df5c21a6598c66dc3fb6b958e4c0171be0323`. Le connector gate v169 refuse localhost, `.local`, IP, HTTP et exige HTTPS + double certification. La jonction finale doit préserver le local sans réactiver l'ancien cœur.

### Amygdala

**Amygdala ≠ GlyphNet.** Son rôle canonique est bien : gardien après décision/cohérence et avant verbalisation, avec veto / freeze / rollback / refus. La source exécutable courante reste `NON_MESURÉE`. Dire « Amygdala trouvée » signifie ici que son contrat/rôle est retrouvé dans le canon, pas qu'un programme exécutable a été localisé.

L'effacement/oubli RGPD / AI Act n'est pas écrit dans le canon actuel. Ne pas l'ajouter sans GO explicite de Fred. La purge réelle reste NON_MESURÉE.

### BGE-M3

La phase reste active après le pré-gate K3. Claude 2 rapporte un déployé `71993b2` « BGE-M3 prêt », mais ce SHA n'est pas résolu dans les dépôts GitHub actuellement accessibles à cet audit. Statut : `NON_MESURE_FROM_CURRENT_GITHUB_ACCESS`. Aucun gain de pourcentage n'est promu sur ce claim seul.

## Chemin de reprise

P0 réconcilier l'identité K3 → P1 geler runtime courant → P2 BGE-M3/corpus/index → P3 ZMOS canonique sans 00→11 → P4 sémantique/scellement → P5 UI locale + voix → P6 Internet hosted E2E → P7 Amygdala → P8 E2E final.

Estimation candidate : **7 chats centraux, 6–9**, sans promotion d'une nouvelle architecture.

## Reprise obligatoire

Lire : canon → objet ZMOS → tracker → registre → ce CURRENT_STATE → derniers rapports 360°. Ne coder qu'après validation du verrou K3 et sans dérive du plan.
