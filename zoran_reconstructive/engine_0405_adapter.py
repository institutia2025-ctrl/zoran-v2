"""Adaptateur RÉEL cadre reconstructif → ENGINE-04/05 (package ISOLÉ).

Implémente le contrat approuvé `specs/reconstructive/FRAME_TO_ENGINE_0405_PROJECTION_CONTRACT.md` :

    cadre reconstructif
    → projection déterministe, provenance-préservante
    → ENGINE-04 réel (run_canon_determination)
    → ENGINE-05 réel (run_coherence_engine)
    → dérivation du verdict depuis les SORTIES RÉELLES
    → gate reconstructif

Ne modifie AUCUN moteur 00-11, ni ZMOS, ni bridge : il APPELLE les implémentations
réelles d'ENGINE-04 et ENGINE-05 (import lecture seule). Il n'invente aucun canon,
conflit, opérant, preuve ni signal de pertinence, et ne produit jamais `NON_PERTINENT`
ni `REDONDANT` (owned par les stages amont). ENGINE-08 n'est PAS câblé ici
(`DEFERRED_POST_LLM`).

Le verdict n'est pas fabriqué par un label : l'adaptateur embarque les sorties moteur
réelles + attestations (digests), et c'est le GATE qui dérive le verdict via
`derive_verdict_from_engine_outputs`, après vérification d'intégrité des attestations.
"""
from __future__ import annotations

from zoran_v2.canon_determination import (
    COMPONENT_ID as CD_COMPONENT_ID,
    PASS as CD_PASS,
    VERSION as CD_VERSION,
    run_canon_determination,
)
from zoran_v2.coherence_engine import (
    COMPONENT_ID as CE_COMPONENT_ID,
    PASS as CE_PASS,
    VERSION as CE_VERSION,
    run_coherence_engine,
)

from zoran_reconstructive.frame_coherence_gate import (
    ADMISSIBLE,
    ALLOWED_VERDICT_SOURCE,
    CONDITIONNEL,
    CONFLICTUEL,
    NON_VERIFIABLE,
    evaluate_frame_admissibility,
    stable_engine_digest,
)

# Type d'objet projeté (constant, non sémantique) et contrat figé du noeud 03 revalidé par 04.
PROJECTED_KIND = "reconstructive_frame"
_OA_COMPONENT = "03_OPERANTS_OPERES_ANALYSIS"
_OA_VERSION = "1.0.0"
_OA_ORDER_KEY = "object_frame_map_order_puis_operant_id_alphabetique"

# Clés attendues des sorties moteur (indexation stable des attestations).
ENGINE_04_KEY = CD_COMPONENT_ID  # "04_CANON_DETERMINATION"
ENGINE_05_KEY = CE_COMPONENT_ID  # "05_COHERENCE_ENGINE"

# Contrat d'attestation exigé par le gate : EXACTEMENT 04 puis 05, aux versions RÉELLES.
REQUIRED_ENGINES = (
    {"component_id": ENGINE_04_KEY, "version": CD_VERSION},
    {"component_id": ENGINE_05_KEY, "version": CE_VERSION},
)


class ProjectionError(ValueError):
    """Projection impossible (donnée absente/incohérente) -> fail-closed NON_VERIFIABLE."""


def _is_nonempty_str(x):
    return isinstance(x, str) and x.strip() != ""


def _has_provenance(obj):
    """Provenance valide = dict portant source_id/source_version/source_digest/status non vides."""
    if not isinstance(obj, dict):
        return False
    prov = obj.get("provenance")
    if not isinstance(prov, dict):
        return False
    return all(_is_nonempty_str(prov.get(k)) for k in
               ("source_id", "source_version", "source_digest", "status"))


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def project_frame(request):
    """Cadre candidat -> (envelope_04, registry). Lève ProjectionError si donnée absente.

    Non-invention : chaque canon de `registry` vient 1:1 d'une référence `grounding`
    provenancée ; chaque opérant vient d'une référence `operants` provenancée. Les
    références sans provenance sont EXCLUES (jamais comblées) : le couple devient alors
    légitimement uncanonized/unanalyzed et ce sont les moteurs qui baissent le score.
    """
    if not isinstance(request, dict):
        raise ProjectionError("request must be a mapping")
    frame = request.get("candidate_frame")
    if not isinstance(frame, dict):
        raise ProjectionError("candidate_frame missing")
    frame_id = frame.get("frame_id")
    relation_type = frame.get("relation_type")
    if not (_is_nonempty_str(frame_id) and _is_nonempty_str(relation_type)):
        raise ProjectionError("frame_id or relation_type missing")

    # registry : un canon par référence grounding provenancée, id str + priorité int.
    registry = []
    for g in frame.get("grounding", []) or []:
        if not _has_provenance(g):
            continue  # exclu, jamais inventé
        cid = g.get("id")
        prio = g.get("priority")
        if not (_is_nonempty_str(cid) and _is_int(prio)):
            continue
        registry.append({
            "id": cid,
            "priority": prio,
            "applies_to_frames": [relation_type],
            "applies_to_kinds": [PROJECTED_KIND],
        })

    # opérants : ids provenancés uniquement, uniques et ordonnés.
    operant_ids = []
    for op in frame.get("operants", []) or []:
        if not _has_provenance(op):
            continue
        oid = op.get("id")
        if _is_nonempty_str(oid) and oid not in operant_ids:
            operant_ids.append(oid)
    operant_ids = sorted(operant_ids)

    pair = {"object_key": frame_id, "frame": relation_type}
    if operant_ids:
        analysis = [{
            "frame": relation_type,
            "object_key": frame_id,
            "operants": operant_ids,
            "operes": [frame_id],
        }]
        unanalyzed = []
    else:
        analysis = []
        unanalyzed = [dict(pair)]

    envelope_04 = {
        "runtime_check": {"status": "PASS"},
        "object_discovery": {
            "status": "PASS",
            "objects": [{"object_key": frame_id, "kind": PROJECTED_KIND}],
        },
        "frame_selection": {
            "status": "PASS",
            "object_frame_map": [{"object_key": frame_id, "frames": [relation_type]}],
        },
        "operants_operes": {
            "component": _OA_COMPONENT,
            "version": _OA_VERSION,
            "status": "PASS",
            "blocked_by": None,
            "analysis": analysis,
            "unanalyzed": unanalyzed,
            "order_key": _OA_ORDER_KEY,
        },
    }
    return envelope_04, registry


