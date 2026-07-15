"""Tests déterministes de 11_TRACE_AND_CLOSE (enveloppe 00→10 + résultat d'exécution / décision humaine injectés).

Vérifie : gate 00→10, REPLAY EXACT de 09 (depuis 00→08) et de 10 (depuis 00→09 + catalogue + permissions +
impact_context) AVANT toute lecture des entrées de clôture, 10 statuts de clôture, résultat d'exécution/décision
humaine falsifiés/incomplets/hors-scope → BLOCKED, absence d'exécution = cas nominal, appariement de scope EXACT,
anti-fuite/surrogate, closure_id (contexte complet, via _fingerprint) + CONTENT_SHA256, objet plat 21 clés, fail-closed.
"""
import copy

import pytest

from zoran_v2.structured_decision import _canonical_sha256, run_structured_decision
from zoran_v2.action_admissibility_and_plan import run_action_admissibility_and_plan
from zoran_v2.trace_and_close import (
    ACTION_10_REPLAY_MISMATCH,
    BLOCKED,
    CI_REFS_MALFORMED,
    CLOSED_ANOMALY,
    CLOSED_APPROVED_NOT_EXECUTED,
    CLOSED_AT_MALFORMED,
    CLOSED_AWAITING_HUMAN_APPROVAL,
    CLOSED_BLOCKED,
    CLOSED_EXECUTED_FAILED,
    CLOSED_EXECUTED_SUCCESS,
    CLOSED_HUMAN_DECLINED,
    CLOSED_NO_ACTION,
    CLOSED_PLAN_READY_NOT_EXECUTED,
    CLOSED_QUARANTINED,
    DECISION_09_REPLAY_MISMATCH,
    EXEC_INCONSISTENT,
    EXEC_MALFORMED,
    EXEC_PROVENANCE,
    EXEC_UNEXPECTED,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    HUMAN_MALFORMED,
    HUMAN_SCOPE_MISMATCH,
    HUMAN_UNEXPECTED,
    LEAK,
    NON_SCALAR_UNICODE,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    PROVENANCE_MALFORMED,
    UPSTREAM_NOT_PASS,
    run_trace_and_close as RUN,
)


def _code(v):
    return (v["blocked_by"] or "").split("@")[0]


def _catalog():
    return {"version": "1.0.0", "actions": [
        {"id": "ACTION_NONE", "requires_action": False, "sensitive_mutation": False, "permissions_required": []},
        {"id": "ACTION_ANNOTATE", "requires_action": True, "sensitive_mutation": False, "permissions_required": []},
        {"id": "ACTION_REPORT", "requires_action": True, "sensitive_mutation": False, "permissions_required": ["PERM_REPORT"]},
        {"id": "ACTION_APPLY_PATCH", "requires_action": True, "sensitive_mutation": True, "permissions_required": ["PERM_WRITE"]},
    ]}


def _permissions(granted=None):
    return {"version": "1.0.0", "granted": granted if granted is not None else ["PERM_WRITE", "PERM_REPORT"]}


def _full_env(action_id="ACTION_ANNOTATE", target_refs=None, assessed=None, granted=None, authority_env=None):
    from tests.test_structured_decision import _env as _env_09

    base = copy.deepcopy(authority_env) if authority_env is not None else _env_09()
    base["structured_decision"] = run_structured_decision(base)
    base["action_request"] = {"action_id": action_id,
                              "target_refs": target_refs if target_refs is not None else [["OBJ-0001", "CODE"]]}
    base["impact_context"] = {"assessed_target_refs": assessed if assessed is not None else [["OBJ-0001", "CODE"]],
                              "global_impact": "impact faible", "risks": ["r1"]}
    perms = _permissions(granted)
    base["permissions"] = perms
    base["action_admissibility_and_plan"] = run_action_admissibility_and_plan(base, _catalog(), perms)
    return base


def _plan(env):
    return env["action_admissibility_and_plan"]


