"""10_ACTION_ADMISSIBILITY_AND_PLAN — porte 10 du pipeline de raisonnement ZORAN V2.

Évalue si la décision structurée de 09 peut devenir une action, puis produit un plan BORNÉ et
vérifiable. AUCUNE exécution, aucune invention (CATALOG_ONLY), aucune action implicite (action_request
explicite), aucune lecture cachée (catalogue + permissions INJECTÉS). Déterministe, immuable, fail-closed
00→09, anti-fuite/anti-surrogate récursifs. NO_LLM / NO_NETWORK.

Réutilise les primitives de 09 (SHA certifié) : `_canonical_sha256` (via `_fingerprint`, aucun 2ᵉ hasher),
`_has_surrogate_codepoint`, `_has_internal_leak` — aucune duplication, aucune divergence.
Contrat figé : specs/SPEC_ENGINE_10_ACTION_ADMISSIBILITY_AND_PLAN.md.
"""
from __future__ import annotations

import re

from zoran_v2.structured_decision import (
    _canonical_sha256,
    _has_internal_leak,
    _has_surrogate_codepoint,
    run_structured_decision,
)

COMPONENT_ID = "10_ACTION_ADMISSIBILITY_AND_PLAN"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-10-ACTION-ADMISSIBILITY-AND-PLAN",
    "META_ID": "META-ZORAN-V2-COMPONENT-10",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_10_ACTION_ADMISSIBILITY_AND_PLAN · branche feat/engine-10-action-admissibility",
    "GUARD_IDS": [
        "NO_LLM", "NO_NETWORK", "NO_ACTION_EXECUTION", "NO_ACTION_INVENTION", "CATALOG_ONLY",
        "GLOBAL_IMPACT_BEFORE_PLAN", "FAIL_CLOSED", "DETERMINISTIC", "IMMUTABLE",
        "HUMAN_GO_REQUIRED_FOR_SENSITIVE_MUTATION", "ANTI_LEAK", "EXACT_STRING_PRESERVATION",
        "NON_SCALAR_UNICODE_BLOCKED", "CANONICAL_PRIMITIVE_REUSED", "OBJECT_FIRST_CONTENT_SHA256",
        "ACTION_PLAN_ID_COVERS_COMPLETE_CONTEXT", "NO_HIDDEN_READ_IN_PURE_FN", "DECISION_09_INTEGRITY_REVALIDATED",
        "DECISION_09_PROVENANCE_REPLAYED_EXACTLY", "CANONICAL_ACTION_CATALOG_COMMITMENT",
    ],
    "TRACEABILITY": "plan {action_plan_id, action_status, global_impact, rollback_plan, approval_scope, justification_refs} ; primitive _fingerprint reutilisee (via 09) ; decision 09 rejouee depuis 00-08 et comparee exactement ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..09 != PASS, decision 09 recue != replay exact 00-08, catalogue injecte != engagement canonique, decision 09 alteree/incomplete/decision_id invalide, action_request malforme, action hors catalogue, catalogue/permissions invalides, cible hors 09, impact_context malforme, fuite ou surrogate",
    "ANTI_REGRESSION": "tests contre-exemples adversariaux + replay exact 09 et engagement catalogue avant toute donnee action + determinisme/contexte action_plan_id + integrite 09 + verdicts + anti-fuite/surrogate + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE", "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_10_ACTION_ADMISSIBILITY_AND_PLAN",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "admissibilite d'action + plan borne deterministe a partir d'une decision 09 certifiee et d'un catalogue gele ; aucune execution",
    "REJECTED_BEHAVIOR": "execution d'action, invention hors catalogue, action implicite, generation/LLM, reseau, lecture cachee, mutation du referentiel/catalogue",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"

# Verdicts (action_status, quand status=PASS).
ACTION_NOT_REQUIRED = "ACTION_NOT_REQUIRED"
ACTION_BLOCKED = "ACTION_BLOCKED"
ACTION_QUARANTINED = "ACTION_QUARANTINED"
ACTION_PLAN_READY = "ACTION_PLAN_READY"
HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"

# Contrat de la sortie 09 (revalidée) et format decision_id.
_SD_KEYS = frozenset((
    "component", "version", "status", "blocked_by", "decision_id", "decision_type", "decision_status",
    "targets", "claims_retained", "claims_rejected", "constraints", "justification_refs",
    "referential_fingerprint", "source_response_fingerprint", "CONTENT_SHA256", "order_key",
))
_DECISION_ID_RE = re.compile(r"^DECISION-[0-9a-f]{64}$")

