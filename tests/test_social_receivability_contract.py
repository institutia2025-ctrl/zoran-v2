"""Tests de contrat + adversariaux T1–T12 du satellite SOCIAL_RECEIVABILITY_SATELLITE_V1.

Deux familles (cf BOUNDARIES.md) :
- ISOLATION (VERTS, déjà valides) : T2 NO_ENGINE_IMPORT · ONE_WAY_FLOW · T3 NO_S_INFLUENCE ·
  T4 NO_GATE_INFLUENCE · T9 SEPARATE_OUTPUT_OBJECT · is_truth_signal constant · emplacement hors zoran_v2.
- COMPORTEMENT (ROUGES attendus, xfail strict) : T1, T5, T6, T7, T8, T10, T11, T12 — démontrent l'ABSENCE
  d'implémentation runtime `wO` (aucun calcul construit). Deviennent verts au futur GO Fred de construction.

Mapping invariant -> test en fin de fichier.
"""
import pathlib

import pytest

from satellites.social_receivability.contract import (
    COMPONENT_ID,
    INPUT_KEYS,
    INVARIANTS,
    IS_TRUTH_SIGNAL,
    N_MIN,
    OUTPUT_KEYS,
    STATUS_NON_MESURE,
    run_social_receivability as RUN,
)

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_ENGINES = [
    "runtime_check", "object_discovery", "frame_selection", "operants_operes_analysis",
    "canon_determination", "coherence_engine", "llm_request_build", "llm_execution",
    "coherence_2", "structured_decision", "action_admissibility_and_plan", "trace_and_close",
]


def _engine_sources():
    out = {}
    for name in _ENGINES:
        p = _ROOT / "zoran_v2" / f"{name}.py"
        if p.exists():
            out[name] = p.read_text(encoding="utf-8")
    return out


def _data(sample_n=100):
    return {"proposition_ref": "x-1", "t": "2026-07-16T00:00:00Z", "context": "c1",
            "population": {"id": "P1", "size": 1000}, "horizon": "H1",
            "observed_data": [{"value": 0.8, "provenance_ref": "prov://o/1",
                               "timestamp": "2026-07-16T00:00:00Z", "sample_n": sample_n}]}


# ---------- ISOLATION (VERTS) ----------

def test_isolation_T2_no_engine_import():
    """T2 NO_ENGINE_IMPORT : aucun moteur zoran_v2/* ne référence le satellite."""
    for name, src in _engine_sources().items():
        assert "social_receiv" not in src.lower(), name
        assert "satellites" not in src, name


def test_isolation_one_way_flow_contract_imports_no_engine():
    """ONE_WAY_FLOW : contract.py n'importe aucun zoran_v2/*."""
    src = (_ROOT / "satellites" / "social_receivability" / "contract.py").read_text(encoding="utf-8")
    import_lines = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    assert all("zoran_v2" not in ln for ln in import_lines), import_lines


def test_isolation_T3_no_s_influence():
    """T3 NO_S_INFLUENCE : le moteur 05 (S) ne référence ni wO ni le satellite."""
    src = _engine_sources().get("coherence_engine", "")
    low = src.lower()
    assert "social_receiv" not in low and "\"wo\"" not in low and "receivab" not in low


def test_isolation_T4_no_gate_influence():
    """T4 NO_GATE_INFLUENCE : moteurs de décision/gate (09/10/11) sans référence wO/satellite."""
    for name in ("structured_decision", "action_admissibility_and_plan", "trace_and_close", "coherence_2"):
        src = _engine_sources().get(name, "").lower()
        assert "social_receiv" not in src and "receivab" not in src, name


def test_isolation_T9_separate_output_object():
    """T9 SEPARATE_OUTPUT_OBJECT : OUTPUT_KEYS disjoint des termes de sortie/vérité des moteurs."""
    engine_truth_terms = {"S", "delta_phi", "verdict", "decision_id", "close_status",
                          "action_status", "resource", "coherence"}
    assert OUTPUT_KEYS.isdisjoint(engine_truth_terms)
    # wO et is_truth_signal ne doivent apparaître dans aucune sortie moteur (source).
    for name, src in _engine_sources().items():
        assert "is_truth_signal" not in src, name


def test_is_truth_signal_false_constant():
    assert IS_TRUTH_SIGNAL is False
    assert "is_truth_signal" in OUTPUT_KEYS


def test_location_outside_zoran_v2():
    assert (_ROOT / "satellites" / "social_receivability" / "contract.py").exists()
    assert not (_ROOT / "zoran_v2" / "social_receivability.py").exists()
    assert COMPONENT_ID == "SOCIAL_RECEIVABILITY_SATELLITE"


