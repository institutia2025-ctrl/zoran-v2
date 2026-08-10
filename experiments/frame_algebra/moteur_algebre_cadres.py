# -*- coding: utf-8 -*-
"""
ZORAN — ALGÈBRE DE CADRES K3 v1.1 CANDIDATE

Rôle borné
----------
Sous-opérateur déterministe du bloc B (Ω∞ COHERENCE CORE) pour COMBINER des
verdicts de cadres déjà produits : PASS / FAIL / NON_MESURÉ.

Ce module :
  - implémente la logique forte de Kleene K3 ;
  - valide strictement les expressions ;
  - conserve NON_MESURÉ sans coercition ;
  - produit une empreinte sémantique déterministe + une empreinte artefact.

Ce module NE :
  - sélectionne pas les cadres ;
  - ne calcule pas β, ΔΦ, T, σ ou S ;
  - ne remplace pas la POLARITÉ sémantique historique ;
  - ne transforme pas une implication logique en preuve causale ;
  - n'autorise aucune action.

Important
---------
K3 autorise par exemple PASS ∨ NON_MESURÉ = PASS et
FAIL ∧ NON_MESURÉ = FAIL : l'inconnu n'est pas converti ; il est simplement
non-déterminant dans ces formules. L'admissibilité globale reste une politique
distincte : si tous les cadres requis doivent passer, utiliser ET sur ces cadres.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
from numbers import Real
from typing import Any, Optional

VERSION = "ZORAN-FRAME-ALGEBRA-K3-1.1-CANDIDATE"

PASS = "PASS"
NON_MESURE = "NON_MESURÉ"
FAIL = "FAIL"
VALEURS = (FAIL, NON_MESURE, PASS)

_RANG = {FAIL: 0, NON_MESURE: 1, PASS: 2}
_VAL = {v: k for k, v in _RANG.items()}

DEFAULT_SEUIL = 6.0


class AlgebreCadresError(ValueError):
    pass


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds")


def _canonical(o: Any) -> bytes:
    return json.dumps(
        o,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha(o: Any) -> str:
    return hashlib.sha256(_canonical(o)).hexdigest()


def _valeur(v: str) -> str:
    if v not in _RANG:
        raise AlgebreCadresError(f"valeur K3 invalide : {v!r}")
    return v


def _nombre_fini(v: Any, nom: str) -> float:
    if isinstance(v, bool) or not isinstance(v, Real):
        raise AlgebreCadresError(f"{nom} doit être un nombre réel fini")
    f = float(v)
    if not math.isfinite(f):
        raise AlgebreCadresError(f"{nom} doit être fini")
    return f


def score_vers_kleene(score: Optional[Real], seuil: Real = DEFAULT_SEUIL) -> str:
    seuil_f = _nombre_fini(seuil, "seuil")
    if score is None:
        return NON_MESURE
    score_f = _nombre_fini(score, "score")
    return PASS if score_f >= seuil_f else FAIL


def projeter_scores(scores: dict[str, Optional[Real]], seuil: Real = DEFAULT_SEUIL) -> dict[str, str]:
    if not isinstance(scores, dict) or not scores:
        raise AlgebreCadresError("scores doit être un dictionnaire non vide")
    out: dict[str, str] = {}
    for nom, score in scores.items():
        if not isinstance(nom, str) or not nom.strip():
            raise AlgebreCadresError("nom de cadre invalide")
        out[nom] = score_vers_kleene(score, seuil)
    return out


def NON(a: str) -> str:
    """Complément d'un VERDICT DE CADRE, pas négation sémantique d'un claim."""
    a = _valeur(a)
    return {PASS: FAIL, FAIL: PASS, NON_MESURE: NON_MESURE}[a]


def ET(*vals: str) -> str:
    if not vals:
        raise AlgebreCadresError("ET vide interdit")
    return _VAL[min(_RANG[_valeur(v)] for v in vals)]


def OU(*vals: str) -> str:
    if not vals:
        raise AlgebreCadresError("OU vide interdit")
    return _VAL[max(_RANG[_valeur(v)] for v in vals)]


def IMPLIQUE(a: str, b: str) -> str:
    """
    Implication vérité-fonctionnelle K3 : ¬a ∨ b.
    Elle n'établit JAMAIS une relation causale.
    """
    return OU(NON(a), _valeur(b))


def DIFFERENCE(a: str, b: str) -> str:
    """A \\ B = A ∧ ¬B."""
    return ET(_valeur(a), NON(b))


def _valider_expression(e: Any) -> dict:
    if not isinstance(e, dict) or len(e) != 1:
        raise AlgebreCadresError("chaque nœud doit contenir exactement un opérateur")
    op, payload = next(iter(e.items()))

    if op == "cadre":
        if not isinstance(payload, str) or not payload.strip():
            raise AlgebreCadresError("nom de cadre invalide")
        return {"cadre": payload}

    if op == "non":
        return {"non": _valider_expression(payload)}

    if op in {"et", "ou"}:
        if not isinstance(payload, list) or not payload:
            raise AlgebreCadresError(f"{op} exige une liste non vide")
        return {op: [_valider_expression(x) for x in payload]}

    if op in {"implique", "difference"}:
        if not isinstance(payload, list) or len(payload) != 2:
            raise AlgebreCadresError(f"{op} exige exactement deux opérandes")
        return {op: [_valider_expression(payload[0]), _valider_expression(payload[1])]}

    raise AlgebreCadresError(f"opérateur inconnu : {op!r}")


def _valider_cadres(cadres: Any) -> dict[str, str]:
    if not isinstance(cadres, dict) or not cadres:
        raise AlgebreCadresError("cadres K3 doit être un dictionnaire non vide")
    out: dict[str, str] = {}
    for nom, verdict in cadres.items():
        if not isinstance(nom, str) or not nom.strip():
            raise AlgebreCadresError("nom de cadre invalide")
        out[nom] = _valeur(verdict)
    return out


def _dependances(expression: dict) -> set[str]:
    op, payload = next(iter(expression.items()))
    if op == "cadre":
        return {payload}
    if op == "non":
        return _dependances(payload)
    deps: set[str] = set()
    for x in payload:
        deps |= _dependances(x)
    return deps


def _eval(expression: dict, cadres: dict[str, str]) -> str:
    op, payload = next(iter(expression.items()))

    if op == "cadre":
        if payload not in cadres:
            raise AlgebreCadresError(f"cadre inconnu dans l'expression : {payload}")
        return cadres[payload]
    if op == "non":
        return NON(_eval(payload, cadres))
    if op == "et":
        return ET(*(_eval(x, cadres) for x in payload))
    if op == "ou":
        return OU(*(_eval(x, cadres) for x in payload))
    if op == "implique":
        return IMPLIQUE(_eval(payload[0], cadres), _eval(payload[1], cadres))
    if op == "difference":
        return DIFFERENCE(_eval(payload[0], cadres), _eval(payload[1], cadres))
    raise AssertionError("expression validée mais opérateur introuvable")


def cout_de_contrainte(cadres: dict[str, str], nom_contrainte: str) -> dict:
    k = _valider_cadres(cadres)
    if nom_contrainte not in k:
        raise AlgebreCadresError(f"cadre absent : {nom_contrainte}")

    avec = ET(*k.values())
    autres = [v for n, v in k.items() if n != nom_contrainte]
    sans = ET(*autres) if autres else PASS

    if avec == sans:
        impact = "AUCUN_EFFET_SUR_ET_GLOBAL"
    elif avec == FAIL and sans != FAIL:
        impact = "BLOQUANTE"
    elif avec == NON_MESURE and sans == PASS:
        impact = "INCERTITUDE_CRITIQUE"
    else:
        impact = "MODIFIE_VERDICT"

    return {
        "avec_contrainte": avec,
        "sans_contrainte": sans,
        "impact": impact,
        "contrainte_est_bloquante": impact == "BLOQUANTE",
        "contrainte_est_inconnue_critique": impact == "INCERTITUDE_CRITIQUE",
        "valeur_contrainte": k[nom_contrainte],
        "convention_sans_aucun_cadre": "ET_VIDE_MATHEMATIQUE=PASS",
    }


def evaluer(expression: dict, cadres: dict[str, str]) -> dict:
    expr = _valider_expression(expression)
    k = _valider_cadres(cadres)

    deps = sorted(_dependances(expr))
    manquants = [n for n in deps if n not in k]
    if manquants:
        raise AlgebreCadresError(f"cadres manquants : {manquants}")

    resultat = _eval(expr, k)
    inconnus_utilises = sorted(n for n in deps if k[n] == NON_MESURE)

    semantique = {
        "_type": "certificat_algebre_cadres",
        "version": VERSION,
        "logique": "Kleene K3 forte",
        "cadres_kleene": {n: k[n] for n in sorted(k)},
        "expression": expr,
        "dependances": deps,
        "cadres_non_mesures_utilises": inconnus_utilises,
        "resultat": resultat,
        "scope": "ALGEBRE_VERDICTS_CADRES_ONLY",
    }
    semantic_hash = _sha(semantique)

    artefact = {
        **semantique,
        "empreinte_semantique_sha256": semantic_hash,
        "horodatage": _now(),
    }
    artefact["empreinte_artefact_sha256"] = _sha(artefact)
    return artefact
