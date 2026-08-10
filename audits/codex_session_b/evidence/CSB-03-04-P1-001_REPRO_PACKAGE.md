TIMESTAMP: 2026-07-15T11:54:13.2178374+02:00

# CSB-03-04-P1-001 — paquet de reproduction complet

MISSION_ID: `TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1`
AI_ACTOR_ID: `CODEX_SESSION_B`
SHA: `6d3f3898a5c7352105f07a03098e7fb22d89899f`
GUARD_IDS: `TRACEABLE_RUNTIME`, `SHA_UNIQUE_AUDIT_V1`, `NO_PRODUCT_MUTATION_V1`, `CSB_03_04_P1_001_REPRO_V1`

## Précondition

```powershell
cd C:\Users\frede\zoran-v2-codex-session-b
git rev-parse HEAD
# 6d3f3898a5c7352105f07a03098e7fb22d89899f
```

## Payload 01 exact

```python
PAYLOAD_01 = {
    "status": "PASS",
    "objects": [
        {"object_key": "k", "kind": "code"},
    ],
}
```

## Payload 02 exact

```python
PAYLOAD_02 = {
    "status": "PASS",
    "object_frame_map": [
        {"object_key": "k", "frames": ["CODE"]},
    ],
}
```

## Payload 03 malformé exact

Il affirme seulement `PASS`. Il ne contient ni `component`, ni `version`, ni `analysis`, ni `unanalyzed`, ni `order_key`.

```python
MALFORMED_PAYLOAD_03 = {
    "status": "PASS",
}
```

## Enveloppe exacte transmise à 04

```python
ENVELOPE = {
    "runtime_check": {"status": "PASS"},
    "object_discovery": PAYLOAD_01,
    "frame_selection": PAYLOAD_02,
    "operants_operes": MALFORMED_PAYLOAD_03,
}
```

Registre injecté:

```python
CANON_REGISTRY = [
    {
        "id": "CANON",
        "applies_to_frames": ["CODE"],
        "applies_to_kinds": ["code"],
        "priority": 1,
    },
]
```

## Appel Python exact

```python
from zoran_v2.canon_determination import run_canon_determination
observed = run_canon_determination(ENVELOPE, CANON_REGISTRY)
```

Exécution autonome:

```powershell
python audits/codex_session_b/evidence/repro_csb_03_04_p1_001.py
```

## Sortie fautive réellement observée

```python
{'component': '04_CANON_DETERMINATION',
 'version': '1.0.0',
 'status': 'PASS',
 'blocked_by': None,
 'canons_selected': [{'object_key': 'k', 'frame': 'CODE', 'canons': ['CANON']}],
 'canon_referential': {'fingerprint': 'f9c0d36b1680b50cf9556400693bc1dedd1ec280019cd7437a136dd6eb49733c',
                       'canons': [{'id': 'CANON',
                                   'priority': 1,
                                   'applies_to_frames': ['CODE'],
                                   'applies_to_kinds': ['code']}],
                       'priorities': {'CANON': 1}},
 'conflicts': [],
 'uncanonized': [],
 'resource_estimate': {'objects': 1,
                       'frames': 1,
                       'pairs': 1,
                       'canons_applied': 1},
 'order_key': 'object_frame_map_order_puis_canon_priority_desc_puis_id_alphabetique'}
```

Exit code du script: `0`.

## Sortie fail-closed attendue

```python
{'component': '04_CANON_DETERMINATION',
 'version': '1.0.0',
 'status': 'BLOCKED',
 'blocked_by': '03_OPERANTS_OPERES_ANALYSIS',
 'canons_selected': [],
 'canon_referential': {'fingerprint': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
                       'canons': [],
                       'priorities': {}},
 'conflicts': [],
 'uncanonized': [],
 'resource_estimate': {'objects': 0,
                       'frames': 0,
                       'pairs': 0,
                       'canons_applied': 0},
 'order_key': 'object_frame_map_order_puis_canon_priority_desc_puis_id_alphabetique'}
```

## Distinction causale obligatoire

### Payload 03 non validé

`zoran_v2/canon_determination.py:206-208` vérifie uniquement que `operants_operes` est un dictionnaire et que sa clé `status` vaut `PASS`. Aucun autre champ contractuel de 03 n'est lu ou validé.

### Payloads 01/02 consommés directement par 04

Après ce contrôle superficiel, 04 reconstruit le travail utile sans le payload de 03:

- `zoran_v2/canon_determination.py:212-215` construit `kind_by_key` directement depuis `object_discovery.objects` de 01;
- `zoran_v2/canon_determination.py:225-234` parcourt directement `frame_selection.object_frame_map` de 02, rejoint le `kind` de 01 et calcule les canons applicables;
- aucune lecture de `oa["analysis"]`, `oa["unanalyzed"]`, `oa["component"]` ou `oa["version"]` n'a lieu.

Le faux PASS 03 sert donc uniquement de jeton de passage. La sélection canonique provient directement des données 01/02.

## Test pytest minimal attendu en échec sur 6d3f389

Fichier: `audits/codex_session_b/evidence/test_csb_03_04_p1_001_regression.py`

```python
from audits.codex_session_b.evidence.repro_csb_03_04_p1_001 import (
    CANON_REGISTRY,
    ENVELOPE,
)
from zoran_v2.canon_determination import run_canon_determination


def test_04_blocks_malformed_pass_payload_from_03():
    observed = run_canon_determination(ENVELOPE, CANON_REGISTRY)

    assert observed["status"] == "BLOCKED"
    assert observed["blocked_by"] == "03_OPERANTS_OPERES_ANALYSIS"
    assert observed["canons_selected"] == []
```

Commande:

```powershell
python -m pytest -q audits/codex_session_b/evidence/test_csb_03_04_p1_001_regression.py
```

Résultat réellement observé sur `6d3f389`:

```text
FAILED audits/codex_session_b/evidence/test_csb_03_04_p1_001_regression.py::test_04_blocks_malformed_pass_payload_from_03
E AssertionError: assert 'PASS' == 'BLOCKED'
1 failed in 0.13s
```

Exit code pytest: `1`, échec attendu démontrant le finding.

## Limites

Ce paquet ne propose ni n'applique aucune correction. Il ne conclut rien sur un autre SHA.