def _exec_result(plan, status="SUCCESS", anomalies=None, **over):
    obj = {
        "execution_result_id": "EXR-1",
        "action_plan_id": plan["action_plan_id"], "action_id": plan["action_id"],
        "target_refs": plan["target_refs"], "executor_id": "EXECUTOR-1",
        "execution_status": status, "started_at_context": "t0", "completed_at_context": "t1",
        "effects": [], "anomalies": anomalies if anomalies is not None else [],
        "rollback_available": True, "provenance_refs": ["prov://exec/1"], "CONTENT_SHA256": None,
    }
    obj.update(over)
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _human(plan, decision="APPROVED", **over):
    obj = {
        "human_decision_id": "HD-1", "action_plan_id": plan["action_plan_id"], "action_id": plan["action_id"],
        "target_refs": plan["target_refs"], "approval_scope": plan["approval_scope"], "decision": decision,
        "identity_ref": "user://fred", "decided_at_context": "th", "provenance_refs": ["prov://human/1"],
        "CONTENT_SHA256": None,
    }
    obj.update(over)
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _close(env, **kw):
    kw.setdefault("provenance_refs", ["prov://close/1"])
    kw.setdefault("ci_refs", ["ci://run/1"])
    kw.setdefault("closed_at_context", "2026-07-15T00:00:00Z")
    return RUN(env, _catalog(), env["permissions"], **kw)


# ---------- schéma & statuts de clôture nominaux ----------

def test_output_schema_plat_21_cles():
    assert tuple(_close(_full_env()).keys()) == OUTPUT_KEYS
    bad = _full_env(); bad["structured_decision"] = {**bad["structured_decision"], "status": "BLOCKED"}
    assert tuple(_close(bad).keys()) == OUTPUT_KEYS  # BLOCKED : même schéma
    assert _close(_full_env())["order_key"] == ORDER_KEY
    assert len(OUTPUT_KEYS) == 21


def test_close_no_action():
    v = _close(_full_env(action_id="ACTION_NONE"))
    assert v["status"] == PASS and v["close_status"] == CLOSED_NO_ACTION
    assert v["closure_id"].startswith("ACTION-CLOSE-") and len(v["closure_id"]) == len("ACTION-CLOSE-") + 64


def test_close_blocked():
    v = _close(_full_env(action_id="ACTION_REPORT", granted=[]))
    assert v["status"] == PASS and v["close_status"] == CLOSED_BLOCKED


def test_close_quarantined():
    v = _close(_full_env(action_id="ACTION_ANNOTATE", assessed=[]))
    assert v["status"] == PASS and v["close_status"] == CLOSED_QUARANTINED
    assert "REVIEW_GLOBAL_IMPACT" in v["resumption_conditions"]


def test_close_plan_ready_not_executed():
    v = _close(_full_env(action_id="ACTION_ANNOTATE"))
    assert v["close_status"] == CLOSED_PLAN_READY_NOT_EXECUTED
    assert "AWAITING_EXECUTOR_RESULT" in v["resumption_conditions"]


def test_close_awaiting_human_approval():
    v = _close(_full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"]))
    assert v["close_status"] == CLOSED_AWAITING_HUMAN_APPROVAL
    assert "AWAITING_HUMAN_GO" in v["resumption_conditions"]


def test_close_human_declined():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    v = _close(env, human_decision=_human(_plan(env), decision="DECLINED"))
    assert v["close_status"] == CLOSED_HUMAN_DECLINED


def test_close_approved_not_executed():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    v = _close(env, human_decision=_human(_plan(env), decision="APPROVED"))
    assert v["close_status"] == CLOSED_APPROVED_NOT_EXECUTED


def test_close_executed_success_plan_ready():
    env = _full_env(action_id="ACTION_ANNOTATE")
    v = _close(env, execution_result=_exec_result(_plan(env), status="SUCCESS"))
    assert v["close_status"] == CLOSED_EXECUTED_SUCCESS
    assert v["execution_result_ref"] is not None


def test_close_executed_success_sensitive_after_go():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    v = _close(env, human_decision=_human(_plan(env), "APPROVED"),
               execution_result=_exec_result(_plan(env), "SUCCESS"))
    assert v["close_status"] == CLOSED_EXECUTED_SUCCESS
    assert v["human_decision_ref"] is not None and v["execution_result_ref"] is not None


def test_close_executed_failed():
    env = _full_env(action_id="ACTION_ANNOTATE")
    v = _close(env, execution_result=_exec_result(_plan(env), status="FAILED"))
    assert v["close_status"] == CLOSED_EXECUTED_FAILED


def test_close_anomaly_partial():
    env = _full_env(action_id="ACTION_ANNOTATE")
    v = _close(env, execution_result=_exec_result(_plan(env), status="PARTIAL"))
    assert v["close_status"] == CLOSED_ANOMALY


def test_close_anomaly_success_with_documented_anomalies():
    env = _full_env(action_id="ACTION_ANNOTATE")
    v = _close(env, execution_result=_exec_result(_plan(env), status="SUCCESS", anomalies=["latence"]))
    assert v["close_status"] == CLOSED_ANOMALY and "latence" in v["anomalies"]


# ---------- contre-exemples DURS (→ BLOCKED) ----------

def test_CE_upstream_not_pass():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"), ("coherence_2", "08_COHERENCE_2"),
                      ("action_admissibility_and_plan", "10_ACTION_ADMISSIBILITY_AND_PLAN")):
        env = _full_env(); env[key] = {**env[key], "status": "BLOCKED"}
        v = _close(env)
        assert v["status"] == BLOCKED and _code(v) == UPSTREAM_NOT_PASS and v["blocked_by"].endswith("@" + comp), comp


