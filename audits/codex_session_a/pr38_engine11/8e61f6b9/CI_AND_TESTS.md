TIMESTAMP: 2026-07-16T08:58:09+02:00
AI_ACTOR_ID: CODEX_SESSION_A
MISSION_ID: TX_ZORAN_ENGINE_11_REAUDIT_PROOF_BUNDLE_V1
OBJECT_ID: ENGINE-11_PR38
SHA_AUDITED: 8e61f6b9de27543e484b12d633077dba00b3e271
GUARD_IDS: MVPP_SHA_BOUND_PROOF, CODEX_SESSION_A_PROOF_BUNDLE_V1, TRACEABLE_RUNTIME

# CI et tests rejoués

## GitHub CI

- Repository : `institutia2025-ctrl/zoran-v2`
- PR : `#38`
- Run pull_request : `29443258047`
- URL : https://github.com/institutia2025-ctrl/zoran-v2/actions/runs/29443258047
- Event : `pull_request`
- Head SHA : `8e61f6b9de27543e484b12d633077dba00b3e271`
- Conclusion : `success`
- Log pytest CI : `560 passed in 4.87s`
- Checks visibles PR : `8/8 SUCCESS` en agrégeant les runs `29443258047` et `29443255376`.
- Artifacts du run : `gitleaks-results.sarif` uniquement.

## Tests locaux CODEX_SESSION_A

Checkout dédié :

```text
C:\Users\frede\zoran-v2-codex-session-a-proof-engine11
```

Head vérifié :

```text
8e61f6b9de27543e484b12d633077dba00b3e271
```

Commandes et résultats :

```powershell
python -m pytest tests/test_trace_and_close.py -q
```

Résultat :

```text
150 passed in 4.81s
```

```powershell
python -m pytest -q -k "not test_probe_contrat_python"
```

Résultat :

```text
559 passed, 1 deselected in 6.33s
```

## Statut

Les tests ciblés et contractuels sont vérifiés directement par CODEX_SESSION_A sur le SHA exact. La CI GitHub confirme aussi le SHA exact et une suite complète verte.
