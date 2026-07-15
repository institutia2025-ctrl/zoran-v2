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

Robustesse (audit indépendant 2026-07-14) :
- registre normalisé/dédupliqué DÉTERMINISTIQUEMENT par `id` (indépendant de
  l'ordre, même en cas de doublon d'id à priorités différentes) ;
- `fingerprint` calculé sur les RECORDS COMPLETS gelés (id + priorité + applies_to) ;
- chargement YAML FAIL-CLOSED (YAML invalide → registre vide, jamais un crash).
"""
from __future__ import annotations

import hashlib
import json

COMPONENT_ID = "04_CANON_DETERMINATION"
VERSION = "1.0.0"
FULL_REGISTRY_SOURCE = "CANONS.yaml"
FULL_REGISTRY_VERSION = "1.0.0"
REGISTRY_NORMALIZATION_ID = "zoran_v2.canon_determination._normalize_registry"
REGISTRY_NORMALIZATION_VERSION = "1.0.0"

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
        "DETERMINISTIC_REGISTRY_NORMALIZATION",
        "FULL_REGISTRY_COMMITMENT",
        "FROZEN_REFERENTIAL_FINGERPRINT",
        "CONFLICT_LISTED_NEVER_SILENT",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "canons_selected + conflicts + uncanonized explicites ; fingerprints du sous-ensemble applique et du registre normalise complet ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions + fingerprint du referentiel",
    "ALERTE": "status=BLOCKED si 00/01/02 != PASS, si payload 03 malforme/faux-PASS (contrat 03 revalide, pas seulement le status) ou si payload 01/02 malforme (type canonique impose, jamais un crash sur cle non hashable) ; uncanonized pour toute paire sans canon ; conflicts pour egalite de priorite",
    "ANTI_REGRESSION": "tests non-invention + fail-closed + determinisme (dont dedup id ordre-independant) + fingerprint complet + conflit liste + loader YAML fail-closed + gouvernance ; gate CI",
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
    "RETAINED_BEHAVIOR": "determination deterministe des canons applicables par appartenance (frame+kind) + gel du referentiel avec fingerprint complet",
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
MALFORMED = "04_CANON_DETERMINATION_MALFORMED_INPUT"
ORDER_KEY = "object_frame_map_order_puis_canon_priority_desc_puis_id_alphabetique"


_VALID_03_KEYS = frozenset((
    "component", "version", "status", "blocked_by", "analysis", "unanalyzed", "order_key",
))
_ANALYSIS_ENTRY_KEYS = frozenset(("frame", "object_key", "operants", "operes"))
_UNANALYZED_ENTRY_KEYS = frozenset(("frame", "object_key"))
_OA_VERSION = "1.0.0"
_OA_ORDER_KEY = "object_frame_map_order_puis_operant_id_alphabetique"


def _valid_03_output(oa, object_keys_01, pairs_02) -> bool:
    """Contrat COMPLET de sortie de 03 (CSB-03-04-P1-001 / GC-PR16-001).

    04 ne fait confiance NI au statut NI au contenu de 03 : il revalide intégralement le payload,
    STRUCTURE et PROVENANCE, contre l'amont autoritaire 01/02. Impose :
    - clés racine EXACTES, component/version/order_key canoniques, status=PASS/blocked_by=None ;
    - chaque entrée `analysis` = {frame:str, object_key:str non vide, operants:list[str],
      operes:[object_key]} avec (object_key,frame) ∈ 02 ET object_key ∈ 01 ;
    - chaque entrée `unanalyzed` = {frame:str, object_key:str non vide} avec (object_key,frame) ∈ 02 ;
    - aucun couple (object_key,frame) en double, ni présent à la fois dans analysis et unanalyzed ;
    - COUVERTURE EXACTE : analysis ∪ unanalyzed == exactement les couples de 02.
    """
    if not (isinstance(oa, dict) and set(oa) == _VALID_03_KEYS):
        return False
    if oa.get("status") != PASS or oa.get("blocked_by") is not None:
        return False
    if (oa.get("component") != "03_OPERANTS_OPERES_ANALYSIS"
            or oa.get("version") != _OA_VERSION or oa.get("order_key") != _OA_ORDER_KEY):
        return False
    analysis, unanalyzed = oa.get("analysis"), oa.get("unanalyzed")
    if not (isinstance(analysis, list) and isinstance(unanalyzed, list)):
        return False
    seen = set()
    for a in analysis:
        if not (isinstance(a, dict) and set(a) == _ANALYSIS_ENTRY_KEYS):
            return False
        ok, fr = a.get("object_key"), a.get("frame")
        if not (isinstance(ok, str) and ok and isinstance(fr, str)):
            return False
        operants = a.get("operants")
        if not (isinstance(operants, list) and all(isinstance(x, str) for x in operants)):
            return False
        if a.get("operes") != [ok]:
            return False
        if ok not in object_keys_01 or (ok, fr) not in pairs_02 or (ok, fr) in seen:
            return False
        seen.add((ok, fr))
    for u in unanalyzed:
        if not (isinstance(u, dict) and set(u) == _UNANALYZED_ENTRY_KEYS):
            return False
        ok, fr = u.get("object_key"), u.get("frame")
        if not (isinstance(ok, str) and ok and isinstance(fr, str)):
            return False
        if (ok, fr) not in pairs_02 or (ok, fr) in seen:
            return False
        seen.add((ok, fr))
    return seen == pairs_02  # couverture exacte des couples autoritaires de 02


def _valid_objects(objects) -> bool:
    """Payload 01 autoritaire : liste d'objets {object_key: str non vide, kind: str}. Type canonique
    STRICT (pas seulement hashable) -> fail-closed déterministe, jamais un crash (CSB-03-04-P1-002)."""
    if not isinstance(objects, list):
        return False
    for o in objects:
        if not (isinstance(o, dict) and isinstance(o.get("object_key"), str) and o.get("object_key")
                and isinstance(o.get("kind"), str)):
            return False
    return True


def _valid_object_frame_map(ofm) -> bool:
    """Payload 02 autoritaire : liste d'entrées {object_key: str non vide, frames: list[str]}."""
    if not isinstance(ofm, list):
        return False
    for e in ofm:
        if not (isinstance(e, dict) and isinstance(e.get("object_key"), str) and e.get("object_key")):
            return False
        frames = e.get("frames")
        if not (isinstance(frames, list) and all(isinstance(f, str) for f in frames)):
            return False
    return True

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "canons_selected", "canon_referential", "full_registry_commitment", "conflicts",
    "uncanonized", "resource_estimate", "order_key",
)


