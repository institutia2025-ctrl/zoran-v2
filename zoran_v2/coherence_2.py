"""08_COHERENCE_2 — porte 8 du pipeline de raisonnement ZORAN V2 (2e passe de cohérence).

SECONDE mesure de cohérence, POST-LLM, DÉTERMINISTE, SANS nouvel appel LLM. Valide la
réponse de 07 contre le référentiel GELÉ (04) et l'état pré-LLM (05), puis émet un verdict
d'admissibilité qui gate 09. NE génère pas, n'appelle AUCUN LLM, ne relit AUCUN texte brut
utilisateur pour reconstruire une vérité parallèle.

Contrat FIGÉ (Fred 2026-07-15) :
- 07 reste inchangé (transporte la réponse brute du client). 08 porte la validation du
  contrat de réponse `RESPONSE_STRUCTURED_ANALYSIS_V1` + la mesure de cohérence post-LLM.
- Formule CANONIQUE inchangée : S_post = (beta * delta_phi_post) / (1 + T_post + sigma_post),
  beta = 1.0 en V1.
- delta_phi_post = part des cibles 06 dont la réponse fournit un résultat COMPLET : identifiable
  (object_public_id ∈ requête), bon frame, ≥1 canon ATTENDU couvert, et chaque opérant ATTENDU
  couvert (applied=true, ou applied=false justifié NON-INSUFFISANT).
- T_post = (conflits + violations) / n_cibles. Violations structurelles : id inconnu, frame
  inconnu, canon hors attendu, opérant hors attendu, cible inventée, cible requise absente,
  fingerprint absent/≠. Conflits = contradictions (même (opid, canon) admissible opposé).
- sigma_post = coefficient de variation du nombre de canon_findings VALIDES ET ATTENDUS par
  cible (cibles absentes = 0). Aucune analyse sémantique libre.
- cinématique : S_pre (05), S_post, delta_S, trend. Pas de dS/dt (< 3 observations).

Séparation BLOCKED vs REJECT (le LLM peut mal répondre : 08 le REJETTE, il ne se met pas en
panne) :
- BLOCKED : 00→07 ≠ PASS ; 07.executed != true ; enveloppe interne malformée ; fingerprint 04
  absent/invalide ; veto ressource 05 absent ou non strictement True.
- REJECT : réponse non-dict, schéma incorrect, fingerprint de réponse ≠, cible/canon/opérant
  inventé, contradiction, fuite de clé interne, résultats vides.
- QUARANTINE : schéma valide, rien d'inventé, fingerprint conforme, aucune violation critique,
  mais partiellement complet OU S_post < S_pre.
- ACCEPT ⇔ schéma exact ∧ fingerprint conforme ∧ 0 violation ∧ 0 contradiction ∧ 0 cible
  manquante ∧ delta_phi_post = 1 ∧ S_post ≥ S_pre. authorize_09 = true UNIQUEMENT pour ACCEPT.
"""
from __future__ import annotations

import math
import re
import statistics

COMPONENT_ID = "08_COHERENCE_2"
VERSION = "1.0.0"

CANONICAL_FORMULA = "S = (beta * delta_phi) / (1 + T + sigma)"
BETA_V1 = 1.0

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-08-COHERENCE-2",
    "META_ID": "META-ZORAN-V2-COMPONENT-08",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_08_COHERENCE_2 · branche mission/engine-08-coherence-2 · contrat fige Fred 2026-07-15",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "CANONICAL_FORMULA_LOCKED",
        "NO_LLM",
        "NO_GENERATION",
        "NO_NETWORK",
        "NO_MEMORY",
        "RESPONSE_SCHEMA_VALIDATED",
        "REQUEST_06_REVALIDATED_STRICT_FAIL_CLOSED",
        "REQUEST_06_AUTHORIZED_REVALIDATED",
        "COHERENCE_S_06_MATCHES_05_FINITE",
        "REFERENTIAL_FINGERPRINT_04_MATCHES_05",
        "RESOURCE_VETO_05_REVALIDATED_STRICT_TRUE",
        "CANONS_OPERANTS_06_TRACE_04_03",
        "REFERENTIAL_FINGERPRINT_VERIFIED",
        "PROVENANCE_TO_03_04_05_06",
        "NO_PII_FROM_RESPONSE",
        "POST_LLM_ADMISSIBILITY_GATE_BEFORE_09",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "verdict + coherence_post {delta_phi,tension,sigma,S} + cinematic {S_pre,S_post,delta_S,trend} + violations/conflicts/missing/unknown ; fingerprint porte ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest (reponses mock conformes/degradees) + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..07 != PASS, 07 non execute, veto ressource 05, enveloppe malformee ou fingerprint 04 absent ; verdict REJECT si reponse non conforme/inventee/fuite ; QUARANTINE si partiel ou S_post<S_pre ; authorize_09 seulement si ACCEPT",
    "ANTI_REGRESSION": "tests schema strict + veto ressource 05 strict True + provenance 04/06 + fingerprint + anti-fuite recursive + BLOCKED/REJECT/QUARANTINE/ACCEPT + determinisme + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_08_COHERENCE_2",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "validation deterministe du contrat de reponse 07 + mesure de coherence post-LLM (formule canonique) + verdict d'admissibilite gate 09",
    "REJECTED_BEHAVIOR": "generation, appel LLM, parser semantique libre, relecture de texte brut utilisateur, panne (BLOCKED) sur une mauvaise reponse LLM (doit REJETER)",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
