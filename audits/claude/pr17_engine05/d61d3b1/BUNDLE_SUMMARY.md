# BUNDLE RÉAUDIT — PR#17 ENGINE-05 @ d61d3b1 (DOCS_ONLY / NO_PRODUCT_CHANGE)
OBJECT_ID = PR17_ENGINE05
SHA_AUDITED = d61d3b107f6da7c1a8c24f7d6c21956817424f6d
Protocole = META-PROTOCOL-V1-PILOT / MINIMUM-DEBT-V1-PILOT (PENDING_GRID, aucune décimale)
Auteur = CLAUDE_CODE (BUILD + PREPARE_MERGE). Correctif produit par CODEX_FIXER (je ne l'ai pas codé).
Statut amont : ChatGPT GLOBAL_COHERENCE = APPROVED sur ce SHA exact. Session B : réaudit probatoire à rejouer.

## 1. Contexte
Le finding `GC-05-P1-CANON-REGISTRY-COMPLETENESS` (05 sans autorité indépendante pour détecter un canon
applicable retiré SIMULTANÉMENT de `canons_selected` ET du sous-référentiel gelé) a été corrigé par Codex Fixer
via une ÉVOLUTION CONTRACTUELLE 04→05. Bundle précédent (53167ac) = **périmé** (voir README parent).

## 2. Évolution contractuelle 04→05 (telle qu'IMPLÉMENTÉE par Codex Fixer — lecture du diff)
Hybride Arch A + Arch B :
- **04 (producteur)** émet désormais un `full_registry_commitment` en sortie :
  `{full_registry_fingerprint (sha256 du registre COMPLET normalisé), registry_version, registry_source="CANONS.yaml",
    normalization {id="zoran_v2.canon_determination._normalize_registry", version}}`.
  Sépare explicitement **registre complet engagé** vs **sous-référentiel appliqué** (guard `FULL_REGISTRY_COMMITMENT`).
- **05 (consommateur)** : signature `run_coherence_engine(envelope, full_registry=None)` — le registre COMPLET est une
  entrée INDÉPENDANTE (2e argument), pas dérivée de 04. 05 :
  1. `_strict_normalized_full_registry(full_registry)` — normalise (mêmes fonctions que 04, source unique) ; rejette
     malformé/doublon → BLOCKED(CD04) ; `full_registry=None` → BLOCKED (guard `INDEPENDENT_FULL_REGISTRY_REQUIRED`).
  2. Recompute le commitment et le compare à celui de 04 : `commitment != _full_registry_commitment(normalized)` →
     BLOCKED(CD04) (guard `FULL_REGISTRY_COMMITMENT_VERIFIED`).
  3. Re-dérive l'applicabilité par paire depuis kinds@01 (`_object_kinds`) + frames@02 (`_object_frame_pairs`) →
     reconstruit `expected_selected` et le compare à `canons_selected` de 04 → détecte omission/invention d'un canon
     applicable même s'il a été retiré des deux côtés. Écart → BLOCKED(CD04).

## 3. Inventaire dataflow ACTUALISÉ (delta vs bundle 53167ac)
| Preuve | Producteur | Validation d61d3b1 | Statut |
|---|---|---|---|
| full_registry (COMPLET) | racine CANONS.yaml (injecté indépendamment à 05) | normalisation stricte + rejet malformé/doublon | **NOUVEAU — autorité indépendante** |
| full_registry_commitment | 04 (sortie) | recomputé par 05 et comparé (fingerprint complet + version + normalization id) | **NOUVEAU — provenance registre complet** |
| applicabilité par paire | 01 kinds + 02 frames + registre complet | re-dérivée par 05, `expected_selected` == canons_selected 04 | **NOUVEAU — ferme la complétude** |
| canons_selected[*].canons | 04 | ⊆ ids gelés (007) + cohérent avec re-dérivation | maintenu + renforcé |
| operants (006) / conflits (E11 reconstruction) / couverture 02 (CSB-PROV-P1-004) | 03/04/02 | inchangés (déjà fermés) | maintenus |

## 4. Tests rouges & preuves post-correctif
- `GC-05-P1-CANON-REGISTRY-COMPLETENESS, contre-exemple rouge exact` (test_coherence_engine.py:605) : canon applicable
  retiré des deux côtés → 05 le détecte par re-dérivation indépendante → BLOCKED. **Contre-exemple exact conservé (REX #9).**
- Guards BLOCKED : registre absent/malformé, commitment ≠, applicabilité re-dérivée ≠ canons_selected.
- Findings antérieurs (006 operants, 007 canon selectionné, E11 reconstruction, CSB-PROV-P1-004 couverture) : tests maintenus verts.

## 5. Résultats CI
- CI GitHub PR#17 @ d61d3b1 : **pass** (runs 29419503966 / 29419506990).
- Suite locale rejouée par Claude @ d61d3b1 : **263 passed, 1 deselected** (seul déselect = `py_lt_314` env-only Python 3.14 local ; vert en CI 3.13).

## 6. Diff de référence
`diff_ref_integration_to_d61d3b1.txt` = `git diff integration/v2-canonical...d61d3b1` (1134 lignes) :
canon_determination.py (+25), coherence_engine.py (+249), tests (+627). Aucun autre fichier produit.

## 7. Portée / limites
DOCS_ONLY. Je n'ai PAS codé ce correctif (CODEX_FIXER). Ce bundle est une PRÉPARATION de merge (mon rôle) et ne vaut PAS
certification : je ne certifie jamais un moteur — la convergence (ChatGPT + Codex A + Codex B) + le GO Fred restent requis.