def run_real_engines(request):
    """Projection + appels RÉELS 04 puis 05. Retourne engine_outputs (dict) + attestations.

    Fail-closed : projection impossible ou exception moteur -> engine_outputs vide (le gate
    dérivera NON_VERIFIABLE). Les moteurs sont eux-mêmes fail-closed (renvoient BLOCKED).
    """
    try:
        envelope_04, registry = project_frame(request)
    except ProjectionError:
        return {}, []

    try:
        e04 = run_canon_determination(envelope_04, registry)
        envelope_05 = dict(envelope_04)
        envelope_05["canon_determination"] = e04
        e05 = run_coherence_engine(envelope_05, registry)
    except Exception:  # noqa: BLE001 — jamais un crash : toute anomalie -> fail-closed
        return {}, []

    engine_outputs = {ENGINE_04_KEY: e04, ENGINE_05_KEY: e05}
    attestations = [
        {
            "component_id": out.get("component"),
            "version": out.get("version"),
            "status": out.get("status"),
            "output_digest": stable_engine_digest(out),
        }
        for out in (e04, e05)
    ]
    return engine_outputs, attestations


def derive_verdict_from_engine_outputs(engine_outputs):
    """Dérive le verdict des SORTIES RÉELLES 04/05 (ordre normatif du contrat approuvé).

    Faits structurels ENGINE-04 avant résolution ENGINE-05. Ne lit jamais `authorize_llm`,
    `S` ou `delta_phi` comme signal de pertinence. Ne produit ni `NON_PERTINENT` ni
    `REDONDANT`.
    """
    if not isinstance(engine_outputs, dict):
        return NON_VERIFIABLE
    e04 = engine_outputs.get(ENGINE_04_KEY)
    e05 = engine_outputs.get(ENGINE_05_KEY)
    if not (isinstance(e04, dict) and isinstance(e05, dict)):
        return NON_VERIFIABLE

    # 1) moteur BLOCKED / sortie invalide / rien d'évaluable -> NON_VERIFIABLE.
    if e04.get("status") != CD_PASS or e05.get("status") != CE_PASS:
        return NON_VERIFIABLE
    coherence = e05.get("coherence")
    if not isinstance(coherence, dict):
        return NON_VERIFIABLE
    total_pairs = coherence.get("total_pairs")
    if not _is_int(total_pairs) or total_pairs == 0:
        return NON_VERIFIABLE

    conflicts = e04.get("conflicts")
    tension = coherence.get("tension")
    uncanonized = e04.get("uncanonized")
    resolved = coherence.get("resolved_pairs")

    # 2) conflit explicite 04 ou tension conflictuelle -> CONFLICTUEL.
    if (isinstance(conflicts, list) and len(conflicts) > 0) or (
        isinstance(tension, (int, float)) and not isinstance(tension, bool) and tension > 0
    ):
        return CONFLICTUEL
    # 3) uncanonized > 0 -> CONDITIONNEL (structure 04, AVANT toute résolution).
    if isinstance(uncanonized, list) and len(uncanonized) > 0:
        return CONDITIONNEL
    # 4) canon présent mais aucune résolution / preuve exploitable -> NON_VERIFIABLE.
    if not _is_int(resolved) or resolved == 0:
        return NON_VERIFIABLE
    # 5) résolu sans conflit -> ADMISSIBLE.
    return ADMISSIBLE


def real_coherence_evaluator(request):
    """Évaluateur RÉEL injecté dans le gate : embarque sorties moteur + attestations.

    Ne décide PAS le verdict (c'est le gate qui le dérive via `derive_verdict_from_engine_outputs`).
    """
    engine_outputs, attestations = run_real_engines(request)
    evidence_refs = []
    e05 = engine_outputs.get(ENGINE_05_KEY) if engine_outputs else None
    if isinstance(e05, dict) and isinstance(e05.get("coherence"), dict):
        coh = e05["coherence"]
        evidence_refs = [
            "referential_fingerprint=" + str(coh.get("referential_fingerprint")),
            "resolved_pairs=" + str(coh.get("resolved_pairs")),
            "total_pairs=" + str(coh.get("total_pairs")),
        ]
    return {
        "source": ALLOWED_VERDICT_SOURCE,
        "engine_outputs": engine_outputs,
        "attestations": attestations,
        "evidence_refs": evidence_refs,
        "policy_version": request.get("policy_version") if isinstance(request, dict) else None,
    }


def evaluate_frame(request):
    """Point d'entrée RÉEL : gate + adaptateur 04/05 + dérivation gate-side du verdict.

    Impose au gate le contrat d'attestation EXACT (04 ET 05, versions réelles) : aucune
    intégration sans sorties conjointes, identifiées et attestées des vrais moteurs.
    """
    return evaluate_frame_admissibility(
        request,
        real_coherence_evaluator,
        verdict_deriver=derive_verdict_from_engine_outputs,
        required_engines=REQUIRED_ENGINES,
    )