ACCEPT = "ACCEPT"
REJECT = "REJECT"
QUARANTINE = "QUARANTINE"

# Prérequis pipeline (fail-closed -> BLOCKED).
_STEPS_00_07 = (
    ("runtime_check", "00_RUNTIME_CHECK"),
    ("object_discovery", "01_OBJECT_DISCOVERY"),
    ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
    ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
    ("canon_determination", "04_CANON_DETERMINATION"),
    ("coherence_engine", "05_COHERENCE_ENGINE"),
    ("llm_request_build", "06_LLM_REQUEST_BUILD"),
    ("llm_execution", "07_LLM_EXECUTION"),
)
NOT_EXECUTED = "07_LLM_EXECUTION_NOT_EXECUTED"
ENVELOPE_MALFORMED = "08_COHERENCE_2_ENVELOPE_MALFORMED"
FINGERPRINT_MISSING = "08_COHERENCE_2_FINGERPRINT_MISSING"
FINGERPRINT_CHAIN_MISMATCH = "08_COHERENCE_2_FINGERPRINT_CHAIN_05_04_MISMATCH"
RESOURCE_VETO_05 = "05_COHERENCE_ENGINE_RESOURCE_VETO"
ORDER_KEY = "coherence_post_llm"

# Contrat de réponse FIGÉ (07.response).
RESPONSE_SCHEMA_ID = "RESPONSE_STRUCTURED_ANALYSIS_V1"
EXPECTED_INSTRUCTION_KIND = "STRUCTURED_ANALYSIS_V1"
_ROOT_KEYS = frozenset(("response_schema", "instruction_kind", "referential_fingerprint", "results"))
_RESULT_KEYS = frozenset(("object_public_id", "frame", "canon_findings", "operant_outcomes"))
_CANON_FINDING_KEYS = frozenset(("canon", "admissible"))
_OPERANT_OUTCOME_KEYS_APPLIED = frozenset(("operant", "applied"))            # applied=true : reason_code ABSENT
_OPERANT_OUTCOME_KEYS_NOT_APPLIED = frozenset(("operant", "applied", "reason_code"))  # applied=false : reason_code présent
_REASON_CODES = frozenset(("NOT_APPLICABLE", "INSUFFICIENT_EVIDENCE", "CONSTRAINT_BLOCKED", "CANON_CONFLICT"))
# reason_codes qui NE comptent PAS un opérant comme couvert (incomplet -> QUARANTINE).
_REASON_INCOMPLETE = frozenset(("INSUFFICIENT_EVIDENCE",))

# Anti-fuite RÉCURSIF : aucune clé interne, aucune valeur portant le séparateur d'object_key.
_PII_FORBIDDEN_KEYS = frozenset((
    "object_key", "normalized", "provenance", "object_id_map",
    "raw_text", "content", "prompt", "user_value", "explanation",
))
_PII_SEP = "\x1f"

