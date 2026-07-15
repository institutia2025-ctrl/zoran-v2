"""09_STRUCTURED_DECISION — porte 9 du pipeline de raisonnement ZORAN V2.

Transforme EXCLUSIVEMENT une réponse ADMISE par 08 (verdict=ACCEPT, authorize_09 is True) en un
OBJET-DÉCISION déterministe, typé, traçable, SANS nouvelle génération. NE juge pas (08), NE résume
pas, NE complète pas, N'invente pas, NE choisit ni N'exécute aucune action (→ 10). Déterministe,
structuré-only, immuable, fail-closed 00→08, anti-fuite récursive. NO_LLM / NO_NETWORK.

Contrat figé : specs/SPEC_ENGINE_09_STRUCTURED_DECISION.md (+ refinements Fred 2026-07-15).
- Canonicalisation : conservation EXACTE des chaînes (aucun NFC/NFD/trim/CRLF) ; clés triées ;
  séparateurs déterministes ; UTF-8 ; ordre des listes défini par le contrat.
- decision_id + CONTENT_SHA256 via la primitive canonique EXISTANTE `_fingerprint` (aucun second hasher).
- Construction OBJECT_FIRST en 2 phases : payload sans identifiants auto-référents -> decision_id ;
  objet final -> CONTENT_SHA256 (hash de l'objet final SANS CONTENT_SHA256).
"""
from __future__ import annotations

import re

from zoran_v2.canon_determination import _fingerprint as _canon_fingerprint

COMPONENT_ID = "09_STRUCTURED_DECISION"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-09-STRUCTURED-DECISION",
    "META_ID": "META-ZORAN-V2-COMPONENT-09",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_09_STRUCTURED_DECISION · branche feat/engine-09-structured-decision",
    "GUARD_IDS": [
        "STRUCTURED_ONLY", "NO_LLM", "NO_NETWORK", "NO_NEW_INFORMATION", "NO_ACTION_EXECUTION",
        "FAIL_CLOSED", "ANTI_LEAK", "IMMUTABLE", "DETERMINISTIC",
        "ADMITTED_ONLY_08_ACCEPT", "FINGERPRINT_CHAIN_04_07_08", "EXACT_COVERAGE_06_TARGETS",
        "CANONICAL_PRIMITIVE_REUSED", "OBJECT_FIRST_CONTENT_SHA256", "EXACT_STRING_PRESERVATION",
        "DECISION_ID_COVERS_COMPLETE_TARGET_CONTEXT",
    ],
    "TRACEABILITY": "objet-decision {decision_id, CONTENT_SHA256, claims_retained/rejected, constraints, justification_refs} ; primitive canonique _fingerprint reutilisee ; fingerprints 04/07 ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..08 != PASS, verdict != ACCEPT, authorize_09 non-True strict, fingerprint 04/07/08 divergent, requete 06 / reponse 07 malformee, provenance canon/operant/cible hors 06, couverture incomplete, ou fuite",
    "ANTI_REGRESSION": "tests contre-exemples adversariaux + determinisme decision_id/CONTENT_SHA256 + conservation exacte des chaines (NFC/NFD, CRLF/LF, ordre cles) + couverture exacte + anti-fuite + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE", "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_09_STRUCTURED_DECISION",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "derivation deterministe d'un objet-decision a partir d'une reponse ADMISE par 08, sans generation",
    "REJECTED_BEHAVIOR": "generation, appel LLM, resume libre, completion, choix/execution d'action, invention, re-jugement",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
ACCEPT = "ACCEPT"

DECISION_TYPE = "STRUCTURED_ANALYSIS_DECISION_V1"
DECISION_STATUS = "DECIDED_ON_ACCEPT"

RESPONSE_SCHEMA_ID = "RESPONSE_STRUCTURED_ANALYSIS_V1"
EXPECTED_INSTRUCTION_KIND = "STRUCTURED_ANALYSIS_V1"
_RESP_ROOT_KEYS = frozenset(("response_schema", "instruction_kind", "referential_fingerprint", "results"))
_RESULT_KEYS = frozenset(("object_public_id", "frame", "canon_findings", "operant_outcomes"))
_CANON_FINDING_KEYS = frozenset(("canon", "admissible"))
_OC_KEYS_APPLIED = frozenset(("operant", "applied"))
_OC_KEYS_NOT_APPLIED = frozenset(("operant", "applied", "reason_code"))
_REASON_CODES = frozenset(("NOT_APPLICABLE", "INSUFFICIENT_EVIDENCE", "CONSTRAINT_BLOCKED", "CANON_CONFLICT"))
_TARGET_KEYS = frozenset(("object_public_id", "kind_public", "frame", "canons", "operants"))
_OBJ_PUBLIC_ID_RE = re.compile(r"^OBJ-\d{4,}$")

