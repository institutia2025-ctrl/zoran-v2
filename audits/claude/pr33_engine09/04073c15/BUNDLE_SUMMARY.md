# BUNDLE RÉAUDIT — PR#33 ENGINE-09 @ 04073c15 (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR33_ENGINE09
SHA_AUDITED = 04073c158b005e3c17dd2599111378179d5e2f2b
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID). Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE).
Build initial + révisions = Claude ; correctif du finding ci-dessous = CODEX_FIXER. Ce bundle ne vaut PAS certification.
Bundle ancré UNIQUEMENT à 04073c15 (les SHA antérieurs b9316f0 / 4137498 ne reçoivent PAS de bundle de certification).

## 1. Moteur 09 = 09_STRUCTURED_DECISION
Transforme EXCLUSIVEMENT une réponse ADMISE par 08 (verdict==ACCEPT, authorize_09 is True strict) en un
objet-décision déterministe, sans génération. Invariants : NO_LLM/NO_NETWORK/NO_NEW_INFORMATION/NO_ACTION_EXECUTION/
FAIL_CLOSED/ANTI_LEAK/IMMUTABLE/DETERMINISTIC. Frontière revalidée 4 niveaux (chaîne fingerprint 04/07/08,
admissibilité 08, schéma 06.targets + 07.response, provenance ⊆ 06, COUVERTURE EXACTE P1). Contrat figé :
specs/SPEC_ENGINE_09_STRUCTURED_DECISION.md.

## 2. Historique des SHA (branche feat/engine-09-structured-decision)
- b9316f0 : 1er jet (hasher local, objet nesté). PÉRIMÉ.
- 4137498 : révision cadrage (réutilisation _fingerprint, OBJECT_FIRST 2 phases, objet plat 16 clés, T-2 NFC/CRLF/ordre). PÉRIMÉ.
- **04073c15 : COURANT** — fix CODEX_FIXER du finding ci-dessous.

## 3. Finding FERMÉ dans ce SHA
**`GC-09-P1-DECISION-ID-TARGET-CONTEXT-OMISSION`** : le payload du `decision_id` omettait `kind_public` des cibles
normalisées -> deux cibles ne différant QUE par `kind_public` produisaient le MÊME decision_id (contexte de cible
incomplet dans l'identité de décision). **Fix (04073c15)** : `kind_public` inclus dans le contexte de cible du payload
decision_id ; guard `DECISION_ID_COVERS_COMPLETE_TARGET_CONTEXT`. Commit « include target kind in decision identity ».

## 4. Vérification indépendante (Claude, lecture code + exécution @ 04073c15)
- Preuve du fix : 2 cibles identiques SAUF `kind_public` (`code` vs `config`) -> decision_id DIFFÉRENTS
  (`DECISION-bdb8bd65…` ≠ `DECISION-de2905e0…`). Finding fermé.
- Déterminisme conservé (mêmes entrées -> même id) ; T-2 (NFC≠NFD, CRLF≠LF, ordre clés = même id) verts.
- decision_id + CONTENT_SHA256 via la primitive `_fingerprint` réutilisée (aucun second hasher) ; canon_determination.py NON modifié.
- Tests @ 04073c15 : ciblés 09 = **30 passed** ; suite complète = **371 passed, 1 deselected** (py_lt_314 env-only).
- CI GitHub PR#33 @ 04073c15 : **success** (pytest · pip-audit · gitleaks · bandit).

## 5. Contenu du bundle
- `diff_ref_integration_to_04073c15.txt` — `git diff integration...04073c15` (796 l.), 4 fichiers 09 uniquement (aucun 04/06/07/08).
- `MANIFEST.json` / `MANIFEST.sha256`.

## 6. Portée
DOCS_ONLY. Aucune modif PR#33 ni du SHA produit. Ce bundle PRÉPARE l'audit indépendant (ChatGPT + Codex A + Codex B)
sur `04073c15` ; il ne vaut PAS certification (SELF_AUDIT builder/correcteur insuffisant).
