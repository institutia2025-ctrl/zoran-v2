"""Gate anti-résurrection — GARDE DE CI (jamais importé par le runtime 00→11).

Deux barrières déterministes, sans LLM/réseau :
- provenance : TOUT module gouverné de zoran_v2/ doit déclarer son origine
  canonique (auto-découverte, PAS de liste codée en dur) sinon PROVENANCE_BLOCKED ;
- behavior : aucun comportement historique interdit (flag, token OU pattern regex)
  ne réapparaît dans zoran_v2/*.py.

Ce fichier NE décide d'aucun raisonnement, NE sélectionne aucun objet, NE remplace
aucun composant : il refuse/accepte au moment de la CI.
"""
import importlib
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = REPO_ROOT / "zoran_v2"

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


def governed_module_names():
    """AUTO-DÉCOUVERTE : tout zoran_v2/*.py hors __init__ et modules privés (_*).

    Aucune liste codée en dur : un nouveau composant est couvert automatiquement.
    """
    out = []
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name == "__init__.py" or p.name.startswith("_"):
            continue
        out.append("zoran_v2." + p.stem)
    return out


# --- Fonctions de contrôle PURES (falsifiables via méta-tests) ---
def check_provenance(decl, canonical_ids):
    if not isinstance(decl, dict):
        return ["no_provenance_decl"]
    errs = [f"missing:{k}" for k in PROVENANCE_REQUIRED if k not in decl]
    if decl.get("CANONICAL_SPEC") not in canonical_ids:
        errs.append("spec_not_canonical")
    return errs


def scan_forbidden(source_text, forbidden):
    hits = []
    for entry in forbidden:
        for tok in entry.get("forbidden_tokens", []):
            if tok in source_text:
                hits.append((entry["id"], "token", tok))
        for pat in entry.get("forbidden_patterns", []):
            if re.search(pat, source_text):
                hits.append((entry["id"], "pattern", pat))
    return hits


def active_forbidden_flags(decl, forbidden):
    flags = (decl or {}).get("BEHAVIOR_FLAGS", {}) if isinstance(decl, dict) else {}
    return [e["id"] for e in forbidden
            if e.get("forbidden_flag") and flags.get(e["forbidden_flag"]) is True]


def _package_source():
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(PKG_DIR.glob("*.py")))


# --- Barrière PROVENANCE (auto-découverte) ---
def test_canonical_sources_non_vide():
    assert _canonical_ids()


def test_discovery_couvre_les_composants_reels():
    names = governed_module_names()
    assert "zoran_v2.runtime_check" in names
    assert "zoran_v2.object_discovery" in names
    assert "zoran_v2._cycle_probe" not in names   # module privé exempté
    assert "zoran_v2.__init__" not in names


def test_provenance_decl_complete_pour_tout_module_gouverne():
    canon = _canonical_ids()
    for name in governed_module_names():
        mod = importlib.import_module(name)
        decl = getattr(mod, "PROVENANCE_DECL", None)
        errs = check_provenance(decl, canon)
        assert not errs, f"PROVENANCE_BLOCKED {name}: {errs}"


# --- Barrière BEHAVIOR ---
def test_aucun_flag_interdit_active():
    forbidden = _forbidden()
    for name in governed_module_names():
        mod = importlib.import_module(name)
        actives = active_forbidden_flags(getattr(mod, "PROVENANCE_DECL", None), forbidden)
        assert not actives, f"LEGACY {name}: comportements interdits actifs {actives}"


def test_aucun_token_ni_pattern_interdit_dans_le_source():
    hits = scan_forbidden(_package_source(), _forbidden())
    assert not hits, f"LEGACY présents dans zoran_v2/: {hits}"


# --- MÉTA-tests : le gate DOIT détecter chaque violation (falsifiabilité) ---
def test_meta_scan_detecte_token_injecte():
    forbidden = _forbidden()
    tok = forbidden[0]["forbidden_tokens"][0]
    assert scan_forbidden(f"x = 42  # {tok}", forbidden)


def test_meta_scan_detecte_pattern_n_candidates():
    # Toutes les variantes d'espacement de la forme historique doivent matcher.
    forbidden = _forbidden()
    for variante in ("n_candidates=3", "n_candidates = 3", "n_candidates=  3",
                     "generate_candidates(x, n_candidates=3)"):
        assert scan_forbidden(variante, forbidden), f"non détecté: {variante!r}"


def test_meta_provenance_manquante_detectee():
    assert check_provenance(None, _canonical_ids()) == ["no_provenance_decl"]


def test_meta_spec_inconnue_detectee():
    bad = {k: "x" for k in PROVENANCE_REQUIRED}
    bad["CANONICAL_SPEC"] = "SPEC_INEXISTANTE"
    assert "spec_not_canonical" in check_provenance(bad, _canonical_ids())


def test_meta_flag_interdit_actif_detecte():
    forbidden = _forbidden()
    flag = forbidden[0]["forbidden_flag"]
    assert active_forbidden_flags({"BEHAVIOR_FLAGS": {flag: True}}, forbidden)
