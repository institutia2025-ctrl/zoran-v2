"""04_CANON_DETERMINATION — porte 4 du pipeline de raisonnement ZORAN V2.

À partir des objets (01), cadres (02) et de l'analyse opérants/opérés (03),
détermine de façon DÉTERMINISTE les canons (référentiels normatifs) applicables à
chaque (objet, cadre), puis GÈLE un référentiel canonique avec empreinte
(`fingerprint`) — preuve, pour 05/08, que le référentiel n'a pas bougé du cycle.

Règle unique d'applicabilité :
`frame ∈ canon.applies_to_frames ET object.kind ∈ canon.applies_to_kinds`.

Priorité : entier ; le plus haut prime ; égalité tranchée par `id` (alpha) ET
signalée dans `conflicts` (jamais écrasée en silence). Aucun canon n'est inventé
(⊆ registre). NE calcule AUCUNE cohérence (→ 05), n'applique aucun opérant (→ 05),
ne score pas, ne construit aucune requête LLM (→ 06), n'appelle pas de LLM.
Structuré-only, immuable, fail-closed.
"""
from __future__ import annotations

import hashlib
import json

COMPONENT_ID = "04_CANON_DETERMINATION"
VERSION = "1.0.0"

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-04-CANON-DETERMINATION",
    "META_ID": "META-ZORAN-V2-COMPONENT-04",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_04_CANON_DETERMINATION · branche mission/engine-04-canon-determination",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "NO_CANON_INVENTION",
        "NO_COHERENCE",
        "NO_OPERANT_EXECUTION",
        "NO_SCORING",
        "NO_LLM",
        "NO_NETWORK",
        "NO_MEMORY",
        "FROZEN_REFERENTIAL_FINGERPRINT",
        "CONFLICT_LISTED_NEVER_SILENT",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "canons_selected + conflicts + uncanonized explicites ; fingerprint sha256 ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions + fingerprint du referentiel",
    "ALERTE": "status=BLOCKED si 00/01/02/03 != PASS ; uncanonized pour toute paire sans canon ; conflicts pour egalite de priorite",
    "ANTI_REGRESSION": "tests non-invention + fail-closed + determinisme + fingerprint stable + conflit liste + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_04_CANON_DETERMINATION",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "determination deterministe des canons applicables par appartenance (frame+kind) + gel du referentiel avec fingerprint",
    "REJECTED_BEHAVIOR": "calcul de coherence, execution d'operant, scoring, requete LLM, invention de canon, modification du referentiel apres emission",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
RC00 = "00_RUNTIME_CHECK"
OD01 = "01_OBJECT_DISCOVERY"
FS02 = "02_ANALYSIS_FRAME_SELECTION"
OA03 = "03_OPERANTS_OPERES_ANALYSIS"
ORDER_KEY = "object_frame_map_order_puis_canon_priority_desc_puis_id_alphabetique"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "canons_selected", "canon_referential", "conflicts",
    "uncanonized", "resource_estimate", "order_key",
)

_EMPTY_REFERENTIAL = {
    "fingerprint": hashlib.sha256(b"[]").hexdigest(),
    "canons": [],
    "priorities": {},
}


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "canons_selected": [], "canon_referential": dict(_EMPTY_REFERENTIAL),
        "conflicts": [], "uncanonized": [],
        "resource_estimate": {"objects": 0, "frames": 0, "pairs": 0, "canons_applied": 0},
        "order_key": ORDER_KEY,
    }