def test_CE_09_replay_mismatch():
    env = _full_env()
    forged = dict(env["structured_decision"])
    forged["targets"] = [{"object_public_id": "OBJ-9999", "frame": "CODE"}]
    forged["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    env["structured_decision"] = forged
    assert _code(_close(env)) == DECISION_09_REPLAY_MISMATCH


def test_CE_10_replay_mismatch():
    env = _full_env()
    forged = dict(env["action_admissibility_and_plan"])
    forged["action_status"] = "ACTION_NOT_REQUIRED"
    forged["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    env["action_admissibility_and_plan"] = forged
    assert _code(_close(env)) == ACTION_10_REPLAY_MISMATCH


def test_CE_replay_avant_lecture_entrees_cloture():
    class Exploding(dict):
        def __getitem__(self, k):
            raise AssertionError("entrée de clôture lue avant replay 09/10")
        def items(self):
            raise AssertionError("entrée de clôture lue avant replay 09/10")

    env = _full_env()
    forged = dict(env["structured_decision"])
    forged["decision_id"] = "DECISION-" + "e" * 64
    forged["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    env["structured_decision"] = forged
    out = RUN(env, _catalog(), env["permissions"], execution_result=Exploding(), human_decision=Exploding(),
              provenance_refs=Exploding(), ci_refs=Exploding(), closed_at_context="t")
    assert out["status"] == BLOCKED and _code(out) == DECISION_09_REPLAY_MISMATCH


def test_CE_exec_malforme():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env)); del er["executor_id"]
    assert _code(_close(env, execution_result=er)) == EXEC_MALFORMED


@pytest.mark.parametrize(("field", "bad"), [
    ("execution_result_id", ""), ("execution_result_id", None), ("execution_result_id", 1),
    ("started_at_context", ""), ("started_at_context", None), ("started_at_context", 1),
    ("completed_at_context", ""), ("completed_at_context", None), ("completed_at_context", 1),
    ("effects", ""), ("effects", None), ("effects", {}),
    ("anomalies", ""), ("anomalies", None), ("anomalies", {}),
    ("anomalies", [""]), ("anomalies", [None]), ("anomalies", [1]),
    ("executor_id", ""), ("executor_id", None), ("executor_id", 1),
    ("provenance_refs", []), ("provenance_refs", None), ("provenance_refs", "prov"),
    ("provenance_refs", [""]), ("provenance_refs", [None]), ("provenance_refs", [1]),
    ("execution_status", ""), ("execution_status", None), ("execution_status", 1),
    ("rollback_available", None), ("rollback_available", 0), ("rollback_available", 1),
    ("rollback_available", "true"),
    ("action_plan_id", ""), ("action_plan_id", None), ("action_plan_id", 1),
    ("action_id", ""), ("action_id", None), ("action_id", 1),
    ("target_refs", []), ("target_refs", None), ("target_refs", "target"),
])
def test_CE_exec_champ_obligatoire_incomplet_bloque(field, bad):
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env))
    er[field] = bad
    er["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in er.items() if k != "CONTENT_SHA256"})

    out = _close(env, execution_result=er)

    assert out["status"] == BLOCKED
    assert out["closure_id"] is None


@pytest.mark.parametrize("bad", ["", None, 1])
def test_CE_exec_content_sha256_incomplet_bloque(bad):
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env))
    er["CONTENT_SHA256"] = bad
    out = _close(env, execution_result=er)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_exec_content_sha256_falsifie():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env)); er["executor_id"] = "TAMPERED"  # CONTENT_SHA256 devient obsolète
    assert _code(_close(env, execution_result=er)) == EXEC_PROVENANCE


