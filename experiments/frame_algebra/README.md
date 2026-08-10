# ZORAN — Algèbre de cadres K3 v1.1 CANDIDATE

**Statut : expérimental, sous-opérateur du bloc B.**

## Décision d'audit

Le v1.0 était mathématiquement proche de K3 correcte, mais insuffisamment fermé
pour ZORAN : NaN/Inf, expressions ambiguës, mauvaises arités, ET/OU vides,
hash de certificat temporel et confusion avec la NEGATION sémantique.

La v1.1 corrige ces points.

## Ce que le module fait

Il combine des verdicts de cadres déjà produits :

- `NON`
- `ET`
- `OU`
- `IMPLIQUE` au sens vérité-fonctionnel K3
- `DIFFERENCE = A ∧ ¬B`

## Ce qu'il ne fait pas

- il ne découvre ni ne sélectionne les cadres ;
- il ne calcule pas S ;
- il ne prouve pas une causalité ;
- il ne remplace pas la polarité sémantique historique ;
- il ne prend aucune décision d'autorisation ou d'action.

## Point important sur NON_MESURÉ

K3 ne "transforme" jamais NON_MESURÉ en PASS ou FAIL, mais une formule peut être
déterminée malgré une branche inconnue :

- `PASS ∨ NON_MESURÉ = PASS`
- `FAIL ∧ NON_MESURÉ = FAIL`

Le certificat conserve donc la liste des cadres NON_MESURÉS utilisés.

Pour une politique exigeant que TOUS les cadres requis passent, le propriétaire
de la politique doit explicitement utiliser `ET` sur ces cadres.

## Placement V3

`B. Ω∞ COHERENCE CORE -> sous-opérateur ALGEBRE_CADRES_K3`.

La polarité `affirmation / négation / contradiction / absence de preuve` reste
dans A/B comme fonction distincte.
