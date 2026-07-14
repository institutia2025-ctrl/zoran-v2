"""Gate anti-résurrection — GARDE DE CI (jamais importé par le runtime 00→11).

Deux barrières déterministes, sans LLM/réseau, **et SANS exécuter le code audité** :
- provenance : lecture STATIQUE (AST) de PROVENANCE_DECL de chaque module gouverné —
  le gate n'importe JAMAIS les modules (pas d'effet de bord d'import). Sinon PROVENANCE_BLOCKED.
- behavior : aucun comportement historique interdit ne réapparaît, détecté par
  ANALYSE AST (sémantique) — jamais sur des chaînes/docstrings/commentaires.

Ne décide d'aucun raisonnement, ne sélectionne aucun objet, ne remplace aucun
composant : refuse/accepte au moment de la CI.
"""
import ast
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


def governed_module_files():
    """AUTO-DÉCOUVERTE : tout zoran_v2/*.py hors __init__ et modules privés (_*)."""
    return [p for p in sorted(PKG_DIR.glob("*.py"))
            if p.name != "__init__.py" and not p.name.startswith("_")]


# --- Lecture STATIQUE de PROVENANCE_DECL par AST (aucune exécution/import) ---
def read_provenance_decl_from_source(source_text):
    """Extrait le littéral PROVENANCE_DECL par AST. None si absent ou non-littéral.

    N'exécute JAMAIS le code : `ast.literal_eval` n'évalue que des littéraux.
    """
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "PROVENANCE_DECL":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError, TypeError):
                        return None
    return None


def read_provenance_decl(path):
    return read_provenance_decl_from_source(path.read_text(encoding="utf-8"))


# --- Contrôles PURS ---
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
    if isinstance(t, ast.Name):
        return t.id
    if isinstance(t, ast.Attribute):
        return t.attr
    return None


def scan_ast(source_text, forbidden):
    """Détection SÉMANTIQUE : parse le code, ignore chaînes/docstrings/commentaires."""
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
                    nm = _target_name(t)
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
    for p in governed_module_files() + [PKG_DIR / "__init__.py"]:
        if p.exists():
            hits += [(p.name, *h) for h in scan_ast(p.read_text(encoding="utf-8"), _forbidden())]
    return hits


# --- Barrière PROVENANCE (auto-découverte + lecture AST) ---
def test_canonical_sources_non_vide():
    assert _canonical_ids()


def test_discovery_couvre_les_composants_reels():
    names = {p.stem for p in governed_module_files()}
    assert "runtime_check" in names and "object_discovery" in names
    assert "_cycle_probe" not in names and "__init__" not in names


def test_provenance_decl_complete_pour_tout_module_gouverne():
    canon = _canonical_ids()
    for p in governed_module_files():
        decl = read_provenance_decl(p)   # LECTURE AST, sans import
        errs = check_provenance(decl, canon)
        assert not errs, f"PROVENANCE_BLOCKED {p.name}: {errs}"


# --- Barrière BEHAVIOR (AST) ---
def test_aucun_flag_interdit_active():
    forbidden = _forbidden()
    for p in governed_module_files():
        actives = active_forbidden_flags(read_provenance_decl(p), forbidden)
        assert not actives, f"LEGACY {p.name}: comportements interdits actifs {actives}"


def test_aucun_comportement_interdit_dans_le_source():
    hits = _scan_package()
    assert not hits, f"LEGACY (AST) présents dans zoran_v2/: {hits}"


# --- MÉTA-tests : falsifiabilité + PREUVE de non-exécution ---
def test_meta_provenance_lue_par_ast_SANS_execution():
    # Un module avec effet de bord à l'import ne doit PAS être exécuté par le gate.
    src = ('raise RuntimeError("import side effect")\n'
           'PROVENANCE_DECL = {"SOURCE_TYPE": "new", "CANONICAL_SPEC": "SPEC_X"}\n')
    d = read_provenance_decl_from_source(src)
    assert d is not None and d["SOURCE_TYPE"] == "new"  # lu malgré le raise -> 0 exécution


def test_meta_provenance_absente_ou_non_litterale():
    assert read_provenance_decl_from_source("x = 1") is None
    # valeur non-littérale (référence de variable) -> None (fail-closed)
    assert read_provenance_decl_from_source("V=1\nPROVENANCE_DECL = {'k': V}") is None


def test_meta_ast_bloque_assign_kwarg_dict():
    f = _forbidden()
    assert scan_ast("n_candidates = 3", f)
    assert scan_ast("resultat = generate(x, n_candidates=3)", f)
    assert scan_ast('CFG = {"n_candidates": 3}', f)


def test_meta_ast_bloque_affectation_attribut():
    f = _forbidden()
    assert scan_ast("cfg.n_candidates = 3", f)
    assert scan_ast("self.n_candidates = 3", f)


def test_meta_ast_ignore_chaines_et_commentaires():
    f = _forbidden()
    inerte = ('"""note: n_candidates=3"""\nDOC = "n_candidates=3"\nx = 1  # n_candidates=3\n')
    assert scan_ast(inerte, f) == []


def test_meta_spec_inconnue_detectee():
    bad = {k: "x" for k in PROVENANCE_REQUIRED}
    bad["CANONICAL_SPEC"] = "SPEC_INEXISTANTE"
    assert "spec_not_canonical" in check_provenance(bad, _canonical_ids())


def test_meta_flag_interdit_actif_detecte():
    f = _forbidden()
    flag = f[0]["forbidden_flag"]
    assert active_forbidden_flags({"BEHAVIOR_FLAGS": {flag: True}}, f)
