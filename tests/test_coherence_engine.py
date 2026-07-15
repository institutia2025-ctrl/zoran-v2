"""Tests déterministes de 05_COHERENCE_ENGINE (envelope injectée).

Vérifie : formule canonique VERROUILLÉE, ΔΦ/T/σ structurels, veto ressource,
fail-closed 00→04 + fingerprint 04, déterminisme, immuabilité, gouvernance/provenance.
"""
import copy

import pytest

from zoran_v2.coherence_engine import (
    BETA_V1,
    BLOCKED,
    CANONICAL_FORMULA,
    COMPONENT_ID,
    DELTA_PHI_MIN,
    GOVERNANCE,
    GOVERNANCE_REQUIRED_KEYS,
    ORDER_KEY,
    OUTPUT_KEYS,
    PASS,
    PROVENANCE_DECL,
    VERSION,
    run_coherence_engine,
)
from zoran_v2.canon_determination import _fingerprint as _canon_fp


def _cd(canons_selected=None, uncanonized=None, conflicts=None, fingerprint=None,
        referential_canons=None, re=None):
    rc = referential_canons or []
    # Par défaut, fingerprint VALIDE (recalculé) ; passer fingerprint=... pour tester l'invalide.
    fp = fingerprint if fingerprint is not None else _canon_fp(rc)
    return {
        "status": PASS,
        "canons_selected": canons_selected or [],
        "uncanonized": uncanonized or [],
        "conflicts": conflicts or [],
        "canon_referential": {"fingerprint": fp, "canons": rc, "priorities": {}},
        "resource_estimate": re or {"objects": 0, "frames": 0, "pairs": 0, "canons_applied": 0},
    }


def _oa(analysis=None):
    return {"status": PASS, "analysis": analysis or [], "unanalyzed": []}


def _env(cd=None, oa=None, rc="PASS", od="PASS", fs="PASS", oa_st="PASS", cd_st="PASS", ofm=None):
    cdn = cd if cd is not None else _cd()
    oan = oa if oa is not None else _oa()
    cdn = {**cdn, "status": cd_st}
    oan = {**oan, "status": oa_st}
    if ofm is None:
        # object_frame_map (02) autoritaire : couvre EXACTEMENT les couples de 04 (canonized ∪ uncanon).
        # 05 recoupe desormais l'univers de 04 contre 02 (CSB-PROV-P1-004). Construction robuste
        # (entrees malformees ignorees ici -> ces cas sont bloques par 05 AVANT le contrôle couverture).
        _pairs = {}
        for c in list(cdn.get("canons_selected") or []) + list(cdn.get("uncanonized") or []):
            if isinstance(c, dict) and isinstance(c.get("object_key"), str) and isinstance(c.get("frame"), str):
                _pairs.setdefault(c["object_key"], set()).add(c["frame"])
        ofm = [{"object_key": k, "frames": sorted(v)} for k, v in sorted(_pairs.items())]
    return {
        "runtime_check": {"status": rc},
        "object_discovery": {"status": od},
        "frame_selection": {"status": fs, "object_frame_map": ofm},
        "operants_operes": oan,
        "canon_determination": cdn,
    }


def test_output_schema_exact_pass_et_blocked():
    assert tuple(run_coherence_engine(_env()).keys()) == OUTPUT_KEYS
    assert tuple(run_coherence_engine(_env(rc="FAIL")).keys()) == OUTPUT_KEYS
    assert run_coherence_engine(_env())["order_key"] == ORDER_KEY


def test_formule_canonique_verrouillee():
    v = run_coherence_engine(_env())
    assert v["coherence"]["formula"] == CANONICAL_FORMULA == "S = (beta * delta_phi) / (1 + T + sigma)"


def test_blocked_fail_closed_00_a_04():
    for kw, comp in (("rc", "00_RUNTIME_CHECK"), ("od", "01_OBJECT_DISCOVERY"),
                     ("fs", "02_ANALYSIS_FRAME_SELECTION"), ("oa_st", "03_OPERANTS_OPERES_ANALYSIS"),
                     ("cd_st", "04_CANON_DETERMINATION")):
        v = run_coherence_engine(_env(**{kw: "BLOCKED"}))
        assert v["status"] == BLOCKED and v["blocked_by"] == comp
        assert v["coherence"] is None and v["resource"] is None


