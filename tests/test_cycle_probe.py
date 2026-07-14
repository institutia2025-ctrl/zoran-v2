"""Test déterministe de la sonde de cycle (aucun LLM, aucune donnée réelle)."""
from zoran_v2._cycle_probe import CYCLE_PROBE_ID, probe


def test_probe_deterministe():
    a, b = probe(), probe()
    assert a == b
    assert a["probe_id"] == CYCLE_PROBE_ID
    assert a["ok"] is True


def test_probe_contrat_python():
    # En Codespaces (Python 3.13) le contrat moteur 00 (<3.14) est satisfait.
    assert probe()["py_lt_314"] is True
