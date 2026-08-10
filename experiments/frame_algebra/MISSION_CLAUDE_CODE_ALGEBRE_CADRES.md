# MISSION CLAUDE CODE — CONTRE-AUDIT ALGÈBRE DE CADRES K3 v1.1

## Objet

Contre-auditer le candidat `experiments/frame_algebra/` et décider s'il peut
être câblé comme **sous-opérateur du bloc B**, sans changer les contrats A/C/D/E/F.

## Interdits

- Ne pas présenter ce module comme remplacement complet de NEGATION/POLARITÉ.
- Ne pas utiliser `IMPLIQUE` comme preuve causale.
- Ne pas laisser une expression UI/utilisateur définir directement une politique d'autorisation.
- Ne pas toucher aux moteurs 03→05 historiques sans GO distinct.
- Aucun merge/déploiement.

## Contrôles obligatoires

1. Rejouer le falsificateur fourni.
2. Vérifier les tables K3 complètes pour NON/ET/OU.
3. Fuzzer schémas d'expression : zéro exception brute hors `AlgebreCadresError`.
4. NaN, ±Inf, bool, strings numériques : refus propre.
5. Vérifier que deux appels identiques donnent le même `empreinte_semantique_sha256`.
6. Vérifier que le hash artefact peut varier avec l'horodatage sans changer le hash sémantique.
7. Vérifier les cas `PASS∨NM=PASS` et `FAIL∧NM=FAIL` et que les dépendances NM restent tracées.
8. Vérifier que `cout_de_contrainte` distingue FAIL bloquant et NM critique.
9. Vérifier qu'aucune API n'autorise/exécute une action.
10. Vérifier que le registre de cadres en amont reste l'autorité : le module combine, il ne crée pas de cadre.

## Greffe autorisée si audit vert

Placement :
`B / Ω∞ -> frame_algebra_k3`

Entrée :
`{frame_id: PASS|FAIL|NON_MESURÉ}` + expression fermée gouvernée.

Sortie :
résultat K3 + dépendances + cadres NM utilisés + hash sémantique.

Le résultat ne devient jamais directement `ACTION_AUTHORIZED`.

## Verdict

- `APPROVED_FOR_B_SUBOPERATOR_WIRING`
- `FIX_REQUIRED`
- `BLOCKED_PRECONDITION`
- `BLOCKED_MAJOR`

Produire dépôt/branche/SHA, tests, diff, limites et preuve d'invariance des autres blocs.