def test_blocked_si_referentiel_non_gele():
    # fingerprint absent -> 04 non gelé -> fail-closed.
    cd = _cd(fingerprint="")
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == "04_CANON_DETERMINATION"


def test_delta_phi_resolution_totale():
    # 1 paire canonisée ET pourvue d'opérants -> ΔΦ = 1.0, S = beta/(1+0+0) = 1.0
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["CANON_STRUCTURE"]}])
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP_DESCRIBE"], "operes": ["k1"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    c = v["coherence"]
    assert c["delta_phi"] == 1.0 and c["tension"] == 0.0 and c["sigma"] == 0.0
    assert c["S"] == round((BETA_V1 * 1.0) / 1.0, 6) == 1.0
    assert c["resolved_pairs"] == 1 and c["total_pairs"] == 1
    assert v["resource"]["authorize_llm"] is True


def test_delta_phi_partiel_et_veto_ressource():
    # 2 paires : 1 canonisée sans opérant, 1 non canonisée -> resolved=0 -> ΔΦ=0 -> veto.
    cd = _cd(
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["CANON_STRUCTURE"]}],
        uncanonized=[{"object_key": "k2", "frame": "TEXT"}],
    )
    oa = _oa(analysis=[])  # aucun opérant
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    c = v["coherence"]
    assert c["total_pairs"] == 2 and c["resolved_pairs"] == 0
    assert c["delta_phi"] == 0.0
    assert v["resource"]["authorize_llm"] is False  # ΔΦ < 0.5 -> 07 INTERDIT


def test_seuil_veto_exact():
    # ΔΦ exactement 0.5 -> autorisé (>=).
    cd = _cd(
        canons_selected=[
            {"object_key": "k1", "frame": "CODE", "canons": ["C1"]},
            {"object_key": "k2", "frame": "CODE", "canons": ["C1"]},
        ],
    )
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP_DESCRIBE"], "operes": ["k1"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["coherence"]["delta_phi"] == 0.5
    assert v["resource"]["authorize_llm"] is True
    assert DELTA_PHI_MIN == 0.5


def test_tension_compte_les_conflits():
    cd = _cd(
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["A", "B"]}],
        conflicts=[{"object_key": "k1", "frame": "CODE", "priority": 5, "canons": ["A", "B"]}],
    )
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP_DESCRIBE"], "operes": ["k1"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    # total_pairs=1, conflicts=1 -> T=1.0 ; ΔΦ=1.0 ; S=1/(1+1+0)=0.5
    assert v["coherence"]["tension"] == 1.0
    assert v["coherence"]["S"] == 0.5


def test_sigma_dispersion_entre_objets():
    # k1 a 2 canons, k2 a 0 canon distinct dans canons_selected (non listé) -> mais σ sur objets listés
    cd = _cd(canons_selected=[
        {"object_key": "k1", "frame": "CODE", "canons": ["A", "B"]},
        {"object_key": "k2", "frame": "CODE", "canons": ["A"]},
    ])
    oa = _oa(analysis=[
        {"object_key": "k1", "frame": "CODE", "operants": ["OP_X"], "operes": ["k1"]},
        {"object_key": "k2", "frame": "CODE", "operants": ["OP_X"], "operes": ["k2"]},
    ])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    # counts = [2,1] -> mean 1.5, pstdev 0.5 -> CV = 0.333333
    assert v["coherence"]["sigma"] == round(0.5 / 1.5, 6)


def test_pipeline_vide_pass_degenere():
    v = run_coherence_engine(_env())
    assert v["status"] == PASS
    assert v["coherence"]["delta_phi"] == 1.0 and v["coherence"]["total_pairs"] == 0
    assert v["coherence"]["S"] == 1.0


def test_deterministe():
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["A"]}])
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP_X"], "operes": ["k1"]}])
    e = _env(cd=cd, oa=oa)
    assert run_coherence_engine(e) == run_coherence_engine(e)


def test_immutabilite_envelope():
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["A"]}])
    e = _env(cd=cd)
    snap = copy.deepcopy(e)
    run_coherence_engine(e)
    assert e == snap


def test_typeerror_envelope_non_dict():
    with pytest.raises(TypeError):
        run_coherence_engine(None)


