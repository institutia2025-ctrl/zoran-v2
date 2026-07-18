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
import json

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


def stable_engine_digest(value):
    """Digest déterministe d'une sortie moteur (peut contenir des flottants: S, delta_phi...).

    Utilise la sérialisation JSON canonique du projet (clés triées, séparateurs compacts),
    la MÊME des deux côtés (adaptateur qui atteste, gate qui re-vérifie) : une attestation
    ne peut donc pas prétendre une sortie moteur différente de celle réellement fournie.
    """
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _is_nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def _engine_attestations_ok(engine_outputs, attestations, required_engines):
    """Autorité NON usurpable : intégration impossible sans les sorties CONJOINTES,
    IDENTIFIÉES et ATTESTÉES des moteurs EXACTEMENT requis.

    `required_engines` = séquence de {component_id, version} attendus (ex. 04 puis 05).
    Retourne (ok, reason). Exige, avant tout `verdict_deriver` :
      - `engine_outputs` porte EXACTEMENT l'ensemble requis (aucun moteur manquant,
        aucune clé supplémentaire, aucun component_id arbitraire) ;
      - une attestation par moteur requis, sans doublon (bloque attestation croisée/réutilisée) ;
      - pour chaque moteur : component_id canonique (la sortie s'auto-identifie via `component`),
        version attendue (attestation ET sortie), status cohérent (attestation == sortie, non vide),
        digest recalculé == output_digest (lie l'attestation À CETTE sortie précise).
    """
    if not isinstance(required_engines, (list, tuple)) or not required_engines:
        return False, "REQUIRED_ENGINES_MISSING"
    required_ids = [r.get("component_id") for r in required_engines]
    required_set = set(required_ids)
    if len(required_set) != len(required_ids):
        return False, "REQUIRED_ENGINES_MALFORMED"
    expected_version = {r.get("component_id"): r.get("version") for r in required_engines}

    if not isinstance(engine_outputs, dict) or not engine_outputs:
        return False, "ENGINE_OUTPUTS_MISSING"
    if not isinstance(attestations, list) or not attestations:
        return False, "ATTESTATIONS_MISSING"

    # Ensemble de sorties EXACTEMENT = ensemble requis (04 ET 05, rien d'autre, rien en trop).
    if set(engine_outputs.keys()) != required_set:
        return False, "ENGINE_SET_MISMATCH"
    if len(attestations) != len(required_ids):
        return False, "ATTESTATION_COUNT_MISMATCH"

    seen = set()
    for att in attestations:
        if not isinstance(att, dict):
            return False, "ATTESTATION_MALFORMED"
        cid = att.get("component_id")
        version = att.get("version")
        status = att.get("status")
        digest = att.get("output_digest")
        if not (_is_nonempty_str(cid) and _is_nonempty_str(digest)):
            return False, "ATTESTATION_MALFORMED"
        if cid not in required_set:
            return False, "ATTESTATION_UNKNOWN_ENGINE"
        if cid in seen:  # attestation réutilisée / croisée
            return False, "ATTESTATION_DUPLICATE"
        seen.add(cid)
        out = engine_outputs[cid]
        if not isinstance(out, dict):
            return False, "ENGINE_OUTPUT_MALFORMED"
        # component_id canonique : la sortie doit s'auto-identifier au même id.
        if out.get("component") != cid:
            return False, "ENGINE_COMPONENT_MISMATCH"
        # version attendue, cohérente entre attestation et sortie.
        if version != expected_version[cid] or out.get("version") != expected_version[cid]:
            return False, "ENGINE_VERSION_MISMATCH"
        # status cohérent (non vide) entre attestation et sortie.
        if not _is_nonempty_str(status) or out.get("status") != status:
            return False, "ENGINE_STATUS_MISMATCH"
        # digest lie l'attestation À CETTE sortie (bloque croisement/réutilisation).
        if stable_engine_digest(out) != digest:
            return False, "ATTESTATION_DIGEST_MISMATCH"

    if seen != required_set:
        return False, "ATTESTATION_COVERAGE_MISMATCH"
    return True, "OK"


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
    engine_outputs=None,
    attestations=None,
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
        "input_digest": stable_engine_digest(request) if isinstance(request, dict) else None,
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
        # Sorties moteur RÉELLES conservées dans la trace (preuve : le verdict provient
        # d'ENGINE-04/05, pas d'un label). None sur le chemin séminal documentaire.
        "engine_outputs": engine_outputs,
        "engine_attestations": list(attestations) if attestations else None,
    }
    trace["trace_digest"] = stable_engine_digest(trace)
    return trace