# Contrat de la requête AUTORITAIRE 06 (llm_request) — 08 la RE-VALIDE (fail-closed -> BLOCKED)
# au lieu de faire confiance à 07 : une enveloppe 06 tampérée mais status=PASS ne doit jamais
# servir de source de vérité (findings GC-08-001/002/003).
_REQUEST_ROOT_KEYS = frozenset((
    "instruction_kind", "referential_fingerprint", "coherence_S",
    "frames", "targets", "pii_policy",
))
_REQUEST_TARGET_KEYS = frozenset((
    "object_public_id", "kind_public", "frame", "canons", "operants",
))
_OBJ_PUBLIC_ID_RE = re.compile(r"^OBJ-\d{4,}$")
_EXPECTED_PII_POLICY = "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT"

# Codes de violation (non-BLOCKED).
V_SCHEMA_INVALID = "RESPONSE_SCHEMA_INVALID"
V_FINGERPRINT_MISMATCH = "RESPONSE_FINGERPRINT_MISMATCH"
V_PII_LEAK = "PII_LEAK"
V_EMPTY_RESULTS = "EMPTY_RESULTS"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by", "verdict",
    "coherence_post", "cinematic", "violations", "conflicts",
    "missing_targets", "unknown_targets", "referential_fingerprint",
    "authorize_09", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by, "verdict": None,
        "coherence_post": None, "cinematic": None,
        "violations": [], "conflicts": [],
        "missing_targets": [], "unknown_targets": [],
        "referential_fingerprint": None, "authorize_09": False, "order_key": ORDER_KEY,
    }


def _has_internal_leak(value) -> bool:
    """True si une clé interne interdite OU le séparateur d'object_key apparaît (récursif)."""
    if isinstance(value, str):
        return _PII_SEP in value
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, str) and (k in _PII_FORBIDDEN_KEYS or _PII_SEP in k):
                return True
            if _has_internal_leak(k) or _has_internal_leak(v):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_has_internal_leak(e) for e in value)
    return False


def _is_bool(x) -> bool:
    return isinstance(x, bool)


def _is_str_list(x) -> bool:
    return isinstance(x, list) and all(isinstance(e, str) for e in x)


def _validate_request_06(request, fp04, s_pre, canon_ids, operant_ids) -> bool:
    """Re-valide la requête AUTORITAIRE 06 avec la MÊME rigueur que la frontière 07 (fail-closed).

    08 utilise 06 comme source de vérité des cibles attendues : on ne fait confiance à AUCUN champ
    de 06 — une source mal validée fausserait la certification post-LLM (GC-08-001..005). Impose :
    schéma racine EXACT, instruction_kind + pii_policy canoniques, fingerprint 06 == fingerprint 04,
    coherence_S 06 FINI ET == S de 05 (arrondi canonique, GC-08-004), cibles = liste non vide au
    schéma EXACT, object_public_id opaque `OBJ-nnnn`, kind_public/frame str, canons & operants listes
    de STR UNIQUEMENT tracant a l'amont (canons ⊆ ids 04 gelés, operants ⊆ opérants 03), AUCUN
    doublon (object_public_id, frame) ni canon/opérant dupliqué, `frames` racine == frames des cibles,
    et aucune clé interne / séparateur (fuite).
    """
    if _has_internal_leak(request):
        return False
    if not isinstance(request, dict) or set(request) != _REQUEST_ROOT_KEYS:
        return False
    if request.get("instruction_kind") != EXPECTED_INSTRUCTION_KIND:
        return False
    if request.get("pii_policy") != _EXPECTED_PII_POLICY:
        return False
    if request.get("referential_fingerprint") != fp04:  # fingerprint 06 DOIT == 04 gelé
        return False
    s = request.get("coherence_S")  # GC-08-004 : fini ET == S autoritaire de 05 (chaîne 05->06 fermée)
    if not (isinstance(s, (int, float)) and not isinstance(s, bool)
            and math.isfinite(s) and round(float(s), 6) == s_pre):
        return False
    if not _is_str_list(request.get("frames")):
        return False
    targets = request.get("targets")
    if not (isinstance(targets, list) and targets):
        return False
    seen_targets = set()
    for t in targets:
        if not isinstance(t, dict) or set(t) != _REQUEST_TARGET_KEYS:
            return False
        opid = t.get("object_public_id")
        if not (isinstance(opid, str) and _OBJ_PUBLIC_ID_RE.match(opid)):
            return False
        frame = t.get("frame")
        if not (isinstance(t.get("kind_public"), str) and isinstance(frame, str)):
            return False
        if (opid, frame) in seen_targets:            # doublon (object_public_id, frame) -> malformé
            return False
        seen_targets.add((opid, frame))
        canons, operants = t.get("canons"), t.get("operants")
        if not (_is_str_list(canons) and _is_str_list(operants)):
            return False
        if len(set(canons)) != len(canons) or len(set(operants)) != len(operants):  # doublon canon/opérant
            return False
        # Provenance amont : chaque canon ∈ référentiel 04 gelé, chaque opérant ∈ analyse 03.
        if not (set(canons) <= canon_ids and set(operants) <= operant_ids):
            return False
    # Cohérence root<->cibles : `frames` racine DOIT être exactement l'ensemble des frames des cibles.
    if set(request["frames"]) != {t["frame"] for t in targets}:
        return False
    return True


