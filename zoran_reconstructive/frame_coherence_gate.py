"""FRAME_COHERENCE_ADMISSIBILITY_GATE — vertical slice V1 (package ISOLÉ).

Point normatif UNIQUE qui autorise ou refuse un cadre candidat pour le cycle, en
application de `specs/reconstructive/RECONSTRUCTIVE_ORCHESTRATOR_CONTRACT.md`
(section FRAME_COHERENCE_ADMISSIBILITY_GATE).

Flux prouvé par ce lot :

    cadre candidat
    -> validation des entrées (fail-closed si provenance/version absente)
    -> évaluation de cohérence par les moteurs 04/05/08 (injectés)
    -> verdict explicite parmi les six valeurs stables
    -> conséquence obligatoire (intégration ou rejet fail-closed)
    -> trace complète (digests canoniques, source du verdict, evidence refs)

Séparation d'autorité (contrat) :
- l'orchestrateur (ce gate) DEMANDE l'évaluation, ENREGISTRE le verdict, mais ne
  l'émet JAMAIS ;
- les moteurs 04/05/08 (fonction `coherence_evaluator` injectée) rendent seuls le
  verdict ;
- le bridge, ZMOS et le LLM ne décident jamais : un verdict dont la `source`
  n'est pas `ENGINES_04_05_08` est refusé fail-closed ;
- aucun seuil numérique n'est fixé ici ; tout seuil non calibré reste `NON_MESURE`.

Le gate ne peut jamais ACCORDER `ADMISSIBLE` de lui-même : ses seules décisions
autonomes sont des refus fail-closed (`NON_VERIFIABLE`). Déterministe, structuré-only,
sans réseau, sans LLM, sans horodatage inventé.
"""
from __future__ import annotations

import hashlib
import unicodedata

COMPONENT_ID = "RECONSTRUCTIVE_FRAME_COHERENCE_GATE"
VERSION = "0.1.0-slice"

# --- Verdicts stables et conséquences obligatoires (contrat, table normative) ---
ADMISSIBLE = "ADMISSIBLE"
CONDITIONNEL = "CONDITIONNEL"
CONFLICTUEL = "CONFLICTUEL"
REDONDANT = "REDONDANT"
NON_PERTINENT = "NON_PERTINENT"
NON_VERIFIABLE = "NON_VERIFIABLE"

VERDICTS = frozenset(
    {ADMISSIBLE, CONDITIONNEL, CONFLICTUEL, REDONDANT, NON_PERTINENT, NON_VERIFIABLE}
)

# Conséquence obligatoire par verdict (verbatim contrat -> code stable).
CONSEQUENCE = {
    ADMISSIBLE: "INTEGRATION_POSSIBLE",
    CONDITIONNEL: "KEPT_WITHOUT_CANONIZATION",
    CONFLICTUEL: "ARBITRATION_ENGINES_04_05_08",
    REDONDANT: "NO_NEW_ACTIVATION",
    NON_PERTINENT: "REJECTED_FOR_CYCLE",
    NON_VERIFIABLE: "FAIL_CLOSED",
}

# Disposition observable du cadre après verdict.
DISPOSITION = {
    ADMISSIBLE: "INTEGRATED",
    CONDITIONNEL: "CONSERVED_NON_CANONICAL",
    CONFLICTUEL: "ROUTED_TO_ARBITRATION",
    REDONDANT: "NO_NEW_ACTIVATION",
    NON_PERTINENT: "REJECTED_CYCLE",
    NON_VERIFIABLE: "FAIL_CLOSED",
}

# Seule autorité admise pour émettre un verdict : les moteurs 04/05/08.
ALLOWED_VERDICT_SOURCE = "ENGINES_04_05_08"
GATE_FAIL_CLOSED_SOURCE = "GATE_FAIL_CLOSED"

# Entrées minimales exigées par le contrat (section "Evaluation input").
REQUIRED_INPUT_KEYS = (
    "candidate_frame",
    "current_state",
    "active_frames",
    "established_facts",
    "provenance",
    "version",
)

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-RECONSTRUCTIVE-FRAME-COHERENCE-GATE",
    "META_ID": "META-ZORAN-RECONSTRUCTIVE-FRAME-COHERENCE-GATE",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": (
        "MISSION ZORAN_RECONSTRUCTIVE_VERTICAL_SLICE_CODE_V1 · "
        "branche feature/reconstructive-frame-gate-slice-v1"
    ),
    "GUARD_IDS": [
        "SINGLE_NORMATIVE_GATE",
        "ENGINES_04_05_08_ONLY_DECIDE",
        "NO_BRIDGE_AUTHORITY",
        "NO_ZMOS_AUTHORITY",
        "NO_LLM_AUTHORITY",
        "SIX_EXPLICIT_VERDICTS",
        "MANDATORY_CONSEQUENCES",
        "FAIL_CLOSED_ON_MISSING_INPUT",
        "FAIL_CLOSED_ON_AMBIGUOUS_VERDICT",
        "NO_INVENTED_NUMERIC_THRESHOLD",
        "DETERMINISTIC",
        "NO_LLM",
        "NO_NETWORK",
        "NO_TIME_INVENTION",
        "ENGINES_00_11_UNCHANGED",
        "ZMOS_UNCHANGED",
    ],
}


