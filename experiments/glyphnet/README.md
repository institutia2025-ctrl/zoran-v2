# GlyphNet ZORAN — candidat de souveraineté structurelle

**Statut : EXPERIMENTAL / NON_MESURÉ — ne pas traiter comme chiffrement.**

## Rôle

GlyphNet est un **canal structurel fermé** pour des unités de type
`CLAIM / FACT / RELATION / UNCERTAINTY / ACTION`.

Il peut fournir une idiosyncrasie propre à une installation, mais **ce n'est pas
une primitive cryptographique**. TLS, chiffrement au repos, contrôle d'accès,
M7/C2 et isolation locale restent nécessaires.

## Gate

Le mode GlyphNet ne s'arme que si une **attestation de runtime local est
validée par un vérificateur injecté**. Un simple booléen transmis par l'appelant
n'est pas considéré comme une preuve.

## Limite majeure à ne pas masquer

Un LLM général ne connaît pas une bijection aléatoire propre à l'installation.
Pour que GlyphNet devienne réellement un canal `LLM <-> moteur`, il faut soit :

1. un modèle local entraîné/contraint sur ce dialecte ;
2. un adaptateur déterministe qui traduit avant/après le LLM.

Tant que cette étape n'est pas mesurée :

- gain tokens : **NON_MESURÉ** ;
- avantage de confidentialité : **NON_MESURÉ** ;
- bénéfice vs JSON/CBOR/MessagePack : **NON_MESURÉ**.

## Falsificateurs v1.1

- cloud/non-local refusé ;
- roundtrip structurel strict ;
- mauvais dialecte refusé ;
- dialectes distincts ;
- rotation archive réellement l'ancien dialecte ;
- polarité fermée ;
- schéma fermé ;
- flux tronqué refusé ;
- empreinte uniquement après parse strict.

## Placement V3

GlyphNet est **périphérique à D/E/F**, pas un moteur de décision.
Il ne modifie jamais un verdict, une modalité, un chiffre ou un `CLAIM_SET`.