def test_gouvernance_contrat_complet():
    for k in GOVERNANCE_REQUIRED_KEYS:
        assert k in GOVERNANCE and GOVERNANCE[k], f"champ gouvernance manquant/vide: {k}"
    assert isinstance(GOVERNANCE["GUARD_IDS"], list) and GOVERNANCE["GUARD_IDS"]
    assert GOVERNANCE["OBJECT_ID"] == "ZORAN-V2-COMPONENT-05-COHERENCE-ENGINE"


def test_provenance_decl_conforme():
    assert PROVENANCE_DECL["CANONICAL_SPEC"] == "SPEC_ENGINE_05_COHERENCE_ENGINE"
    assert PROVENANCE_DECL["BEHAVIOR_FLAGS"]["requests_llm_prechoices"] is False
    assert COMPONENT_ID == "05_COHERENCE_ENGINE" and VERSION == "1.0.0"


# --- RÉGRESSIONS audit ChatGPT (via MCP) 2026-07-14 ---

def test_object_key_liste_fail_closed_sans_crash():
    # ChatGPT #5 : object_key=liste -> TypeError unhashable. Doit être fail-closed, pas un crash.
    from zoran_v2.coherence_engine import MALFORMED
    cd = _cd(canons_selected=[{"object_key": ["x"], "frame": "CODE", "canons": ["A"]}])
    v = run_coherence_engine(_env(cd=cd))  # ne doit PAS lever TypeError
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED


def test_univers_vide_n_autorise_pas_le_llm():
    # ChatGPT #1 : univers vide -> S=1.0 mais NE DOIT PAS autoriser le LLM « à vide ».
    v = run_coherence_engine(_env())
    assert v["status"] == PASS and v["coherence"]["total_pairs"] == 0
    assert v["coherence"]["delta_phi"] == 1.0
    assert v["resource"]["authorize_llm"] is False


def test_fingerprint_non_str_bloque():
    # ChatGPT #3 : fingerprint non vérifié en type. Non-str -> fail-closed.
    cd = _cd(fingerprint=123)
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == "04_CANON_DETERMINATION"