class GateInputError(ValueError):
    """Entrée de gate structurellement invalide (déclenche un refus fail-closed)."""


def _canonical_json(value):
    """Sérialisation canonique déterministe (sous-ensemble du schéma constellation).

    UTF-8, chaînes normalisées NFC, clés d'objet triées lexicographiquement, `null`
    JSON explicite, aucun espace insignifiant. Suffisant et stable pour les digests
    de trace de ce lot.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        normalized = unicodedata.normalize("NFC", value)
        escaped = (
            normalized.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
        return '"' + escaped + '"'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key in sorted(value.keys()):
            if not isinstance(key, str):
                raise GateInputError("object keys MUST be strings for canonical JSON")
            parts.append(_canonical_json(key) + ":" + _canonical_json(value[key]))
        return "{" + ",".join(parts) + "}"
    # Types flottants exclus : pas de sérialisation numérique ambiguë dans ce lot.
    raise GateInputError("unsupported type for canonical JSON: " + type(value).__name__)


def _digest(value):
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _is_nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def _validate_inputs(request):
    """Valide les entrées minimales. Retourne (reason, candidate_ref).

    reason == None si les entrées sont complètes ; sinon un code de refus fail-closed.
    Provenance ou version absente n'est PAS un cas `NON_MESURE` : elle force
    `NON_VERIFIABLE` (contrat).
    """
    if not isinstance(request, dict):
        raise GateInputError("request MUST be a mapping")

    for key in REQUIRED_INPUT_KEYS:
        if key not in request:
            return "INPUT_KEY_MISSING:" + key, {}

    candidate = request.get("candidate_frame")
    if not isinstance(candidate, dict):
        return "INPUT_CANDIDATE_FRAME_INVALID", {}

    frame_id = candidate.get("frame_id")
    frame_version = candidate.get("frame_version")
    candidate_ref = {
        "frame_id": frame_id if isinstance(frame_id, str) else None,
        "frame_version": frame_version if isinstance(frame_version, str) else None,
    }
    if not _is_nonempty_str(frame_id):
        return "INPUT_FRAME_ID_MISSING", candidate_ref
    if not _is_nonempty_str(frame_version):
        return "INPUT_FRAME_VERSION_MISSING", candidate_ref

    provenance = request.get("provenance")
    if not isinstance(provenance, dict) or len(provenance) == 0:
        return "INPUT_PROVENANCE_MISSING", candidate_ref

    if not _is_nonempty_str(request.get("version")):
        return "INPUT_VERSION_MISSING", candidate_ref

    return None, candidate_ref


def _fail_closed_trace(request, candidate_ref, reason, verdict_source):
    """Construit une trace de refus fail-closed (verdict forcé NON_VERIFIABLE)."""
    return _build_trace(
        request=request,
        candidate_ref=candidate_ref,
        verdict=NON_VERIFIABLE,
        verdict_source=verdict_source,
        evidence_refs=[],
        policy_version=request.get("policy_version")
        if isinstance(request, dict)
        else None,
        reason=reason,
    )


def _build_trace(
    request,
    candidate_ref,
    verdict,
    verdict_source,
    evidence_refs,
    policy_version,
    reason,
):
    run_id = request.get("run_id") if isinstance(request, dict) else None
    trace_id = request.get("trace_id") if isinstance(request, dict) else None
    consequence = CONSEQUENCE[verdict]
    disposition = DISPOSITION[verdict]
    fail_closed = verdict == NON_VERIFIABLE

    trace = {
        "component_id": COMPONENT_ID,
        "version": VERSION,
        "run_id": run_id,
        "trace_id": trace_id,
        "candidate_frame_ref": candidate_ref,
        "input_digest": _digest(request) if isinstance(request, dict) else None,
        "verdict": verdict,
        "verdict_source": verdict_source,
        "consequence": consequence,
        "disposition": disposition,
        "integration": verdict == ADMISSIBLE,
        "fail_closed": fail_closed,
        "evidence_refs": list(evidence_refs) if evidence_refs else [],
        "policy_version": policy_version,
        "reason": reason,
        "gate_authority": "orchestrator_requests_engines_decide",
    }
    trace["trace_digest"] = _digest(trace)
    return trace


def evaluate_frame_admissibility(request, coherence_evaluator):
    """Gate d'admissibilité d'un cadre par cohérence.

    Args:
        request: dict portant les entrées minimales
            (candidate_frame, current_state, active_frames, established_facts,
             provenance, version) et optionnellement run_id/trace_id/policy_version.
        coherence_evaluator: callable représentant les moteurs 04/05/08. Reçoit
            `request` et retourne un dict {verdict, evidence_refs, source, policy_version}.
            Le gate n'émet jamais le verdict lui-même ; il ne fait que le demander,
            le valider et en tirer la conséquence obligatoire.

    Returns:
        Une trace complète (dict) incluant verdict, source, conséquence, disposition,
        intégration (bool), fail_closed (bool), digests canoniques.

    Règles fail-closed :
        - provenance ou version absente -> NON_VERIFIABLE (sans appeler l'évaluateur) ;
        - verdict absent/ambigu/hors des six valeurs -> NON_VERIFIABLE ;
        - source de verdict != ENGINES_04_05_08 (bridge/ZMOS/LLM) -> NON_VERIFIABLE.
    """
    reason, candidate_ref = _validate_inputs(request)
    if reason is not None:
        # Refus fail-closed du gate : ce n'est pas une décision d'admissibilité.
        return _fail_closed_trace(
            request, candidate_ref, reason, GATE_FAIL_CLOSED_SOURCE
        )

    if not callable(coherence_evaluator):
        raise GateInputError("coherence_evaluator MUST be callable (engines 04/05/08 seam)")

    evaluation = coherence_evaluator(request)

    # Verdict absent ou structurellement invalide -> fail-closed.
    if not isinstance(evaluation, dict):
        return _fail_closed_trace(
            request, candidate_ref, "EVALUATOR_RESULT_INVALID", GATE_FAIL_CLOSED_SOURCE
        )

    verdict = evaluation.get("verdict")
    source = evaluation.get("source")

    # Autorité : seuls les moteurs 04/05/08 décident. Bridge/ZMOS/LLM -> refus.
    if source != ALLOWED_VERDICT_SOURCE:
        return _fail_closed_trace(
            request, candidate_ref, "AUTHORITY_VIOLATION", GATE_FAIL_CLOSED_SOURCE
        )

    # Verdict ambigu / hors des six valeurs stables -> fail-closed.
    if verdict not in VERDICTS:
        return _fail_closed_trace(
            request, candidate_ref, "VERDICT_AMBIGUOUS", GATE_FAIL_CLOSED_SOURCE
        )

    return _build_trace(
        request=request,
        candidate_ref=candidate_ref,
        verdict=verdict,
        verdict_source=ALLOWED_VERDICT_SOURCE,
        evidence_refs=evaluation.get("evidence_refs"),
        policy_version=evaluation.get("policy_version"),
        reason="OK",
    )


# --- Évaluateur de référence 04/05/08 (seam de démonstration, aucun seuil numérique) ---

# Dimensions minimales que les moteurs 04/05/08 DOIVENT évaluer (contrat).
COHERENCE_DIMENSIONS = (
    "compatibility_facts",
    "compatibility_active_frames",
    "contradiction",
    "relevance",
    "new_contribution",
    "bounds_authorizations",
)

# Résultats de dimension autorisés (structurels, non numériques).
_SIGNAL_OK = "OK"
_SIGNAL_VIOLATED = "VIOLATED"
_SIGNAL_UNKNOWN = "UNKNOWN"
_SIGNAL_CONDITIONAL = "CONDITIONAL"
_ALLOWED_SIGNALS = frozenset(
    {_SIGNAL_OK, _SIGNAL_VIOLATED, _SIGNAL_UNKNOWN, _SIGNAL_CONDITIONAL}
)


def reference_coherence_evaluator(request):
    """Évaluateur 04/05/08 de référence : signaux structurels -> verdict déterministe.

    Ne calcule AUCUN score et n'invente AUCUN seuil : il agrège des signaux de
    dimension explicites (`candidate_frame.coherence_signals`) par priorité stable.
    Représente la place où les vrais moteurs 04/05/08 se branchent, via la même
    interface, sans modifier ces moteurs.
    """
    candidate = request.get("candidate_frame", {}) if isinstance(request, dict) else {}
    signals = candidate.get("coherence_signals")
    evidence_refs = candidate.get("evidence_refs", [])
    policy_version = request.get("policy_version") if isinstance(request, dict) else None

    def _result(verdict):
        return {
            "verdict": verdict,
            "evidence_refs": list(evidence_refs) if evidence_refs else [],
            "source": ALLOWED_VERDICT_SOURCE,
            "policy_version": policy_version,
        }

    # Évaluation incomplète ou valeurs hors domaine -> non vérifiable (fail-closed).
    if not isinstance(signals, dict):
        return _result(NON_VERIFIABLE)
    for dim in COHERENCE_DIMENSIONS:
        if dim not in signals or signals[dim] not in _ALLOWED_SIGNALS:
            return _result(NON_VERIFIABLE)

    values = {dim: signals[dim] for dim in COHERENCE_DIMENSIONS}

    if _SIGNAL_UNKNOWN in values.values():
        return _result(NON_VERIFIABLE)
    if (
        values["contradiction"] == _SIGNAL_VIOLATED
        or values["compatibility_facts"] == _SIGNAL_VIOLATED
        or values["compatibility_active_frames"] == _SIGNAL_VIOLATED
        or values["bounds_authorizations"] == _SIGNAL_VIOLATED
    ):
        return _result(CONFLICTUEL)
    if values["relevance"] == _SIGNAL_VIOLATED:
        return _result(NON_PERTINENT)
    if values["new_contribution"] == _SIGNAL_VIOLATED:
        return _result(REDONDANT)
    if _SIGNAL_CONDITIONAL in values.values():
        return _result(CONDITIONNEL)
    return _result(ADMISSIBLE)
