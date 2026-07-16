"""11_TRACE_AND_CLOSE — porte 11 (TERMINALE) du pipeline de raisonnement ZORAN V2.

Clôture une transaction de raisonnement/action SANS exécuter l'action : consolide les preuves 00→10,
l'état final, la décision humaine éventuelle, le résultat d'exécution externe éventuel, les anomalies et
les conditions de reprise, en UN objet-clôture déterministe, immuable, traçable. Ne re-juge jamais 09/10.

Invariant central (Fred 2026-07-15) : 11 REJOUE déterministiquement 09 (depuis 00→08) et 10 (depuis 00→09 +
catalogue canonique + permissions + impact_context) et exige `received == expected`, AVANT toute lecture de
autorités humaines/exécuteurs, puis human_decision / execution_result / provenance / ci_refs / closed_at_context.
Toute divergence → BLOCKED.

Réutilise les primitives certifiées de 09 (`_canonical_sha256` via `_fingerprint`, `_has_surrogate_codepoint`,
`_has_internal_leak`) et rejoue 09/10 via leurs fonctions pures. NO_LLM / NO_NETWORK / NO_ACTION_EXECUTION /
NO_HIDDEN_READ / NO_INVENTION / NO_REJUDGMENT_OF_09_OR_10 / FAIL_CLOSED / DETERMINISTIC / IMMUTABLE.
Contrat figé : specs/SPEC_ENGINE_11_TRACE_AND_CLOSE.md.
"""
from __future__ import annotations

import base64

from zoran_v2.structured_decision import (
    _canonical_sha256,
    _has_internal_leak,
    _has_surrogate_codepoint,
    run_structured_decision,
)
from zoran_v2.action_admissibility_and_plan import run_action_admissibility_and_plan

COMPONENT_ID = "11_TRACE_AND_CLOSE"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-11-TRACE-AND-CLOSE",
    "META_ID": "META-ZORAN-V2-COMPONENT-11",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_11_TRACE_AND_CLOSE · branche feat/engine-11-trace-and-close",
    "GUARD_IDS": [
        "NO_LLM", "NO_NETWORK", "NO_ACTION_EXECUTION", "NO_HIDDEN_READ", "NO_INVENTION",
        "NO_REJUDGMENT_OF_09_OR_10", "FAIL_CLOSED", "DETERMINISTIC", "IMMUTABLE",
        "ANTI_LEAK", "EXACT_STRING_PRESERVATION", "NON_SCALAR_UNICODE_BLOCKED",
        "CANONICAL_PRIMITIVE_REUSED", "OBJECT_FIRST_CONTENT_SHA256",
        "INTEGRITY_REVALIDATION_NOT_REJUDGMENT", "DETERMINISTIC_REPLAY_09_AND_10",
        "CLOSURE_COMPLETENESS", "EXTERNAL_RESULT_INJECTED_AND_VERIFIED",
        "HUMAN_GO_SCOPE_BOUNDED_EXACT", "NO_TIME_INVENTION",
        "INDEPENDENT_HUMAN_AUTHORITY", "INDEPENDENT_EXECUTOR_AUTHORITY",
        "EXACT_AUTHORITY_SCOPE", "AUTHORITY_FINGERPRINT_REVALIDATED",
        "EXTERNAL_EMITTER_RS256_AUTHENTICATED", "EXACT_EXTERNAL_PAYLOAD_SIGNED",
    ],
    "TRACEABILITY": "objet-cloture {closure_id, close_status, pipeline_gate_digest 00-10, final_state, human_decision_ref, execution_result_ref, anomalies, resumption_conditions, rollback_plan_ref, CONTENT_SHA256} ; 09/10 rejoues ; autorites engagees + cles publiques canoniques + signatures RS256 du payload externe exact ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..10 != PASS, replay 09/10 divergent, autorite absente/divergente/hors-scope, signature externe absente/invalide/hors-contexte, resultat d'execution/decision humaine falsifie/incomplet, execution sans plan/sans GO/apres refus, provenance/ci/closed_at absents, fuite ou surrogate",
    "ANTI_REGRESSION": "tests adversariaux + replay 09/10 puis autorites engagees AVANT entrees de cloture + identites/executants/actions/scopes/provenances exacts + 10 statuts + determinisme + anti-fuite/surrogate ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE", "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_11_TRACE_AND_CLOSE",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "cloture deterministe d'une transaction : consolidation 00-10 + replay exact 09/10 + etat final + decision humaine/execution injectees et verifiees ; aucune execution",
    "REJECTED_BEHAVIOR": "execution d'action, re-jugement de 09/10, invention, generation/LLM, reseau, lecture cachee, transformation d'un plan en preuve d'execution, mutation d'un objet de cloture existant",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"