def test_fingerprint_recalcule_et_compare():
    # Audit total P0 : 05 doit RECALCULER le sha256 des canons et comparer, pas juste vérifier
    # qu'une chaîne existe. Fingerprint valide en type mais ne correspondant pas -> BLOCKED.
    from zoran_v2.coherence_engine import FINGERPRINT_MISMATCH
    cd = _cd(referential_canons=[{"id": "C", "priority": 10,
                                  "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}],
             fingerprint="0000000000000000000000000000000000000000000000000000000000000000")
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == FINGERPRINT_MISMATCH


def test_fingerprint_valide_correspond_passe():
    # Fingerprint recalculé cohérent avec les canons -> PASS (pas de faux blocage).
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    cd = _cd(canons_selected=[{"object_key": "k", "frame": "CODE", "canons": ["C"]}],
             referential_canons=canons)  # fingerprint recalculé automatiquement
    oa = _oa(analysis=[{"object_key": "k", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["status"] == PASS and v["resource"]["authorize_llm"] is True


def test_S_kind_structural_v1_declare():
    # Audit total P2 : l'échelle S∈[0,1] doit être nommée pour ne pas la confondre avec S>=6.
    v = run_coherence_engine(_env())
    assert v["coherence"]["S_kind"] == "S_structural_v1"
    assert v["coherence"]["S_range"] == [0.0, 1.0]


def test_reason_univers_vide_correcte():
    # Audit total P2 : motif de veto correct pour univers vide (pas "delta_phi<seuil").
    v = run_coherence_engine(_env())
    assert v["resource"]["authorize_llm"] is False
    assert "univers vide" in v["resource"]["reason"]


def test_sigma_inclut_objets_zero_canon():
    # ChatGPT #7-8 : σ doit inclure les objets à 0 canon (dispersion non sous-estimée).
    cd = _cd(
        canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["A"]}],
        uncanonized=[{"object_key": "k2", "frame": "TEXT"}],
    )
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    # counts = [1, 0] (k1=1 canon, k2=0) -> mean .5, pstdev .5 -> CV = 1.0 (avant fix : 0.0)
    assert v["coherence"]["sigma"] == 1.0


# --- RÉGRESSIONS audit ChatGPT global coherence 2026-07-15 ---

def test_referentiel_04_malforme_fail_closed_sans_crash():
    # P2 : 05 recalcule le fingerprint via 04 (_fingerprint lit c["id"]). Un référentiel GELÉ
    # malformé (record non-dict / id absent-vide-non str) ferait lever KeyError/TypeError.
    # DOIT être BLOCKED(FINGERPRINT_MISMATCH), JAMAIS un crash.
    from zoran_v2.coherence_engine import FINGERPRINT_MISMATCH
    for bad in ([[]], [{}], ["x"], [{"id": 123}], [{"id": ""}], [{"priority": 1}]):
        cd = _cd(fingerprint="FP_ARBITRAIRE", referential_canons=bad)  # jamais atteint : bloqué avant compare
        v = run_coherence_engine(_env(cd=cd))  # ne doit PAS lever
        assert v["status"] == BLOCKED and v["blocked_by"] == FINGERPRINT_MISMATCH, bad


def test_element_non_dict_dans_listes_bloque_pas_ignore():
    # P2 : un élément non-dict dans canons_selected/uncanonized/analysis doit BLOQUER (fail-closed),
    # pas être silencieusement écarté (sinon PASS trompeur).
    from zoran_v2.coherence_engine import MALFORMED
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    for field in ("canons_selected", "uncanonized"):
        cd = _cd(referential_canons=canons,
                 **{field: [{"object_key": "k", "frame": "CODE"}, "GARBAGE_NON_DICT"]})
        v = run_coherence_engine(_env(cd=cd))
        assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED, field
    # analysis (via 03)
    cd = _cd(referential_canons=canons,
             canons_selected=[{"object_key": "k", "frame": "CODE", "canons": ["C"]}])
    oa = _oa(analysis=[{"object_key": "k", "frame": "CODE", "operants": ["O"]}, ["pas", "un", "dict"]])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED


def test_conteneur_non_liste_bloque_sans_crash():
    # Défense en profondeur : un conteneur non-liste (ex. dict) ne doit pas faire itérer sur un scalaire.
    from zoran_v2.coherence_engine import MALFORMED
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    cd = _cd(referential_canons=canons, canons_selected={"object_key": "k", "frame": "CODE"})
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED


# --- RÉGRESSION audit ChatGPT GC-D1-002 2026-07-15 : conteneur falsy non-liste ---

def test_conteneur_falsy_non_liste_bloque_pas_normalise():
    # GC-D1-002 : {} / 0 / '' / () sont FALSY -> `or []` les masquait en [] (PASS trompeur).
    # Ils doivent désormais être BLOQUÉS (conteneur non-liste malformé). Injection APRÈS _cd/_oa
    # pour contourner le `or []` des helpers de test.
    from zoran_v2.coherence_engine import MALFORMED
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    base = _cd(referential_canons=canons)
    for bad in ({}, 0, "", ()):
        for field in ("canons_selected", "uncanonized", "conflicts"):
            cd = {**base, field: bad}
            v = run_coherence_engine(_env(cd=cd))
            assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED, (field, bad)
        # analysis vit dans l'enveloppe 03 : injection directe
        e = _env(cd=base)
        e["operants_operes"] = {**e["operants_operes"], "analysis": bad}
        v = run_coherence_engine(e)
        assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED, ("analysis", bad)


def test_conteneur_none_ou_absent_reste_legitime():
    # None / clé absente = liste vide LÉGITIME (ne pas sur-bloquer) -> PASS dégénéré.
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    base = _cd(referential_canons=canons)
    cd = {**base, "canons_selected": None, "uncanonized": None, "conflicts": None}
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == PASS


def test_conflicts_element_non_dict_bloque():
    # GC-5FD-002 : un élément non-dict de conflicts doit BLOQUER (fail-closed), pas passer via len().
    from zoran_v2.coherence_engine import MALFORMED
    canons = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]
    base = _cd(referential_canons=canons,
               canons_selected=[{"object_key": "k", "frame": "CODE", "canons": ["C"]}])
    cd = {**base, "conflicts": [{"object_key": "k", "frame": "CODE"}, "GARBAGE_NON_DICT"]}
    oa = _oa(analysis=[{"object_key": "k", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["status"] == BLOCKED and v["blocked_by"] == MALFORMED


# --- RÉGRESSION Codex Session B CSB-PROV-P1-004 : couverture 04 vs univers autoritaire 02 ---

_CANONS = [{"id": "C", "priority": 10, "applies_to_frames": ["CODE"], "applies_to_kinds": ["code"]}]


def test_04_omet_une_paire_de_02_bloque():
    from zoran_v2.coherence_engine import CD04
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             referential_canons=_CANONS)
    # 02 contient (k1,CODE) ET (k2,TEXT) ; 04 (declare PASS) OMET (k2,TEXT) -> couverture trouee.
    ofm = [{"object_key": "k1", "frames": ["CODE"]}, {"object_key": "k2", "frames": ["TEXT"]}]
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa, ofm=ofm))
    assert v["status"] == BLOCKED and v["blocked_by"] == CD04


def test_04_invente_une_paire_absente_de_02_bloque():
    from zoran_v2.coherence_engine import CD04
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]},
                              {"object_key": "kX", "frame": "ZZZ", "canons": ["C"]}],
             referential_canons=_CANONS)
    ofm = [{"object_key": "k1", "frames": ["CODE"]}]  # (kX,ZZZ) inventee par 04, absente de 02
    v = run_coherence_engine(_env(cd=cd, ofm=ofm))
    assert v["status"] == BLOCKED and v["blocked_by"] == CD04


