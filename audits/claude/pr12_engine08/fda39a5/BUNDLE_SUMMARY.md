# BUNDLE PRÉPARATION D'AUDIT — PR#12 ENGINE-08 @ fda39a5 (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR12_ENGINE08
SHA_AUDITED = fda39a5cbcb780d3e4601550a576e524957f4d4f
Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE). Correctifs du code = CODEX_FIXER. Supersede a048bcc + 37f40b1 (périmés).

## Findings FERMÉS dans ce SHA
- **GC-08-P1-FINGERPRINT-CHAIN-05-04** (a048bcc) : 04.fingerprint == 05.coherence.referential_fingerprint avant validation 06.
- **CSB-08-P1-001 RESOURCE_VETO_05_BYPASS** (fda39a5) : 08 exige `05.resource.authorize_llm is True` (identité STRICTE)
  AVANT validation 06 / jugement / authorize_09 ; sinon BLOCKED(`05_COHERENCE_ENGINE_RESOURCE_VETO`). Classe fermée :
  resource absent/non-dict, authorize_llm absent/false/0/1/"true"/null, veto 05 avec 07.executed=true. Guard `RESOURCE_VETO_05_REVALIDATED_STRICT_TRUE`.

## Vérification indépendante (Claude, lecture code + exécution @ fda39a5)
- Contrôle lu (coherence_2.py l.285-287) : `resource5=ce.get("resource")` ; `if not (isinstance(resource5,dict) and resource5.get("authorize_llm") is True): return _blocked(RESOURCE_VETO_05)`.
- Repro exacte du contournement : veto False + 07.executed=True -> **BLOCKED(05_COHERENCE_ENGINE_RESOURCE_VETO)**, verdict None, authorize_09 False. Nominal True -> PASS.
- Tests @ fda39a5 (pytest 9.1.1) : ciblés 08 = **72 passed** ; suite complète = **341 passed, 1 deselected** (py_lt_314 env-only). CI GitHub = **5/5 success** (pytest, test, pip-audit, gitleaks, bandit).
- pytest-9 compatible (= contrainte de la nouvelle integration post-PR#32).

## Contenu
- PREP_AUDIT_08.md (dataflow, risques ; H1 + RESOURCE_VETO marqués FERMÉS ; H2-H7 à auditer). diff de référence. MANIFEST.

## Risques RESTANTS à auditer
H2 (skip silencieux vocab) · H3 (gate delta_s≥0) · H4 (sigma métrique) · H5 (reason_code couvert) · H6 (transfert 09) · H7 (anti-fuite profond).

## Portée
DOCS_ONLY. Aucune modif PR#12 ni du SHA produit. Correctifs par CODEX_FIXER. Ce bundle PRÉPARE l'audit indépendant
(ChatGPT + Codex A + Codex B) sur fda39a5 ; il ne vaut PAS certification (SELF_AUDIT correcteur + builder = insuffisant).
