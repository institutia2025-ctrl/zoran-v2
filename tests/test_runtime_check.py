"""Tests déterministes de 00_RUNTIME_CHECK (aucun LLM, aucun réseau, faits injectés)."""
import pytest

from zoran_v2.runtime_check import (
    COMPONENT_ID,
    FAIL,
    PASS,
    UNVERIFIED,
    VERSION,
    collect_facts,
    run_runtime_check,
)

GOOD = {
    "python_version_info": (3, 13, 14),
    "python_implementation": "CPython",
    "available_memory_bytes": 4 * 1024 ** 3,
    "free_disk_bytes": 10 * 1024 ** 3,
}


def test_pass_quand_tout_bon():
    v = run_runtime_check(GOOD)
    assert v["status"] == PASS
    assert v["first_failure"] is None
    assert v["component"] == COMPONENT_ID
    assert v["version"] == VERSION
    assert v["fail_closed"] is True
    assert [c["id"] for c in v["checks"]] == ["RC00", "RC01", "RC02", "RC03"]


def test_fail_python_trop_recent():
    v = run_runtime_check({**GOOD, "python_version_info": (3, 14, 0)})
    assert v["status"] == FAIL and v["first_failure"] == "RC00"


def test_fail_python_trop_ancien():
    v = run_runtime_check({**GOOD, "python_version_info": (3, 10, 0)})
    assert v["status"] == FAIL and v["first_failure"] == "RC00"


def test_fail_implementation_non_cpython():
    v = run_runtime_check({**GOOD, "python_implementation": "PyPy"})
    assert v["status"] == FAIL and v["first_failure"] == "RC01"


def test_fail_memoire_insuffisante():
    v = run_runtime_check({**GOOD, "available_memory_bytes": 1024})
    assert v["status"] == FAIL and v["first_failure"] == "RC02"


def test_fail_disque_insuffisant():
    v = run_runtime_check({**GOOD, "free_disk_bytes": 1024})
    assert v["status"] == FAIL and v["first_failure"] == "RC03"


def test_non_verifie_fait_absent_est_fail_closed():
    v = run_runtime_check({**GOOD, "available_memory_bytes": None})
    rc02 = next(c for c in v["checks"] if c["id"] == "RC02")
    assert rc02["status"] == UNVERIFIED
    assert v["status"] == FAIL and v["first_failure"] == "RC02"


def test_deterministe():
    assert run_runtime_check(GOOD) == run_runtime_check(GOOD)


def test_facts_invalides_leve_typeerror():
    with pytest.raises(TypeError):
        run_runtime_check(None)


def test_collect_facts_contrat_cles():
    f = collect_facts()
    assert set(f.keys()) == {
        "python_version_info",
        "python_implementation",
        "available_memory_bytes",
        "free_disk_bytes",
    }
    assert isinstance(f["python_version_info"], tuple)
