# ZORAN — ÉTAT COURANT PERSISTANT

**Horodatage autoritaire : 2026-08-21T14:10:00+02:00**  
**Autorité : Fred**  
**Plan unique : `../ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**  
**Objet ZMOS : `ZORAN_FINAL_PLAN_V1.zmos.json`**  
**Tracker : `ZORAN_BUILD_TRACKER_V1.json`**  
**Registre briques : `ZORAN_COMPONENT_REGISTRY_V1.json`**  
**Politique migration : `ZORAN_MIGRATION_APPROVAL_POLICY_V1.md`**  
**Dernier audit 360° : `../reports/ZORAN_CLAUDE2_DELTA_360_AUDIT_20260821.md`**

## État pour reprise

- Construction canonique promue : **62 %**
- Construction observée après audits Claude + ZMOS : **~69 % ±5**
- Delta d'observation total depuis le verrouillage : **+7 points**
- Delta supplémentaire depuis Claude 2 : **+0 point promouvable**
- Delta de code produit : **+0 point**
- Plan structurel modifié : **NON**
- Runtime modifié : **NON**
- Verdict : `WAITING_FOR_CLEAN_REPOSITORY_WITH_PER_COMPONENT_MIGRATION_APPROVAL_LOCKED`

## Nouveau dépôt produit propre

Fred prépare un nouveau dépôt dédié à Zoran IA déterministe. Le nom exact du dépôt sera fourni par Fred lorsque créé.

Objectif : cesser de mélanger archives, donneurs et runtime final. Les anciens dépôts restent sources/provenance ; le nouveau dépôt devient la cible produit propre après migrations autorisées.

### Règle non négociable de migration

`NO_COMPONENT_CLONE_COPY_IMPORT_MIGRATION_WITHOUT_FRED_EXPLICIT_PER_COMPONENT_GO`

- Audit/lecture : autorisés si l'accès existe.
- Recommandation : n'autorise rien.
- PASS technique : n'autorise rien.
- Aucun clonage, copie, import, cherry-pick, déplacement ou migration sans GO explicite de Fred pour la brique concernée.
- Un GO sur une brique ne vaut jamais GO sur la suivante.
- Avant chaque migration proposée : annoncer source repo/branche/SHA, destination, tests, licence, S_OBJECTIF, delta attendu et risques ; attendre le GO de Fred.
- Aucun token/secret GitHub ne doit être persisté dans ZMOS, GitHub, logs ou rapports.

Politique complète : `ZORAN_MIGRATION_APPROVAL_POLICY_V1.md`.

## Conclusion Claude 1 + Claude 2 vs audit

**Chemin retenu = MIX sélectif, architecture canonique inchangée.**

À conserver de Claude : fraîcheur GitHub, K3 candidat 12/12, ZMOS direct très avancé, couture 05B→06 existante, piège réel du connector gate UI, contrainte Python <3.14 du pipeline historique, confirmation Amygdala != GlyphNet et confirmation UI de référence.

À ne pas promouvoir : 00→11 comme route produit, Python 3.13 comme premier verrou du Zoran final, score 90 % comme achèvement produit, garantie de fin en quatre sessions, `GLYPHNET = Amygdala`, et claim `71993b2 BGE-M3 prêt` tant que repo/branche/SHA/tests ne sont pas reliés.

## Verrou technique prioritaire à la reprise de construction

`K3_CANONICAL_IDENTITY_RECONCILIATION`

Trois identités K3 restent à réconcilier avant greffe fonctionnelle. Ce pré-gate ne change pas l'architecture.

## Architecture toujours verrouillée

`NLP.js/ZTRACE → BGE-M3 retrieval → corpus/ZMOS → cadres → K3 → cohérence → Semantic Decision → Amygdala → verbaliseur → voix/UI → ZMOS`

BGE-M3 reste retrieval uniquement. LLM reasoning/decision reste zéro. 00→11 reste historique/donneur uniquement.

## États importants

- NLP.js 4.26.1 MIT : borné et déjà avancé.
- ZMOS direct prioritaire : `Zoran-IA-Mimetique/zmos-v2-transactional-bench@112ee9439a36130b97176bc71f01cd1b8606a0a3`.
- UI référence : `Zoran-IA-Mimetique/ZORAN-UI-27-07-2026@721df5c21a6598c66dc3fb6b958e4c0171be0323`.
- Semantic Decision 05B : donneur de contrat/scellement, pas moteur linguistique final général.
- Amygdala : rôle canonique trouvé ; source exécutable courante NON_MESURÉE.
- BGE-M3/corpus/index : phase fonctionnelle suivante après le pré-gate K3.
- Hosted Internet E2E, voix finale et E2E unifié restent NON_MESURÉS.

## Chemin de reprise

1. recevoir de Fred le dépôt GitHub produit propre ;
2. vérifier l'accès en lecture ;
3. NE RIEN CLONER/MIGRER sans GO brique par brique ;
4. reprendre P0 identité K3 ;
5. proposer ensuite chaque migration individuellement avec preuves ;
6. continuer le plan canonique sans dérive.

Estimation candidate inchangée : **7 chats centraux, 6–9**.

## Reprise obligatoire

Lire : canon → objet ZMOS → tracker → registre → politique migration → ce CURRENT_STATE → derniers rapports 360°. Aucun transfert de brique sans GO explicite de Fred.