_PII_SEP = "\x1f"
_FORBIDDEN_KEYS = frozenset((
    "object_key", "normalized", "provenance", "object_id_map",
    "raw_text", "content", "prompt", "user_value", "explanation",
))

_STEPS_00_08 = (
    ("runtime_check", "00_RUNTIME_CHECK"),
    ("object_discovery", "01_OBJECT_DISCOVERY"),
    ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
    ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
    ("canon_determination", "04_CANON_DETERMINATION"),
    ("coherence_engine", "05_COHERENCE_ENGINE"),
    ("llm_request_build", "06_LLM_REQUEST_BUILD"),
    ("llm_execution", "07_LLM_EXECUTION"),
    ("coherence_2", "08_COHERENCE_2"),
)

# Codes blocked_by DÉDIÉS 09 (le champ blocked_by = "<code>@<frontière/moteur source>", P2).
UPSTREAM_NOT_PASS = "09_STRUCTURED_DECISION_UPSTREAM_NOT_PASS"
NOT_ADMITTED = "09_STRUCTURED_DECISION_NOT_ADMITTED"
FINGERPRINT_CHAIN = "09_STRUCTURED_DECISION_FINGERPRINT_CHAIN"
REQUEST_MALFORMED = "09_STRUCTURED_DECISION_REQUEST_MALFORMED"
RESPONSE_MALFORMED = "09_STRUCTURED_DECISION_RESPONSE_MALFORMED"
PROVENANCE = "09_STRUCTURED_DECISION_PROVENANCE"
COVERAGE = "09_STRUCTURED_DECISION_COVERAGE"
LEAK = "09_STRUCTURED_DECISION_LEAK"

ORDER_KEY = "structured_decision_deterministe_puis_scellement"

# Objet final PLAT (P-C2). CONTENT_SHA256 avant order_key.
OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "decision_id", "decision_type", "decision_status", "targets",
    "claims_retained", "claims_rejected", "constraints", "justification_refs",
    "referential_fingerprint", "source_response_fingerprint", "CONTENT_SHA256", "order_key",
)
_DECISION_FIELDS = (
    "decision_id", "decision_type", "decision_status", "targets",
    "claims_retained", "claims_rejected", "constraints", "justification_refs",
    "referential_fingerprint", "source_response_fingerprint",
)


def _canonical_sha256(value) -> str:
    """Réutilise DIRECTEMENT la primitive canonique existante `_fingerprint` (aucun second hasher).
    `_fingerprint` attend une liste de records triables par 'id' -> on emballe la valeur en un record
    unique déterministe. Sérialisation : json trié + séparateurs déterministes + UTF-8, CHAÎNES EXACTES."""
    return _canon_fingerprint([{"id": "__zoran_canonical__", "value": value}])


def _finalize(fields: dict) -> dict:
    """Assemble l'objet final PLAT (ordre OUTPUT_KEYS) puis calcule CONTENT_SHA256 sur l'objet SANS ce champ."""
    obj = {k: fields.get(k) for k in OUTPUT_KEYS}
    obj["CONTENT_SHA256"] = None
    obj["CONTENT_SHA256"] = _canonical_sha256({k: v for k, v in obj.items() if k != "CONTENT_SHA256"})
    return obj


def _blocked(code: str, source: str) -> dict:
    fields = {"component": COMPONENT_ID, "version": VERSION, "status": BLOCKED,
              "blocked_by": f"{code}@{source}", "order_key": ORDER_KEY}
    return _finalize(fields)


def _has_internal_leak(value) -> bool:
    if isinstance(value, str):
        return _PII_SEP in value
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, str) and (k in _FORBIDDEN_KEYS or _PII_SEP in k):
                return True
            if _has_internal_leak(k) or _has_internal_leak(v):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_has_internal_leak(e) for e in value)
    return False


def _is_str_list(x) -> bool:
    return isinstance(x, list) and all(isinstance(e, str) and e for e in x)


def _is_bool(x) -> bool:
    return isinstance(x, bool)


def _validate_targets_06(request, fp04):
    if not isinstance(request, dict):
        return None
    if request.get("referential_fingerprint") != fp04:
        return None
    targets = request.get("targets")
    if not (isinstance(targets, list) and targets):
        return None
    expected = {}
    for t in targets:
        if not isinstance(t, dict) or set(t) != _TARGET_KEYS:
            return None
        opid, frame = t.get("object_public_id"), t.get("frame")
        if not (isinstance(opid, str) and _OBJ_PUBLIC_ID_RE.match(opid)):
            return None
        if not (isinstance(t.get("kind_public"), str) and isinstance(frame, str) and frame):
            return None
        canons, operants = t.get("canons"), t.get("operants")
        if not (_is_str_list(canons) and _is_str_list(operants)):
            return None
        if len(set(canons)) != len(canons) or len(set(operants)) != len(operants):
            return None
        if (opid, frame) in expected:
            return None
        expected[(opid, frame)] = {"canons": set(canons), "operants": set(operants),
                                   "kind_public": t["kind_public"]}
    return expected


