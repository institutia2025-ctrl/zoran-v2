# BUNDLE RÉAUDIT — PR#35 ENGINE-10 @ adbfa0e (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR35_ENGINE10
SHA_AUDITED = adbfa0ef1b7539d4a6f9d7a07f0803b11ec3d3f4
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID). Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE).
Build = Claude ; correctifs = CODEX_FIXER. Ce bundle ne vaut PAS certification. Ancré UNIQUEMENT à adbfa0e.
Supersède le dossier `61f67bb/` (SHA précédent) — celui-ci reste comme historique, la certification vise adbfa0e.

## 0. Findings FERMÉS depuis 61f67bb (→ adbfa0e)
- **GC-10-P1-DECISION-09-PROVENANCE-REPLAY** (ChatGPT GLOBAL_COHERENCE) — rejeu de provenance de la décision 09 :
  l'intégrité de 09 doit être re-prouvée par recomputation, pas seulement lue. Fermé par le durcissement de la revalidation
  d'intégrité 09 (CONTENT_SHA256 recomputé == 09 avant tout verdict).
- **CSB-10-P1-001 UNBOUND_ACTION_CATALOG_PROVENANCE** (Codex Session B) — le catalogue d'actions n'était pas lié à un
  engagement canonique : provenance du catalogue non bornée. Fermé par `fix(engine-10): bind catalog to canonical commitment`
  (le catalogue est désormais lié à un commitment canonique versionné, provenance bornée et vérifiée).

## 1. Moteur 10 = 10_ACTION_ADMISSIBILITY_AND_PLAN
Évalue si la décision structurée de 09 (certifiée) peut devenir une action, produit un plan BORNÉ. **AUCUNE exécution.**
CATALOG_ONLY (aucune invention) ; `action_request` explicite ; catalogue + permissions INJECTÉS ; réutilise les primitives
de 09 certifié (`_canonical_sha256` via `_fingerprint` → aucun 2ᵉ hasher ; `_has_surrogate_codepoint` ; `_has_internal_leak`).
Contrat figé : `SPEC_ENGINE_10_FROZEN.md` (inclus). Catalogue lié à un commitment canonique (fix adbfa0e).

## 2. Gate + verdicts
- **Gate** (fail-closed → status=BLOCKED) : 00→09 PASS · **intégrité 09** (schéma exact + `decision_id` valide +
  `CONTENT_SHA256` RECALCULÉ == 09, décision non altérée — renforcé, cf GC-10-P1) · `action_request` bien formé ·
  action ∈ catalogue versionné **lié au commitment canonique** (cf CSB-10-P1-001) · permissions valides · cibles ⊆ 09 ·
  anti-fuite · anti-surrogate.
- **Verdicts** (status=PASS) : `ACTION_NOT_REQUIRED` · `ACTION_BLOCKED` · `ACTION_QUARANTINED` (GLOBAL_IMPACT_BEFORE_PLAN) ·
  `ACTION_PLAN_READY` · `HUMAN_APPROVAL_REQUIRED` (`sensitive_mutation=true`).
- `action_plan_id` = contexte COMPLET via `_fingerprint` réutilisé ; `CONTENT_SHA256` séparé ; OBJECT_FIRST 2 phases ; aucune auto-référence.

## 3. Vérification (Claude, exécution live @ adbfa0e)
- **Tests ciblés 10** : **36 passed** (`pytest tests/test_action_admissibility_and_plan.py`).
- **Suite contractuelle** : **409 passed, 1 deselected** (`test_probe_contrat_python` = env-only Python 3.14 local, deselected en CI 3.13).
- **CI GitHub @ adbfa0e** : **SUCCESS** (pytest · pip-audit · gitleaks · bandit).
- `_fingerprint` réutilisé (aucun 2ᵉ hasher) ; **aucune modif 00→09**.

## 4. Contenu du bundle
- `SPEC_ENGINE_10_FROZEN.md` — contrat figé ENGINE-10 (copie @ adbfa0e).
- `ACTIONS_CATALOG.yaml` — catalogue versionné gelé, lié au commitment canonique (copie @ adbfa0e).
- `diff_ref_integration_to_adbfa0e.txt` — `git diff integration...adbfa0e` (824 l.), 5 fichiers 10 uniquement.
- `MANIFEST.json` / `MANIFEST.sha256`.

## 5. Portée
DOCS_ONLY / NO_PRODUCT_CHANGE. Aucune modif du SHA produit `adbfa0e` ni de PR#35. Ce bundle PRÉPARE l'audit indépendant
(ChatGPT + Codex A + Codex B) sur `adbfa0e` ; il ne vaut PAS certification.