# Statuts de clôture (close_status, quand status=PASS).
CLOSED_NO_ACTION = "CLOSED_NO_ACTION"
CLOSED_BLOCKED = "CLOSED_BLOCKED"
CLOSED_QUARANTINED = "CLOSED_QUARANTINED"
CLOSED_PLAN_READY_NOT_EXECUTED = "CLOSED_PLAN_READY_NOT_EXECUTED"
CLOSED_AWAITING_HUMAN_APPROVAL = "CLOSED_AWAITING_HUMAN_APPROVAL"
CLOSED_HUMAN_DECLINED = "CLOSED_HUMAN_DECLINED"
CLOSED_APPROVED_NOT_EXECUTED = "CLOSED_APPROVED_NOT_EXECUTED"
CLOSED_EXECUTED_SUCCESS = "CLOSED_EXECUTED_SUCCESS"
CLOSED_EXECUTED_FAILED = "CLOSED_EXECUTED_FAILED"
CLOSED_ANOMALY = "CLOSED_ANOMALY"

# Verdicts 10 consommés.
_A_NOT_REQUIRED = "ACTION_NOT_REQUIRED"
_A_BLOCKED = "ACTION_BLOCKED"
_A_QUARANTINED = "ACTION_QUARANTINED"
_A_PLAN_READY = "ACTION_PLAN_READY"
_A_HUMAN_APPROVAL = "HUMAN_APPROVAL_REQUIRED"

# Codes blocked_by DÉDIÉS 11 (blocked_by = "<code>@<frontière/moteur source>").
UPSTREAM_NOT_PASS = "11_CLOSE_UPSTREAM_NOT_PASS"
DECISION_09_REPLAY_MISMATCH = "11_CLOSE_DECISION_09_REPLAY_MISMATCH"
ACTION_10_REPLAY_MISMATCH = "11_CLOSE_ACTION_10_REPLAY_MISMATCH"
EXEC_MALFORMED = "11_CLOSE_EXEC_MALFORMED"
EXEC_PROVENANCE = "11_CLOSE_EXEC_PROVENANCE"
EXEC_INCONSISTENT = "11_CLOSE_EXEC_INCONSISTENT"
EXEC_UNEXPECTED = "11_CLOSE_EXEC_UNEXPECTED"
HUMAN_MALFORMED = "11_CLOSE_HUMAN_MALFORMED"
HUMAN_SCOPE_MISMATCH = "11_CLOSE_HUMAN_SCOPE_MISMATCH"
HUMAN_UNEXPECTED = "11_CLOSE_HUMAN_UNEXPECTED"
AUTHORITY_MALFORMED = "11_CLOSE_AUTHORITY_MALFORMED"
AUTHORITY_FINGERPRINT_MISMATCH = "11_CLOSE_AUTHORITY_FINGERPRINT_MISMATCH"
HUMAN_UNAUTHORIZED = "11_CLOSE_HUMAN_UNAUTHORIZED"
EXECUTOR_UNAUTHORIZED = "11_CLOSE_EXECUTOR_UNAUTHORIZED"
PROVENANCE_MALFORMED = "11_CLOSE_PROVENANCE_MALFORMED"
CI_REFS_MALFORMED = "11_CLOSE_CI_REFS_MALFORMED"
CLOSED_AT_MALFORMED = "11_CLOSE_CLOSED_AT_MALFORMED"
LEAK = "11_CLOSE_LEAK"
NON_SCALAR_UNICODE = "11_CLOSE_NON_SCALAR_UNICODE"

