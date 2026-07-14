"""Sonde de cycle — objet trivial et déterministe.

Unique but : prouver le cycle BASE_SHA → Codespace → commit → Actions → audit,
AVANT de construire le moteur. Ne contient aucune logique de raisonnement.
"""
from __future__ import annotations

import sys

CYCLE_PROBE_ID = "ZORAN-V2-CYCLE-PROBE"


def probe() -> dict:
    """Retourne un état déterministe (aucune horloge, aucun aléa)."""
    return {
        "probe_id": CYCLE_PROBE_ID,
        "ok": True,
        "python_major_minor": (sys.version_info.major, sys.version_info.minor),
        # Contrat moteur 00 : Python < 3.14 requis. Vrai en Codespaces (3.13).
        "py_lt_314": sys.version_info < (3, 14),
    }
