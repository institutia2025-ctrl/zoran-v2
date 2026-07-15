"""Tests déterministes de 10_ACTION_ADMISSIBILITY_AND_PLAN (envelope 00→09 + catalogue + permissions injectés).

Vérifie : gate 00→09, INTÉGRITÉ 09 (CONTENT_SHA256 recalculé), action_request explicite ⊆ catalogue gelé,
permissions, impact global avant plan, 5 verdicts, mutation sensible → HUMAN_APPROVAL_REQUIRED, anti-fuite/surrogate,
action_plan_id (contexte complet, via _fingerprint) + CONTENT_SHA256, objet plat 19 clés, fail-closed.
"""
import copy

import pytest

from zoran_v2.structured_decision import _canonical_sha256, run_structured_decision
from zoran_v2.action_admissibility_and_plan import (
    ACTION_BLOCKED,
    ACTION_NOT_IN_CATALOG,
    ACTION_NOT_REQUIRED,
    ACTION_PLAN_READY,
    ACTION_QUARANTINED,
    ACTION_REQUEST_MALFORMED,
    BLOCKED,
    CATALOG_INVALID,
    DECISION_REPLAY_MISMATCH,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    HUMAN_APPROVAL_REQUIRED,
    IMPACT_CONTEXT_MALFORMED,
    LEAK,
    NON_SCALAR_UNICODE,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PERMISSIONS_INVALID,
    PROVENANCE_DECL,
    TARGET_PROVENANCE,
    UPSTREAM_NOT_PASS,
    run_action_admissibility_and_plan as RUN,
)


def _code(v):
    return (v["blocked_by"] or "").split("@")[0]


