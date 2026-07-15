TIMESTAMP: 2026-07-15T11:27:49.5647934+02:00

# Preuves reproductibles — interface 03→04

MISSION_ID: `TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1`
GUARD_IDS: `TRACEABLE_RUNTIME`, `SHA_UNIQUE_AUDIT_V1`, `NO_PRODUCT_MUTATION_V1`

Environnement: checkout dédié, branche `audit/codex-session-b-00-07-v1`, HEAD `6d3f3898a5c7352105f07a03098e7fb22d89899f`.

## Tests existants

Commande: `python -m pytest -q tests/test_operants_operes_analysis.py tests/test_canon_determination.py`
Résultat: `51 passed in 0.46s`, exit `0`.

## CI exacte

Commande: `gh api repos/institutia2025-ctrl/zoran-v2/commits/6d3f3898a5c7352105f07a03098e7fb22d89899f/check-runs`
Résultat: run `29402762441`, job `87310995624`, check `test`, `completed/success`, head SHA exact.

## Sorties des sondes adversariales

```text
missing_03_payload PASS [{'object_key': 'k', 'frame': 'CODE', 'canons': ['CANON']}]
contradictory_03 PASS [{'object_key': 'k', 'frame': 'CODE', 'canons': ['CANON']}]
wrong_component PASS [{'object_key': 'k', 'frame': 'CODE', 'canons': ['CANON']}]
03_unhashable_operant_id CRASH TypeError cannot use 'list' as a set element (unhashable type: 'list')
03_unhashable_object_key CRASH TypeError cannot use 'list' as a dict key (unhashable type: 'list')
04_unhashable_object_key CRASH TypeError cannot use 'list' as a dict key (unhashable type: 'list')
```

Les sondes importent directement les fonctions publiques des moteurs et n'écrivent aucun fichier produit.
