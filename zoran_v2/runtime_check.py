"""00_RUNTIME_CHECK — porte 0 du pipeline de raisonnement ZORAN V2.

Vérifie que l'environnement d'exécution satisfait les préconditions DURES du
moteur AVANT toute étape 01→11. Fail-closed : toute condition non satisfaite
OU non vérifiable empêche le moteur de continuer.

Déterministe (fonction pure), sans LLM, sans réseau, sans donnée réelle,
sans mutation. Compatible Python 3.13.
"""
from __future__ import annotations

COMPONENT_ID = "00_RUNTIME_CHECK"
VERSION = "1.0.0"

# --- Contrat de gouvernance du composant (objet V2 gouverné complet) ---
GOVERNANCE = {
    "OBJECT_ID": "ZORAN-V2-COMPONENT-00-RUNTIME-CHECK",
    "META_ID": "META-ZORAN-V2-COMPONENT-00",
    "VERSION": VERSION,
    "OWNER": "FRED",
    "PROVENANCE": "MISSION ENGINE_00_RUNTIME_CHECK · spec 00 · branche mission/engine-00-runtime-check",
    "GUARD_IDS": [
        "FAIL_CLOSED",
        "DETERMINISTIC",
        "NO_LLM",
        "NO_NETWORK",
        "NO_REAL_DATA",
        "NO_MUTATION",
        "UNVERIFIED_IS_FAIL",
    ],
    "TRACEABILITY": "sortie structuree checks[]+first_failure ; SHA git ; run CI",
    "VALIDATION": "tests deterministes pytest + CI Python 3.13",
    "ROLLBACK": "git : branche non fusionnee dans seed-bootstrap ; git revert du commit",
    "DETECTION_MODIF": "SHA git + CI GitHub Actions",
    "ALERTE": "status=FAIL / first_failure ; jamais PASS silencieux (NON_VERIFIE = echec porte)",
    "ANTI_REGRESSION": "tests fail-closed + NON_VERIFIE + contrat de gouvernance verifie par test ; CI bloque le merge",
}

GOVERNANCE_REQUIRED_KEYS = (
    "OBJECT_ID", "META_ID", "VERSION", "OWNER", "PROVENANCE", "GUARD_IDS",
    "TRACEABILITY", "VALIDATION", "ROLLBACK", "DETECTION_MODIF", "ALERTE",
    "ANTI_REGRESSION",
)

# Contrat de version Python : >= 3.11 et < 3.14
PY_MIN = (3, 11)
PY_MAX_EXCL = (3, 14)
REQUIRED_MEMORY_BYTES = 512 * 1024 * 1024   # 512 MiB
REQUIRED_DISK_BYTES = 256 * 1024 * 1024     # 256 MiB
REQUIRED_IMPLEMENTATION = "cpython"

PASS = "PASS"
FAIL = "FAIL"
UNVERIFIED = "NON_VERIFIE"

FACT_KEYS = (
    "python_version_info",
    "python_implementation",
    "available_memory_bytes",
    "free_disk_bytes",
)


def _check(cid: str, name: str, observed, ok: bool, expected) -> dict:
    """Construit un check. Fait absent (observed None) => NON_VERIFIE (fail-closed)."""
    if observed is None:
        status = UNVERIFIED
    else:
        status = PASS if ok else FAIL
    return {"id": cid, "name": name, "status": status,
            "observed": observed, "expected": expected}


def run_runtime_check(facts: dict, cfg: dict | None = None) -> dict:
    """Fonction PURE : (facts, cfg) -> verdict structuré déterministe.

    Ne lève que sur mauvais usage (facts non-dict). Ne lève jamais sur un
    échec de check : l'échec est porté par la sortie structurée.
    """
    if not isinstance(facts, dict):
        raise TypeError("facts doit être un dict")
    cfg = cfg or {}
    py_min = tuple(cfg.get("py_min", PY_MIN))
    py_max_excl = tuple(cfg.get("py_max_excl", PY_MAX_EXCL))
    req_mem = int(cfg.get("required_memory_bytes", REQUIRED_MEMORY_BYTES))
    req_disk = int(cfg.get("required_disk_bytes", REQUIRED_DISK_BYTES))
    req_impl = str(cfg.get("required_implementation", REQUIRED_IMPLEMENTATION)).lower()

    pv = facts.get("python_version_info")
    pv_t = tuple(pv) if pv is not None else None
    impl_raw = facts.get("python_implementation")
    impl = impl_raw.lower() if isinstance(impl_raw, str) else None
    mem = facts.get("available_memory_bytes")
    disk = facts.get("free_disk_bytes")

    checks = [
        _check("RC00", "python_version", pv_t,
               pv_t is not None and py_min <= pv_t < py_max_excl,
               {"min": list(py_min), "max_excl": list(py_max_excl)}),
        _check("RC01", "python_implementation", impl,
               impl is not None and impl == req_impl, req_impl),
        _check("RC02", "available_memory_bytes", mem,
               isinstance(mem, int) and mem >= req_mem, {">=": req_mem}),
        _check("RC03", "free_disk_bytes", disk,
               isinstance(disk, int) and disk >= req_disk, {">=": req_disk}),
    ]
    first_failure = next((c["id"] for c in checks if c["status"] != PASS), None)
    status = PASS if first_failure is None else FAIL
    return {
        "component": COMPONENT_ID,
        "version": VERSION,
        "status": status,
        "fail_closed": True,
        "first_failure": first_failure,
        "checks": checks,
    }


def collect_facts() -> dict:
    """Partie IMPURE et fine : lit les faits runtime réels. Aucun réseau.

    Un fait indisponible reste None -> traité comme NON_VERIFIE (fail-closed).
    """
    import os
    import platform
    import shutil
    import sys

    mem = None
    try:
        names = getattr(os, "sysconf_names", {})
        if "SC_AVPHYS_PAGES" in names and "SC_PAGE_SIZE" in names:
            mem = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    except (ValueError, OSError):
        mem = None

    try:
        disk = shutil.disk_usage(os.getcwd()).free
    except OSError:
        disk = None

    return {
        "python_version_info": tuple(sys.version_info[:3]),
        "python_implementation": platform.python_implementation(),
        "available_memory_bytes": mem,
        "free_disk_bytes": disk,
    }


def main() -> dict:
    """Point d'entrée : collecte les faits réels puis applique la porte 0."""
    return run_runtime_check(collect_facts())
