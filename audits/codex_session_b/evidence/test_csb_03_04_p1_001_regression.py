# MISSION_ID: TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1
# GUARD_IDS: TRACEABLE_RUNTIME, SHA_UNIQUE_AUDIT_V1, NO_PRODUCT_MUTATION_V1, CSB_03_04_P1_001_REPRO_V1
"""Ce test doit échouer sur 6d3f389 et passer uniquement après un vrai fail-closed."""

from audits.codex_session_b.evidence.repro_csb_03_04_p1_001 import (
    CANON_REGISTRY,
    ENVELOPE,
)
from zoran_v2.canon_determination import run_canon_determination


def test_04_blocks_malformed_pass_payload_from_03():
    observed = run_canon_determination(ENVELOPE, CANON_REGISTRY)

    assert observed["status"] == "BLOCKED"
    assert observed["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"
    assert observed["canons_selected"] == []
