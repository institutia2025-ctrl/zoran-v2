"""05_COHERENCE_ENGINE — porte 5 du pipeline de raisonnement ZORAN V2 (1re passe).

Exécute les opérants (03) dans le référentiel canonique GELÉ (04, `fingerprint`
revérifié) et mesure la cohérence via la formule CANONIQUE VERROUILLÉE :

    S = (beta * delta_phi) / (1 + T + sigma)

Produit S + un verdict RESSOURCE (autorise/veto l'appel LLM de 07). Déterministe,
structuré-only, immuable, fail-closed 00→04. NE génère pas (07), ne construit pas
la requête (06), n'appelle AUCUN LLM.

V1 — opérationnalisation STRUCTURELLE (falsifiable, non « vérité ») :
- ΔΦ = taux de résolution = part des paires (objet,cadre) à la fois CANONISÉES (04)
       ET pourvues d'opérants (03). ∈ [0,1].
- T  = tension = (conflits de canons (04) + violations de contraintes) / paires.
       V1 : violations = 0 (l'exécution SÉMANTIQUE des opérants placeholders est
       différée ; V1 mesure la PRÉSENCE structurelle, pas un verdict sémantique).
- σ  = dispersion = coefficient de variation du nombre de canons par objet.
- beta = 1.0 (neutre V1). Veto RESSOURCE si ΔΦ < DELTA_PHI_MIN (= 0.5).
"""
from __future__ import annotations

import statistics

from zoran_v2.canon_determination import _fingerprint as _canon_fingerprint

COMPONENT_ID = "05_COHERENCE_ENGINE"
VERSION = "1.0.0"

# Formule CANONIQUE — chaîne verrouillée (identique au canonical_guard historique).
CANONICAL_FORMULA = "S = (beta * delta_phi) / (1 + T + sigma)"
BETA_V1 = 1.0
DELTA_PHI_MIN = 0.5

GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-05-COHERENCE-ENGINE",
    "META_ID": "META-ZORAN-V2-COMPONENT-05",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_05_COHERENCE_ENGINE · branche mission/engine-05-coherence-engine",
    "GUARD_IDS": [
        "STRUCTURED_ONLY",
        "CANONICAL_FORMULA_LOCKED",
        "NO_LLM",
        "NO_GENERATION",
        "NO_NETWORK",
        "NO_MEMORY",
        "REFERENTIAL_FINGERPRINT_VERIFIED",
        "RESOURCE_VETO_BEFORE_07",
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "IMMUTABLE_SNAPSHOT",
    ],
    "TRACEABILITY": "coherence {delta_phi,tension,sigma,S} + resource verdict ; fingerprint 04 verifie ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=BLOCKED si 00/01/02/03/04 != PASS ou fingerprint 04 absent ; veto RESSOURCE si delta_phi < 0.5",
    "ANTI_REGRESSION": "tests formule canonique verrouillee + determinisme + fail-closed + veto ressource + gouvernance ; gate CI",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

PROVENANCE_DECL = {
    "SOURCE_TYPE": "new",
    "CANONICAL_SPEC": "SPEC_ENGINE_05_COHERENCE_ENGINE",
    "SOURCE_SHA": None,
    "RETAINED_BEHAVIOR": "mesure de coherence structurelle (delta_phi/T/sigma) via formule canonique verrouillee + verdict ressource (veto 07)",
    "REJECTED_BEHAVIOR": "generation, appel LLM, construction de requete, modification du referentiel, deviation de la formule canonique",
    "LEGACY_CHECK": "aucun comportement du registre FORBIDDEN reintroduit",
    "BEHAVIOR_FLAGS": {"requests_llm_prechoices": False},
}

PASS = "PASS"
BLOCKED = "BLOCKED"
RC00 = "00_RUNTIME_CHECK"
OD01 = "01_OBJECT_DISCOVERY"
FS02 = "02_ANALYSIS_FRAME_SELECTION"
OA03 = "03_OPERANTS_OPERES_ANALYSIS"
CD04 = "04_CANON_DETERMINATION"
MALFORMED = "05_COHERENCE_ENGINE_MALFORMED_INPUT"
FINGERPRINT_MISMATCH = "05_COHERENCE_ENGINE_FINGERPRINT_MISMATCH"
ORDER_KEY = "coherence_globale_deterministe_puis_verdict_ressource"