# Schémas catalogue / permissions / action_request / impact_context.
_CATALOG_KEYS = frozenset(("version", "actions"))
_ACTION_KEYS = frozenset(("id", "requires_action", "sensitive_mutation", "permissions_required"))
_PERMISSIONS_KEYS = frozenset(("version", "granted"))
_ACTION_REQUEST_KEYS = frozenset(("action_id", "target_refs"))
_IMPACT_KEYS = frozenset(("assessed_target_refs", "global_impact", "risks"))

# Engagement autoritaire indépendant de l'argument `catalog` injecté. Il scelle
# ACTIONS_CATALOG.yaml v1.0.0 après normalisation par `_validate_catalog`.
CANONICAL_CATALOG_FINGERPRINT = "c5d3d0c9900999502c9162ad145c4c10c2213126282a120499a3118f20fa8afc"

_STEPS_00_09 = (
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
)

# Codes blocked_by DÉDIÉS 10 (blocked_by = "<code>@<frontière/moteur source>").
UPSTREAM_NOT_PASS = "10_ACTION_UPSTREAM_NOT_PASS"
DECISION_INTEGRITY = "10_ACTION_DECISION_09_INTEGRITY"
DECISION_REPLAY_MISMATCH = "10_ACTION_DECISION_09_REPLAY_MISMATCH"
ACTION_REQUEST_MALFORMED = "10_ACTION_REQUEST_MALFORMED"
ACTION_NOT_IN_CATALOG = "10_ACTION_NOT_IN_CATALOG"
CATALOG_INVALID = "10_ACTION_CATALOG_INVALID"
CATALOG_PROVENANCE_MISMATCH = "10_ACTION_CATALOG_PROVENANCE_MISMATCH"
PERMISSIONS_INVALID = "10_ACTION_PERMISSIONS_INVALID"
TARGET_PROVENANCE = "10_ACTION_TARGET_PROVENANCE"
IMPACT_CONTEXT_MALFORMED = "10_ACTION_IMPACT_CONTEXT_MALFORMED"
LEAK = "10_ACTION_LEAK"
NON_SCALAR_UNICODE = "10_ACTION_NON_SCALAR_UNICODE"

ORDER_KEY = "action_admissibility_puis_plan_borne"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "action_plan_id", "action_status", "decision_id", "action_id", "target_refs",
    "prerequisites", "permissions_required", "risks", "global_impact", "rollback_plan",
    "approval_required", "approval_scope", "justification_refs", "CONTENT_SHA256", "order_key",
)


def _finalize(fields: dict) -> dict:
    obj = {k: fields.get(k) for k in OUTPUT_KEYS}
    obj["CONTENT_SHA256"] = None
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _blocked(code: str, source: str) -> dict:
    return _finalize({"component": COMPONENT_ID, "version": VERSION, "status": BLOCKED,
                      "blocked_by": f"{code}@{source}", "order_key": ORDER_KEY,
                      "approval_required": None})


def _is_str_list(x) -> bool:
    return isinstance(x, list) and all(isinstance(e, str) and e for e in x)


def _is_pair_list(x) -> bool:
    return (isinstance(x, list)
            and all(isinstance(p, list) and len(p) == 2 and isinstance(p[0], str) and p[0]
                    and isinstance(p[1], str) and p[1] for p in x))


def _validate_catalog(catalog):
    """Catalogue versionné valide -> (actions_by_id, catalog_fingerprint) ou (None, None)."""
    if not isinstance(catalog, dict) or set(catalog) != _CATALOG_KEYS:
        return None, None
    if not (isinstance(catalog.get("version"), str) and catalog["version"]):
        return None, None
    actions = catalog.get("actions")
    if not (isinstance(actions, list) and actions):
        return None, None
    by_id = {}
    for a in actions:
        if not isinstance(a, dict) or set(a) != _ACTION_KEYS:
            return None, None
        if not (isinstance(a.get("id"), str) and a["id"]):
            return None, None
        if not (isinstance(a.get("requires_action"), bool) and isinstance(a.get("sensitive_mutation"), bool)):
            return None, None
        if not (isinstance(a.get("permissions_required"), list)
                and all(isinstance(p, str) and p for p in a["permissions_required"])
                and len(set(a["permissions_required"])) == len(a["permissions_required"])):
            return None, None
        if a["id"] in by_id:
            return None, None
        by_id[a["id"]] = a
    fingerprint = _canonical_sha256({
        "version": catalog["version"],
        "actions": [{"id": a["id"], "requires_action": a["requires_action"],
                     "sensitive_mutation": a["sensitive_mutation"],
                     "permissions_required": sorted(a["permissions_required"])}
                    for a in sorted(actions, key=lambda x: x["id"])],
    })
    return by_id, fingerprint