def run_coherence_2(envelope: dict) -> dict:
    """Fonction PURE : envelope(00→07) -> validation réponse + cohérence post-LLM + verdict."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    # 1) Prérequis 00→07 = PASS -> sinon BLOCKED.
    for key, comp in _STEPS_00_07:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(comp)

    # 2) 07 doit avoir RÉELLEMENT exécuté (sinon rien à juger).
    ex = envelope["llm_execution"]
    if ex.get("executed") is not True:
        return _blocked(NOT_EXECUTED)

    # 3) Fingerprint 04 autoritaire + VOCABULAIRE autoritaire (ids de canons 04 gelés, opérants 03).
    cd = envelope["canon_determination"]
    referential = cd.get("canon_referential")
    fingerprint = referential.get("fingerprint") if isinstance(referential, dict) else None
    if not (isinstance(fingerprint, str) and fingerprint):
        return _blocked(FINGERPRINT_MISSING)
    ce = envelope["coherence_engine"]
    coherence5 = ce.get("coherence")
    resource5 = ce.get("resource")
    if not (isinstance(resource5, dict) and resource5.get("authorize_llm") is True):
        return _blocked(RESOURCE_VETO_05)
    fingerprint5 = coherence5.get("referential_fingerprint") if isinstance(coherence5, dict) else None
    if not (isinstance(fingerprint5, str) and fingerprint5):
        return _blocked(FINGERPRINT_MISSING)
    if fingerprint != fingerprint5:
        return _blocked(FINGERPRINT_CHAIN_MISMATCH)
    canon_ids = {c["id"] for c in (referential.get("canons") or [])
                 if isinstance(c, dict) and isinstance(c.get("id"), str)}
    oa = envelope["operants_operes"]
    operant_ids = {op for a in (oa.get("analysis") or []) if isinstance(a, dict)
                   for op in (a.get("operants") or []) if isinstance(op, str)}

    # 4) S_pre depuis 05 — validé FINI, AVANT la validation 06 (recoupement coherence_S, GC-08-004).
    s_raw = coherence5.get("S") if isinstance(coherence5, dict) else None
    if not (isinstance(s_raw, (int, float)) and not isinstance(s_raw, bool) and math.isfinite(s_raw)):
        return _blocked(ENVELOPE_MALFORMED)
    s_pre = round(float(s_raw), 6)

    # 5) Requête 06 AUTORITAIRE : autorisation RÉELLE (GC-08-005) + re-validation STRICTE (fail-closed),
    #    sans confiance à 07. On ne fait confiance à AUCUN champ de 06 : coherence_S==05, canons⊆04,
    #    operants⊆03, fingerprint==04 -> chaîne 05→06→08 fermée (GC-08-001..005).
    lrb = envelope["llm_request_build"]
    if lrb.get("authorized") is not True:
        return _blocked(ENVELOPE_MALFORMED)
    request = lrb.get("llm_request")
    if not _validate_request_06(request, fingerprint, s_pre, canon_ids, operant_ids):
        return _blocked(ENVELOPE_MALFORMED)
    # Cibles attendues, clef (object_public_id, frame). L'unicité est déjà garantie par la validation.
    expected = {
        (t["object_public_id"], t["frame"]): {"canons": set(t["canons"]), "operants": set(t["operants"])}
        for t in request["targets"]
    }

    # ---- status PASS : on JUGE la réponse (une mauvaise réponse -> REJECT, jamais BLOCKED) ----
    return _judge(ex.get("response"), request, expected, fingerprint, s_pre)


def _degenerate(verdict, violations, fingerprint, s_pre, conflicts=None,
                missing=None, unknown=None) -> dict:
    """Sortie PASS non-ACCEPT à delta_phi=0 (réponse non exploitable structurellement)."""
    coherence_post = {
        "beta": BETA_V1, "delta_phi": 0.0, "tension": 0.0, "sigma": 0.0, "S": 0.0,
        "S_kind": "S_structural_v1", "S_range": [0.0, 1.0], "formula": CANONICAL_FORMULA,
    }
    return _emit(PASS, None, verdict, coherence_post, s_pre, 0.0, sorted(set(violations)),
                 conflicts or [], missing or [], unknown or [], fingerprint,
                 authorize_09=False)


def _emit(status, blocked_by, verdict, coherence_post, s_pre, s_post, violations,
          conflicts, missing, unknown, fingerprint, authorize_09) -> dict:
    delta_s = round(s_post - s_pre, 6)
    trend = "IMPROVING" if delta_s > 0 else ("DEGRADING" if delta_s < 0 else "STABLE")
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": status, "blocked_by": blocked_by, "verdict": verdict,
        "coherence_post": coherence_post,
        "cinematic": {"S_pre": s_pre, "S_post": round(s_post, 6),
                      "delta_S": delta_s, "trend": trend},
        "violations": violations, "conflicts": conflicts,
        "missing_targets": missing, "unknown_targets": unknown,
        "referential_fingerprint": fingerprint,
        "authorize_09": authorize_09, "order_key": ORDER_KEY,
    }


def _outcome_ok(outcome) -> bool:
    """Structure valide d'un operant_outcome (clés/typage/enum stricts)."""
    if not isinstance(outcome, dict):
        return False
    applied = outcome.get("applied")
    if not _is_bool(applied):
        return False
    if applied:
        return set(outcome) == _OPERANT_OUTCOME_KEYS_APPLIED and isinstance(outcome.get("operant"), str)
    return (set(outcome) == _OPERANT_OUTCOME_KEYS_NOT_APPLIED
            and isinstance(outcome.get("operant"), str)
            and outcome.get("reason_code") in _REASON_CODES)


