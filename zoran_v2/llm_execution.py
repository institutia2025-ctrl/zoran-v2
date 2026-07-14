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
        "INJECTED_CLIENT",
        "NO_NETWORK_WITHOUT_CLIENT",
        "NO_MEMORY",
        "REFERENTIAL_FINGERPRINT_CARRIED",
        "FAIL_CLOSED",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "executed + response + fingerprint porte + error explicite ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest (client mock) + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00..06 != PASS ou client manquant alors qu'autorise ; executed=False si veto ou erreur client",
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
ORDER_KEY = "appel_llm_unique_sur_requete_06"

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