OUTPUT_KEYS = (
    "component", "version", "status", "blocked_by",
    "coherence", "resource", "order_key",
)


def _blocked(by: str) -> dict:
    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": BLOCKED, "blocked_by": by,
        "coherence": None, "resource": None, "order_key": ORDER_KEY,
    }


def _pair(entry_key, frame):
    return (entry_key, frame)


def _keys_all_str(*lists) -> bool:
    """True ssi CHAQUE entrée est un dict avec object_key ET frame str (hashable, bien formé).

    Un élément non-dict est REJETÉ, PAS ignoré : sinon un enregistrement malformé serait
    écarté silencieusement et pourrait mener à un PASS trompeur (finding audit global).
    Empêche aussi le TypeError (object_key=liste -> unhashable). Un conteneur non-liste est
    lui-même rejeté (jamais d'itération sur un scalaire). Entrée malformée -> fail-closed.
    """
    for lst in lists:
        if not isinstance(lst, list):
            return False
        for e in lst:
            if not isinstance(e, dict):
                return False
            if not (isinstance(e.get("object_key"), str) and isinstance(e.get("frame"), str)):
                return False
    return True


def _frozen_referential_wellformed(frozen_canons: list) -> bool:
    """True ssi chaque record du référentiel GELÉ (04) est un dict avec un `id` str non vide.

    Condition NÉCESSAIRE pour recalculer le fingerprint (04 trie sur ``c["id"]``) SANS lever
    KeyError/TypeError. Un record malformé (``{}``, ``[]``, str, ``id`` non-str/vide) -> fail-closed
    au lieu d'un crash (finding audit : 05 crashait sur un référentiel 04 malformé).
    """
    for c in frozen_canons:
        if not (isinstance(c, dict) and isinstance(c.get("id"), str) and c.get("id")):
            return False
    return True


