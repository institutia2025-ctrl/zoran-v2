"""06_LLM_REQUEST_BUILD — porte 6 du pipeline de raisonnement ZORAN V2.

Assemble de façon DÉTERMINISTE la requête destinée au LLM à partir de l'analyse
structurée (01→04) et du verdict de cohérence/ressource (05). NE construit la
requête QUE si 05 a AUTORISÉ l'appel LLM ; sinon fail-closed (07 interdit sans
autorisation explicite de 05 — contrat RESSOURCE). N'appelle AUCUN LLM (→ 07),
ne génère rien, déterministe, immuable.

RULE-078 (anonymisation) — satisfaite PAR CONSTRUCTION en V1 : la requête ne porte
que des données STRUCTURELLES (object_key = identifiants, kind, frames, canons,
operants) et le fingerprint du référentiel — AUCUN contenu utilisateur brut, donc
aucune PII n'atteint le LLM.
"""
from __future__ import annotations

COMPONENT_ID = "06_LLM_REQUEST_BUILD"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-06-LLM-REQUEST-BUILD",
    "META_ID": "META-ZORAN-V2-COMPONENT-06",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_06_LLM_REQUEST_BUILD · branche mission/engine-06-llm-request-build",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "RESOURCE_VETO_RESPECTED",
        "NO_LLM_CALL",
        "NO_GENERATION",
        "NO_NETWORK",
        "NO_MEMORY",
        "NO_RAW_USER_CONTENT",
        "PII_FREE_BY_CONSTRUCTION",
        "REFERENTIAL_FINGERPRINT_CARRIED",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "llm_request structurel + authorized + fingerprint porte ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..05 != PASS ; authorized=False si 05 a veto (llm_request=None)",
    "ANTI_REGRESSION": "tests veto respecte + pii-free + determinisme + fail-closed + fingerprint porte + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_06_LLM_REQUEST_BUILD",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "assemblage deterministe de la requete LLM structurelle si 05 autorise ; anonymisation par construction",
    "REJECTED_BEHAVIOR": "appel LLM, generation, construction de requete sans autorisation 05, fuite de contenu utilisateur brut/PII",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
_STEPS = (
    ("runtime_check", "00_RUNTIME_CHECK"),
    ("object_discovery", "01_OBJECT_DISCOVERY"),
    ("frame_selection", "02_ANALYSIS_FRAME_SELECTION"),
    ("operants_operes", "03_OPERANTS_OPERES_ANALYSIS"),
    ("canon_determination", "04_CANON_DETERMINATION"),
    ("coherence_engine", "05_COHERENCE_ENGINE"),
)
ORDER_KEY = "targets_par_object_key_puis_frame"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "authorized", "llm_request", "object_id_map", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "authorized": False, "llm_request": None, "object_id_map": {},
        "order_key": ORDER_KEY,
    }


def run_llm_request_build(envelope: dict) -> dict:
    """Fonction PURE : envelope(00→05) -> requête LLM structurelle si 05 autorise."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    for key, comp in _STEPS:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(comp)

    ce = envelope["coherence_engine"]
    resource = ce.get("resource") or {}
    coherence = ce.get("coherence") or {}

    # Contrat RESSOURCE : sans autorisation explicite de 05, PAS de requête (07 interdit).
    if not resource.get("authorize_llm"):
        return {
            "component": COMPONENT_ID, "version": VERSION,
            "status": PASS, "blocked_by": None,
            "authorized": False, "llm_request": None, "object_id_map": {},
            "order_key": ORDER_KEY,
        }

    cd = envelope["canon_determination"]
    oa = envelope["operants_operes"]
    od = envelope["object_discovery"]

    kind_by_key = {
        o.get("object_key"): o.get("kind")
        for o in (od.get("objects") or []) if isinstance(o, dict)
    }
    canons_by_pair = {
        (c.get("object_key"), c.get("frame")): list(c.get("canons") or [])
        for c in (cd.get("canons_selected") or []) if isinstance(c, dict)
    }
    operants_by_pair = {
        (a.get("object_key"), a.get("frame")): list(a.get("operants") or [])
        for a in (oa.get("analysis") or []) if isinstance(a, dict)
    }

    # Cibles = paires RÉSOLUES (canonisées ET pourvues d'opérants) — déterministe, triées.
    pairs = sorted(set(canons_by_pair) & set(operants_by_pair))

    # RULE-078 : object_key dérive du contenu utilisateur normalisé (01 : f"{kind}\x1f{normalized}").
    # Il NE DOIT PAS partir au LLM. On attribue un identifiant OPAQUE déterministe (OBJ-0001…) ;
    # la table de correspondance reste LOCALE (object_id_map), jamais envoyée (07 n'envoie que llm_request).
    distinct_keys = sorted({ok for (ok, _fr) in pairs})
    public_id = {ok: f"OBJ-{i + 1:04d}" for i, ok in enumerate(distinct_keys)}

    targets = [
        {
            "object_public_id": public_id[ok],
            "kind": kind_by_key.get(ok),
            "frame": fr,
            "canons": canons_by_pair[(ok, fr)],
            "operants": operants_by_pair[(ok, fr)],
        }
        for (ok, fr) in pairs
    ]

    referential = cd.get("canon_referential") or {}
    llm_request = {
        "instruction_kind": "STRUCTURED_ANALYSIS_V1",
        "referential_fingerprint": referential.get("fingerprint"),
        "coherence_S": coherence.get("S"),
        "frames": sorted({fr for (_, fr) in pairs}),
        "targets": targets,
        "pii_policy": "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT",  # RULE-078 réellement appliquée
    }

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "authorized": True, "llm_request": llm_request,
        "object_id_map": {pid: ok for ok, pid in public_id.items()},  # LOCAL, jamais au LLM
        "order_key": ORDER_KEY,
    }


def main(envelope: dict) -> dict:
    return run_llm_request_build(envelope)
