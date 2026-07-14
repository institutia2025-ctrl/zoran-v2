"""Gate anti-résurrection — GARDE DE CI (jamais importé par le runtime 00→11).

Deux barrières, déterministes, sans LLM/réseau :
- behavior : aucun comportement historique interdit (flag ou token) ne réapparaît ;
- provenance : chaque composant gouverné déclare son origine canonique, sinon PROVENANCE_BLOCKED.

Ce fichier NE décide d'aucun raisonnement, NE sélectionne aucun objet, NE remplace
aucun composant. Il ne fait que refuser/accepter au moment de la CI.
"""
import importlib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = REPO_ROOT / "zoran_v2"

# Composants gouvernés : modules exposant GOVERNANCE + PROVENANCE_DECL.
GOVERNED_MODULES = ["zoran_v2.runtime_check", "zoran_v2.object_discovery"]

PROVENANCE_REQUIRED = (
    "SOURCE_TYPE", "CANONICAL_SPEC", "SOURCE_SHA",
    "RETAINED_BEHAVIOR", "REJECTED_BEHAVIOR", "LEGACY_CHECK", "BEHAVIOR_FLAGS",
)


def _load_yaml(name):
    with open(REPO_ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _canonical_ids():
    return {s["id"] for s in _load_yaml("CANONICAL_SOURCES.yaml").get("sources", [])}


def _forbidden():
    return _load_yaml("FORBIDDEN_LEGACY_BEHAVIORS.yaml").get("forbidden", [])


# --- Fonctions de contrôle PURES (falsifiables via méta-tests) ---
def check_provenance(decl, canonical_ids):
    if not isinstance(decl, dict):
        return ["no_provenance_decl"]
    errs = [f"missing:{k}" for k in PROVENANCE_REQUIRED if k not in decl]
    if decl.get("CANONICAL_SPEC") not in canonical_ids:
        errs.append("spec_not_canonical")
    return errs


def scan_forbidden_tokens(source_text, forbidden):
    hits = []
    for entry in forbidden:
        for tok in entry.get("forbidden_tokens", []):
            if tok in source_text:
                hits.append((entry["id"], tok))
    return hits


def active_forbidden_flags(decl, forbidden):
    flags = (decl or {}).get("BEHAVIOR_FLAGS", {}) if isinstance(decl, dict) else {}
    return [e["id"] for e in forbidden
            if e.get("forbidden_flag") and flags.get(e["forbidden_flag"]) is True]


# --- Barrière PROVENANCE ---
def test_canonical_sources_non_vide():
    assert _canonical_ids()


def test_provenance_decl_complete_pour_chaque_composant():
    canon = _canonical_ids()
    for name in GOVERNED_MODULES:
        mod = importlib.import_module(name)
        decl = getattr(mod, "PROVENANCE_DECL", None)
        errs = check_provenance(decl, canon)
        assert not errs, f"PROVENANCE_BLOCKED {name}: {errs}"


# --- Barrière BEHAVIOR ---
def test_aucun_flag_interdit_active():
    forbidden = _forbidden()
    for name in GOVERNED_MODULES:
        mod = importlib.import_module(name)
        actives = active_forbidden_flags(getattr(mod, "PROVENANCE_DECL", None), forbidden)
        assert not actives, f"LEGACY {name}: comportements interdits actifs {actives}"


def test_aucun_token_interdit_dans_le_source():
    source = "\n".join(p.read_text(encoding="utf-8") for p in sorted(PKG_DIR.glob("*.py")))
    hits = scan_forbidden_tokens(source, _forbidden())
    assert not hits, f"LEGACY tokens présents dans zoran_v2/: {hits}"


# --- MÉTA-tests : le gate DOIT détecter une violation (falsifiabilité) ---
def test_meta_scan_detecte_token_injecte():
    forbidden = _forbidden()
    tok = forbidden[0]["forbidden_tokens"][0]
    assert scan_forbidden_tokens(f"x = 42  # {tok}", forbidden)


def test_meta_provenance_manquante_detectee():
    assert check_provenance(None, _canonical_ids()) == ["no_provenance_decl"]


def test_meta_spec_inconnue_detectee():
    bad = {k: "x" for k in PROVENANCE_REQUIRED}
    bad["CANONICAL_SPEC"] = "SPEC_INEXISTANTE"
    assert "spec_not_canonical" in check_provenance(bad, _canonical_ids())


def test_meta_flag_interdit_actif_detecte():
    forbidden = _forbidden()
    flag = forbidden[0]["forbidden_flag"]
    fake = {"BEHAVIOR_FLAGS": {flag: True}}
    assert active_forbidden_flags(fake, forbidden)