def test_02_object_frame_map_malforme_bloque():
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             referential_canons=_CANONS)
    for bad in ([{"object_key": [], "frames": ["CODE"]}],
                [{"object_key": "k1", "frames": "CODE"}], "x", [42], {}):
        v = run_coherence_engine(_env(cd=cd, ofm=bad))
        assert v["status"] == BLOCKED and v["blocked_by"] == "02_ANALYSIS_FRAME_SELECTION", bad


def test_04_couvre_exactement_02_passe():
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             referential_canons=_CANONS)
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))  # ofm auto = exactement (k1,CODE)
    assert v["status"] == PASS and v["resource"]["authorize_llm"] is True


def test_04_meme_paire_canonisee_ET_uncanonized_bloque():
    from zoran_v2.coherence_engine import CD04
    # contradiction interne 04 : (k1,CODE) a la fois canonisee ET non-canonisee -> BLOCKED (le set
    # masquait la contradiction ; delta_phi=1.0/authorize_llm=True devenaient possibles a tort).
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             uncanonized=[{"object_key": "k1", "frame": "CODE"}],
             referential_canons=_CANONS)
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["O"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["status"] == BLOCKED and v["blocked_by"] == CD04


def test_04_doublon_dans_canons_selected_bloque():
    from zoran_v2.coherence_engine import CD04
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]},
                              {"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             referential_canons=_CANONS)
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == CD04


def test_04_doublon_dans_uncanonized_bloque():
    from zoran_v2.coherence_engine import CD04
    cd = _cd(uncanonized=[{"object_key": "k2", "frame": "TEXT"},
                          {"object_key": "k2", "frame": "TEXT"}],
             referential_canons=_CANONS)
    v = run_coherence_engine(_env(cd=cd))
    assert v["status"] == BLOCKED and v["blocked_by"] == CD04


# --- RÉGRESSION ChatGPT GC-05-P1-005 : validation stricte du champ `canons` de 04 ---

def test_05_canons_champ_malforme_bloque():
    from zoran_v2.coherence_engine import CD04
    # canons doit etre une liste NON VIDE de str UNIQUES non vides ; sinon la paire serait comptee
    # canonisee/resolue SANS canon valide -> faux delta_phi=1.0 / authorize_llm (normalisation `or []`).
    for bad in ({}, "", [], [12, None], ["C", "C"], ["C", ""], "C"):
        cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": bad}],
                 referential_canons=_CANONS)
        oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP"]}])
        v = run_coherence_engine(_env(cd=cd, oa=oa))
        assert v["status"] == BLOCKED and v["blocked_by"] == CD04, bad


def test_05_canons_valide_passe():
    cd = _cd(canons_selected=[{"object_key": "k1", "frame": "CODE", "canons": ["C"]}],
             referential_canons=_CANONS)
    oa = _oa(analysis=[{"object_key": "k1", "frame": "CODE", "operants": ["OP"]}])
    v = run_coherence_engine(_env(cd=cd, oa=oa))
    assert v["status"] == PASS and v["resource"]["authorize_llm"] is True
