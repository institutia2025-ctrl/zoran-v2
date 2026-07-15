"""01_OBJECT_DISCOVERY — porte 1 du pipeline de raisonnement ZORAN V2.

Voie A ratifiée : DÉCOUVERTE STRUCTURÉE UNIQUEMENT. Ne traite QUE
`object_candidates` fournis par l'enveloppe. Aucune extraction depuis du
texte libre, aucun NLP/heuristique, aucun LLM/réseau/mémoire.

Bloqué si 00_RUNTIME_CHECK != PASS. Déterministe, immuable (snapshots),
fail-closed (candidat non ancrable -> dropped, jamais inventé).
"""
from __future__ import annotations

import unicodedata

COMPONENT_ID = "01_OBJECT_DISCOVERY"
VERSION = "1.0.0"

# --- Contrat de gouvernance du composant (objet V2 gouverné complet) ---
GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-01-OBJECT-DISCOVERY",
    "META_ID": "META-ZORAN-V2-COMPONENT-01",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_01_OBJECT_DISCOVERY · voie A · branche mission/engine-01-object-discovery",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "NO_INVENTION",
        "TEXT_IDENTITY_UNICODE_NFC",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "NO_LLM",
        "NO_NETWORK",
        "NO_MEMORY",
        "DEDUP_IDEMPOTENT",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "chaque objet porte sa provenance ; dropped explicite ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee dans seed-bootstrap ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00!=PASS ; dropped[] pour tout candidat non admissible (jamais silencieux) ; identite textuelle normalisee Unicode NFC (formes equivalentes -> meme object_key)",
    "ANTI_REGRESSION": "tests non-invention + dedup + ordre + fail-closed + gouvernance ; CI bloque le merge",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

# --- Déclaration de provenance (gate anti-résurrection) — métadonnée pure ---
PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_01_OBJECT_DISCOVERY",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "decouverte structuree-only, fail-closed, dedup deterministe",
    "REJECTED_BEHAVIOR": "extraction NLP/texte libre ; invention d'objets",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
RC00 = "00_RUNTIME_CHECK"
_SEP = "\x1f"  # séparateur de clé, non typable dans du texte normal
# Description stable de l'ordre déterministe (exposée dans la sortie, cf. contrat).
ORDER_KEY = "in_text.offset(1re_occurrence)_puis_object_key"


def _normalize(value):
    """Normalisation déterministe. Retourne None si non normalisable."""
    if isinstance(value, bool):
        return None  # un booléen n'est pas un objet-valeur
    if isinstance(value, str):
        # CSB-META-P1-003 : identité textuelle CANONIQUE. Normalisation Unicode NFC (REX #15, NFC par
        # défaut) pour que deux chaînes canoniquement équivalentes (formes précomposée/décomposée)
        # produisent le MÊME object_key. NFC appliqué APRÈS casefold pour recomposer la sortie.
        n = unicodedata.normalize("NFC", " ".join(value.split()).casefold())
        return n or None
    if isinstance(value, (int, float)):
        return repr(value)
    return None


def _verify_provenance(candidate: dict, input_text):
    """Retourne la provenance vérifiée, ou None (=> dropped)."""
    prov = candidate.get("provenance")
    if not isinstance(prov, dict):
        return None
    if "in_text" in prov:
        span = prov["in_text"]
        if not isinstance(span, dict):
            return None
        off, ln = span.get("offset"), span.get("len")
        if not (isinstance(off, int) and isinstance(ln, int)):
            return None
        if not isinstance(input_text, str) or off < 0 or ln < 0 or off + ln > len(input_text):
            return None
        raw = candidate.get("value")
        raw_s = raw if isinstance(raw, str) else str(raw)
        if input_text[off:off + ln] != raw_s:
            return None
        return {"in_text": {"offset": off, "len": ln}}
    if prov.get("structured"):
        return {"structured": True}
    return None


def run_object_discovery(envelope: dict) -> dict:
    """Fonction PURE : enveloppe -> liste d'objets découverts (structurés).

    Ne mute jamais l'enveloppe. Ne lève que sur mauvais usage de type.
    """
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    rc = envelope.get("runtime_check")
    if not (isinstance(rc, dict) and rc.get("status") == PASS):
        return {
            "component": COMPONENT_ID, "version": VERSION,
            "status": BLOCKED, "blocked_by": RC00,
            "objects": [], "count": 0, "dropped": [], "order_key": ORDER_KEY,
        }

    input_text = envelope.get("input_text")
    candidates = envelope.get("object_candidates")
    if candidates is None:
        candidates = []
    if not isinstance(candidates, list):
        raise TypeError("object_candidates doit être une liste")

    dropped: list[dict] = []
    by_key: dict[str, dict] = {}

    def _drop(idx, candidate, reason):
        # Conforme au contrat : on réémet le candidat rejeté (+ son index, traçabilité).
        dropped.append({"candidate_index": idx, "candidate": candidate, "reason": reason})

    for i, cand in enumerate(candidates):
        if not isinstance(cand, dict):
            _drop(i, cand, "not_a_dict")
            continue
        kind = cand.get("kind")
        if not (isinstance(kind, str) and kind.strip()):
            _drop(i, cand, "missing_kind")
            continue
        normalized = _normalize(cand.get("value"))
        if normalized is None:
            _drop(i, cand, "value_not_normalizable")
            continue
        prov = _verify_provenance(cand, input_text)
        if prov is None:
            _drop(i, cand, "provenance_unverified")
            continue

        key = f"{kind.strip()}{_SEP}{normalized}"
        off = prov.get("in_text", {}).get("offset") if "in_text" in prov else None
        if key in by_key:
            by_key[key]["provenance"].append(prov)
            if off is not None and (by_key[key]["order"] is None or off < by_key[key]["order"]):
                by_key[key]["order"] = off
        else:
            by_key[key] = {
                "object_key": key, "kind": kind.strip(),
                "normalized": normalized, "provenance": [prov], "order": off,
            }

    big = float("inf")
    ordered = sorted(
        by_key.values(),
        key=lambda o: (big if o["order"] is None else o["order"], o["object_key"]),
    )
    objects = [
        {"object_key": o["object_key"], "kind": o["kind"],
         "normalized": o["normalized"], "provenance": o["provenance"]}
        for o in ordered
    ]
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "objects": objects, "count": len(objects), "dropped": dropped,
        "order_key": ORDER_KEY,
    }
