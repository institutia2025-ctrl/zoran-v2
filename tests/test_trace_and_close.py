"""Tests déterministes de 11_TRACE_AND_CLOSE (enveloppe 00→10 + résultat d'exécution / décision humaine injectés).

Vérifie : gate 00→10, REPLAY EXACT de 09 (depuis 00→08) et de 10 (depuis 00→09 + catalogue + permissions +
impact_context) AVANT toute lecture des entrées de clôture, 10 statuts de clôture, résultat d'exécution/décision
humaine falsifiés/incomplets/hors-scope → BLOCKED, absence d'exécution = cas nominal, appariement de scope EXACT,
anti-fuite/surrogate, closure_id (contexte complet, via _fingerprint) + CONTENT_SHA256, objet plat 21 clés, fail-closed.
"""
import base64
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

_HUMAN_N = int("22257822511297263857735046943867968420363575251328596241453709180862563914629761888058994309982106830747179588599188430400836571089812443826062042432449881918181938580223032266390670012013862399618838440671750656254758513329245566374645313089292827740742932206721682681211206320174732905661849827015661555361708852513247096809620673616207725918929040652679953845687264753129470058933985159151847170690785957789838151818463892808287414766125927431038684393343433213441968208809731644556802698216173802994644887313107284943918200428027444395529306366159451132502370713668356646829951358976646279106235511933764247402693")
_HUMAN_D = int("3015420932025887383872698598545367114947328894559314187082214937967613551993820259755615846464647924431947156145002735499358037529390607376301148347454329448724505045533900662758688395397532398196679155364363735587865437084731358964384730359820539455622340194553155318458336483440673356823552331532039993204832653141739074482637562696150108468658244152256925609649242166774878986347160895107874977028894484613025904400327029511848597881608239839829856186786049535579421129247447980076563319695464870614126793095825594641457499312661399075714633579953151598852060683903162666640371705821436499653631333993538713282513")
_EXECUTOR_N = int("22454497963301209412983786996647158576330813716094883142833213543249203855375670753316479635856463834866453104227876146649273164753844711782749470874925091613706369341093154273904067185293106528429385131977428165602260299488713316957369273414857331253656719141539918933986602304330008249647594277806652250527882044401311637437216840752414142730266798231321700354610125080211887219196042399797041277519081103984074697532459852293037991864860833371157309416149030955721312744400538218498799024930036375527682005351509441871413674902069472806916176968917063107566673811068232598715730552683082658107368555170477698322927")
_EXECUTOR_D = int("10484784464103666018454054317071242552658611104156088415634078219078391012409457078560420092110740162696885189572750536364004039721299097420080381051604745273919090916451197957075778750488228015162912997485500831738980553806305759629994290559603836342200224160547993183368036535330496474534855978947774064185418312140766186854432745886293951135767139672416826863632388913414743571141954195191324219980776634942485369054588490021844248276906487826056158665147818272763853126358246127350401309292069061785515167151575390548486050684650837012768050692187587682982343238122934098783001039682313505197825150215964481902473")


def _sign(obj, n, d, key_id):
    payload = {k: v for k, v in obj.items() if k not in ("CONTENT_SHA256", "authenticity_proof")}
    digest = bytes.fromhex(_canonical_sha256(payload))
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + digest
    size = (n.bit_length() + 7) // 8
    encoded = b"\x00\x01" + b"\xff" * (size - len(digest_info) - 3) + b"\x00" + digest_info
    signature = pow(int.from_bytes(encoded, "big"), d, n).to_bytes(size, "big")
    return {"algorithm": "RS256", "key_id": key_id,
            "signature_b64": base64.b64encode(signature).decode("ascii")}


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


def _human_authority(plan, identity_ref="user://fred", action_id=None, target_refs=None):
    registry = {"version": "1.0.0", "source": "HUMAN_AUTHORITY_REGISTRY", "identities": [{
        "identity_ref": identity_ref, "roles": ["ACTION_APPROVER"],
        "allowed_action_ids": [action_id if action_id is not None else "ACTION_APPLY_PATCH"],
        "allowed_target_refs": target_refs if target_refs is not None else [["OBJ-0001", "CODE"]],
        "provenance_refs": ["prov://human/1"], "key_id": "HUMAN-FRED-RSA-1",
        "rsa_n": str(_HUMAN_N), "rsa_e": 65537,
    }]}
    return registry, _canonical_sha256(registry)


