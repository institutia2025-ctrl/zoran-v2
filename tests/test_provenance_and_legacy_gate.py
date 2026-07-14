"""Gate anti-résurrection — GARDE DE CI (jamais importé par le runtime 00→11).

Deux barrières déterministes, sans LLM/réseau :
- provenance : TOUT module gouverné de zoran_v2/ doit déclarer son origine canonique
  (AUTO-DÉCOUVERTE, pas de liste codée en dur) sinon PROVENANCE_BLOCKED ;
- behavior : aucun comportement historique interdit ne réapparaît, détecté par
  ANALYSE AST (sémantique) — jamais sur des chaînes, docstrings ou commentaires.

Ne décide d'aucun raisonnement, ne sélectionne aucun objet, ne remplace aucun
composant : refuse/accepte au moment de la CI.
"""
import ast
import importlib
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
    """AUTO-DÉCOUVERTE : tout zoran_v2/*.py hors __init__ et modules privés (_*)."""
    return ["zoran_v2." + p.stem for p in sorted(PKG_DIR.glob("*.py"))
            if p.name != "__init__.py" and not p.name.startswith("_")]


# --- Contrôles PURS (falsifiables via méta-tests) ---
def check_provenance(decl, canonical_ids):
    if not isinstance(decl, dict):
        return ["no_provenance_decl"]
    errs = [f"missing:{k}" for k in PROVENANCE_REQUIRED if k not in decl]
    if decl.get("CANONICAL_SPEC") not in canonical_ids:
        errs.append("spec_not_canonical")
    return errs


def active_forbidden_flags(decl, forbidden):
    flags = (decl or {}).get("BEHAVIOR_FLAGS", {}) if isinstance(decl, dict) else {}
    return [e["id"] for e in forbidden
            if e.get("forbidden_flag") and flags.get(e["forbidden_flag"]) is True]


def _int_const(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, int)
            and not isinstance(node.value, bool))


def _target_name(t):
    """Nom d'une cible d'affectation : `x` (Name) ou `obj.x` / `self.x` (Attribute)."""
    if isinstance(t, ast.Name):
        return t.id
    if isinstance(t, ast.Attribute):
        return t.attr
    return None


def scan_ast(source_text, forbidden):
    """Détection SÉMANTIQUE : parse le code, ignore chaînes/docstrings/commentaires.

    Bloque : identifiant interdit utilisé comme code ; `name = N` ; `f(name=N)` ;
    `{"name": N}`. N'inspecte jamais le contenu des chaînes.
    """
    idents = {i for e in forbidden for i in e.get("forbidden_identifiers", [])}
    params = {(p["name"], p["value"]) for e in forbidden
              for p in e.get("forbidden_int_params", [])}
    tree = ast.parse(source_text)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in idents:
            hits.append(("identifier", node.id))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in idents:
            hits.append(("def", node.name))
        elif isinstance(node, ast.Assign):
            if _int_const(node.value):
                for t in node.targets:
                    nm = _target_name(t)   # Name OU Attribute (cfg.x / self.x)
                    if nm and (nm, node.value.value) in params:
                        hits.append(("assign", nm, node.value.value))
        elif isinstance(node, ast.AnnAssign):
            nm = _target_name(node.target)
            if (nm and node.value is not None and _int_const(node.value)
                    and (nm, node.value.value) in params):
                hits.append(("annassign", nm))
        elif isinstance(node, ast.keyword):
            if node.arg and _int_const(node.value) and (node.arg, node.value.value) in params:
                hits.append(("kwarg", node.arg))
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                        and _int_const(v) and (k.value, v.value) in params):
                    hits.append(("dict_key", k.value))
    return hits


def _scan_package():
    hits = []
    for p in sorted(PKG_DIR.glob("*.py")):
        hits += [(p.name, *h) for h in scan_ast(p.read_text(encoding="utf-8"), _forbidden())]
    return hits


# --- Barrière PROVENANCE (auto-découverte) ---
def test_canonical_sources_non_vide():
    assert _canonical_ids()


def test_discovery_couvre_les_composants_reels():
    names = governed_module_names()
    assert "zoran_v2.runtime_check" in names and "zoran_v2.object_discovery" in names
    assert "zoran_v2._cycle_probe" not in names and "zoran_v2.__init__" not in names


def test_provenance_decl_complete_pour_tout_module_gouverne():
    canon = _canonical_ids()
    for name in governed_module_names():
        mod = importlib.import_module(name)
        errs = check_provenance(getattr(mod, "PROVENANCE_DECL", None), canon)
        assert not errs, f"PROVENANCE_BLOCKED {name}: {errs}"


# --- Barrière BEHAVIOR (AST) ---
def test_aucun_flag_interdit_active():
    forbidden = _forbidden()
    for name in governed_module_names():
        mod = importlib.import_module(name)
        actives = active_forbidden_flags(getattr(mod, "PROVENANCE_DECL", None), forbidden)
        assert not actives, f"LEGACY {name}: comportements interdits actifs {actives}"


def test_aucun_comportement_interdit_dans_le_source():
    hits = _scan_package()
    assert not hits, f"LEGACY (AST) présents dans zoran_v2/: {hits}"


# --- MÉTA-tests : détecte le vrai code, IGNORE strings/commentaires (anti-faux-positif) ---
def test_meta_ast_bloque_assign_kwarg_dict():
    f = _forbidden()
    assert scan_ast("n_candidates = 3", f)
    assert scan_ast("n_candidates=3", f)
    assert scan_ast("resultat = generate(x, n_candidates=3)", f)
    assert scan_ast('CFG = {"n_candidates": 3}', f)


def test_meta_ast_bloque_affectation_attribut():
    # Contournement Codex : cfg.n_candidates = 3 / self.n_candidates = 3
    f = _forbidden()
    assert scan_ast("cfg.n_candidates = 3", f)
    assert scan_ast("self.n_candidates = 3", f)
    assert scan_ast("obj.deep.n_prechoices = 3", f)


def test_meta_ast_ignore_chaines_et_commentaires():
    f = _forbidden()
    inerte = (
        '"""historical note: n_candidates=3 was forbidden"""\n'
        'DOC = "n_candidates=3"\n'
        'x = 1  # n_candidates=3 in a comment only\n'
    )
    assert scan_ast(inerte, f) == []


def test_meta_ast_bloque_identifiant_mais_pas_en_chaine():
    f = _forbidden()
    assert scan_ast("def generate_three_prechoices():\n    return 1", f)
    assert scan_ast('s = "generate_three_prechoices"', f) == []


def test_meta_provenance_manquante_detectee():
    assert check_provenance(None, _canonical_ids()) == ["no_provenance_decl"]


def test_meta_spec_inconnue_detectee():
    bad = {k: "x" for k in PROVENANCE_REQUIRED}
    bad["CANONICAL_SPEC"] = "SPEC_INEXISTANTE"
    assert "spec_not_canonical" in check_provenance(bad, _canonical_ids())


def test_meta_flag_interdit_actif_detecte():
    f = _forbidden()
    flag = f[0]["forbidden_flag"]
    assert active_forbidden_flags({"BEHAVIOR_FLAGS": {flag: True}}, f)