_STEPS_00_10 = (
    ("runtime_check", "00_RUNTIME_CHECK"),
    ("object_discovery", "01_OBJECT_DISCOVERY"),
    ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
    ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
    ("canon_determination", "04_CANON_DETERMINATION"),
    ("coherence_engine", "05_COHERENCE_ENGINE"),
    ("llm_request_build", "06_LLM_REQUEST_BUILD"),
    ("llm_execution", "07_LLM_EXECUTION"),
    ("coherence_2", "08_COHERENCE_2"),
    ("structured_decision", "09_STRUCTURED_DECISION"),
    ("action_admissibility_and_plan", "10_ACTION_ADMISSIBILITY_AND_PLAN"),
)

# Schémas figés injectés (EXECUTION_RESULT_SCHEMA.yaml / HUMAN_DECISION_SCHEMA.yaml).
_EXEC_KEYS = frozenset((
    "execution_result_id", "action_plan_id", "action_id", "target_refs", "executor_id",
    "execution_status", "started_at_context", "completed_at_context", "effects", "anomalies",
    "rollback_available", "provenance_refs", "authenticity_proof", "CONTENT_SHA256",
))
_EXEC_STATUS_ENUM = frozenset(("SUCCESS", "FAILED", "PARTIAL"))
_HUMAN_KEYS = frozenset((
    "human_decision_id", "action_plan_id", "action_id", "target_refs", "approval_scope",
    "decision", "identity_ref", "decided_at_context", "provenance_refs", "authenticity_proof", "CONTENT_SHA256",
))
_HUMAN_DECISION_ENUM = frozenset(("APPROVED", "DECLINED"))
_HUMAN_AUTH_KEYS = frozenset(("version", "source", "identities"))
_IDENTITY_KEYS = frozenset(("identity_ref", "roles", "allowed_action_ids", "allowed_target_refs",
                            "provenance_refs", "key_id", "rsa_n", "rsa_e"))
_EXECUTOR_AUTH_KEYS = frozenset(("version", "source", "executors"))
_EXECUTOR_KEYS = frozenset(("executor_id", "allowed_action_ids", "allowed_target_refs",
                            "provenance_refs", "key_id", "rsa_n", "rsa_e"))
_AUTH_PROOF_KEYS = frozenset(("algorithm", "key_id", "signature_b64"))
CANONICAL_HUMAN_AUTHORITY_FINGERPRINT = "003fab738e2dd19fbb862377a7c384815c44ab8a6c173c6eb66b21ad1deed7ae"
CANONICAL_EXECUTOR_AUTHORITY_FINGERPRINT = "5e3ffcd470eab2d83aea1d1e118504dc970fa8c02fc37197b6c6b29bde663368"

ORDER_KEY = "trace_consolidation_puis_cloture"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "closure_id", "close_status", "decision_id", "action_plan_id", "action_status",
    "pipeline_gate_digest", "final_state", "human_decision_ref", "execution_result_ref",
    "anomalies", "resumption_conditions", "rollback_plan_ref", "provenance_refs", "ci_refs",
    "closed_at_context", "CONTENT_SHA256", "order_key",
)


def _finalize(fields: dict) -> dict:
    obj = {k: fields.get(k) for k in OUTPUT_KEYS}
    obj["CONTENT_SHA256"] = None
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _blocked(code: str, source: str) -> dict:
    return _finalize({"component": COMPONENT_ID, "version": VERSION, "status": BLOCKED,
                      "blocked_by": f"{code}@{source}", "order_key": ORDER_KEY})


