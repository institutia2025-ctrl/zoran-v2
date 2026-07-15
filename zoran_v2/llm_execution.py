"""07_LLM_EXECUTION — porte 7 du pipeline de raisonnement ZORAN V2.

SEULE étape GÉNÉRATIVE du pipeline : exécute l'appel LLM à partir de la requête
construite en 06. Le LLM est ici un OUTIL du dernier kilomètre, JAMAIS le moteur —
il n'est appelé que sur la requête déterministe de 06, autorisée par 05.

Le client LLM est INJECTÉ (`llm_client` callable) : le composant reste testable et
backend-agnostic (Ollama, API, mock…). L'appel est UNIQUE (aucune pré-sélection à
n candidats — comportement legacy interdit). Fail-closed : sans autorisation (06),
aucun appel ; sur erreur du client, `executed=False` + erreur (jamais un crash).
"""
from __future__ import annotations

import re

COMPONENT_ID = "07_LLM_EXECUTION"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-07-LLM-EXECUTION",
    "META_ID": "META-ZORAN-V2-COMPONENT-07",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_07_LLM_EXECUTION · branche mission/engine-07-llm-execution",
    "GUARD_IDS": [
        "LLM_IS_TOOL_NOT_ENGINE",
        "SINGLE_CALL_NO_PRECHOICES",
        "REQUIRES_05_06_AUTHORIZATION",
        "REQUEST_SCHEMA_VALIDATED_06_TO_07",
        "REQUEST_VALUES_TRACE_TO_ENVELOPE_PROVENANCE",
        "INJECTED_CLIENT",
        "NO_NETWORK_WITHOUT_CLIENT",
        "NO_MEMORY",
        "REFERENTIAL_FINGERPRINT_CARRIED",
        "NO_PII_TO_LLM",
        "FAIL_CLOSED",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "executed + response + fingerprint porte + error explicite ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest (client mock) + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..06 != PASS, client manquant alors qu'autorise, ou llm_request 06 hors schema/PII (frontiere 06->07) ; executed=False si veto ou erreur client",
    "ANTI_REGRESSION": "tests veto respecte + appel unique + erreur client geree + fail-closed + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_07_LLM_EXECUTION",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "appel LLM UNIQUE sur requete 06 autorisee, via client injecte ; LLM = outil, pas moteur",
    "REJECTED_BEHAVIOR": "LLM comme moteur, pre-selection a n candidats, appel sans autorisation 05/06, crash sur erreur client",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit (pas de n_candidates)",
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
    ("llm_request_build", "06_LLM_REQUEST_BUILD"),
)
NO_CLIENT = "07_LLM_EXECUTION_NO_CLIENT"
CLIENT_ERROR = "07_LLM_CLIENT_ERROR"
MALFORMED_REQUEST = "07_LLM_REQUEST_MALFORMED"
ORDER_KEY = "appel_llm_unique_sur_requete_06"

# --- Contrat de la frontière 06 -> 07 : schéma EXACT de la requête produite par
# 06_LLM_REQUEST_BUILD. 07 ne transmet au client QUE ce qui correspond à ce contrat ;
# toute déviation (absente/None, non-dict, hors schéma, PII) => fail-closed AVANT tout appel.
_EXPECTED_INSTRUCTION_KIND = "STRUCTURED_ANALYSIS_V1"
_EXPECTED_PII_POLICY = "OPAQUE_PUBLIC_IDS_ONLY_NO_DERIVED_USER_CONTENT"
_REQUIRED_REQUEST_KEYS = frozenset((
    "instruction_kind", "referential_fingerprint", "coherence_S",
    "frames", "targets", "pii_policy",
))
_REQUIRED_TARGET_KEYS = frozenset((
    "object_public_id", "kind_public", "frame", "canons", "operants",
))  # GC-051-001 : `kind_public` (vocabulaire canonique 04) remplace le `kind` brut de 01
# object_public_id = SEUL identifiant autorisé côté LLM : format opaque déterministe généré
# par 06 (`OBJ-0001`…). Toute autre forme = valeur potentiellement dérivée du contenu -> refus.
_OBJ_PUBLIC_ID_RE = re.compile(r"^OBJ-\d{4,}$")
# Séparateur de la clé DÉRIVÉE object_key (01 : f"{kind}\x1f{normalized}"). N'apparaît JAMAIS dans
# une valeur STRUCTURELLE légitime (OBJ-nnnn, noms de cadres, ids de canons/opérants) -> sa présence
# dans une valeur quelconque = tentative de fuite PII (RULE-078).
_PII_SEP = "\x1f"


