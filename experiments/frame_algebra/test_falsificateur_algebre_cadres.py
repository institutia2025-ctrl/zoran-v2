# -*- coding: utf-8 -*-
import json
from moteur_algebre_cadres import (
    PASS, FAIL, NON_MESURE,
    NON, ET, OU, IMPLIQUE, DIFFERENCE,
    score_vers_kleene,
    cout_de_contrainte, evaluer, AlgebreCadresError,
)

R = {}

R["K1_non"] = (
    NON(PASS) == FAIL
    and NON(FAIL) == PASS
    and NON(NON_MESURE) == NON_MESURE
)

R["K2_et"] = (
    ET(PASS, PASS) == PASS
    and ET(PASS, FAIL) == FAIL
    and ET(PASS, NON_MESURE) == NON_MESURE
    and ET(FAIL, NON_MESURE) == FAIL
)

R["K3_ou"] = (
    OU(FAIL, FAIL) == FAIL
    and OU(PASS, FAIL) == PASS
    and OU(FAIL, NON_MESURE) == NON_MESURE
    and OU(PASS, NON_MESURE) == PASS
)

R["K4_implique_k3"] = (
    IMPLIQUE(PASS, FAIL) == FAIL
    and IMPLIQUE(FAIL, FAIL) == PASS
    and IMPLIQUE(NON_MESURE, PASS) == PASS
    and IMPLIQUE(NON_MESURE, FAIL) == NON_MESURE
)

R["K5_difference"] = (
    DIFFERENCE(PASS, FAIL) == PASS
    and DIFFERENCE(PASS, PASS) == FAIL
    and DIFFERENCE(PASS, NON_MESURE) == NON_MESURE
)

bad_mapping = []
for x in (float("nan"), float("inf"), float("-inf"), True, "7"):
    try:
        score_vers_kleene(x)
        bad_mapping.append(False)
    except AlgebreCadresError:
        bad_mapping.append(True)
R["K6_mapping_strict"] = (
    all(bad_mapping)
    and score_vers_kleene(None) == NON_MESURE
    and score_vers_kleene(7.0) == PASS
    and score_vers_kleene(4.0) == FAIL
)

guards = []
for f in (
    lambda: ET(),
    lambda: OU(),
    lambda: ET("UNKNOWN"),
    lambda: OU("UNKNOWN"),
):
    try:
        f()
        guards.append(False)
    except AlgebreCadresError:
        guards.append(True)
R["K7_operateurs_fermes"] = all(guards)

guards = []
for expr in (
    {"cadre": "a", "non": {"cadre": "a"}},
    {"et": []},
    {"ou": []},
    {"implique": [{"cadre": "a"}]},
    {"implique": [{"cadre": "a"}, {"cadre": "b"}, {"cadre": "c"}]},
    {"difference": [{"cadre": "a"}]},
    {"truc": [{"cadre": "a"}]},
):
    try:
        evaluer(expr, {"a": PASS, "b": FAIL, "c": NON_MESURE})
        guards.append(False)
    except AlgebreCadresError:
        guards.append(True)
R["K8_expression_fermee"] = all(guards)

cc_fail = cout_de_contrainte(
    {"securite": PASS, "legal": PASS, "budget": FAIL}, "budget"
)
cc_nm = cout_de_contrainte(
    {"securite": PASS, "legal": PASS, "budget": NON_MESURE}, "budget"
)
R["K9_cout_contrainte"] = (
    cc_fail["impact"] == "BLOQUANTE"
    and cc_fail["contrainte_est_bloquante"] is True
    and cc_nm["impact"] == "INCERTITUDE_CRITIQUE"
    and cc_nm["contrainte_est_bloquante"] is False
)

expr = {"et": [
    {"cadre": "securite"},
    {"ou": [{"cadre": "legal"}, {"cadre": "budget"}]},
]}
cadres = {"securite": PASS, "legal": PASS, "budget": FAIL}
c1 = evaluer(expr, cadres)
c2 = evaluer(expr, cadres)
R["K10_double_hash"] = (
    c1["resultat"] == PASS
    and c1["empreinte_semantique_sha256"] == c2["empreinte_semantique_sha256"]
    and len(c1["empreinte_semantique_sha256"]) == 64
    and len(c1["empreinte_artefact_sha256"]) == 64
)

c3 = evaluer(
    {"ou": [{"cadre": "a"}, {"cadre": "b"}]},
    {"a": PASS, "b": NON_MESURE},
)
R["K11_nm_non_coerce"] = (
    c3["resultat"] == PASS
    and c3["cadres_non_mesures_utilises"] == ["b"]
)

import moteur_algebre_cadres as m
R["K12_pas_autorite_action"] = not any(
    hasattr(m, name)
    for name in ("autoriser", "executer", "agent_agit", "ACTION_AUTHORIZED")
)

print(json.dumps(R, indent=2, ensure_ascii=False, sort_keys=True))
ok = all(R.values())
print(
    f"=== ALGÈBRE K3 : {sum(R.values())}/{len(R)} VERTS ===",
    "✅ CANDIDAT" if ok else "🔴 FIX_REQUIRED",
)
raise SystemExit(0 if ok else 1)
