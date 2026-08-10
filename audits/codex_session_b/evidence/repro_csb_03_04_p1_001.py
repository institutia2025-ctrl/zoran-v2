#!/usr/bin/env python3
# MISSION_ID: TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1
# GUARD_IDS: TRACEABLE_RUNTIME, SHA_UNIQUE_AUDIT_V1, NO_PRODUCT_MUTATION_V1, CSB_03_04_P1_001_REPRO_V1
"""Contre-exemple exécutable exact de CSB-03-04-P1-001 sur 6d3f389."""

from pathlib import Path
from pprint import pprint
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from zoran_v2.canon_determination import run_canon_determination


PAYLOAD_01 = {
    "status": "PASS",
    "objects": [
        {"object_key": "k", "kind": "code"},
    ],
}

PAYLOAD_02 = {
    "status": "PASS",
    "object_frame_map": [
        {"object_key": "k", "frames": ["CODE"]},
    ],
}

MALFORMED_PAYLOAD_03 = {
    "status": "PASS",
}

ENVELOPE = {
    "runtime_check": {"status": "PASS"},
    "object_discovery": PAYLOAD_01,
    "frame_selection": PAYLOAD_02,
    "operants_operes": MALFORMED_PAYLOAD_03,
}

CANON_REGISTRY = [
    {
        "id": "CANON",
        "applies_to_frames": ["CODE"],
        "applies_to_kinds": ["code"],
        "priority": 1,
    },
]


if __name__ == "__main__":
    pprint(run_canon_determination(ENVELOPE, CANON_REGISTRY), sort_dicts=False)
