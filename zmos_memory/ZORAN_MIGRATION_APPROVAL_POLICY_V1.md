# ZORAN — POLITIQUE D’AUTORISATION DE MIGRATION V1

**Horodatage : 2026-08-21T14:10:00+02:00**
**Autorité : Fred**
**Statut : VERROUILLÉ**

## Règle absolue

Le futur dépôt produit propre `Zoran-IA-deterministe` (nom exact à confirmer par Fred lors de la fourniture du dépôt) ne reçoit aucune brique par défaut.

Pour CHAQUE brique, composant, fichier, sous-module, corpus, index, modèle, test, configuration ou artefact candidat :

1. audit et lecture sont autorisés lorsque l’accès existe ;
2. recommandation / score / PASS technique ne valent JAMAIS autorisation de migration ;
3. aucune copie, aucun clonage, aucun cherry-pick, aucun import, aucun déplacement, aucune migration ni réécriture dans le nouveau dépôt ne peut être exécuté sans GO explicite de Fred pour CETTE brique ;
4. l’autorisation d’une brique ne vaut pas autorisation pour une autre ;
5. une autorisation générale implicite est interdite ;
6. avant tout transfert, annoncer exactement : composant, source repo/branche/SHA, destination proposée, tests, licence, S_OBJECTIF, delta attendu, risques ;
7. attendre ensuite le GO explicite de Fred ;
8. après transfert autorisé, enregistrer commit/SHA destination, tests et verdict PASS/FAIL/NON_MESURÉ.

## Invariant stable

`NO_COMPONENT_CLONE_COPY_IMPORT_MIGRATION_WITHOUT_FRED_EXPLICIT_PER_COMPONENT_GO`

## Séparation audit / action

`AUDIT_IS_NOT_AUTHORIZATION`
`RECOMMENDATION_IS_NOT_AUTHORIZATION`
`PASS_IS_NOT_AUTHORIZATION`
`ONE_COMPONENT_GO_DOES_NOT_AUTHORIZE_ANOTHER_COMPONENT`

## Accès GitHub / secrets

Les identifiants, jetons personnels et secrets ne doivent jamais être inscrits dans ZMOS, le canon, les logs, les commits ou les rapports. Utiliser un accès GitHub autorisé/connector lorsque disponible. Si un mécanisme d’authentification supplémentaire est requis, il doit être fourni via un canal de connexion prévu à cet effet et non persisté dans le dépôt.

## Effet sur le plan

Cette politique ne change pas l’architecture canonique ni le pourcentage de construction. Elle gouverne seulement la migration vers le dépôt propre final.