def _content_ok(obj: dict) -> bool:
    """Recompute déterministe du CONTENT_SHA256 (aucune confiance dans le seul champ stocké)."""
    stored = obj.get("CONTENT_SHA256")
    if not (isinstance(stored, str) and stored):
        return False
    return _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"}) == stored


def _valid_refs(refs) -> bool:
    return isinstance(refs, list) and bool(refs) and all(isinstance(r, str) and r for r in refs)


def _normalized_authority(registry, kind):
    list_key = "identities" if kind == "human" else "executors"
    id_key = "identity_ref" if kind == "human" else "executor_id"
    principals = []
    for principal in registry[list_key]:
        normalized = dict(principal)
        for key in ("roles", "allowed_action_ids", "provenance_refs"):
            if key in normalized:
                normalized[key] = sorted(normalized[key])
        normalized["allowed_target_refs"] = sorted(normalized["allowed_target_refs"])
        principals.append(normalized)
    return {"version": registry["version"], "source": registry["source"],
            list_key: sorted(principals, key=lambda item: item[id_key])}


def _validate_authority(registry, kind):
    if _has_internal_leak(registry) or _has_surrogate_codepoint(registry):
        raise ValueError((AUTHORITY_MALFORMED, f"{kind}_authority"))
    top_keys = _HUMAN_AUTH_KEYS if kind == "human" else _EXECUTOR_AUTH_KEYS
    list_key = "identities" if kind == "human" else "executors"
    expected_source = "HUMAN_AUTHORITY_REGISTRY" if kind == "human" else "EXECUTOR_AUTHORITY_REGISTRY"
    if not (isinstance(registry, dict) and set(registry) == top_keys
            and isinstance(registry["version"], str) and registry["version"]
            and registry["source"] == expected_source
            and isinstance(registry[list_key], list) and registry[list_key]):
        raise ValueError((AUTHORITY_MALFORMED, f"{kind}_authority"))
    for principal in registry[list_key]:
        principal_keys = _IDENTITY_KEYS if kind == "human" else _EXECUTOR_KEYS
        id_key = "identity_ref" if kind == "human" else "executor_id"
        if not (isinstance(principal, dict) and set(principal) == principal_keys
                and isinstance(principal[id_key], str) and principal[id_key]
                and _valid_refs(principal["allowed_action_ids"])
                and isinstance(principal["allowed_target_refs"], list)
                and _valid_refs(principal["provenance_refs"])
                and isinstance(principal["key_id"], str) and principal["key_id"]
                and isinstance(principal["rsa_n"], str) and principal["rsa_n"].isdigit()
                and isinstance(principal["rsa_e"], int) and principal["rsa_e"] > 1):
            raise ValueError((AUTHORITY_MALFORMED, f"{kind}_authority.{list_key}"))
        if kind == "human" and not _valid_refs(principal["roles"]):
            raise ValueError((AUTHORITY_MALFORMED, "human_authority.roles"))
    expected = (CANONICAL_HUMAN_AUTHORITY_FINGERPRINT if kind == "human"
                else CANONICAL_EXECUTOR_AUTHORITY_FINGERPRINT)
    if _canonical_sha256(_normalized_authority(registry, kind)) != expected:
        raise ValueError((AUTHORITY_FINGERPRINT_MISMATCH, f"{kind}_authority.canonical_commitment"))
    return registry[list_key]


def _authorized_principal(principals, id_key, principal_id, plan, provenance_refs, role=None):
    for principal in principals:
        if principal[id_key] != principal_id:
            continue
        if role is not None and role not in principal["roles"]:
            continue
        if (plan["action_plan_id"]
                and plan["action_id"] in principal["allowed_action_ids"]
                and plan["target_refs"] == principal["allowed_target_refs"]
                and principal["provenance_refs"] == provenance_refs):
            return principal
    return None


def _authentic_payload(obj):
    return {k: v for k, v in obj.items() if k not in ("CONTENT_SHA256", "authenticity_proof")}