def _schema_ok(response, fingerprint) -> bool:
    """Validation STRUCTURELLE stricte du contrat RESPONSE_STRUCTURED_ANALYSIS_V1 (hors provenance)."""
    if not isinstance(response, dict) or set(response) != _ROOT_KEYS:
        return False
    if response.get("response_schema") != RESPONSE_SCHEMA_ID:
        return False
    if response.get("instruction_kind") != EXPECTED_INSTRUCTION_KIND:
        return False
    if not isinstance(response.get("results"), list):
        return False
    seen_results = set()
    for r in response["results"]:
        if not isinstance(r, dict) or set(r) != _RESULT_KEYS:
            return False
        opid, frame = r.get("object_public_id"), r.get("frame")
        if not (isinstance(opid, str) and isinstance(frame, str)):
            return False
        if (opid, frame) in seen_results:          # unicité (object_public_id, frame)
            return False
        seen_results.add((opid, frame))
        cfs = r.get("canon_findings")
        ops = r.get("operant_outcomes")
        if not (isinstance(cfs, list) and isinstance(ops, list)):
            return False
        seen_canon = set()
        for cf in cfs:
            if not isinstance(cf, dict) or set(cf) != _CANON_FINDING_KEYS:
                return False
            if not (isinstance(cf.get("canon"), str) and _is_bool(cf.get("admissible"))):
                return False
            if cf["canon"] in seen_canon:           # unicité canon dans la cible
                return False
            seen_canon.add(cf["canon"])
        seen_op = set()
        for outcome in ops:
            if not _outcome_ok(outcome):
                return False
            if outcome["operant"] in seen_op:       # unicité opérant dans la cible
                return False
            seen_op.add(outcome["operant"])
    return True