def _validate_response_07(response, fp04):
    if not isinstance(response, dict) or set(response) != _RESP_ROOT_KEYS:
        return None
    if response.get("response_schema") != RESPONSE_SCHEMA_ID:
        return None
    if response.get("instruction_kind") != EXPECTED_INSTRUCTION_KIND:
        return None
    if response.get("referential_fingerprint") != fp04:
        return None
    results = response.get("results")
    if not isinstance(results, list):
        return None
    seen = set()
    for r in results:
        if not isinstance(r, dict) or set(r) != _RESULT_KEYS:
            return None
        opid, frame = r.get("object_public_id"), r.get("frame")
        if not (isinstance(opid, str) and isinstance(frame, str)):
            return None
        if (opid, frame) in seen:
            return None
        seen.add((opid, frame))
        cfs, ops = r.get("canon_findings"), r.get("operant_outcomes")
        if not (isinstance(cfs, list) and isinstance(ops, list)):
            return None
        seen_canon = set()
        for cf in cfs:
            if not isinstance(cf, dict) or set(cf) != _CANON_FINDING_KEYS:
                return None
            if not (isinstance(cf.get("canon"), str) and cf["canon"] and _is_bool(cf.get("admissible"))):
                return None
            if cf["canon"] in seen_canon:
                return None
            seen_canon.add(cf["canon"])
        seen_op = set()
        for oc in ops:
            if not isinstance(oc, dict):
                return None
            applied = oc.get("applied")
            if not _is_bool(applied):
                return None
            if applied:
                if set(oc) != _OC_KEYS_APPLIED or not (isinstance(oc.get("operant"), str) and oc["operant"]):
                    return None
            else:
                if (set(oc) != _OC_KEYS_NOT_APPLIED or not (isinstance(oc.get("operant"), str) and oc["operant"])
                        or oc.get("reason_code") not in _REASON_CODES):
                    return None
            if oc["operant"] in seen_op:
                return None
            seen_op.add(oc["operant"])
    return results