def run_coherence_engine(envelope: dict) -> dict:
    """Fonction PURE : envelope(00→04) -> cohérence S canonique + verdict ressource."""
    if not isinstance(envelope, dict):
        raise TypeError("envelope doit être un dict")

    for key, comp in (("runtime_check", RC00), ("object_discovery", OD01),
                      ("frame_selection", FS02), ("operants_operes", OA03),
                      ("canon_determination", CD04)):
        node = envelope.get(key)
        if not (isinstance(node, dict) and node.get("status") == PASS):
            return _blocked(comp)

    cd = envelope["canon_determination"]
    referential = cd.get("canon_referential")
    fingerprint = referential.get("fingerprint") if isinstance(referential, dict) else None
    if not (isinstance(fingerprint, str) and fingerprint):
        return _blocked(CD04)  # référentiel non gelé / fingerprint invalide -> fail-closed
    # Ré-vérification RÉELLE du gel : recalculer le sha256 des canons et comparer.
    # (Sinon un référentiel modifié gardant le même texte de fingerprint passerait.)
    frozen_canons = referential.get("canons")
    # Un référentiel 04 malformé (record non-dict, ou `id` non-str) ferait lever _fingerprint
    # (KeyError/TypeError sur c["id"]) AVANT toute comparaison : on valide D'ABORD -> fail-closed.
    if not isinstance(frozen_canons, list) or not _frozen_referential_wellformed(frozen_canons):
        return _blocked(FINGERPRINT_MISMATCH)
    try:
        recomputed_fp = _canon_fingerprint(frozen_canons)
    except Exception:  # noqa: BLE001 — référentiel 04 non-sérialisable/inattendu -> fail-closed, jamais un crash
        return _blocked(FINGERPRINT_MISMATCH)
    if recomputed_fp != fingerprint:
        return _blocked(FINGERPRINT_MISMATCH)

    canons_selected = cd.get("canons_selected")
    uncanonized = cd.get("uncanonized")
    conflicts = cd.get("conflicts")
    oa = envelope["operants_operes"]
    analysis = oa.get("analysis")

    # Clé absente/None -> liste vide LÉGITIME. Toute AUTRE valeur non-liste (ex. {}, 0, '', ())
    # est MALFORMÉE : elle doit être BLOQUÉE, pas normalisée silencieusement en [] par `or []`
    # (finding GC-D1-002 : un conteneur falsy non-liste ne doit pas contourner le fail-closed).
    for lst in (canons_selected, uncanonized, conflicts, analysis):
        if lst is not None and not isinstance(lst, list):
            return _blocked(MALFORMED)
    canons_selected = canons_selected or []
    uncanonized = uncanonized or []
    conflicts = conflicts or []
    analysis = analysis or []

    # Entrée malformée (object_key/frame non-str -> non hashable) -> fail-closed, jamais un crash.
    if not _keys_all_str(canons_selected, uncanonized, analysis):
        return _blocked(MALFORMED)

    operant_pairs = {
        _pair(a.get("object_key"), a.get("frame"))
        for a in analysis if isinstance(a, dict)
    }
    # Univers des paires = tout ce que 04 a vu (canonisées + non canonisées).
    canonized_pairs = {
        _pair(c.get("object_key"), c.get("frame"))
        for c in canons_selected if isinstance(c, dict)
    }
    uncanon_pairs = {
        _pair(u.get("object_key"), u.get("frame"))
        for u in uncanonized if isinstance(u, dict)
    }
    universe = canonized_pairs | uncanon_pairs
    total_pairs = len(universe)

    # ΔΦ = part des paires résolues (canonisées ET pourvues d'opérants).
    resolved = len(canonized_pairs & operant_pairs)
    delta_phi = 1.0 if total_pairs == 0 else round(resolved / total_pairs, 6)

    # T = (conflits + violations) / paires. V1 : violations sémantiques = 0.
    violations = 0
    tension = 0.0 if total_pairs == 0 else round((len(conflicts) + violations) / total_pairs, 6)

    # σ = coefficient de variation du nombre de canons par objet, sur TOUS les objets
    # de l'univers (un objet à 0 canon compte comme 0 -> dispersion non sous-estimée).
    all_objects = {ok for (ok, _fr) in universe}
    canons_by_object = {ok: set() for ok in all_objects}
    for c in canons_selected:
        if isinstance(c, dict):
            canons_by_object.setdefault(c.get("object_key"), set()).update(c.get("canons") or [])
    counts = [len(canons_by_object[ok]) for ok in sorted(all_objects)]
    if len(counts) >= 2 and statistics.mean(counts) > 0:
        sigma = round(statistics.pstdev(counts) / statistics.mean(counts), 6)
    else:
        sigma = 0.0

    S = round((BETA_V1 * delta_phi) / (1.0 + tension + sigma), 6)

    # Autorisation LLM : jamais « à vide » (univers vide) — total_pairs > 0 requis.
    authorize = total_pairs > 0 and delta_phi >= DELTA_PHI_MIN
    if authorize:
        reason = "delta_phi>=seuil : 07 autorisé"
    elif total_pairs == 0:
        reason = "univers vide : rien à raisonner, 07 INTERDIT"
    else:
        reason = "delta_phi<seuil : 07 INTERDIT (veto ressource)"
    coherence = {
        "beta": BETA_V1,
        "delta_phi": delta_phi,
        "tension": tension,
        "sigma": sigma,
        "S": S,
        "S_kind": "S_structural_v1",   # échelle [0,1] — NE PAS confondre avec le S général (>=6)
        "S_range": [0.0, 1.0],
        "formula": CANONICAL_FORMULA,
        "resolved_pairs": resolved,
        "total_pairs": total_pairs,
        "conflicts": len(conflicts),
        "referential_fingerprint": fingerprint,
    }
    resource = {
        "authorize_llm": authorize,
        "delta_phi_min": DELTA_PHI_MIN,
        "reason": reason,
        "resource_estimate_echo": cd.get("resource_estimate"),
    }

    return {
        "component": COMPONENT_ID, "version": VERSION,
        "status": PASS, "blocked_by": None,
        "coherence": coherence, "resource": resource, "order_key": ORDER_KEY,
    }


def main(envelope: dict) -> dict:
    return run_coherence_engine(envelope)