def _judge(response, request, expected, fingerprint, s_pre) -> dict:
    n_targets = len(expected)

    # Réponse non-dict / schéma illisible -> REJECT (pas BLOCKED).
    if _has_internal_leak(response):
        return _degenerate(REJECT, [V_PII_LEAK], fingerprint, s_pre)
    if not _schema_ok(response, fingerprint):
        return _degenerate(REJECT, [V_SCHEMA_INVALID], fingerprint, s_pre)

    # Fingerprint de réponse doit == fingerprint 04 gelé.
    if response.get("referential_fingerprint") != fingerprint:
        return _degenerate(REJECT, [V_FINGERPRINT_MISMATCH], fingerprint, s_pre)

    request_opids = {opid for (opid, _fr) in expected}
    violations, conflicts, unknown, complete_targets = [], [], [], set()
    canon_findings_count = {key: 0 for key in expected}
    admissible_by_element = {}  # (opid, canon) -> set(bool) pour détecter contradictions

    for r in response["results"]:
        opid, frame = r["object_public_id"], r["frame"]
        key = (opid, frame)
        if opid not in request_opids:
            unknown.append(f"{opid}:{frame}")
            violations.append(f"UNKNOWN_TARGET:{opid}:{frame}")
            continue
        if key not in expected:
            violations.append(f"FRAME_NOT_EXPECTED:{opid}:{frame}")
            continue
        exp = expected[key]
        addressed_expected_canons = set()
        for cf in r["canon_findings"]:
            canon = cf["canon"]
            if canon not in exp["canons"]:
                violations.append(f"CANON_NOT_EXPECTED:{opid}:{frame}:{canon}")
                continue
            addressed_expected_canons.add(canon)
            canon_findings_count[key] += 1
            admissible_by_element.setdefault((opid, canon), set()).add(cf["admissible"])
        covered_operants = set()
        for outcome in r["operant_outcomes"]:
            op = outcome["operant"]
            if op not in exp["operants"]:
                violations.append(f"OPERANT_NOT_EXPECTED:{opid}:{frame}:{op}")
                continue
            if outcome["applied"] or outcome.get("reason_code") not in _REASON_INCOMPLETE:
                covered_operants.add(op)
        # Cible COMPLÈTE : ≥1 canon attendu couvert ET tous les opérants attendus couverts.
        if addressed_expected_canons and exp["operants"] <= covered_operants:
            complete_targets.add(key)

    # Contradictions : même (opid, canon) admissible à la fois vrai et faux.
    for (opid, canon), vals in sorted(admissible_by_element.items()):
        if len(vals) > 1:
            conflicts.append({"object_public_id": opid, "canon": canon, "reason": "CONTRADICTION"})

    present_keys = {(r["object_public_id"], r["frame"]) for r in response["results"]}
    missing = sorted(f"{opid}:{fr}" for (opid, fr) in expected if (opid, fr) not in present_keys)
    for m in missing:
        violations.append(f"MISSING_TARGET:{m}")

    if not response["results"]:
        violations.append(V_EMPTY_RESULTS)

    violations = sorted(set(violations))
    unknown = sorted(set(unknown))

    # Métriques déterministes.
    delta_phi = 0.0 if n_targets == 0 else round(len(complete_targets) / n_targets, 6)
    n_viol = len(violations) + len(conflicts)
    tension = 0.0 if n_targets == 0 else round(n_viol / n_targets, 6)
    counts = [canon_findings_count[k] for k in sorted(expected)]
    if len(counts) >= 2 and statistics.mean(counts) > 0:
        sigma = round(statistics.pstdev(counts) / statistics.mean(counts), 6)
    else:
        sigma = 0.0
    s_post = round((BETA_V1 * delta_phi) / (1.0 + tension + sigma), 6)

    # Violations CRITIQUES -> REJECT ; sinon complétude + delta_S décident ACCEPT/QUARANTINE.
    critical = bool(conflicts) or bool(unknown) or not response["results"] or any(
        v.split(":", 1)[0] in ("CANON_NOT_EXPECTED", "OPERANT_NOT_EXPECTED",
                               "FRAME_NOT_EXPECTED", "UNKNOWN_TARGET",
                               V_SCHEMA_INVALID, V_FINGERPRINT_MISMATCH, V_PII_LEAK)
        for v in violations)
    delta_s = round(s_post - s_pre, 6)
    if critical:
        verdict = REJECT
    elif delta_phi == 1.0 and delta_s >= 0:
        verdict = ACCEPT
    else:
        verdict = QUARANTINE

    coherence_post = {
        "beta": BETA_V1, "delta_phi": delta_phi, "tension": tension, "sigma": sigma, "S": s_post,
        "S_kind": "S_structural_v1", "S_range": [0.0, 1.0], "formula": CANONICAL_FORMULA,
    }
    return _emit(PASS, None, verdict, coherence_post, s_pre, s_post, violations,
                 conflicts, missing, unknown, fingerprint, authorize_09=(verdict == ACCEPT))


def main(envelope: dict) -> dict:
    return run_coherence_2(envelope)