def _rsa_sha256_valid(obj, principal):
    proof = obj.get("authenticity_proof")
    if not (isinstance(proof, dict) and set(proof) == _AUTH_PROOF_KEYS
            and proof["algorithm"] == "RS256" and proof["key_id"] == principal["key_id"]
            and isinstance(proof["signature_b64"], str) and proof["signature_b64"]):
        return False
    try:
        signature = base64.b64decode(proof["signature_b64"], validate=True)
        n, e = int(principal["rsa_n"]), principal["rsa_e"]
        size = (n.bit_length() + 7) // 8
        if len(signature) != size:
            return False
        encoded = pow(int.from_bytes(signature, "big"), e, n).to_bytes(size, "big")
    except (ValueError, TypeError):
        return False
    digest = bytes.fromhex(_canonical_sha256(_authentic_payload(obj)))
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + digest
    padding_len = size - len(digest_info) - 3
    expected = b"\x00\x01" + b"\xff" * padding_len + b"\x00" + digest_info
    return padding_len >= 8 and encoded == expected


def _close_from_exec(execution_result: dict):
    """Résultat d'exécution vérifié -> (close_status, anomalies). Frontière DOUCE (status reste PASS)."""
    status = execution_result["execution_status"]
    anomalies = list(execution_result["anomalies"])
    if status == "SUCCESS":
        return (CLOSED_ANOMALY if anomalies else CLOSED_EXECUTED_SUCCESS), anomalies
    if status == "FAILED":
        return CLOSED_EXECUTED_FAILED, anomalies
    return CLOSED_ANOMALY, anomalies  # PARTIAL


def _validate_execution_result(execution_result, plan, executor_principals):
    """-> (ref, close_status, anomalies) si valide+cohérent ; sinon (code, source) via ValueError."""
    if not (isinstance(execution_result, dict) and set(execution_result) == _EXEC_KEYS):
        raise ValueError((EXEC_MALFORMED, "execution_result"))
    if not _content_ok(execution_result):
        raise ValueError((EXEC_PROVENANCE, "execution_result.CONTENT_SHA256"))
    if not (isinstance(execution_result["execution_result_id"], str)
            and execution_result["execution_result_id"]):
        raise ValueError((EXEC_MALFORMED, "execution_result.execution_result_id"))
    for field in ("started_at_context", "completed_at_context"):
        if not (isinstance(execution_result[field], str) and execution_result[field]):
            raise ValueError((EXEC_MALFORMED, f"execution_result.{field}"))
    if not isinstance(execution_result["effects"], list):
        raise ValueError((EXEC_MALFORMED, "execution_result.effects"))
    if not (isinstance(execution_result["anomalies"], list)
            and all(isinstance(item, str) and item for item in execution_result["anomalies"])):
        raise ValueError((EXEC_MALFORMED, "execution_result.anomalies"))
    if not _valid_refs(execution_result["provenance_refs"]):
        raise ValueError((EXEC_PROVENANCE, "execution_result.provenance_refs"))
    if not (isinstance(execution_result["executor_id"], str) and execution_result["executor_id"]):
        raise ValueError((EXEC_MALFORMED, "execution_result.executor_id"))
    if execution_result["execution_status"] not in _EXEC_STATUS_ENUM:
        raise ValueError((EXEC_MALFORMED, "execution_result.execution_status"))
    if not isinstance(execution_result["rollback_available"], bool):
        raise ValueError((EXEC_MALFORMED, "execution_result.rollback_available"))
    if execution_result["action_plan_id"] != plan["action_plan_id"]:
        raise ValueError((EXEC_INCONSISTENT, "execution_result.action_plan_id"))
    if execution_result["action_id"] != plan["action_id"]:
        raise ValueError((EXEC_INCONSISTENT, "execution_result.action_id"))
    if execution_result["target_refs"] != plan["target_refs"]:
        raise ValueError((EXEC_INCONSISTENT, "execution_result.target_refs"))
    principal = _authorized_principal(executor_principals, "executor_id", execution_result["executor_id"],
                                      plan, execution_result["provenance_refs"])
    if principal is None or not _rsa_sha256_valid(execution_result, principal):
        raise ValueError((EXECUTOR_UNAUTHORIZED, "execution_result.executor_authority"))
    close_status, anomalies = _close_from_exec(execution_result)
    ref = {"execution_result_id": execution_result["execution_result_id"],
           "execution_status": execution_result["execution_status"],
           "CONTENT_SHA256": execution_result["CONTENT_SHA256"]}
    return ref, close_status, anomalies