def _valid_permissions(permissions) -> bool:
    return (isinstance(permissions, dict) and set(permissions) == _PERMISSIONS_KEYS
            and isinstance(permissions.get("version"), str) and permissions["version"]
            and isinstance(permissions.get("granted"), list)
            and all(isinstance(p, str) and p for p in permissions["granted"])
            and len(set(permissions["granted"])) == len(permissions["granted"]))


def run_action_admissibility_and_plan(envelope: dict, catalog: dict, permissions: dict) -> dict:
    """Fonction PURE : envelope(00→09) + catalogue + permissions (INJECTÉS) -> plan borné ou BLOCKED."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    # 1) Prérequis 00→09 = PASS.
    for key, comp in _STEPS_00_09:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(UPSTREAM_NOT_PASS, comp)

    sd = envelope["structured_decision"]
    # 2) Replay 09 depuis 00→08 + comparaison exacte, avant toute donnée d'action.
    expected_sd = run_structured_decision(envelope)
    if sd != expected_sd:
        return _blocked(DECISION_REPLAY_MISMATCH, "frontier:09.received<->09.replayed")

    # 3) Défense en profondeur sur la décision 09 autoritaire.
    for payload, src in ((sd, "09.decision"),):
        if _has_internal_leak(payload):
            return _blocked(LEAK, src)
        if _has_surrogate_codepoint(payload):
            return _blocked(NON_SCALAR_UNICODE, src)

    # 4) Intégrité de la décision 09 (revalidée, jamais confiance au statut) : schéma exact, decision_id valide,
    #    CONTENT_SHA256 RECALCULÉ == (décision non altérée).
    if set(sd) != _SD_KEYS:
        return _blocked(DECISION_INTEGRITY, "09.schema")
    if not (isinstance(sd.get("decision_id"), str) and _DECISION_ID_RE.match(sd["decision_id"])):
        return _blocked(DECISION_INTEGRITY, "09.decision_id")
    if not (isinstance(sd.get("CONTENT_SHA256"), str) and sd["CONTENT_SHA256"]):
        return _blocked(DECISION_INTEGRITY, "09.CONTENT_SHA256")
    recomputed = _canonical_sha256({k: v for k, v in sd.items() if k != "CONTENT_SHA256"})
    if recomputed != sd["CONTENT_SHA256"]:
        return _blocked(DECISION_INTEGRITY, "09.CONTENT_SHA256.altered")
    decision_targets = {(t["object_public_id"], t["frame"]) for t in sd["targets"]
                        if isinstance(t, dict) and isinstance(t.get("object_public_id"), str)
                        and isinstance(t.get("frame"), str)}

    # 5) Catalogue injecté : validation, normalisation et comparaison à
    #    l'engagement canonique indépendant, avant toute donnée d'action.
    if _has_internal_leak(catalog):
        return _blocked(LEAK, "catalog")
    if _has_surrogate_codepoint(catalog):
        return _blocked(NON_SCALAR_UNICODE, "catalog")
    actions_by_id, catalog_fp = _validate_catalog(catalog)
    if actions_by_id is None:
        return _blocked(CATALOG_INVALID, "catalog")
    if catalog_fp != CANONICAL_CATALOG_FINGERPRINT:
        return _blocked(CATALOG_PROVENANCE_MISMATCH,
                        "frontier:catalog.injected<->catalog.canonical_commitment")

    # 6) action_request explicite (P-10-1) : schéma et cibles ⊆ 09.
    action_request = envelope.get("action_request")
    if _has_internal_leak(action_request):
        return _blocked(LEAK, "action_request")
    if _has_surrogate_codepoint(action_request):
        return _blocked(NON_SCALAR_UNICODE, "action_request")
    if not (isinstance(action_request, dict) and set(action_request) == _ACTION_REQUEST_KEYS):
        return _blocked(ACTION_REQUEST_MALFORMED, "action_request")
    action_id = action_request.get("action_id")
    target_refs_raw = action_request.get("target_refs")
    if not (isinstance(action_id, str) and action_id and _is_pair_list(target_refs_raw)):
        return _blocked(ACTION_REQUEST_MALFORMED, "action_request")
    req_pairs = {(p[0], p[1]) for p in target_refs_raw}
    if not req_pairs <= decision_targets:
        return _blocked(TARGET_PROVENANCE, "frontier:action_request<->09.targets")

    # 7) Permissions injectées revalidées.
    if _has_internal_leak(permissions):
        return _blocked(LEAK, "permissions")
    if _has_surrogate_codepoint(permissions):
        return _blocked(NON_SCALAR_UNICODE, "permissions")
    if not _valid_permissions(permissions):
        return _blocked(PERMISSIONS_INVALID, "permissions")
    if action_id not in actions_by_id:
        return _blocked(ACTION_NOT_IN_CATALOG, "catalog")

    # 8) impact_context revalidé.
    impact_context = envelope.get("impact_context")
    if _has_internal_leak(impact_context):
        return _blocked(LEAK, "impact_context")
    if _has_surrogate_codepoint(impact_context):
        return _blocked(NON_SCALAR_UNICODE, "impact_context")
    if not (isinstance(impact_context, dict) and set(impact_context) == _IMPACT_KEYS):
        return _blocked(IMPACT_CONTEXT_MALFORMED, "impact_context")
    if not (_is_pair_list(impact_context["assessed_target_refs"]) and _is_str_list(impact_context["risks"])):
        return _blocked(IMPACT_CONTEXT_MALFORMED, "impact_context")
    if not (isinstance(impact_context["global_impact"], str) and impact_context["global_impact"]):
        return _blocked(IMPACT_CONTEXT_MALFORMED, "impact_context")
    assessed_pairs = {(p[0], p[1]) for p in impact_context["assessed_target_refs"]}

    action = actions_by_id[action_id]
    target_refs = sorted([list(p) for p in req_pairs])
    permissions_required = sorted(action["permissions_required"])
    granted = set(permissions["granted"])

    # 9) VERDICT (déterministe).
    approval_required = False
    approval_scope = None
    global_impact = None
    rollback_plan = None
    risks = None
    prerequisites = None

    if not action["requires_action"]:
        action_status = ACTION_NOT_REQUIRED
    elif not set(action["permissions_required"]) <= granted:
        action_status = ACTION_BLOCKED
    elif not req_pairs <= assessed_pairs:                       # GLOBAL_IMPACT_BEFORE_PLAN
        action_status = ACTION_QUARANTINED
    else:
        prerequisites = permissions_required
        risks = sorted(impact_context["risks"])
        global_impact = impact_context["global_impact"]
        rollback_plan = {"revert_action": action_id, "targets": target_refs}
        if action["sensitive_mutation"]:                       # HUMAN_GO_REQUIRED_FOR_SENSITIVE_MUTATION
            action_status = HUMAN_APPROVAL_REQUIRED
            approval_required = True
            approval_scope = {"action_id": action_id, "target_refs": target_refs}
        else:
            action_status = ACTION_PLAN_READY

    justification_refs = {
        "decision_id": sd["decision_id"],
        "decision_content_sha256": sd["CONTENT_SHA256"],
        "action_id": action_id,
        "catalog_version": catalog["version"],
        "catalog_fingerprint": catalog_fp,
        "permissions_version": permissions["version"],
    }

    # 10) action_plan_id (contexte COMPLET, sans self-ref) — seulement si un plan/approbation est émis.
    action_plan_id = None
    if action_status in (ACTION_PLAN_READY, HUMAN_APPROVAL_REQUIRED):
        payload = {
            "decision_id": sd["decision_id"], "decision_content_sha256": sd["CONTENT_SHA256"],
            "action_id": action_id, "target_refs": target_refs,
            "catalog_version": catalog["version"], "catalog_fingerprint": catalog_fp,
            "permissions": {"version": permissions["version"], "granted": sorted(granted)},
            "prerequisites": prerequisites, "risks": risks, "global_impact": global_impact,
            "rollback_plan": rollback_plan, "approval_scope": approval_scope,
        }
        action_plan_id = "ACTION-PLAN-" + _canonical_sha256(payload)

    return _finalize({
        "component": COMPONENT_ID, "version": VERSION, "status": PASS, "blocked_by": None,
        "action_plan_id": action_plan_id, "action_status": action_status,
        "decision_id": sd["decision_id"], "action_id": action_id, "target_refs": target_refs,
        "prerequisites": prerequisites, "permissions_required": permissions_required,
        "risks": risks, "global_impact": global_impact, "rollback_plan": rollback_plan,
        "approval_required": approval_required, "approval_scope": approval_scope,
        "justification_refs": justification_refs, "order_key": ORDER_KEY,
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


def main(envelope: dict) -> dict:
    # Impur (fin) : catalogue chargé du fichier gelé ; permissions INJECTÉES via l'enveloppe (aucune lecture cachée dans run).
    return run_action_admissibility_and_plan(envelope, _load_catalog(), envelope.get("permissions"))
