"""03_OPERANTS_OPERES_ANALYSIS — porte 3 du pipeline de raisonnement ZORAN V2.

Pour chaque (objet de 01, cadre de 02), identifie de façon DÉTERMINISTE les
opérants (Ω) applicables et l'opéré (l'objet lui-même). Règle unique :
`frame ∈ operant.applies_to_frames ET object.kind ∈ operant.applies_to_kinds`.

Ne détermine PAS le canon (→ 04), ne calcule AUCUNE cohérence (→ 05), ne
construit AUCUNE requête LLM (→ 06), n'appelle pas LLM, n'invente aucun opérant
(⊆ registre). Structuré-only, immuable, fail-closed.
"""
from __future__ import annotations

COMPONENT_ID = "03_OPERANTS_OPERES_ANALYSIS"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-03-OPERANTS-OPERES-ANALYSIS",
    "META_ID": "META-ZORAN-V2-COMPONENT-03",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_03_OPERANTS_OPERES_ANALYSIS · branche mission/engine-03-operants-operes",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "NO_OPERANT_INVENTION",
        "NO_CANON_DETERMINATION",
        "NO_SCORING",
        "NO_LLM",
        "NO_NETWORK",
        "NO_MEMORY",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "analysis + unanalyzed explicites par (objet,cadre) ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00/01/02 != PASS ; unanalyzed pour toute paire sans operant",
    "ANTI_REGRESSION": "tests non-invention + fail-closed + determinisme + dedup + unanalyzed + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_03_OPERANTS_OPERES_ANALYSIS",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "analyse deterministe operants/operes par appartenance (frame+kind)",
    "REJECTED_BEHAVIOR": "determination du canon, scoring, requete LLM, invention d'operant",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
RC00 = "00_RUNTIME_CHECK"
OD01 = "01_OBJECT_DISCOVERY"
FS02 = "02_ANALYSIS_FRAME_SELECTION"
ORDER_KEY = "object_frame_map_order_puis_operant_id_alphabetique"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "analysis", "unanalyzed", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "analysis": [], "unanalyzed": [], "order_key": ORDER_KEY,
    }


def _operants_for(frame, kind, registry) -> list:
    """Opérants du REGISTRE applicables à (frame, kind). Dédup + tri, ⊆ registre."""
    out = set()
    for op in registry:
        if not isinstance(op, dict) or "id" not in op:
            continue
        frames = op.get("applies_to_frames")
        kinds = op.get("applies_to_kinds")
        if (isinstance(frames, list) and isinstance(kinds, list)
                and frame in frames and kind in kinds):
            out.add(op["id"])
    return sorted(out)


def run_operants_operes_analysis(envelope: dict, registry: list) -> dict:
    """Fonction PURE : (envelope, registry) -> analyse opérants/opérés déterministe."""
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
    fs = envelope.get("frame_selection")
    if not (isinstance(fs, dict) and fs.get("status") == PASS):
        return _blocked(FS02)

    kind_by_key = {
        o.get("object_key"): o.get("kind")
        for o in (od.get("objects") or []) if isinstance(o, dict)
    }

    analysis = []
    unanalyzed = []
    for entry in (fs.get("object_frame_map") or []):
        if not isinstance(entry, dict):
            continue
        key = entry.get("object_key")
        kind = kind_by_key.get(key)
        for frame in (entry.get("frames") or []):
            operants = _operants_for(frame, kind, registry)
            if operants:
                analysis.append({
                    "frame": frame, "object_key": key,
                    "operants": operants, "operes": [key],
                })
            else:
                unanalyzed.append({"frame": frame, "object_key": key})

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "analysis": analysis, "unanalyzed": unanalyzed, "order_key": ORDER_KEY,
    }


def _operants_from_yaml_obj(obj) -> list:
    """Fail-closed : [] si YAML vide/non-dict, ou si 'operants' n'est pas une liste."""
    if not isinstance(obj, dict):
        return []
    operants = obj.get("operants")
    return operants if isinstance(operants, list) else []


def load_operant_registry(path=None) -> list:
    """Partie IMPURE fine : charge OPERANTS.yaml (FAIL-CLOSED : YAML invalide/fichier -> [])."""
    import yaml
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "OPERANTS.yaml"
    try:
        with open(p, encoding="utf-8") as f:
            return _operants_from_yaml_obj(yaml.safe_load(f))
    except (yaml.YAMLError, OSError):
        return []


def main(envelope: dict) -> dict:
    return run_operants_operes_analysis(envelope, load_operant_registry())