def _validate_human_decision(human_decision, plan, human_principals):
    """-> (ref, decision) si valide+scope EXACT ; sinon (code, source) via ValueError."""
    if not (isinstance(human_decision, dict) and set(human_decision) == _HUMAN_KEYS):
        raise ValueError((HUMAN_MALFORMED, "human_decision"))
    if not _content_ok(human_decision):
        raise ValueError((HUMAN_MALFORMED, "human_decision.CONTENT_SHA256"))
    if not (isinstance(human_decision["human_decision_id"], str)
            and human_decision["human_decision_id"]):
        raise ValueError((HUMAN_MALFORMED, "human_decision.human_decision_id"))
    if not _valid_refs(human_decision["provenance_refs"]):
        raise ValueError((HUMAN_MALFORMED, "human_decision.provenance_refs"))
    if not (isinstance(human_decision["identity_ref"], str) and human_decision["identity_ref"]):
        raise ValueError((HUMAN_MALFORMED, "human_decision.identity_ref"))
    if not (isinstance(human_decision["decided_at_context"], str) and human_decision["decided_at_context"]):
        raise ValueError((HUMAN_MALFORMED, "human_decision.decided_at_context"))
    if human_decision["decision"] not in _HUMAN_DECISION_ENUM:
        raise ValueError((HUMAN_MALFORMED, "human_decision.decision"))
    # Appariement de scope EXACT (jamais seulement inclusif).
    if (human_decision["action_plan_id"] != plan["action_plan_id"]
            or human_decision["action_id"] != plan["action_id"]
            or human_decision["target_refs"] != plan["target_refs"]
            or human_decision["approval_scope"] != plan["approval_scope"]):
        raise ValueError((HUMAN_SCOPE_MISMATCH, "frontier:human_decision.scope<->10.plan"))
    principal = _authorized_principal(human_principals, "identity_ref", human_decision["identity_ref"],
                                      plan, human_decision["provenance_refs"], role="ACTION_APPROVER")
    if principal is None or not _rsa_sha256_valid(human_decision, principal):
        raise ValueError((HUMAN_UNAUTHORIZED, "human_decision.identity_authority"))
    ref = {"human_decision_id": human_decision["human_decision_id"],
           "decision": human_decision["decision"], "CONTENT_SHA256": human_decision["CONTENT_SHA256"]}
    return ref, human_decision["decision"]


