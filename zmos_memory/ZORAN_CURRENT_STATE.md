# ZORAN — ÉTAT COURANT PERSISTANT

**Horodatage autoritaire : 2026-08-21T13:47:00+02:00**  
**Autorité : Fred**  
**Plan unique : `../ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**  
**Objet ZMOS : `ZORAN_FINAL_PLAN_V1.zmos.json`**  
**Tracker : `ZORAN_BUILD_TRACKER_V1.json`**  
**Registre briques : `ZORAN_COMPONENT_REGISTRY_V1.json`**  
**Pause : `ZORAN_PAUSE_BEFORE_CLAUDE_DELTA_20260821.md`**  
**Dernier audit 360° : `../reports/ZORAN_CLAUDE_DELTA_360_AUDIT_20260821.md`**

## État pour reprise

- Construction canonique promue : **62 %**
- Construction observée après delta Claude + ZMOS : **~69 % ±5**
- Delta d'observation : **+7 points**
- Delta de code pendant ce chat : **+0 point**
- Plan structurel modifié : **NON**
- Runtime modifié : **NON**
- Verdict : `PASS_DELTA_AUDIT_WITH_CRITICAL_K3_IDENTITY_GATE`

## Conclusion Claude vs audit

**Chemin retenu = MIX.**

À conserver de Claude : fraîcheur GitHub, K3 candidat 12/12, ZMOS direct très avancé, couture 05B→06 existante, piège réel du connector gate UI, contrainte Python <3.14 du pipeline historique.

À rejeter : `GLYPHNET = Amygdala`, 00→11 comme route produit, Python 3.13 comme premier verrou du Zoran final, score 90 % comme achèvement produit, « seulement quatre trous », garantie de fin en quatre sessions.

## Verrou prioritaire découvert

`K3_CANONICAL_IDENTITY_RECONCILIATION`

La mémoire ZMOS récente signale trois identités K3 distinctes :

1. candidat Python historique `865e6120…` ;
2. source TypeScript courante `e9d0d7cc…` ;
3. runtime K3 gouverné `8b8839f2…`.

Avant toute greffe fonctionnelle, il faut déterminer l'identité réellement exécutée et lier SHA + autorité + replay. Ceci est un pré-gate de cohérence, pas un changement d'architecture.

## Architecture toujours verrouillée

`NLP.js/ZTRACE → BGE-M3 retrieval → corpus/ZMOS → cadres → K3 → cohérence → Semantic Decision → Amygdala → verbaliseur → voix/UI → ZMOS`

BGE-M3 reste retrieval uniquement. LLM reasoning/decision reste zéro. 00→11 reste historique/donneur uniquement.

## États importants retrouvés

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

Le connector gate v169 refuse localhost, `.local`, IP, HTTP et exige HTTPS + double certification. Le runtime local RC2 dispose néanmoins d'un raccord UI interne documenté. La jonction finale doit préserver le local sans réactiver l'ancien cœur.

### Amygdala

**Amygdala ≠ GlyphNet.** Amygdala V10 est historiquement prouvée mais source courante / raccord / purge réelle restent NON_MESURÉS. GlyphNet est périphérique et non décisionnel.

## Chemin proposé, en attente de reprise

P0 réconcilier l'identité K3 → P1 geler runtime courant → P2 BGE-M3/corpus/index → P3 ZMOS canonique sans 00→11 → P4 sémantique/scellement → P5 UI locale + voix → P6 Internet hosted E2E → P7 Amygdala → P8 E2E final.

Estimation révisée candidate : **7 chats centraux, 6–9**, non encore gravée comme nouvelle architecture.

## Reprise obligatoire

Lire : canon → objet ZMOS → tracker → registre → ce CURRENT_STATE → rapport delta Claude. Ne coder qu'après validation du verrou K3 et sans dérive du plan.