def _is_str_list(x) -> bool:
    return isinstance(x, list) and all(isinstance(e, str) for e in x)


def _has_pii_separator(value) -> bool:
    """True si le séparateur d'object_key (\\x1f) apparaît dans une valeur (clé ou contenu)."""
    if isinstance(value, str):
        return _PII_SEP in value
    if isinstance(value, dict):
        return any(_has_pii_separator(k) or _has_pii_separator(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_has_pii_separator(e) for e in value)
    return False


def _request_well_formed(request) -> bool:
    """Valide la requête 06 AVANT tout appel client : schéma EXACT + TYPES + aucune PII.

    Fail-closed (findings audit P1 : frontière 06->07 + GC-D1-001) : une enveloppe 06 AUTORISÉE
    n'atteint le client QUE si elle est absolument conforme au contrat 06 —
    - clés EXACTES à la racine ET dans chaque cible (bloque tout ajout, ex. object_key) ;
    - TYPES valides pour chaque champ (pas seulement les clés) ;
    - object_public_id au FORMAT opaque `OBJ-nnnn` (jamais une valeur dérivée du contenu) ;
    - AUCUNE valeur ne contient le séparateur d'object_key (\\x1f) -> pas de PII dans une valeur.
    Sinon : pas d'appel LLM.
    """
    if not isinstance(request, dict):
        return False
    if set(request) != _REQUIRED_REQUEST_KEYS:  # clés EXACTES -> bloque tout ajout (ex. object_key racine)
        return False
    if request.get("instruction_kind") != _EXPECTED_INSTRUCTION_KIND:
        return False
    if request.get("pii_policy") != _EXPECTED_PII_POLICY:
        return False
    fingerprint = request.get("referential_fingerprint")
    if not (isinstance(fingerprint, str) and fingerprint):
        return False
    coherence_s = request.get("coherence_S")
    if not (coherence_s is None or (isinstance(coherence_s, (int, float)) and not isinstance(coherence_s, bool))):
        return False
    if not _is_str_list(request.get("frames")):
        return False
    targets = request.get("targets")
    if not isinstance(targets, list):
        return False
    for t in targets:
        if not isinstance(t, dict) or set(t) != _REQUIRED_TARGET_KEYS:  # clés EXACTES par cible
            return False
        opid = t.get("object_public_id")
        if not (isinstance(opid, str) and _OBJ_PUBLIC_ID_RE.match(opid)):
            return False  # doit être l'ID opaque OBJ-nnnn, jamais une valeur dérivée du contenu
        if not isinstance(t.get("kind_public"), str):
            return False
        if not isinstance(t.get("frame"), str):
            return False
        if not (_is_str_list(t.get("canons")) and _is_str_list(t.get("operants"))):
            return False
    # Verrou PII TRANSVERSAL : aucune valeur (même dans un champ au type autorisé) ne doit porter
    # le séparateur d'object_key -> ferme la fuite via kind/frame/canons/operants/object_public_id.
    if _has_pii_separator(request):
        return False
    return True


def _request_traces_to_envelope(request: dict, envelope: dict) -> bool:
    """Validation de PROVENANCE (finding GC-5FD-001) : chaque valeur STRUCTURELLE de la requête 06
    doit TRACER à l'amont autoritaire de l'enveloppe (03/04). Une valeur injectée en 06 mais ABSENTE
    de l'amont (ex. canons=['dossier médical de X'], frame/opérant fabriqué) est refusée AVANT tout
    appel — ce que le type/format seuls ne peuvent attraper.

    CONVERGENT (contrairement aux heuristiques de contenu) : l'ensemble autorisé est FINI et défini
    par l'amont réel, pas deviné. Ce n'est pas un ré-assemblage de 06 mais un contrôle de
    CONTENANCE (⊆). GC-051-001 : `kind_public` doit appartenir au vocabulaire canonique du
    référentiel gelé (04) -> aucune chaîne brute de 01 (PII possible) ne peut atteindre le LLM.
    """
    cd = envelope.get("canon_determination") or {}
    oa = envelope.get("operants_operes") or {}

    canons_selected = cd.get("canons_selected") or []
    analysis = oa.get("analysis") or []
    valid_frames = ({c.get("frame") for c in canons_selected if isinstance(c, dict)}
                    | {a.get("frame") for a in analysis if isinstance(a, dict)})
    valid_canons = {cn for c in canons_selected if isinstance(c, dict) for cn in (c.get("canons") or [])}
    valid_operants = {op for a in analysis if isinstance(a, dict) for op in (a.get("operants") or [])}

    # Le fingerprint porté doit être CELUI du référentiel réellement gelé par 04 (pas un autre).
    referential = cd.get("canon_referential") or {}
    if request.get("referential_fingerprint") != referential.get("fingerprint"):
        return False
    # kind_public doit appartenir au vocabulaire CANONIQUE du référentiel gelé (04) — trace à 04,
    # pas seulement à 01 (GC-051-001). Un kind_public hors registre = refus avant appel.
    canonical_kinds = {
        k for c in (referential.get("canons") or []) if isinstance(c, dict)
        for k in (c.get("applies_to_kinds") or []) if isinstance(k, str)
    }
    if not set(request.get("frames") or []) <= valid_frames:
        return False
    for t in (request.get("targets") or []):
        if t.get("kind_public") not in canonical_kinds:
            return False
        if t.get("frame") not in valid_frames:
            return False
        if not set(t.get("canons") or []) <= valid_canons:
            return False
        if not set(t.get("operants") or []) <= valid_operants:
            return False
    return True

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "executed", "response", "error", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "executed": False, "response": None, "error": None, "order_key": ORDER_KEY,
    }