def run_trace_and_close(envelope: dict, catalog: dict, permissions: dict,
                        human_authority, executor_authority, execution_result=None,
                        human_decision=None, provenance_refs=None, ci_refs=None,
                        closed_at_context=None) -> dict:
    """Fonction PURE : enveloppe(00→10) + catalogue/permissions (pour replay) + entrées de clôture INJECTÉES
    -> objet-clôture PLAT (21 clés), ou BLOCKED (fail-closed)."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    # 1) Prérequis 00→10 = PASS.
    for key, comp in _STEPS_00_10:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(UPSTREAM_NOT_PASS, comp)

    sd = envelope["structured_decision"]
    ad = envelope["action_admissibility_and_plan"]

    # 2) Défense en profondeur sur les entrées AUTORITAIRES amont (avant replay).
    for payload, src in ((sd, "09.decision"), (ad, "10.action"), (catalog, "catalog"), (permissions, "permissions")):
        if _has_internal_leak(payload):
            return _blocked(LEAK, src)
        if _has_surrogate_codepoint(payload):
            return _blocked(NON_SCALAR_UNICODE, src)

    # 3) REPLAY EXACT de 09 (depuis 00→08) — AVANT toute lecture des entrées de clôture.
    if sd != run_structured_decision(envelope):
        return _blocked(DECISION_09_REPLAY_MISMATCH, "frontier:09.received<->09.replayed")

    # 4) REPLAY EXACT de 10 (depuis 00→09 + catalogue + permissions + impact_context) — AVANT lecture clôture.
    if ad != run_action_admissibility_and_plan(envelope, catalog, permissions):
        return _blocked(ACTION_10_REPLAY_MISMATCH, "frontier:10.received<->10.replayed")

    # 5) Autorités indépendantes versionnées et engagées, avant toute entrée de clôture.
    try:
        human_principals = _validate_authority(human_authority, "human")
        executor_principals = _validate_authority(executor_authority, "executor")
    except ValueError as e:
        code, src = e.args[0]
        return _blocked(code, src)

    # --- 09 et 10 sont désormais AUTORITAIRES (revalidés, jamais re-jugés). Lecture des entrées de clôture. ---
    action_status = ad["action_status"]
    action_plan_id = ad["action_plan_id"]

    # 5) Anti-fuite / anti-surrogate sur les entrées de clôture injectées.
    for payload, src in ((execution_result, "execution_result"), (human_decision, "human_decision"),
                         (provenance_refs, "provenance_refs"), (ci_refs, "ci_refs"),
                         (closed_at_context, "closed_at_context")):
        if _has_internal_leak(payload):
            return _blocked(LEAK, src)
        if _has_surrogate_codepoint(payload):
            return _blocked(NON_SCALAR_UNICODE, src)

    # 6) Provenance / CI / horodatage de clôture (obligatoires, injectés, jamais d'horloge).
    if not (isinstance(closed_at_context, str) and closed_at_context):
        return _blocked(CLOSED_AT_MALFORMED, "closed_at_context")
    if not _valid_refs(provenance_refs):
        return _blocked(PROVENANCE_MALFORMED, "provenance_refs")
    if not _valid_refs(ci_refs):
        return _blocked(CI_REFS_MALFORMED, "ci_refs")

    executes_allowed = action_status in (_A_PLAN_READY, _A_HUMAN_APPROVAL)

    # 7) Décision humaine : valide UNIQUEMENT quand 10=HUMAN_APPROVAL_REQUIRED ; scope EXACT.
    human_ref = None
    human_decision_value = None
    if human_decision is not None:
        if action_status != _A_HUMAN_APPROVAL:
            return _blocked(HUMAN_UNEXPECTED, "human_decision")
        try:
            human_ref, human_decision_value = _validate_human_decision(human_decision, ad, human_principals)
        except ValueError as e:
            code, src = e.args[0]
            return _blocked(code, src)

    # 8) Résultat d'exécution : valide UNIQUEMENT si un plan existe ET (non sensible OU GO humain APPROVED).
    exec_ref = None
    exec_close_status = None
    exec_anomalies = []
    if execution_result is not None:
        if not executes_allowed:
            return _blocked(EXEC_UNEXPECTED, "execution_result.no_plan")
        if action_status == _A_HUMAN_APPROVAL and human_decision_value != "APPROVED":
            return _blocked(EXEC_UNEXPECTED, "execution_result.without_human_go")
        try:
            exec_ref, exec_close_status, exec_anomalies = _validate_execution_result(
                execution_result, ad, executor_principals)
        except ValueError as e:
            code, src = e.args[0]
            return _blocked(code, src)

    # 9) close_status (déterministe) + conditions de reprise.
    resumption_conditions = []
    anomalies = []
    if action_status == _A_NOT_REQUIRED:
        close_status = CLOSED_NO_ACTION
    elif action_status == _A_BLOCKED:
        close_status = CLOSED_BLOCKED
    elif action_status == _A_QUARANTINED:
        close_status = CLOSED_QUARANTINED
        resumption_conditions = ["REVIEW_GLOBAL_IMPACT"]
    elif action_status == _A_PLAN_READY:
        if execution_result is None:
            close_status = CLOSED_PLAN_READY_NOT_EXECUTED
            resumption_conditions = ["AWAITING_EXECUTOR_RESULT"]
        else:
            close_status, anomalies = exec_close_status, exec_anomalies
    else:  # _A_HUMAN_APPROVAL
        if human_decision is None:
            close_status = CLOSED_AWAITING_HUMAN_APPROVAL
            resumption_conditions = ["AWAITING_HUMAN_GO"]
        elif human_decision_value == "DECLINED":
            close_status = CLOSED_HUMAN_DECLINED
        elif execution_result is None:
            close_status = CLOSED_APPROVED_NOT_EXECUTED
            resumption_conditions = ["AWAITING_EXECUTOR_RESULT"]
        else:
            close_status, anomalies = exec_close_status, exec_anomalies

    # 10) Digest 00→10 + état final + rollback porté (jamais exécuté).
    pipeline_gate_digest = {
        comp: {"status": envelope[key].get("status"), "content_sha256": envelope[key].get("CONTENT_SHA256")}
        for key, comp in _STEPS_00_10
    }
    final_state = {"action_status": action_status,
                   "execution_status": execution_result["execution_status"] if execution_result is not None else None,
                   "human_decision": human_decision_value}
    rollback_plan_ref = ad.get("rollback_plan")

    # 11) closure_id (contexte COMPLET, sans self-ref) puis CONTENT_SHA256 (objet final SANS lui-même).
    payload = {
        "close_status": close_status,
        "decision_id": sd["decision_id"], "decision_content_sha256": sd["CONTENT_SHA256"],
        "action_plan_id": action_plan_id, "action_content_sha256": ad["CONTENT_SHA256"],
        "action_status": action_status, "pipeline_gate_digest": pipeline_gate_digest,
        "final_state": final_state, "human_decision_ref": human_ref, "execution_result_ref": exec_ref,
        "anomalies": anomalies, "resumption_conditions": resumption_conditions,
        "rollback_plan_ref": rollback_plan_ref, "provenance_refs": provenance_refs,
        "ci_refs": ci_refs, "closed_at_context": closed_at_context,
    }
    closure_id = "ACTION-CLOSE-" + _canonical_sha256(payload)

    return _finalize({
        "component": COMPONENT_ID, "version": VERSION, "status": PASS, "blocked_by": None,
        "closure_id": closure_id, "close_status": close_status,
        "decision_id": sd["decision_id"], "action_plan_id": action_plan_id, "action_status": action_status,
        "pipeline_gate_digest": pipeline_gate_digest, "final_state": final_state,
        "human_decision_ref": human_ref, "execution_result_ref": exec_ref,
        "anomalies": anomalies, "resumption_conditions": resumption_conditions,
        "rollback_plan_ref": rollback_plan_ref, "provenance_refs": provenance_refs, "ci_refs": ci_refs,
        "closed_at_context": closed_at_context, "order_key": ORDER_KEY,
    })


def _load_catalog(path=None):
    import yaml
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "ACTIONS_CATALOG.yaml"
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, OSError):
        return None


def main(envelope: dict, human_authority: dict, executor_authority: dict) -> dict:
    # Impur (fin) : catalogue chargé du fichier gelé ; entrées de clôture INJECTÉES via l'enveloppe (aucune lecture cachée dans run).
    return run_trace_and_close(
        envelope, _load_catalog(), envelope.get("permissions"), human_authority, executor_authority,
        execution_result=envelope.get("execution_result"),
        human_decision=envelope.get("human_decision"),
        provenance_refs=envelope.get("closure_provenance_refs"),
        ci_refs=envelope.get("closure_ci_refs"),
        closed_at_context=envelope.get("closed_at_context"),
    )
