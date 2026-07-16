"""SOCIAL_RECEIVABILITY_SATELLITE_V1 — CONTRAT FIGÉ (PLACEHOLDER, AUCUN RUNTIME).

Satellite de sociétabilité / adoption contextuelle. Mesure `wO` (réceptabilité sociale d'une
proposition dans une population à un instant), PAS une vérité. HORS `zoran_v2/` et HORS pipeline 00→11.

Ce module ne calcule RIEN. Il fige le contrat (constantes, clés de schéma, invariants) et laisse les
tests adversariaux T1–T12 rouges (xfail) jusqu'à un futur GO Fred de construction runtime.

INTERDITS (gravés) : calcul `wO` ici · import `zoran_v2/*` · écriture canonique · action automatique ·
filtre éliminatoire · influence sur S, le verdict ressource (05) ou les gates · inférence sans données.
Source de vérité : verdict Claude FEATURE-AUDIT (2026-07-16) + SPEC `CONTRACT.md`.
"""
from __future__ import annotations

COMPONENT_ID = "SOCIAL_RECEIVABILITY_SATELLITE"
VERSION = "1.0.0"

# Constante DURE : ce satellite n'émet jamais un signal de vérité.
IS_TRUTH_SIGNAL = False

# Statuts de sortie.
STATUS_MEASURED = "MEASURED"
STATUS_NON_MESURE = "NON_MESURE"   # fail-closed : données observées insuffisantes
STATUS_BLOCKED = "BLOCKED"         # entrée/provenance malformée ou falsifiée
STATUSES = frozenset((STATUS_MEASURED, STATUS_NON_MESURE, STATUS_BLOCKED))

# Contrat de données (schéma figé — cf SCHEMA.yaml).
INPUT_KEYS = frozenset((
    "proposition_ref", "t", "context", "population", "horizon", "observed_data",
))
OUTPUT_KEYS = frozenset((
    "status", "wO", "uncertainty_interval", "confidence", "provenance_refs",
    "trend", "counter_evidence", "is_truth_signal", "measured_from_sample_n", "as_of_t",
))

# Paramètre de contrat : taille d'échantillon minimale sous laquelle -> NON_MESURE.
N_MIN = 30

# Invariants gravés et rendus testables (mapping invariant -> test dans les tests de contrat).
INVARIANTS = (
    "NO_ENGINE_IMPORT",              # aucun moteur zoran_v2/* n'importe ce satellite
    "ONE_WAY_FLOW",                  # pipeline -> satellite uniquement ; ce module n'importe pas zoran_v2
    "SEPARATE_OUTPUT_OBJECT",        # OUTPUT_KEYS disjoint des sorties moteurs (05/09/10/11)
    "NO_S_INFLUENCE",                # wO n'entre jamais dans les entrées de 05 ni dans S
    "NO_GATE_INFLUENCE",            # aucune décision PASS/BLOCKED ni verdict ressource ne lit wO
    "NON_MESURE_FAIL_CLOSED",        # sans données suffisantes -> NON_MESURE
    "IS_TRUTH_SIGNAL_FALSE_CONST",   # is_truth_signal = False constant
    "COUNTER_EVIDENCE_MANDATORY",    # counter_evidence toujours présent
    "NO_CANONICAL_WRITE",            # aucune écriture canonique
    "NO_AUTO_ACTION",                # aucune action automatique
    "NO_ELIMINATORY_FILTER",         # jamais un filtre qui passe/supprime
    "NO_INFERENCE_WITHOUT_DATA",     # aucune inférence sans données observées
)


def run_social_receivability(*args, **kwargs):
    """PLACEHOLDER DE CONTRAT — n'implémente aucun calcul `wO`.

    Lève `NotImplementedError` : la construction runtime exige un GO Fred explicite APRÈS audit
    indépendant du présent contrat. C'est ce qui rend les tests comportementaux T1/T5–T12 rouges
    (xfail attendus et documentés)."""
    raise NotImplementedError(
        "SOCIAL_RECEIVABILITY runtime non construit : PR contrat + tests rouges uniquement "
        "(aucun calcul wO). Construction future = GO Fred explicite après audit du contrat."
    )