def _result(executed, response, error) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "executed": executed, "response": response, "error": error,
        "order_key": ORDER_KEY,
    }


def run_llm_execution(envelope: dict, llm_client=None) -> dict:
    """Fonction : envelope(00→06) + client injecté -> exécution LLM unique (ou veto)."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    for key, comp in _STEPS:
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(comp)

    lrb = envelope["llm_request_build"]
    if not lrb.get("authorized"):
        # 05/06 n'ont pas autorisé -> AUCUN appel LLM (veto ressource respecté).
        return _result(executed=False, response=None, error=None)

    request = lrb.get("llm_request")
    # Frontière 06->07 fail-closed : 06 a autorisé, mais on ne transmet RIEN au client tant que
    # la requête n'est pas STRUCTURELLEMENT conforme au contrat 06 (finding audit P1). Une enveloppe
    # 06 malformée/tamperée (llm_request=None, non-dict, ou portant un object_key) est bloquée ICI.
    if not _request_well_formed(request):
        return _blocked(MALFORMED_REQUEST)
    # Provenance (GC-5FD-001) : au-delà du schéma/type, chaque valeur doit tracer à l'amont réel.
    # Bloque une PII injectée dans une valeur au type pourtant autorisé (kind/canons/operants/frame).
    if not _request_traces_to_envelope(request, envelope):
        return _blocked(MALFORMED_REQUEST)
    if not callable(llm_client):
        return _blocked(NO_CLIENT)  # autorisé mais pas de client -> fail-closed

    # Appel UNIQUE. Erreur du client -> fail-closed : status=BLOCKED (PAS un PASS déguisé),
    # pour que 08+ ne prennent JAMAIS une panne LLM pour une porte réussie.
    try:
        response = llm_client(request)
    except Exception as exc:  # noqa: BLE001 — on isole toute défaillance backend
        return {
            "component": COMPONENT_ID, "version": VERSION,
            "status": BLOCKED, "blocked_by": CLIENT_ERROR,
            "executed": False, "response": None,
            "error": f"{type(exc).__name__}: {exc}", "order_key": ORDER_KEY,
        }

    return _result(executed=True, response=response, error=None)


def main(envelope: dict, llm_client=None) -> dict:
    return run_llm_execution(envelope, llm_client)