def _fingerprint(frozen_canons: list) -> str:
    """Empreinte déterministe du référentiel gelé (sha256 des RECORDS COMPLETS triés)."""
    ordered = sorted(frozen_canons, key=lambda c: c["id"])
    payload = json.dumps(ordered, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_EMPTY_FINGERPRINT = _fingerprint([])


def _empty_referential() -> dict:
    return {"fingerprint": _EMPTY_FINGERPRINT, "canons": [], "priorities": {}}


def _full_registry_commitment(normalized_registry: list) -> dict:
    """Engagement versionne du registre NORMALISE COMPLET, distinct du sous-referentiel applique."""
    return {
        "full_registry_fingerprint": _fingerprint(normalized_registry),
        "registry_version": FULL_REGISTRY_VERSION,
        "registry_source": FULL_REGISTRY_SOURCE,
        "normalization": {
            "id": REGISTRY_NORMALIZATION_ID,
            "version": REGISTRY_NORMALIZATION_VERSION,
        },
    }


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "canons_selected": [], "canon_referential": _empty_referential(),
        "full_registry_commitment": _full_registry_commitment([]),
        "conflicts": [], "uncanonized": [],
        "resource_estimate": {"objects": 0, "frames": 0, "pairs": 0, "canons_applied": 0},
        "order_key": ORDER_KEY,
    }


def _norm_str_list(xs) -> list:
    return sorted({x for x in xs if isinstance(x, str)})


def _clean_canon(c) -> dict | None:
    """Valide + normalise un canon. None si malformé (fail-closed).

    id DOIT être une str non vide (sinon inutilisable comme clé -> rejet, pas de TypeError).
    """
    if not isinstance(c, dict):
        return None
    cid = c.get("id")
    if not (isinstance(cid, str) and cid):
        return None
    frames = c.get("applies_to_frames")
    kinds = c.get("applies_to_kinds")
    prio = c.get("priority")
    if not (isinstance(frames, list) and isinstance(kinds, list)):
        return None
    if isinstance(prio, bool) or not isinstance(prio, int):
        return None
    return {
        "id": c["id"],
        "priority": prio,
        "applies_to_frames": _norm_str_list(frames),
        "applies_to_kinds": _norm_str_list(kinds),
    }