def run_structured_decision(envelope: dict) -> dict:
    """Fonction PURE : envelope(00→08) -> objet-décision structuré PLAT, ou BLOCKED (fail-closed)."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    # 1) Prérequis 00→08 = PASS (tout ABANDON/dégradé/incohérent -> BLOCKED).
    for key, comp in _STEPS_00_08:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(UPSTREAM_NOT_PASS, comp)

    # 2) Admissibilité 08 : verdict==ACCEPT ET authorize_09 is True (identité stricte).
    c2 = envelope["coherence_2"]
    if c2.get("verdict") != ACCEPT:
        return _blocked(NOT_ADMITTED, "08_COHERENCE_2.verdict")
    if c2.get("authorize_09") is not True:
        return _blocked(NOT_ADMITTED, "08_COHERENCE_2.authorize_09")
    fp08 = c2.get("referential_fingerprint")
    if not (isinstance(fp08, str) and fp08):
        return _blocked(FINGERPRINT_CHAIN, "08_COHERENCE_2.referential_fingerprint")

    # 3) Chaîne de fingerprint : 04 gelé == 08.
    cd = envelope["canon_determination"]
    referential = cd.get("canon_referential")
    fp04 = referential.get("fingerprint") if isinstance(referential, dict) else None
    if not (isinstance(fp04, str) and fp04 and fp04 == fp08):
        return _blocked(FINGERPRINT_CHAIN, "04_CANON_DETERMINATION.fingerprint")

    # 4) Anti-fuite récursif sur les entrées consommées.
    lrb = envelope["llm_request_build"]
    ex = envelope["llm_execution"]
    if _has_internal_leak(lrb.get("llm_request")) or _has_internal_leak(ex.get("response")):
        return _blocked(LEAK, "frontier:06/07.leak")

    # 5) Requête 06 AUTORITAIRE : univers des cibles (indépendant du résultat).
    if lrb.get("authorized") is not True:
        return _blocked(REQUEST_MALFORMED, "06_LLM_REQUEST_BUILD.authorized")
    expected = _validate_targets_06(lrb.get("llm_request"), fp04)
    if expected is None:
        return _blocked(REQUEST_MALFORMED, "06_LLM_REQUEST_BUILD.targets")

    # 6) Réponse 07 ADMISE : schéma exact + fingerprint == 04.
    if ex.get("executed") is not True:
        return _blocked(RESPONSE_MALFORMED, "07_LLM_EXECUTION.executed")
    results = _validate_response_07(ex.get("response"), fp04)
    if results is None:
        return _blocked(RESPONSE_MALFORMED, "07_LLM_EXECUTION.response")

    # 7) Provenance : chaque (opid,frame)/canon/opérant ⊆ attendus 06.
    present = {}
    for r in results:
        pair = (r["object_public_id"], r["frame"])
        if pair not in expected:
            return _blocked(PROVENANCE, "frontier:07.response<->06.targets")
        exp = expected[pair]
        for cf in r["canon_findings"]:
            if cf["canon"] not in exp["canons"]:
                return _blocked(PROVENANCE, "frontier:07.canon<->06")
        for oc in r["operant_outcomes"]:
            if oc["operant"] not in exp["operants"]:
                return _blocked(PROVENANCE, "frontier:07.operant<->06")
        present[pair] = r

    # 8) COUVERTURE EXACTE (P1).
    if set(present) != set(expected):
        return _blocked(COVERAGE, "frontier:06.targets_coverage")

    # 9) Dérivation DÉTERMINISTE (verbatim, chaînes EXACTES, tri canonique des listes).
    claims_retained, claims_rejected, constraints = [], [], []
    canon_refs, operant_refs = set(), set()
    for pair in sorted(expected):
        r = present[pair]
        opid, frame = pair
        for cf in sorted(r["canon_findings"], key=lambda c: c["canon"]):
            entry = {"object_public_id": opid, "frame": frame, "canon": cf["canon"]}
            (claims_retained if cf["admissible"] else claims_rejected).append(entry)
            canon_refs.add(cf["canon"])
        for oc in sorted(r["operant_outcomes"], key=lambda o: o["operant"]):
            c = {"object_public_id": opid, "frame": frame, "operant": oc["operant"], "applied": oc["applied"]}
            if not oc["applied"]:
                c["reason_code"] = oc["reason_code"]
            constraints.append(c)
            operant_refs.add(oc["operant"])

    targets = [{"object_public_id": o, "frame": f} for (o, f) in sorted(expected)]
    justification_refs = {
        "canon_refs": sorted(canon_refs),
        "operant_refs": sorted(operant_refs),
        "target_refs": [[o, f] for (o, f) in sorted(expected)],
        "response_fingerprint": fp04,
        "referential_fingerprint": fp04,
    }

    # 10) PHASE 1 : decision_id = sha256 d'un payload SANS identifiants auto-référents (ni decision_id, ni CONTENT_SHA256).
    normalized_response = [
        {"object_public_id": o, "frame": f,
         "canon_findings": sorted(({"canon": cf["canon"], "admissible": cf["admissible"]}
                                   for cf in present[(o, f)]["canon_findings"]), key=lambda c: c["canon"]),
         "operant_outcomes": sorted(({k: oc[k] for k in sorted(oc)}
                                     for oc in present[(o, f)]["operant_outcomes"]), key=lambda o2: o2["operant"])}
        for (o, f) in sorted(expected)
    ]
    normalized_targets = [
        {"object_public_id": o, "kind_public": expected[(o, f)]["kind_public"], "frame": f,
         "canons": sorted(expected[(o, f)]["canons"]), "operants": sorted(expected[(o, f)]["operants"])}
        for (o, f) in sorted(expected)
    ]
    payload_decision = {
        "decision_type": DECISION_TYPE, "verdict": ACCEPT, "referential_fingerprint": fp04,
        "targets_06": normalized_targets, "response_07": normalized_response,
        "claims_retained": claims_retained, "claims_rejected": claims_rejected,
        "constraints": constraints, "justification_refs": justification_refs,
    }
    decision_id = "DECISION-" + _canonical_sha256(payload_decision)

    # 11) PHASE 2 : objet final PLAT + CONTENT_SHA256 (hash de l'objet final SANS CONTENT_SHA256). Aucune auto-référence.
    fields = {
        "component": COMPONENT_ID, "version": VERSION, "status": PASS, "blocked_by": None,
        "decision_id": decision_id, "decision_type": DECISION_TYPE, "decision_status": DECISION_STATUS,
        "targets": targets, "claims_retained": claims_retained, "claims_rejected": claims_rejected,
        "constraints": constraints, "justification_refs": justification_refs,
        "referential_fingerprint": fp04, "source_response_fingerprint": fp04, "order_key": ORDER_KEY,
    }
    return _finalize(fields)


def main(envelope: dict) -> dict:
    return run_structured_decision(envelope)
