# BUNDLE PRÉPARATION D'AUDIT — PR#12 ENGINE-08 @ a048bcc (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR12_ENGINE08
SHA_AUDITED = a048bcc1d2d86e5d5f9c773a829ec80545b920ec
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID). Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE).
Supersede le bundle 37f40b1 (périmé). Correctif du finding = par CODEX_FIXER.

## 1. Contexte
`a048bcc` = `37f40b1` + fix CODEX_FIXER « bind fingerprint authority to engine 05 ».
Fichiers 08 modifiés vs integration : `zoran_v2/coherence_2.py`, `tests/test_coherence_2.py`, `CANONICAL_SOURCES.yaml`.

## 2. Finding FERMÉ dans ce SHA
**`GC-08-P1-FINGERPRINT-CHAIN-05-04`** (= risque H1 de la préparation, remonté par ChatGPT) : 08 utilisait le
fingerprint de 04 comme autorité SANS vérifier qu'il correspond au fingerprint déjà validé et propagé par 05.
Contre-exemple : `05.coherence.referential_fingerprint = FP_ORIGINAL` mais `04/06/07 = FP_FALSIFIE` → 08 jugeait
la chaîne falsifiée. **Fix (a048bcc)** : AVANT validation 06 et tout jugement/authorize_09, exiger
`04.canon_referential.fingerprint == 05.coherence.referential_fingerprint` (deux str NON VIDES) ; sinon
`FINGERPRINT_MISSING` (fp05 absent/vide/non-str) ou `FINGERPRINT_CHAIN_MISMATCH` (divergence). Guard
`REFERENTIAL_FINGERPRINT_04_MATCHES_05`. Classe fermée : fp05 absent/vide/non-str, divergence 04/05, fp04 absent, nominal identique → PASS.

## 3. Contenu du bundle
- `PREP_AUDIT_08.md` — dossier READ-ONLY ré-ancré `a048bcc` : matrice dataflow (§2), preuves par sortie (§3),
  risques (§4 — **H1 marqué FERMÉ**, H2–H7 restent à auditer), frontières 04→06→07→08 (§5), deps 08→09 (§6),
  3 rôles possibles de 09 (§7), questions contractuelles (§8).
- `diff_ref_integration_to_a048bcc.txt` — `git diff integration...a048bcc` (1143 l.).
- `MANIFEST.json` / `MANIFEST.sha256`.

## 4. Résultats des tests (rejoués par Claude @ a048bcc)
- Tests ciblés 08 (`tests/test_coherence_2.py`) : **65 passed** (dont contre-exemple exact FP_ORIGINAL/FP_FALSIFIE → BLOCKED).
- Suite complète : **334 passed, 1 deselected** (`py_lt_314` env-only Python 3.14 local ; vert CI 3.13).
- CI GitHub PR#12 @ a048bcc : **success**.

## 5. Risques RESTANTS à auditer (détail PREP_AUDIT_08.md §4)
H2 (skip silencieux vocab 04/03) · H3 (gate delta_s≥0, espaces S_pre/S_post différents) · H4 (sigma métrique) ·
H5 (reason_code CONSTRAINT_BLOCKED/CANON_CONFLICT comptent couvert) · H6 (transfert 09 : revalider verdict↔authorize_09) ·
H7 (anti-fuite récursif sur payload profond). **H1 = FERMÉ.**

## 6. Portée / limites
DOCS_ONLY. Aucune modif PR#12 ni du SHA produit. Correctif du finding par CODEX_FIXER. Ce bundle PRÉPARE l'audit
indépendant (ChatGPT + Codex A + Codex B) sur `a048bcc` ; il ne vaut PAS certification.
