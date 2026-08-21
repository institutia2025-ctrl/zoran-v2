# ZORAN — ÉTAT COURANT PERSISTANT

**Horodatage autoritaire : 2026-08-21T14:56:00+02:00**  
**Autorité : Fred**  
**Plan unique : `../ZORAN_FINAL_CONSTRUCTION_CANON_V1.md`**  
**Objet ZMOS : `ZORAN_FINAL_PLAN_V1.zmos.json`**  
**Tracker : `ZORAN_BUILD_TRACKER_V1.json`**  
**Registre briques : `ZORAN_COMPONENT_REGISTRY_V1.json`**  
**Politique migration : `ZORAN_MIGRATION_APPROVAL_POLICY_V1.md`**

## État pour reprise

- Construction canonique promue : **62 %**
- Construction observée : **~69 % ±5**
- Delta de code produit : **+0 point**
- Plan structurel modifié : **NON**
- Runtime modifié : **NON**
- Nouveau dépôt produit : **créé et visible publiquement**
- Écriture depuis le connecteur ChatGPT : **NON DISPONIBLE À CET INSTANT**

## Nouveau dépôt produit propre

Dépôt actuellement visible par l'API GitHub :

`zorania2025/Zoran-IA-deteriniste`

Le nom doit encore être corrigé en `Zoran-IA-deterministe` avant migration fonctionnelle.

### État d'accès

- Invitation de collaboration donnée par Fred à `institutia2025-ctrl` : **déclarée acceptée côté UI GitHub**.
- Le connecteur GitHub utilisé ici est authentifié sur `institutia2025-ctrl`.
- Le dépôt n'apparaît pas dans les installations GitHub App accessibles au connecteur.
- `list_installed_accounts` ne contient actuellement que `Zoran-IA-Mimetique` et `institutia2025-ctrl`.
- Le dépôt `zorania2025/Zoran-IA-deteriniste` reste visible publiquement, mais les droits API du connecteur restent `push=false` / permission non accessible.
- Conclusion : **le GitHub App/connector doit être installé ou autorisé sur le compte `zorania2025` ou explicitement sur ce dépôt** avant toute écriture depuis ChatGPT.

## Règle absolue de migration

`NO_COMPONENT_CLONE_COPY_IMPORT_MIGRATION_WITHOUT_FRED_EXPLICIT_PER_COMPONENT_GO`

Aucun clone, copie, import, cherry-pick, déplacement ou migration sans GO explicite de Fred pour la brique précise.

## Architecture canonique inchangée

`NLP.js/ZTRACE → BGE-M3 retrieval → corpus/ZMOS → cadres → K3 → cohérence → Semantic Decision → Amygdala → verbaliseur → voix/UI → ZMOS`

## Verrou technique prioritaire après ouverture écriture

`K3_CANONICAL_IDENTITY_RECONCILIATION`

Trois identités K3 restent à réconcilier avant toute greffe fonctionnelle.

## Reprise obligatoire

1. ouvrir l'accès GitHub App/connector au dépôt `zorania2025/Zoran-IA-deteriniste` ;
2. vérifier l'écriture réelle ;
3. corriger le nom du dépôt si possible via les outils disponibles, sinon demander à Fred de le faire dans GitHub ;
4. ne migrer aucune brique sans GO explicite ;
5. reprendre P0 identité K3.