def test_invariants_engraved():
    for inv in ("NO_ENGINE_IMPORT", "ONE_WAY_FLOW", "SEPARATE_OUTPUT_OBJECT", "NO_S_INFLUENCE",
                "NO_GATE_INFLUENCE", "NON_MESURE_FAIL_CLOSED", "IS_TRUTH_SIGNAL_FALSE_CONST",
                "COUNTER_EVIDENCE_MANDATORY", "NO_CANONICAL_WRITE", "NO_AUTO_ACTION",
                "NO_ELIMINATORY_FILTER", "NO_INFERENCE_WITHOUT_DATA"):
        assert inv in INVARIANTS
    assert INPUT_KEYS and N_MIN == 30


# ---------- COMPORTEMENT (ROUGES attendus — xfail strict, runtime non construit) ----------

@pytest.mark.xfail(strict=True, reason="T1 runtime wO non construit (contract-red)")
def test_T1_non_mesure_without_data():
    """T1 : sans données observées -> NON_MESURE (jamais d'inférence)."""
    env = _data(); env["observed_data"] = []
    assert RUN(env)["status"] == STATUS_NON_MESURE


@pytest.mark.xfail(strict=True, reason="T5 runtime wO non construit (contract-red)")
def test_T5_majority_bias_not_truth():
    """T5 : forte adoption mais incohérente -> wO élevé MAIS is_truth_signal:false + counter_evidence présent."""
    v = RUN(_data())
    assert v["is_truth_signal"] is False and v["counter_evidence"] != []


@pytest.mark.xfail(strict=True, reason="T6 runtime wO non construit (contract-red)")
def test_T6_falsified_provenance_blocked():
    """T6 : provenance falsifiée -> NON_MESURE/BLOCKED, jamais un wO."""
    env = _data(); env["observed_data"][0]["provenance_ref"] = ""
    assert RUN(env)["status"] in ("NON_MESURE", "BLOCKED")


@pytest.mark.xfail(strict=True, reason="T7 runtime wO non construit (contract-red)")
def test_T7_population_or_sample_insufficient():
    """T7 : population indéfinie / sample_n < N_MIN -> NON_MESURE."""
    assert RUN(_data(sample_n=N_MIN - 1))["status"] == STATUS_NON_MESURE


@pytest.mark.xfail(strict=True, reason="T8 runtime wO non construit (contract-red)")
def test_T8_horizon_beyond_data():
    """T8 : horizon hors données -> NON_MESURE (pas d'extrapolation)."""
    env = _data(); env["horizon"] = "H_BEYOND"
    assert RUN(env)["status"] == STATUS_NON_MESURE


@pytest.mark.xfail(strict=True, reason="T10 runtime wO non construit (contract-red)")
def test_T10_no_automatic_action():
    """T10 : aucune action automatique déclenchée par wO (sortie advisory seule)."""
    v = RUN(_data())
    assert "action" not in v and set(v.keys()) <= OUTPUT_KEYS


@pytest.mark.xfail(strict=True, reason="T11 runtime wO non construit (contract-red)")
def test_T11_staleness_lowers_or_non_mesure():
    """T11 : fraîcheur dépassée -> NON_MESURE ou confiance abaissée + drapeau."""
    env = _data(); env["observed_data"][0]["timestamp"] = "2000-01-01T00:00:00Z"
    v = RUN(env)
    assert v["status"] == STATUS_NON_MESURE or v["confidence"] < 0.5


@pytest.mark.xfail(strict=True, reason="T12 runtime wO non construit (contract-red)")
def test_T12_anti_drift_no_state_mutation():
    """T12 : runs répétés ne mutent aucun état influençant un futur S (déterminisme, aucun feedback)."""
    a = RUN(_data()); b = RUN(_data())
    assert a == b


# ---------- MAPPING INVARIANT -> TEST ----------
# NO_ENGINE_IMPORT              -> test_isolation_T2_no_engine_import (GREEN)
# ONE_WAY_FLOW                  -> test_isolation_one_way_flow_contract_imports_no_engine (GREEN)
# NO_S_INFLUENCE                -> test_isolation_T3_no_s_influence (GREEN)
# NO_GATE_INFLUENCE             -> test_isolation_T4_no_gate_influence (GREEN)
# SEPARATE_OUTPUT_OBJECT        -> test_isolation_T9_separate_output_object (GREEN)
# IS_TRUTH_SIGNAL_FALSE_CONST   -> test_is_truth_signal_false_constant (GREEN)
# (emplacement hors zoran_v2)   -> test_location_outside_zoran_v2 (GREEN)
# (invariants gravés)           -> test_invariants_engraved (GREEN)
# NON_MESURE_FAIL_CLOSED        -> T1/T7/T8/T11 (RED xfail)
# NO_INFERENCE_WITHOUT_DATA     -> T1 (RED xfail)
# COUNTER_EVIDENCE_MANDATORY    -> T5 (RED xfail)
# (biais majoritaire)           -> T5 (RED xfail)
# (provenance falsifiée)        -> T6 (RED xfail)
# NO_AUTO_ACTION                -> T10 (RED xfail)
# (anti-dérive normative)       -> T12 (RED xfail)