def _applicable_canons(frame, kind, registry) -> list:
    """Canons du REGISTRE applicables à (frame, kind), triés priorité desc puis id.

    Dédup par id, ⊆ registre. Canon malformé (non-dict, sans id, applies_to non-liste,
    priority non-entière) → ignoré (fail-closed), jamais un crash.
    """
    seen: dict = {}
    for c in registry:
        if not isinstance(c, dict) or "id" not in c:
            continue
        frames = c.get("applies_to_frames")
        kinds = c.get("applies_to_kinds")
        prio = c.get("priority")
        if not (isinstance(frames, list) and isinstance(kinds, list)):
            continue
        if isinstance(prio, bool) or not isinstance(prio, int):
            continue
        if frame in frames and kind in kinds:
            seen[c["id"]] = prio
    return sorted(
        ({"id": cid, "priority": prio} for cid, prio in seen.items()),
        key=lambda x: (-x["priority"], x["id"]),
    )


def _conflicts_for(key, frame, apps) -> list:
    """Conflit = ≥2 canons applicables de MÊME priorité (précédence ambiguë).

    Résolu déterministiquement par id, mais LISTÉ (jamais écrasé en silence).
    """
    by_prio: dict = {}
    for a in apps:
        by_prio.setdefault(a["priority"], []).append(a["id"])
    out = []
    for prio in sorted(by_prio, reverse=True):
        ids = by_prio[prio]
        if len(ids) >= 2:
            out.append({
                "object_key": key, "frame": frame,
                "priority": prio, "canons": sorted(ids),
            })
    return out


def _fingerprint(priorities: dict) -> str:
    """Empreinte déterministe du référentiel gelé (sha256 des (id, priorité) triés)."""
    payload = json.dumps(sorted(priorities.items()), separators=(",", ":"),
                         ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_canon_determination(envelope: dict, registry: list) -> dict:
    """Fonction PURE : (envelope, registry) -> détermination + gel des canons."""
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
    oa = envelope.get("operants_operes")
    if not (isinstance(oa, dict) and oa.get("status") == PASS):
        return _blocked(OA03)

    kind_by_key = {
        o.get("object_key"): o.get("kind")
        for o in (od.get("objects") or []) if isinstance(o, dict)
    }

    canons_selected = []
    conflicts = []
    uncanonized = []
    priorities: dict = {}
    objects_seen = set()
    frames_seen = set()
    pairs = 0

    for entry in (fs.get("object_frame_map") or []):
        if not isinstance(entry, dict):
            continue
        key = entry.get("object_key")
        kind = kind_by_key.get(key)
        objects_seen.add(key)
        for frame in (entry.get("frames") or []):
            pairs += 1
            frames_seen.add(frame)
            apps = _applicable_canons(frame, kind, registry)
            if apps:
                canons_selected.append({
                    "object_key": key, "frame": frame,
                    "canons": [a["id"] for a in apps],
                })
                conflicts.extend(_conflicts_for(key, frame, apps))
                for a in apps:
                    priorities[a["id"]] = a["priority"]
            else:
                uncanonized.append({"object_key": key, "frame": frame})

    canon_referential = {
        "fingerprint": _fingerprint(priorities),
        "canons": sorted(priorities),
        "priorities": dict(sorted(priorities.items())),
    }
    resource_estimate = {
        "objects": len(objects_seen),
        "frames": len(frames_seen),
        "pairs": pairs,
        "canons_applied": len(priorities),
    }

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "canons_selected": canons_selected,
        "canon_referential": canon_referential,
        "conflicts": conflicts,
        "uncanonized": uncanonized,
        "resource_estimate": resource_estimate,
        "order_key": ORDER_KEY,
    }


def _canons_from_yaml_obj(obj) -> list:
    """Fail-closed : liste vide si YAML vide (None) ou top-level non-dict."""
    return obj.get("canons", []) if isinstance(obj, dict) else []


def load_canon_registry(path=None) -> list:
    """Partie IMPURE fine : charge le registre CANONS.yaml (fail-closed)."""
    import yaml
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "CANONS.yaml"
    with open(p, encoding="utf-8") as f:
        return _canons_from_yaml_obj(yaml.safe_load(f))


def main(envelope: dict) -> dict:
    return run_canon_determination(envelope, load_canon_registry())