def _executor_authority(plan, executor_id="EXECUTOR-1", action_id=None, target_refs=None):
    registry = {"version": "1.0.0", "source": "EXECUTOR_AUTHORITY_REGISTRY", "executors": [{
        "executor_id": executor_id,
        "allowed_action_ids": ([action_id] if action_id is not None
                               else ["ACTION_ANNOTATE", "ACTION_APPLY_PATCH"]),
        "allowed_target_refs": target_refs if target_refs is not None else [["OBJ-0001", "CODE"]],
        "provenance_refs": ["prov://exec/1"], "key_id": "EXECUTOR-1-RSA-1",
        "rsa_n": str(_EXECUTOR_N), "rsa_e": 65537,
    }]}
    return registry, _canonical_sha256(registry)


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
        "rollback_available": True, "provenance_refs": ["prov://exec/1"],
        "authenticity_proof": None, "CONTENT_SHA256": None,
    }
    obj.update(over)
    if obj["authenticity_proof"] is None:
        obj["authenticity_proof"] = _sign(obj, _EXECUTOR_N, _EXECUTOR_D, "EXECUTOR-1-RSA-1")
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _human(plan, decision="APPROVED", **over):
    obj = {
        "human_decision_id": "HD-1", "action_plan_id": plan["action_plan_id"], "action_id": plan["action_id"],
        "target_refs": plan["target_refs"], "approval_scope": plan["approval_scope"], "decision": decision,
        "identity_ref": "user://fred", "decided_at_context": "th", "provenance_refs": ["prov://human/1"],
        "authenticity_proof": None, "CONTENT_SHA256": None,
    }
    obj.update(over)
    if obj["authenticity_proof"] is None:
        obj["authenticity_proof"] = _sign(obj, _HUMAN_N, _HUMAN_D, "HUMAN-FRED-RSA-1")
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _close(env, **kw):
    kw.setdefault("provenance_refs", ["prov://close/1"])
    kw.setdefault("ci_refs", ["ci://run/1"])
    kw.setdefault("closed_at_context", "2026-07-15T00:00:00Z")
    human_authority, human_fp = _human_authority(_plan(env))
    executor_authority, executor_fp = _executor_authority(_plan(env))
    human_authority = kw.pop("human_authority", human_authority)
    human_fp = kw.pop("human_authority_fingerprint", human_fp)
    executor_authority = kw.pop("executor_authority", executor_authority)
    executor_fp = kw.pop("executor_authority_fingerprint", executor_fp)
    return RUN(env, _catalog(), env["permissions"], human_authority, executor_authority, **kw)


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
    ha, hfp = _human_authority(_plan(env)); ea, efp = _executor_authority(_plan(env))
    out = RUN(env, _catalog(), env["permissions"], ha, ea,
              execution_result=Exploding(), human_decision=Exploding(),
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


def test_CE_identity_attacker_rehashee_bloquee():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    hd = _human(_plan(env), identity_ref="ATTACKER")
    assert _close(env, human_decision=hd)["status"] == BLOCKED


def test_CE_usurpation_identite_autorisee_sans_preuve_authentique_bloquee():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    forged = _human(_plan(env), identity_ref="user://fred")
    forged["authenticity_proof"]["signature_b64"] = base64.b64encode(b"forged").decode("ascii")
    forged["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    assert _close(env, human_decision=forged)["status"] == BLOCKED


def test_CE_executor_attacker_rehashe_bloque():
    env = _full_env(action_id="ACTION_ANNOTATE")
    er = _exec_result(_plan(env), executor_id="ATTACKER")
    assert _close(env, execution_result=er)["status"] == BLOCKED


def test_CE_usurpation_executeur_autorise_sans_preuve_authentique_bloquee():
    env = _full_env(action_id="ACTION_ANNOTATE")
    forged = _exec_result(_plan(env), executor_id="EXECUTOR-1")
    forged["authenticity_proof"]["signature_b64"] = base64.b64encode(b"forged").decode("ascii")
    forged["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    assert _close(env, execution_result=forged)["status"] == BLOCKED


@pytest.mark.parametrize("signed_change", ["plan", "action", "targets"])
def test_CE_signature_humaine_autre_contexte_non_rejouable(signed_change):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    plan = _plan(env)
    signed_plan = dict(plan)
    overrides = {}
    if signed_change == "plan":
        signed_plan["action_plan_id"] = "ACTION-PLAN-" + "f" * 64
    elif signed_change == "action":
        overrides["action_id"] = "ACTION_OTHER"
    else:
        overrides["target_refs"] = [["OBJ-9999", "CODE"]]
    foreign = _human(signed_plan, **overrides)
    received = _human(plan)
    received["authenticity_proof"] = foreign["authenticity_proof"]
    received["CONTENT_SHA256"] = _canonical_sha256(
        {k: v for k, v in received.items() if k != "CONTENT_SHA256"})
    out = _close(env, human_decision=received)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_registre_humain_attacker_et_auto_fingerprint_bloques():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    authority, _ = _human_authority(_plan(env), identity_ref="ATTACKER")
    out = _close(env, human_decision=_human(_plan(env), identity_ref="ATTACKER"),
                 human_authority=authority,
                 human_authority_fingerprint=_canonical_sha256(authority))
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_registre_executeur_attacker_et_auto_fingerprint_bloques():
    env = _full_env(action_id="ACTION_ANNOTATE")
    authority, _ = _executor_authority(_plan(env), executor_id="ATTACKER")
    out = _close(env, execution_result=_exec_result(_plan(env), executor_id="ATTACKER"),
                 executor_authority=authority,
                 executor_authority_fingerprint=_canonical_sha256(authority))
    assert out["status"] == BLOCKED and out["closure_id"] is None


@pytest.mark.parametrize("mutation", [
    lambda h, e: h["identities"].append(copy.deepcopy(h["identities"][0])),
    lambda h, e: e["executors"].append(copy.deepcopy(e["executors"][0])),
    lambda h, e: h["identities"][0]["roles"].append("ATTACKER_ROLE"),
    lambda h, e: h["identities"][0].__setitem__(
        "allowed_target_refs", [["OBJ-0001", "CODE"], ["OBJ-9999", "CODE"]]),
    lambda h, e: e["executors"][0].__setitem__("provenance_refs", ["prov://attacker"]),
    lambda h, e: h.__setitem__("version", "9.9.9"),
])
def test_CE_toute_mutation_registre_bloquee_par_engagement_canonique(mutation):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    ha, _ = _human_authority(_plan(env)); ea, _ = _executor_authority(_plan(env))
    mutation(ha, ea)
    out = _close(env, human_decision=_human(_plan(env)),
                 human_authority=ha, executor_authority=ea)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_registre_reordonne_semantiquement_identique_accepte():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    ha, _ = _human_authority(_plan(env)); ea, _ = _executor_authority(_plan(env))
    ea["executors"][0]["allowed_action_ids"].reverse()
    out = _close(env, human_decision=_human(_plan(env)), execution_result=_exec_result(_plan(env)),
                 human_authority=ha, executor_authority=ea)
    assert out["status"] == PASS and out["closure_id"] is not None


def test_CE_identite_valide_non_autorisee_action_bloquee():
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    authority, fp = _human_authority(_plan(env), action_id="ACTION_OTHER")
    out = _close(env, human_decision=_human(_plan(env)),
                 human_authority=authority, human_authority_fingerprint=fp)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_executeur_valide_non_autorise_action_bloque():
    env = _full_env(action_id="ACTION_ANNOTATE")
    authority, fp = _executor_authority(_plan(env), action_id="ACTION_OTHER")
    out = _close(env, execution_result=_exec_result(_plan(env)),
                 executor_authority=authority, executor_authority_fingerprint=fp)
    assert out["status"] == BLOCKED and out["closure_id"] is None


@pytest.mark.parametrize("targets", [[], [["OBJ-0001", "CODE"], ["OBJ-9999", "CODE"]]])
def test_CE_scope_autoritaire_humain_non_exact_bloque(targets):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    authority, fp = _human_authority(_plan(env), target_refs=targets)
    out = _close(env, human_decision=_human(_plan(env)),
                 human_authority=authority, human_authority_fingerprint=fp)
    assert out["status"] == BLOCKED and out["closure_id"] is None


@pytest.mark.parametrize("targets", [[], [["OBJ-0001", "CODE"], ["OBJ-9999", "CODE"]]])
def test_CE_scope_autoritaire_executeur_non_exact_bloque(targets):
    env = _full_env(action_id="ACTION_ANNOTATE")
    authority, fp = _executor_authority(_plan(env), target_refs=targets)
    out = _close(env, execution_result=_exec_result(_plan(env)),
                 executor_authority=authority, executor_authority_fingerprint=fp)
    assert out["status"] == BLOCKED and out["closure_id"] is None


@pytest.mark.parametrize("kind", ["human", "executor"])
def test_CE_registre_modifie_ou_version_falsifiee_bloque(kind):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    ha, hfp = _human_authority(_plan(env))
    ea, efp = _executor_authority(_plan(env))
    registry = ha if kind == "human" else ea
    registry["version"] = "9.9.9"
    out = _close(env, human_decision=_human(_plan(env)),
                 human_authority=ha, human_authority_fingerprint=hfp,
                 executor_authority=ea, executor_authority_fingerprint=efp)
    assert out["status"] == BLOCKED and out["closure_id"] is None


@pytest.mark.parametrize("kind", ["human", "executor"])
def test_CE_engagement_canonique_autorite_divergent_bloque(kind):
    env = _full_env(action_id="ACTION_APPLY_PATCH", granted=["PERM_WRITE"])
    authority, _ = (_human_authority(_plan(env)) if kind == "human"
                    else _executor_authority(_plan(env)))
    authority["version"] = "9.9.9"
    kw = {f"{kind}_authority": authority}
    out = _close(env, human_decision=_human(_plan(env)), **kw)
    assert out["status"] == BLOCKED and out["closure_id"] is None


def test_CE_autorite_divergente_bloque_avant_toute_entree_cloture():
    class Exploding(dict):
        def items(self):
            raise AssertionError("entree de cloture lue avant validation des autorites")

    env = _full_env(action_id="ACTION_ANNOTATE")
    ha, _ = _human_authority(_plan(env)); ea, _ = _executor_authority(_plan(env))
    ha["version"] = "9.9.9"
    unread = Exploding()
    out = RUN(env, _catalog(), env["permissions"], ha, ea,
              execution_result=unread, human_decision=unread, provenance_refs=unread,
              ci_refs=unread, closed_at_context=unread)
    assert out["status"] == BLOCKED and out["closure_id"] is None


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
        RUN(None, _catalog(), _permissions(), {}, {})


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