def _decision(targets=None, decision_id=None):
    tgts = targets if targets is not None else [{"object_public_id": "OBJ-0001", "frame": "CODE"}]
    d = {
        "component": "09_STRUCTURED_DECISION", "version": "1.0.0", "status": "PASS", "blocked_by": None,
        "decision_id": decision_id or ("DECISION-" + "a" * 64),
        "decision_type": "STRUCTURED_ANALYSIS_DECISION_V1", "decision_status": "DECIDED_ON_ACCEPT",
        "targets": tgts, "claims_retained": [], "claims_rejected": [], "constraints": [],
        "justification_refs": {}, "referential_fingerprint": "FP", "source_response_fingerprint": "FP",
        "CONTENT_SHA256": None, "order_key": "x",
    }
    d["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in d.items() if k != "CONTENT_SHA256"})
    return d


def _catalog():
    return {"version": "1.0.0", "actions": [
        {"id": "ACTION_NONE", "requires_action": False, "sensitive_mutation": False, "permissions_required": []},
        {"id": "ACTION_ANNOTATE", "requires_action": True, "sensitive_mutation": False, "permissions_required": []},
        {"id": "ACTION_REPORT", "requires_action": True, "sensitive_mutation": False, "permissions_required": ["PERM_REPORT"]},
        {"id": "ACTION_APPLY_PATCH", "requires_action": True, "sensitive_mutation": True, "permissions_required": ["PERM_WRITE"]},
    ]}


def _permissions(granted=None):
    return {"version": "1.0.0", "granted": granted if granted is not None else ["PERM_WRITE", "PERM_REPORT"]}


def _env(action_id="ACTION_ANNOTATE", target_refs=None, assessed=None, decision=None,
         authority_env=None, **over):
    from tests.test_structured_decision import _env as _env_09

    base = copy.deepcopy(authority_env) if authority_env is not None else _env_09()
    base.update({
        "structured_decision": decision if decision is not None else run_structured_decision(base),
        "action_request": {"action_id": action_id,
                           "target_refs": target_refs if target_refs is not None else [["OBJ-0001", "CODE"]]},
        "impact_context": {"assessed_target_refs": assessed if assessed is not None else [["OBJ-0001", "CODE"]],
                           "global_impact": "impact faible", "risks": ["r1"]},
    })
    base.update(over)
    return base


# ---------- schéma & verdicts nominaux ----------

def test_output_schema_plat_19_cles():
    assert tuple(RUN(_env(), _catalog(), _permissions()).keys()) == OUTPUT_KEYS
    assert tuple(RUN(_env(action_id="ZZZ"), _catalog(), _permissions()).keys()) == OUTPUT_KEYS  # BLOCKED : même schéma
    assert RUN(_env(), _catalog(), _permissions())["order_key"] == ORDER_KEY


def test_verdict_plan_ready():
    v = RUN(_env(action_id="ACTION_ANNOTATE"), _catalog(), _permissions())
    assert v["status"] == PASS and v["action_status"] == ACTION_PLAN_READY
    assert v["action_plan_id"].startswith("ACTION-PLAN-") and len(v["action_plan_id"]) == len("ACTION-PLAN-") + 64
    assert v["global_impact"] == "impact faible" and v["rollback_plan"] is not None
    assert v["approval_required"] is False and v["approval_scope"] is None
    assert isinstance(v["CONTENT_SHA256"], str) and len(v["CONTENT_SHA256"]) == 64


def test_verdict_not_required():
    v = RUN(_env(action_id="ACTION_NONE"), _catalog(), _permissions())
    assert v["status"] == PASS and v["action_status"] == ACTION_NOT_REQUIRED
    assert v["action_plan_id"] is None and v["global_impact"] is None


def test_verdict_action_blocked_permissions_deny():
    # ACTION_REPORT exige PERM_REPORT ; permissions VALIDES mais ne l'accordent pas -> ACTION_BLOCKED (verdict).
    v = RUN(_env(action_id="ACTION_REPORT"), _catalog(), _permissions(granted=[]))
    assert v["status"] == PASS and v["action_status"] == ACTION_BLOCKED and v["action_plan_id"] is None


def test_verdict_quarantined_impact_incomplet():
    # impact ne couvre pas la cible -> QUARANTINED (GLOBAL_IMPACT_BEFORE_PLAN).
    v = RUN(_env(action_id="ACTION_ANNOTATE", assessed=[]), _catalog(), _permissions())
    assert v["status"] == PASS and v["action_status"] == ACTION_QUARANTINED and v["action_plan_id"] is None


def test_verdict_human_approval_pour_mutation_sensible():
    v = RUN(_env(action_id="ACTION_APPLY_PATCH"), _catalog(), _permissions(granted=["PERM_WRITE"]))
    assert v["status"] == PASS and v["action_status"] == HUMAN_APPROVAL_REQUIRED
    assert v["approval_required"] is True and v["approval_scope"] == {"action_id": "ACTION_APPLY_PATCH", "target_refs": [["OBJ-0001", "CODE"]]}
    assert v["action_plan_id"] is not None  # plan préparé mais gaté sur GO humain


# ---------- contre-exemples (→ BLOCKED) ----------

def test_CE_09_status_non_pass():
    env = _env(); env["structured_decision"] = {**env["structured_decision"], "status": "BLOCKED"}
    v = RUN(env, _catalog(), _permissions())
    assert v["status"] == BLOCKED and _code(v) == UPSTREAM_NOT_PASS and v["blocked_by"].endswith("@09_STRUCTURED_DECISION")


def test_CE_upstream_00_a_08_non_pass():
    for key, comp in (("runtime_check", "00_RUNTIME_CHECK"), ("coherence_2", "08_COHERENCE_2")):
        env = _env(); env[key] = {**env[key], "status": "BLOCKED"}
        v = RUN(env, _catalog(), _permissions())
        assert _code(v) == UPSTREAM_NOT_PASS and v["blocked_by"].endswith("@" + comp), comp


def test_CE_decision_id_invalide():
    env = _env(decision=_decision(decision_id="NOT-A-DECISION-ID"))
    assert _code(RUN(env, _catalog(), _permissions())) == DECISION_REPLAY_MISMATCH


def test_CE_content_sha256_09_falsifie():
    d = _decision()
    d["referential_fingerprint"] = "TAMPERED"  # CONTENT_SHA256 devient obsolète (décision altérée)
    assert _code(RUN(_env(decision=d), _catalog(), _permissions())) == DECISION_REPLAY_MISMATCH


def test_CE_decision_09_rehashee_mais_divergente_du_replay_00_08():
    from tests.test_structured_decision import _env as _env_09

    env = _env_09()
    forged = dict(run_structured_decision(env))
    forged["targets"] = [{"object_public_id": "OBJ-9999", "frame": "CODE"}]
    forged["decision_id"] = "DECISION-" + "b" * 64
    forged["CONTENT_SHA256"] = _canonical_sha256(
        {k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    env.update({
        "structured_decision": forged,
        "action_request": {"action_id": "ACTION_ANNOTATE", "target_refs": [["OBJ-9999", "CODE"]]},
        "impact_context": {"assessed_target_refs": [["OBJ-9999", "CODE"]],
                           "global_impact": "impact faible", "risks": ["r1"]},
    })

    out = RUN(env, _catalog(), _permissions())

    assert out["status"] == BLOCKED
    assert out["action_plan_id"] is None


def test_CE_divergence_09_bloquee_avant_lecture_action_request():
    from tests.test_structured_decision import _env as _env_09

    class ExplodingActionRequest(dict):
        def items(self):
            raise AssertionError("action_request lue avant replay 09")

    env = _env_09()
    forged = dict(run_structured_decision(env))
    forged["decision_id"] = "DECISION-" + "c" * 64
    forged["CONTENT_SHA256"] = _canonical_sha256(
        {k: v for k, v in forged.items() if k != "CONTENT_SHA256"})
    env["structured_decision"] = forged
    unread = ExplodingActionRequest()
    env["action_request"] = unread
    env["impact_context"] = unread

    out = RUN(env, unread, unread)

    assert out["status"] == BLOCKED
    assert out["action_plan_id"] is None


def test_CE_decision_incomplete():
    d = _decision(); del d["targets"]
    assert _code(RUN(_env(decision=d), _catalog(), _permissions())) == DECISION_REPLAY_MISMATCH


def test_CE_action_hors_catalogue():
    assert _code(RUN(_env(action_id="ACTION_INVENTED"), _catalog(), _permissions())) == ACTION_NOT_IN_CATALOG


def test_CE_catalogue_invalide():
    for bad in ({"version": "1.0.0"}, {"version": "", "actions": []},
                {"version": "1.0.0", "actions": [{"id": "X"}]}):
        assert _code(RUN(_env(), bad, _permissions())) == CATALOG_INVALID, bad


@pytest.mark.parametrize("mutation", [
    lambda c: c["actions"].append(
        {"id": "ACTION_INVENTED", "requires_action": True,
         "sensitive_mutation": False, "permissions_required": []}),
    lambda c: c["actions"].pop(),
    lambda c: c["actions"][1].__setitem__("requires_action", False),
    lambda c: c["actions"][1].__setitem__("sensitive_mutation", True),
    lambda c: c["actions"][1].__setitem__("permissions_required", ["PERM_FORGED"]),
    lambda c: c.__setitem__("version", "9.9.9"),
])
def test_CE_catalogue_structurellement_valide_mais_divergent_bloque_avant_donnees_action(mutation):
    class ExplodingMapping(dict):
        def items(self):
            raise AssertionError("donnee action lue avant engagement canonique catalogue")

    catalog = _catalog()
    mutation(catalog)
    env = _env()
    unread = ExplodingMapping()
    env["action_request"] = unread
    env["impact_context"] = unread

    out = RUN(env, catalog, unread)

    assert out["status"] == BLOCKED
    assert out["action_plan_id"] is None


def test_catalogue_reordonne_semantiquement_identique_reste_accepte():
    catalog = _catalog()
    catalog["actions"].reverse()
    for action in catalog["actions"]:
        action["permissions_required"].reverse()

    out = RUN(_env(), catalog, _permissions())

    assert out["status"] == PASS
    assert out["action_status"] == ACTION_PLAN_READY


def test_CE_permissions_invalides():
    for bad in (None, {}, {"version": "1.0.0"}, {"version": "1.0.0", "granted": "x"}):
        assert _code(RUN(_env(), _catalog(), bad)) == PERMISSIONS_INVALID, bad


def test_CE_action_request_malforme():
    for env in (_env(target_refs="x"), {**_env(), "action_request": {"action_id": "ACTION_ANNOTATE"}}):
        assert _code(RUN(env, _catalog(), _permissions())) == ACTION_REQUEST_MALFORMED


def test_CE_target_hors_09():
    assert _code(RUN(_env(target_refs=[["OBJ-9999", "CODE"]]), _catalog(), _permissions())) == TARGET_PROVENANCE


def test_CE_impact_context_malforme():
    for env in ({**_env(), "impact_context": {"assessed_target_refs": [["OBJ-0001", "CODE"]], "risks": ["r"]}},
                {**_env(), "impact_context": {"assessed_target_refs": "x", "global_impact": "g", "risks": ["r"]}},
                {**_env(), "impact_context": {"assessed_target_refs": [["OBJ-0001", "CODE"]], "global_impact": "", "risks": ["r"]}}):
        assert _code(RUN(env, _catalog(), _permissions())) == IMPACT_CONTEXT_MALFORMED


def test_CE_surrogate_bloque():
    v = RUN(_env(action_id="ACTION_ANNOTATE", target_refs=[["OBJ-0001", "CODE"]]),
            {**_catalog(), "version": "1.0\ud800"}, _permissions())
    assert v["status"] == BLOCKED and _code(v) == NON_SCALAR_UNICODE


def test_CE_fuite_x1f_bloque():
    v = RUN(_env(), _catalog(), {"version": "1.0.0", "granted": ["PERM\x1fLEAK"]})
    assert v["status"] == BLOCKED and _code(v) == LEAK


# ---------- déterminisme & contexte complet de action_plan_id ----------

def test_action_plan_id_deterministe():
    a = RUN(_env(), _catalog(), _permissions())
    b = RUN(_env(), _catalog(), _permissions())
    assert a["action_plan_id"] == b["action_plan_id"] and a["CONTENT_SHA256"] == b["CONTENT_SHA256"]


def test_action_plan_id_contexte_target_change_id():
    from tests.test_structured_decision import _env as _env_09, _response

    targets = [
        {"object_public_id": "OBJ-0001", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP"]},
        {"object_public_id": "OBJ-0002", "kind_public": "code", "frame": "CODE",
         "canons": ["C"], "operants": ["OP"]},
    ]
    results = [
        {"object_public_id": opid, "frame": "CODE",
         "canon_findings": [{"canon": "C", "admissible": True}],
         "operant_outcomes": [{"operant": "OP", "applied": True}]}
        for opid in ("OBJ-0001", "OBJ-0002")
    ]
    authority = _env_09(targets=targets, response=_response(results=results))
    a = RUN(_env(authority_env=authority, target_refs=[["OBJ-0001", "CODE"]]), _catalog(), _permissions())
    b = RUN(_env(authority_env=authority, target_refs=[["OBJ-0002", "CODE"]]), _catalog(), _permissions())
    assert a["action_plan_id"] != b["action_plan_id"]  # cible différente -> plan différent


def test_action_plan_id_contexte_permissions_change_id():
    a = RUN(_env(), _catalog(), _permissions(granted=["PERM_WRITE"]))
    b = RUN(_env(), _catalog(), _permissions(granted=["PERM_WRITE", "PERM_EXTRA"]))
    assert a["action_plan_id"] != b["action_plan_id"]  # contexte permissions -> id différent


def test_content_sha256_exclut_son_propre_champ():
    v = RUN(_env(), _catalog(), _permissions())
    obj_sans = {k: v[k] for k in OUTPUT_KEYS if k != "CONTENT_SHA256"}
    assert v["CONTENT_SHA256"] == _canonical_sha256(obj_sans)


# ---------- invariants divers ----------

def test_immutabilite_envelope():
    e = _env(); snap = copy.deepcopy(e)
    RUN(e, _catalog(), _permissions())
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        RUN(None, _catalog(), _permissions())


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], k
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-10-ACTION-ADMISSIBILITY-AND-PLAN"
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_10_ACTION_ADMISSIBILITY_AND_PLAN"


def test_garde_enumerante():
    cases = [
        ("09.status", (lambda: (lambda e: (e.__setitem__("structured_decision", {**e["structured_decision"], "status": "BLOCKED"}), e)[1])(_env()))(), UPSTREAM_NOT_PASS),
        ("action hors catalogue", _env(action_id="X"), ACTION_NOT_IN_CATALOG),
        ("target hors 09", _env(target_refs=[["OBJ-9999", "CODE"]]), TARGET_PROVENANCE),
    ]
    for label, env, expected in cases:
        assert _code(RUN(env, _catalog(), _permissions())) == expected, label
