"""ZORAN reconstructive orchestrator — package ISOLÉ (hors moteurs 00-11).

Ce package implémente l'orchestrateur reconstructif transverse décrit dans
`specs/reconstructive/`. Il NE modifie AUCUN moteur 00-11 et NE touche PAS ZMOS :
les moteurs de cohérence 04/05/08 sont injectés comme dépendance (seam) et rendent
seuls le verdict d'admissibilité. Ce lot est un premier vertical slice documentaire
et exécutable du `FRAME_COHERENCE_ADMISSIBILITY_GATE`.

Périmètre de ce lot : cadre candidat -> évaluation 04/05/08 -> verdict explicite ->
intégration ou rejet fail-closed -> trace complète. Aucune généralisation multicadre.
"""

__version__ = "0.1.0-slice"
