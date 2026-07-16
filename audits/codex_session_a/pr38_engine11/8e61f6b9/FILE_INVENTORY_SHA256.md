TIMESTAMP: 2026-07-16T08:58:09+02:00
AI_ACTOR_ID: CODEX_SESSION_A
MISSION_ID: TX_ZORAN_ENGINE_11_REAUDIT_PROOF_BUNDLE_V1
OBJECT_ID: ENGINE-11_PR38
SHA_AUDITED: 8e61f6b9de27543e484b12d633077dba00b3e271
GUARD_IDS: MVPP_SHA_BOUND_PROOF, CODEX_SESSION_A_PROOF_BUNDLE_V1

# Inventaire SHA-256 — blobs Git canoniques

Commande de référence :

```powershell
python -c "import subprocess,hashlib,json; repo=r'C:\\Users\\frede\\zoran-v2-codex-session-a-proof-engine11'; sha='8e61f6b9de27543e484b12d633077dba00b3e271'; files=['zoran_v2/trace_and_close.py','tests/test_trace_and_close.py','EXECUTION_RESULT_SCHEMA.yaml','HUMAN_DECISION_SCHEMA.yaml']; out=[]; [out.append({'path':f,'bytes':len((d:=subprocess.check_output(['git','-C',repo,'show',sha+':'+f]))),'sha256':hashlib.sha256(d).hexdigest().upper()}) for f in files]; print(json.dumps(out, indent=2))"
```

| Fichier | Octets blob Git | SHA-256 blob Git |
|---|---:|---|
| `zoran_v2/trace_and_close.py` | 29102 | `D06D1F1ECB6CD4F86C328325447A37F3D6E4A3F764610714ACBBD6B08B947052` |
| `tests/test_trace_and_close.py` | 34831 | `6DF36FD189F55590ECDF19F41DED3D991F53148F620F775814094991B3F5F130` |
| `EXECUTION_RESULT_SCHEMA.yaml` | 1873 | `CE3CE4BCAB0DA087958FCF8AE44407A26BE9505DD9EE09C0BE729C9F90CF0EAD` |
| `HUMAN_DECISION_SCHEMA.yaml` | 1367 | `DEA9A8833ECC2714B3B9B9C026E24ADEDDDBEA16AF20E47450C3A303918D10C2` |

## Note de concordance

Les SHA-256 ci-dessus sont calculés depuis `git show 8e61f6b9:<path>`. Ce sont les valeurs reproductibles depuis GitHub.

Les hashes de working tree Windows peuvent différer à cause de la normalisation de fin de ligne au checkout. Ils ne sont pas utilisés comme source canonique.