def evaluate_frame_admissibility(
    request, coherence_evaluator, verdict_deriver=None, required_engines=None
):
    """Gate d'admissibilité d'un cadre par cohérence.

    Args:
        request: dict portant les entrées minimales
            (candidate_frame, current_state, active_frames, established_facts,
             provenance, version) et optionnellement run_id/trace_id/policy_version.
        coherence_evaluator: callable représentant les moteurs 04/05/08. Reçoit
            `request` et retourne un dict {source, evidence_refs, policy_version, ...}.
            Le gate n'émet jamais le verdict lui-même.
        verdict_deriver: callable pur `engine_outputs -> verdict`, REQUIS. C'est la SEULE
            voie d'autorisation : le gate dérive lui-même le verdict des sorties moteur
            RÉELLES et attestées (`evaluation["engine_outputs"]`), après vérification que
            chaque sortie est attestée (digest recalculé). Le gate ne lit JAMAIS un
            `evaluation["verdict"]` auto-déclaré. Si `verdict_deriver is None`, aucune
            intégration n'est possible : le gate renvoie `NON_VERIFIABLE`
            (`integration=false`). Il n'existe donc aucun chemin déclaratif d'intégration.
        required_engines: séquence {component_id, version} des moteurs EXACTEMENT requis
            (04 ET 05). Le gate exige l'ensemble exact, la version attendue, un status
            cohérent et un digest liant chaque attestation à sa sortie, AVANT le deriver ;
            sinon `NON_VERIFIABLE`. Absent -> `NON_VERIFIABLE` (fail-closed).

    Returns:
        Une trace complète (dict) incluant verdict, source, conséquence, disposition,
        intégration (bool), fail_closed (bool), sorties moteur réelles, digests.

    Règles fail-closed (toutes -> NON_VERIFIABLE, integration=false) :
        - provenance ou version absente (sans appeler l'évaluateur) ;
        - `verdict_deriver` absent (aucune autorité de dérivation) ;
        - source != ENGINES_04_05_08 (bridge/ZMOS/LLM) ;
        - sorties moteur absentes ou attestations manquantes/incohérentes ;
        - verdict dérivé hors des six valeurs / dérivation en erreur.
    """
    reason, candidate_ref = _validate_inputs(request)
    if reason is not None:
        # Refus fail-closed du gate : ce n'est pas une décision d'admissibilité.
        return _fail_closed_trace(
            request, candidate_ref, reason, GATE_FAIL_CLOSED_SOURCE
        )

    if not callable(coherence_evaluator):
        raise GateInputError("coherence_evaluator MUST be callable (engines 04/05/08 seam)")

    # AUTORITÉ UNIQUE : sans dérivation à partir de sorties moteur RÉELLES et attestées,
    # aucune intégration n'est possible. Un verdict auto-déclaré ne peut RIEN autoriser.
    if verdict_deriver is None:
        return _fail_closed_trace(
            request, candidate_ref, "VERDICT_DERIVER_REQUIRED", GATE_FAIL_CLOSED_SOURCE
        )

    evaluation = coherence_evaluator(request)

    # Résultat d'évaluateur absent ou structurellement invalide -> fail-closed.
    if not isinstance(evaluation, dict):
        return _fail_closed_trace(
            request, candidate_ref, "EVALUATOR_RESULT_INVALID", GATE_FAIL_CLOSED_SOURCE
        )

    # Autorité : seuls les moteurs 04/05/08 décident. Bridge/ZMOS/LLM -> refus.
    if evaluation.get("source") != ALLOWED_VERDICT_SOURCE:
        return _fail_closed_trace(
            request, candidate_ref, "AUTHORITY_VIOLATION", GATE_FAIL_CLOSED_SOURCE
        )

    engine_outputs = evaluation.get("engine_outputs")
    attestations = evaluation.get("attestations")

    # Sorties CONJOINTES, IDENTIFIÉES et ATTESTÉES des moteurs EXACTEMENT requis (04 ET 05),
    # vérifiées AVANT tout appel au deriver (fail-closed).
    ok, att_reason = _engine_attestations_ok(engine_outputs, attestations, required_engines)
    if not ok:
        return _fail_closed_trace(
            request, candidate_ref, "ENGINE_ATTESTATION_" + att_reason,
            GATE_FAIL_CLOSED_SOURCE,
        )

    # Le gate DÉRIVE lui-même le verdict des sorties réelles (jamais un label).
    try:
        verdict = verdict_deriver(engine_outputs)
    except Exception:  # noqa: BLE001 — dérivation défaillante -> fail-closed, jamais un crash
        return _fail_closed_trace(
            request, candidate_ref, "VERDICT_DERIVATION_ERROR", GATE_FAIL_CLOSED_SOURCE
        )
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
        engine_outputs=engine_outputs,
        attestations=attestations,
    )


# --- Évaluateur de référence — ILLUSTRATIF, NON AUTORITATIF (aucun seuil numérique) ---
# Il ne porte AUCUNE sortie moteur attestée ni `verdict_deriver` : passé au gate, il aboutit
# TOUJOURS à `NON_VERIFIABLE` (integration=false). Le champ `verdict` qu'il renvoie est un
# indice pédagogique du mapping signaux->verdict, jamais une autorité d'intégration.

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
    """Évaluateur de référence ILLUSTRATIF et NON AUTORITATIF : signaux -> verdict indicatif.

    Ne calcule AUCUN score, n'invente AUCUN seuil, et ne porte NI sorties moteur attestées
    NI autorité : soumis au gate il aboutit toujours à `NON_VERIFIABLE`. Le `verdict` renvoyé
    n'est qu'un indice du mapping signaux->verdict. La vraie autorité est le câblage réel
    04/05 (`engine_0405_adapter`). Ne modifie aucun moteur.
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
