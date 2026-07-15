# BUNDLE PRÉPARATION D'AUDIT — PR#12 ENGINE-08 @ 37f40b1 (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR12_ENGINE08
SHA_AUDITED = 37f40b169eb1e94aab054bf424f070a9289cb9ad
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID, aucune décimale)
Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE). Ceci est une PRÉPARATION d'audit, PAS une certification.

## 1. Contexte
08 = 2e passe de cohérence POST-LLM (déterministe, NO_LLM). SHA `37f40b1` = rebase MÉCANIQUE de l'ex-SHA
`8227167` sur `integration @ 2e44923` (après merge 05 certifié). Rebase 0 conflit → **logique 08 identique**.
Fichiers réellement modifiés par la branche 08 (vs integration) : `zoran_v2/coherence_2.py`,
`tests/test_coherence_2.py`, `CANONICAL_SOURCES.yaml` (les 3 fichiers 08 uniquement).

## 2. Contenu du bundle
- `PREP_AUDIT_08.md` — dossier complet READ-ONLY : **matrice dataflow** (§2), preuves par sortie (§3),
  **risques H1–H7** (§4), **frontières 04→06→07→08 + provenance** (§5), dépendances 08→09 (§6),
  matrice non canonique des 3 rôles de 09 (§7), questions contractuelles (§8).
- `diff_ref_integration_to_37f40b1.txt` — `git diff integration/v2-canonical...37f40b1` (1102 l.).
- `MANIFEST.json` / `MANIFEST.sha256`.

## 3. Résumé matrice dataflow (détail dans PREP_AUDIT_08.md §2)
08 consomme : status 00→07 · 07.executed · 04.fingerprint (comparé, **NON recalculé** — cf. H1) ·
04.canons.id / 03.operants (vocab, filtre) · 05.coherence.S (s_pre) · 06.authorized · 06.llm_request
(re-validé strictement) · 07.response (jugée). Sorties : BLOCKED / REJECT / QUARANTINE / ACCEPT + `authorize_09`
(=ACCEPT) + coherence_post.

## 4. Risques / contre-exemples à jouer par l'auditeur (détail §4)
- **H1** (frontière clé) : fingerprint 04 non recalculé par 08 (05 le recalcule) → 04 tampéré avec fp string conservé.
- H2 : skip silencieux du vocab 04/03 malformé (fail-closed en aval, asymétrie vs 05).
- H3 : gate `delta_s≥0` compare S_pre (05, paires) et S_post (08, cibles réponse) — espaces différents.
- H4 : sigma métrique seulement.
- H5 : reason_code CONSTRAINT_BLOCKED/CANON_CONFLICT comptent l'opérant COUVERT (question contrat).
- H6 : transfert 09 — 09 devra revalider `verdict==ACCEPT ⇔ authorize_09` + fingerprint chain.
- H7 : anti-fuite récursif à confirmer sur payload profond.

## 5. Frontières 04→06→07→08 (détail §5)
05→06 (`coherence_S==05.S`), 04→06 (`fp==04`, `canons⊆04`, `operants⊆03`), 06→07→08 (réponse comparée à `expected`)
= re-validées ✓. Point faible : 04→08 direct, fp non recalculé (H1).

## 6. Résultats des tests (rejoués par Claude @ 37f40b1)
- Tests ciblés 08 (`tests/test_coherence_2.py`) : **58 passed**.
- 06/07/08 (`test_llm_request_build` + `test_llm_execution` + `test_coherence_2`) : **107 passed** → 04→05 ne rompt PAS 06/07/08.
- Suite complète : **327 passed, 1 deselected** (`py_lt_314` env-only Python 3.14 local ; vert CI 3.13).
- CI GitHub PR#12 @ 37f40b1 : **success**.

## 7. Portée / limites
DOCS_ONLY. Aucune modif PR#12 ni du SHA produit. Ce bundle PRÉPARE l'audit indépendant (ChatGPT + Codex A + Codex B) ;
il ne vaut PAS certification. Claude ne certifie jamais un moteur qu'il prépare.
