"""02_ANALYSIS_FRAME_SELECTION — porte 2 du pipeline de raisonnement ZORAN V2.

Sélectionne de façon DÉTERMINISTE le ou les cadres d'analyse applicables aux
objets découverts par 01. Règle unique : `object.kind ∈ frame.applies_to_kinds`.

Ne raisonne pas, ne score pas, n'analyse aucun opérant/opéré (→ 03), n'invente
aucun cadre (⊆ registre). Structuré-only : aucun LLM/réseau/mémoire. Immuable.
Fail-closed : bloqué si 00 ≠ PASS ou 01 ≠ PASS.
"""
from __future__ import annotations

COMPONENT_ID = "02_ANALYSIS_FRAME_SELECTION"
VERSION = "1.0.0"

# --- Contrat de gouvernance (objet V2 gouverné complet) ---
GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-02-ANALYSIS-FRAME-SELECTION",
    "META_ID": "META-ZORAN-V2-COMPONENT-02",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_02_ANALYSIS_FRAME_SELECTION · branche mission/engine-02-frame-selection",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "NO_INVENTION",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "NO_LLM",
        "NO_NETWORK",
        "NO_MEMORY",
        "NO_SCORING",
        "NO_OPERANT_ANALYSIS",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "object_frame_map + unmatched_objects explicites ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00/01 != PASS ; unmatched_objects pour tout objet sans cadre",
    "ANTI_REGRESSION": "tests non-invention + fail-closed + determinisme + unmatched + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

# --- Déclaration de provenance (gate anti-résurrection) ---
PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_02_ANALYSIS_FRAME_SELECTION",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "selection deterministe de cadres par appartenance kind",
    "REJECTED_BEHAVIOR": "raisonnement, scoring, analyse d'operants, invention de cadre",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
RC00 = "00_RUNTIME_CHECK"
OD01 = "01_OBJECT_DISCOVERY"
ORDER_KEY = "frame_id_alphabetique"

# Clés exactes de la sortie (contrat) — sert aussi de contrôle de conformité.
OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "frames_selected", "object_frame_map", "unmatched_objects", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "frames_selected": [], "object_frame_map": [],
        "unmatched_objects": [], "order_key": ORDER_KEY,
    }


def _frames_for_kind(kind, registry) -> list:
    """Cadres du REGISTRE dont applies_to_kinds contient kind. Triés, ⊆ registre."""
    out = []
    for f in registry:
        if not isinstance(f, dict) or "id" not in f:
            continue
        if kind in (f.get("applies_to_kinds") or []):
            out.append(f["id"])
    return sorted(out)


def run_frame_selection(envelope: dict, registry: list) -> dict:
    """Fonction PURE : (envelope, registry) -> cadres sélectionnés (déterministe).

    Ne mute jamais l'enveloppe. Ne lève que sur mauvais usage de type.
    """
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")
    if not isinstance(registry, list):
        raise TypeError("registry doit être une liste")

    rc = envelope.get("runtime_check")
    if not (isinstance(rc, dict) and rc.get("status") == PASS):
        return _blocked(RC00)
    od = envelope.get("object_discovery")
    if not (isinstance(od, dict) and od.get("status") == PASS):
        return _blocked(OD01)

    objects = od.get("objects") or []
    object_frame_map = []
    unmatched = []
    selected = set()
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        key = obj.get("object_key")
        kind = obj.get("kind")
        frames = _frames_for_kind(kind, registry)
        if frames:
            object_frame_map.append({"object_key": key, "frames": frames})
            selected.update(frames)
        else:
            unmatched.append({"object_key": key, "kind": kind})

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "frames_selected": sorted(selected),
        "object_frame_map": object_frame_map,
        "unmatched_objects": unmatched,
        "order_key": ORDER_KEY,
    }


def load_frame_registry(path=None) -> list:
    """Partie IMPURE fine : charge le registre déclaratif ANALYSIS_FRAMES.yaml."""
    import yaml
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "ANALYSIS_FRAMES.yaml"
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f).get("frames", [])


def main(envelope: dict) -> dict:
    """Point d'entrée : charge le registre canonique puis sélectionne."""
    return run_frame_selection(envelope, load_frame_registry())