def _normalize_registry(registry: list) -> list:
    """Dédup DÉTERMINISTE par id (indépendant de l'ordre) + validation fail-closed.

    Doublon d'id : on garde le record au (priorité max ; à égalité, JSON trié max)
    — résolution stable, jamais dépendante de l'ordre du registre.
    """
    best: dict = {}
    for c in registry:
        rec = _clean_canon(c)
        if rec is None:
            continue
        key = (rec["priority"], json.dumps(rec, sort_keys=True, ensure_ascii=False))
        cur = best.get(rec["id"])
        if cur is None or key > cur[0]:
            best[rec["id"]] = (key, rec)
    return [best[i][1] for i in sorted(best)]


def _applicable_canons(frame, kind, norm_registry) -> list:
    """Records du registre NORMALISÉ applicables à (frame, kind), triés priorité desc puis id."""
    out = [c for c in norm_registry
           if frame in c["applies_to_frames"] and kind in c["applies_to_kinds"]]
    return sorted(out, key=lambda c: (-c["priority"], c["id"]))


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
    if not (isinstance(oa, dict) and oa.get("status") == PASS):  # gate rapide de statut 03
        return _blocked(OA03)

    # Payloads AUTORITAIRES consommés (01 objects, 02 object_frame_map) : type canonique STRICT,
    # fail-closed déterministe (jamais un crash sur une clé non hashable, CSB-03-04-P1-002).
    if not (_valid_objects(od.get("objects")) and _valid_object_frame_map(fs.get("object_frame_map"))):
        return _blocked(MALFORMED)
    object_keys_01 = {o["object_key"] for o in od["objects"]}
    pairs_02 = {(e["object_key"], f) for e in fs["object_frame_map"] for f in e["frames"]}

    # Contrat COMPLET de 03 (CSB-03-04-P1-001 / GC-PR16-001) : au-dela du statut, 04 revalide la
    # STRUCTURE de chaque entree ET sa PROVENANCE (couples ⊆ 02, object_key des analyses ⊆ 01,
    # couverture exacte des couples de 02). Un payload 03 fictif/incoherent est rejete.
    if not _valid_03_output(oa, object_keys_01, pairs_02):
        return _blocked(OA03)

    norm_registry = _normalize_registry(registry)
    full_registry_commitment = _full_registry_commitment(norm_registry)

    # Payloads déjà VALIDÉS (type canonique) -> accès direct, sans `or []` ni skip silencieux.
    kind_by_key = {o["object_key"]: o["kind"] for o in od["objects"]}

    canons_selected = []
    conflicts = []
    uncanonized = []
    frozen: dict = {}          # id -> record complet gelé
    objects_seen = set()
    frames_seen = set()
    pairs = 0

    for entry in fs["object_frame_map"]:
        key = entry["object_key"]
        kind = kind_by_key.get(key)
        objects_seen.add(key)
        for frame in entry["frames"]:
            pairs += 1
            frames_seen.add(frame)
            apps = _applicable_canons(frame, kind, norm_registry)
            if apps:
                canons_selected.append({
                    "object_key": key, "frame": frame,
                    "canons": [a["id"] for a in apps],
                })
                conflicts.extend(_conflicts_for(key, frame, apps))
                for a in apps:
                    frozen[a["id"]] = a
            else:
                uncanonized.append({"object_key": key, "frame": frame})

    frozen_list = [frozen[i] for i in sorted(frozen)]
    canon_referential = {
        "fingerprint": _fingerprint(frozen_list),
        "canons": frozen_list,   # RECORDS COMPLETS (id + priorité + applies_to) — fingerprint complet
        "priorities": {c["id"]: c["priority"] for c in frozen_list},
    }
    resource_estimate = {
        "objects": len(objects_seen),
        "frames": len(frames_seen),
        "pairs": pairs,
        "canons_applied": len(frozen_list),
    }

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "canons_selected": canons_selected,
        "canon_referential": canon_referential,
        "full_registry_commitment": full_registry_commitment,
        "conflicts": conflicts,
        "uncanonized": uncanonized,
        "resource_estimate": resource_estimate,
        "order_key": ORDER_KEY,
    }


def _canons_from_yaml_obj(obj) -> list:
    """Fail-closed : liste vide si YAML vide (None) ou top-level non-dict."""
    return obj.get("canons", []) if isinstance(obj, dict) else []


def load_canon_registry(path=None) -> list:
    """Partie IMPURE fine : charge le registre CANONS.yaml (FAIL-CLOSED).

    YAML invalide (erreur de parse) ou fichier illisible → registre VIDE, jamais un crash.
    """
    import yaml
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parents[1] / "CANONS.yaml"
    try:
        with open(p, encoding="utf-8") as f:
            return _canons_from_yaml_obj(yaml.safe_load(f))
    except (yaml.YAMLError, OSError):
        return []


def main(envelope: dict) -> dict:
    return run_canon_determination(envelope, load_canon_registry())
