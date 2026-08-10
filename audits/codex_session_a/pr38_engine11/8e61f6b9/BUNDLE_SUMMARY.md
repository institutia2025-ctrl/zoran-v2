TIMESTAMP: 2026-07-16T08:58:09+02:00
AI_ACTOR_ID: CODEX_SESSION_A
MISSION_ID: TX_ZORAN_ENGINE_11_REAUDIT_PROOF_BUNDLE_V1
OBJECT_ID: ENGINE-11_PR38
SHA_AUDITED: 8e61f6b9de27543e484b12d633077dba00b3e271
GUARD_IDS: CODEX_SESSION_A_PROOF_BUNDLE_V1, META_PROTOCOL_V1_EVIDENCE_BUNDLE, MVPP_SHA_BOUND_PROOF, DOCS_ONLY_NO_PRODUCT_CHANGE, NO_MERGE_AUTHORITY

# ENGINE-11 PR #38 — bundle de réaudit CODEX_SESSION_A

## Destinataires

- ChatGPT GLOBAL_COHERENCE : lever ou maintenir le blocage documentaire.
- Claude : vérifier la convergence après réaudit.
- Fred : décider seul du merge.
- Codex Session B : comparaison des preuves si nécessaire.

## État réel observé

- PR produit : https://github.com/institutia2025-ctrl/zoran-v2/pull/38
- PR #38 : OPEN, draft, mergeable.
- Head produit confirmé : `8e61f6b9de27543e484b12d633077dba00b3e271`.
- Base : `integration/v2-canonical` à `aaf1964145419cdcea48c38293a8344f2ead2471`.
- CI pull_request run : `29443258047`, conclusion `success`, head SHA exact.
- Artifacts GitHub du run : seulement `gitleaks-results.sarif`.

## Verrou traité

ChatGPT GLOBAL_COHERENCE a bloqué la certification parce que le bundle de réaudit n'était pas publié et que les métadonnées PR #38 pointaient encore vers `22a8be2` / 453 tests.

Ce bundle fournit :

- manifest rattaché au SHA exact ;
- inventaire des quatre fichiers du correctif ;
- SHA-256 canoniques des blobs Git ;
- sorties de tests rejouées localement ;
- références CI GitHub ;
- état des artifacts ;
- consigne de mise à jour des métadonnées PR sans mutation produit.

## Résultat CODEX_SESSION_A

`PROOF_BUNDLE_READY_FOR_CHATGPT_REAUDIT`

Ce résultat ne certifie pas ENGINE-11. Il rend le paquet probatoire vérifiable pour que ChatGPT puisse relancer `GLOBAL_COHERENCE` sur `8e61f6b9de27543e484b12d633077dba00b3e271`.

## Mutation

- Produit : aucune.
- Merge : aucun.
- Branche produit PR #38 : inchangée.
- Branche bundle : docs-only.