def test_CE_exec_incoherent_action_id():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env), action_id="ACTION_OTHER")
    er["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in er.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env, execution_result=er)) == EXEC_INCONSISTENT


def test_CE_exec_incoherent_target_refs():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env), target_refs=[["OBJ-9999", "CODE"]])
    er["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in er.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env, execution_result=er)) == EXEC_INCONSISTENT


def test_CE_exec_status_hors_enum():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env), status="WHATEVER")
    er["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in er.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env, execution_result=er)) == EXEC_MALFORMED


def test_CE_exec_inattendu_sans_plan():
    env = _full_env(action_id="ACTION_NONE")
    # plan ACTION_NONE : action_plan_id None -> résultat d'exécution non attendu
    er = _exec_result({"action_plan_id": None, "action_id": "ACTION_NONE", "target_refs": [["OBJ-0001", "CODE"]]})
    assert _code(_close(env, execution_result=er)) == EXEC_UNEXPECTED


def test_CE_exec_sans_go_sur_mutation_sensible():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    er = _exec_result(_plan(env), status="SUCCESS")
    # exécution présente MAIS aucune décision humaine -> illégitime
    assert _code(_close(env, execution_result=er)) == EXEC_UNEXPECTED


def test_CE_exec_apres_refus():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    er = _exec_result(_plan(env), status="SUCCESS")
    assert _code(_close(env, human_decision=_human(_plan(env), "DECLINED"),
                        execution_result=er)) == EXEC_UNEXPECTED


def test_CE_human_malforme():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env)); del hd["identity_ref"]
    assert _code(_close(env, human_decision=hd)) == HUMAN_MALFORMED


@pytest.mark.parametrize(("field", "bad"), [
    ("human_decision_id", ""), ("human_decision_id", None), ("human_decision_id", 1),
    ("identity_ref", ""), ("identity_ref", None), ("identity_ref", 1),
    ("decided_at_context", ""), ("decided_at_context", None), ("decided_at_context", 1),
    ("provenance_refs", []), ("provenance_refs", None), ("provenance_refs", "prov"),
    ("provenance_refs", [""]), ("provenance_refs", [None]), ("provenance_refs", [1]),
    ("decision", ""), ("decision", None), ("decision", 1),
    ("action_plan_id", ""), ("action_plan_id", None), ("action_plan_id", 1),
    ("action_id", ""), ("action_id", None), ("action_id", 1),
    ("target_refs", []), ("target_refs", None), ("target_refs", "target"),
    ("approval_scope", {}), ("approval_scope", None), ("approval_scope", "scope"),
])
def test_CE_human_champ_obligatoire_incomplet_bloque(field, bad):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env))
    hd[field] = bad
    hd["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in hd.items() if k != "CONTENT_SHA256"})

    out = _close(env, human_decision=hd)

    assert out["status"] == BLOCKED
    assert out["closure_id"] is None


@pytest.mark.parametrize("bad", ["", None, 1])
def test_CE_human_content_sha256_incomplet_bloque(bad):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env))
    hd["CONTENT_SHA256"] = bad
    out = _close(env, human_decision=hd)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_human_scope_mismatch():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env), target_refs=[["OBJ-9999", "CODE"]])
    hd["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in hd.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env, human_decision=hd)) == HUMAN_SCOPE_MISMATCH


def test_CE_human_inattendu_sur_plan_non_sensible():
    env = _full_env(action_id="ACTION_ANNOTATE")
    hd = _human(_plan(env), approval_scope=None)
    hd["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in hd.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env, human_decision=hd)) == HUMAN_UNEXPECTED


def test_CE_human_content_falsifie():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env)); hd["identity_ref"] = "TAMPERED"
    assert _code(_close(env, human_decision=hd)) == HUMAN_MALFORMED


