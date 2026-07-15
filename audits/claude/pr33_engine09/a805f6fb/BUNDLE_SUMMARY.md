# BUNDLE RÉAUDIT — PR#33 ENGINE-09 @ a805f6fb (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR33_ENGINE09
SHA_AUDITED = a805f6fbf120ed7b65238f58a48c946ad9ce1959
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID). Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE).
Build initial + révisions = Claude ; correctifs findings = CODEX_FIXER. Ce bundle ne vaut PAS certification.
Bundle ancré UNIQUEMENT à a805f6fb ; les SHA antérieurs (b9316f0 / 4137498 / 04073c15) ne reçoivent PAS de bundle de certification.

## 1. Moteur 09 = 09_STRUCTURED_DECISION
Transforme EXCLUSIVEMENT une réponse ADMISE par 08 (verdict==ACCEPT, authorize_09 is True strict) en un objet-décision
déterministe, sans génération. Frontière revalidée 4 niveaux + couverture exacte P1 ; decision_id + CONTENT_SHA256 via la
primitive `_fingerprint` réutilisée (aucun second hasher) ; OBJECT_FIRST 2 phases ; conservation exacte des chaînes.
Contrat figé : specs/SPEC_ENGINE_09_STRUCTURED_DECISION.md.

## 2. Historique des SHA (branche feat/engine-09-structured-decision)
- b9316f0 : 1er jet. PÉRIMÉ.
- 4137498 : révision cadrage. PÉRIMÉ.
- 04073c15 : fix GC-09-P1-DECISION-ID-TARGET-CONTEXT-OMISSION. PÉRIMÉ (puis FIX_REQUIRED sur surrogate).
- **a805f6fb : COURANT** — fix CODEX_FIXER du finding ci-dessous.

## 3. Findings FERMÉS (cumulés dans a805f6fb)
- `GC-09-P1-DECISION-ID-TARGET-CONTEXT-OMISSION` (04073c15) : `kind_public` inclus dans l'identité de décision.
- **`CSB-09-P1-001 UNPAIRED_SURROGATE_HASH_CRASH`** (a805f6fb) : les validateurs acceptaient des chaînes avec codepoints
  surrogate (U+D800–U+DFFF) ; le hash canonique `_fingerprint` crashait ensuite à l'encodage UTF-8 strict. **Fix** : détection
  récursive `_has_surrogate_codepoint` du payload AVANT hash -> `BLOCKED(09_STRUCTURED_DECISION_NON_SCALAR_UNICODE@…payload_decision)`,
  `decision_id=null`, AUCUNE exception. Unicode scalaire valide (accents, emoji) PRÉSERVÉ. Commit « block non-scalar Unicode before sealing ».

## 4. Vérification indépendante (Claude, lecture code + exécution @ a805f6fb)
- Repro : `A\ud800B` (+ `\ud800`, `\udfff`, `X\udc00Y`) -> **BLOCKED** (`NON_SCALAR_UNICODE`), decision_id null, **aucun crash**.
- Non-régression unicode : `café🚀` (accent + emoji scalaires) -> **PASS** avec decision_id.
- Fix précédent maintenu : 2 cibles ne différant que par `kind_public` -> decision_id différents. Déterminisme + T-2 verts.
- `_fingerprint` réutilisé (aucun 2ᵉ hasher) ; `canon_determination.py` NON modifié.
- Tests @ a805f6fb : ciblés 09 = **32 passed** ; suite complète = **373 passed, 1 deselected** (py_lt_314 env-only).
- CI GitHub PR#33 @ a805f6fb : **success** (pytest · pip-audit · gitleaks · bandit).

## 5. Contenu du bundle
- `diff_ref_integration_to_a805f6fb.txt` — `git diff integration...a805f6fb` (859 l.), 4 fichiers 09 uniquement (aucun 04/06/07/08).
- `MANIFEST.json` / `MANIFEST.sha256`.

## 6. Portée
DOCS_ONLY. Aucune modif PR#33 ni du SHA produit. Correctifs = CODEX_FIXER. Ce bundle PRÉPARE l'audit indépendant
(ChatGPT + Codex A + Codex B) sur `a805f6fb` ; il ne vaut PAS certification.