def test_CE_closed_at_absent():
    assert _code(_close(_full_env(), closed_at_context=None)) == CLOSED_AT_MALFORMED


def test_CE_provenance_refs_absent():
    assert _code(_close(_full_env(), provenance_refs=None)) == PROVENANCE_MALFORMED


def test_CE_ci_refs_absent():
    assert _code(_close(_full_env(), ci_refs=None)) == CI_REFS_MALFORMED


def test_CE_surrogate_bloque():
    assert _code(_close(_full_env(), closed_at_context="2026\ud800")) == NON_SCALAR_UNICODE


def test_CE_fuite_bloque():
    assert _code(_close(_full_env(), provenance_refs=["prov\x1fleak"])) == LEAK


# ---------- déterminisme & contexte complet du closure_id ----------

def test_closure_id_deterministe():
    a, b = _close(_full_env()), _close(_full_env())
    assert a["closure_id"] == b["closure_id"] and a["CONTENT_SHA256"] == b["CONTENT_SHA256"]


def test_closure_id_contexte_exec_change_id():
    env = _full_env(action_id="ACTION_ANNOTATE")
    a = _close(env)
    b = _close(env, execution_result=_exec_result(_plan(env), "SUCCESS"))
    assert a["closure_id"] != b["closure_id"]


def test_closure_id_contexte_closed_at_change_id():
    env = _full_env()
    a = _close(env, closed_at_context="2026-07-15T00:00:00Z")
    b = _close(env, closed_at_context="2026-07-15T00:00:01Z")
    assert a["closure_id"] != b["closure_id"]


def test_content_sha256_exclut_son_propre_champ():
    v = _close(_full_env())
    obj_sans = {k: v[k] for k in OUTPUT_KEYS if k != "CONTENT_SHA256"}
    assert v["CONTENT_SHA256"] == _canonical_sha256(obj_sans)


# ---------- invariants divers ----------

def test_no_rejudgment_echoes_09_10_verdicts():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    v = _close(env)
    assert v["decision_id"] == env["structured_decision"]["decision_id"]
    assert v["action_status"] == env["action_admissibility_and_plan"]["action_status"]
    assert v["action_plan_id"] == env["action_admissibility_and_plan"]["action_plan_id"]


def test_pipeline_gate_digest_complet_00_10():
    v = _close(_full_env())
    digest = v["pipeline_gate_digest"]
    for comp in ("00_RUNTIME_CHECK", "05_COHERENCE_ENGINE", "09_STRUCTURED_DECISION",
                 "10_ACTION_ADMISSIBILITY_AND_PLAN"):
        assert comp in digest and digest[comp]["status"] == PASS


def test_immutabilite_envelope():
    e = _full_env(); snap = copy.deepcopy(e)
    _close(e)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        RUN(None, _catalog(), _permissions())


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], k
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-11-TRACE-AND-CLOSE"
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_11_TRACE_AND_CLOSE"


def test_garde_enumerante():
    cases = [
        ("10 replay", (lambda: (lambda e: (e.__setitem__(
            "action_admissibility_and_plan",
            {**e["action_admissibility_and_plan"], "action_status": "ACTION_NOT_REQUIRED"}), e)[1])(_full_env()))(),
            ACTION_10_REPLAY_MISMATCH),
        ("closed_at absent", None, CLOSED_AT_MALFORMED),
    ]
    env0, exp0 = cases[0][1], cases[0][2]
    # recalcule le CONTENT_SHA256 pour que seul action_status diverge du replay
    ad = env0["action_admissibility_and_plan"]
    ad["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in ad.items() if k != "CONTENT_SHA256"})
    assert _code(_close(env0)) == exp0
    assert _code(_close(_full_env(), closed_at_context=None)) == CLOSED_AT_MALFORMED
