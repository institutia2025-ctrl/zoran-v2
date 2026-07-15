# INVENTAIRE DATAFLOW — 05_COHERENCE_ENGINE @ f041aae
Builder: CLAUDE. SHA gelé: f041aaecef0f3b81c702f359fdb22e66176bf62f. But: fermer la CLASSE
« toute preuve structurelle consommée par 05 → valide + rattachée à source autoritaire + cohérente
référentiel + unique + non contradictoire + fail-closed AVANT calcul ». Aucune décimale (PENDING_GRID).

## 1. Sorties calculées et leurs entrées
- authorize_llm = (total_pairs>0) AND (delta_phi>=0.5)      # NE dépend QUE de delta_phi + total_pairs
- delta_phi     = resolved/total_pairs ; resolved=|canonized_pairs ∩ operant_pairs|
- tension       = (len(conflicts)+0)/total_pairs           # metric seulement (n'affecte PAS authorize)
- sigma         = CV(canons_par_objet sur univers)         # metric seulement
- S             = beta*delta_phi/(1+tension+sigma)         # metric composite

## 2. Table des preuves consommées
| # | Preuve | Source autoritaire | Validé f041aae | Risque | Tier |
|---|---|---|---|---|---|
| E1 | node.status 00–04 | chaque moteur | ✓ G0 | — | — |
| E2 | referential.fingerprint | 04 | ✓ G1 | — | — |
| E3 | frozen_canons[*].id | 04 | ✓ G2+G3 (sha256 recalculé) | référentiel falsifié | closed |
| E4 | canons_selected[*].object_key/frame | 04 | ✓ G5+G7+G8 | invention/doublon/contradiction | closed |
| E5 | canons_selected[*].canons (forme) | 04 | ✓ G6 (005) | vide/malformé/doublon | closed |
| **E6** | **canons_selected[*].canons[*] ∈ frozen ids** | **référentiel 04 gelé** | **✗** | **canon inventé → faux canonisé → faux delta_phi↑** | **A (007)** |
| E7 | uncanonized[*].object_key/frame | 04 | ✓ G5+G7+G8 | contradiction/couverture | closed |
| E8 | analysis[*].object_key/frame | 03 (→02/01) | ✓ G5 (borné par ∩ canonized) | invention hors-univers | ok |
| **E9** | **analysis[*].operants** | **contrat 03** | **✗** | **couple « résolu » sans opérant réel → faux delta_phi↑** | **A (006)** |
| E10 | object_frame_map (02) | 02 | ✓ G8 (_object_frame_pairs) | omission/invention couverture | closed |
| **E11** | **conflicts == reconstruction EXACTE de 04** (canons_selected + priorités gelées ; groupe ≥2 même priorité, ids triés, 1 entrée/(paire,priorité)) | **04 (reconstruit)** | **✗→ fermé 53167ac (GC-05-P1-E11-CONFLICT-EXACTNESS)** | **priorité inventée/mélangée, doublon réordonné, multi-entrées, groupe partiel, ordre non canonique, conflit omis/ajouté → tension/S faussés** | **B (métrique, propage à 08)** |

Gardes présentes (G0..G8) : statuts PASS ; fingerprint non vide ; frozen wellformed ; sha256 recalculé==déclaré ;
non-liste→MALFORMED (pas de `or []` sur falsy non-liste) ; _keys_all_str ; canons forme (005) ;
non-doublon + non-contradiction canonized/uncanon ; univers==paires autoritaires 02 (CSB-PROV-P1-004).

## 3. Invariants transversaux (définition de la CLASSE)
- INV-TYPE : chaque porteur bien typé (⊆ G5/G6).
- INV-NONEMPTY : porteurs de résolution non vides (canons ✓005 ; **operants ✗**).
- INV-UNIQUE : pas de doublon interne (canons ✓005 ; **operants ✗** ; **conflicts ✗**).
- INV-PROVENANCE : ids rattachés à la source gelée (**canons⊆frozen ✗007** ; paires⊆02 ✓G8).
- INV-NONCONTRADICTION : canonized ∩ uncanon = ∅ ✓G7.
- INV-FAILCLOSED-BEFORE-COMPUTE : tout validé AVANT arithmétique (structure ✓ ; **E6/E9/E11 calculés sur preuve non validée**).

## 4. Deux niveaux de risque
- **Tier A — faux authorize_llm** (P1 critique) : surface = {E6(007), E9(006), total_pairs}. total_pairs clos (G7/G8).
  ⇒ **E6 + E9 = seuls vecteurs ouverts de faux authorize**.
- **Tier B — faux S/métrique** (D_METRIC) : E11 (conflits sur/sous-comptés ou hors-univers) ; E6 distord aussi sigma.
  N'affecte PAS authorize (car authorize ignore tension/sigma), mais fausse la métrique publiée S.

## 5. Contre-exemples par classe (tests ROUGES)
- 006/E9 : operants ∈ {absent, {}, "", [], [12], ["OP","OP"], [""]} + canon valide ⇒ attendu BLOCKED(OA03) ;
  ["OP"] ⇒ PASS. (Actuel f041aae : PASS/delta_phi=1.0/authorize=true → ROUGE.)
- 007/E6 : frozen {id:"C"} + canons=["INVENTED"] ⇒ attendu BLOCKED(CD04) ; ["C"] ⇒ PASS.
  (Actuel : PASS/canonisé → ROUGE.)
- E11 : conflit dupliqué (même paire ×2) ⇒ BLOCKED(CD04) ; conflit hors univers ⇒ BLOCKED(CD04) ;
  conflits uniques in-univers ⇒ PASS.
- GARDE ÉNUMÉRANTE : test paramétré sur CHAQUE porteur de preuve × chaque malformation ⇒ BLOCKED
  (empêche la « fermeture d'exemple » future — c'est LE mécanisme).

## 6. Patch de fermeture de classe (UN seul SHA, sur GO)
1. E9/006 : après G6, boucle `for a in analysis` : `operants` = liste non vide de str non vides UNIQUES → sinon BLOCKED(OA03).
   Hypothèse de contrat 03 : toute entrée `analysis` (analysée) PORTE des opérants (les non-analysées sont dans `unanalyzed`). À reconfirmer vs schéma 03.
2. E6/007 : `allowed = {c["id"] for c in frozen_canons}` ; pour chaque canons_selected exiger `set(canons) ⊆ allowed` → sinon BLOCKED(CD04).
3. E11 : exiger conflits sans doublon de paire ET chaque paire ∈ universe → sinon BLOCKED(CD04). (Ferme le tier B ; tension fiable.)
4. Garde énumérante (§5) en régression.

## 7. Impact (REX #7)
1. Source: 05. 2. Aval: 06/07 lisent authorize_llm/S → uniquement plus de BLOCKED, jamais un PASS plus faux ; 08 post-LLM indépendant. 3. Fixtures: test_coherence_engine.py doit fournir operants valides + canons⊆frozen + conflits uniques in-univers (REX #8 : fixtures=payloads réels 03/04). 4. Invariants: +NONEMPTY/UNIQUE/PROVENANCE sur operants+conflicts. 5. Baseline: tag 05 (+01). 6. Nouveau tag après cert. 7. Rollback: branche non fusionnée / revert. 8. Composition: après 01 mergé.

## 8. Dette (MINIMUM-DEBT, PENDING_GRID)
DEBT_REDUCING : retire faux-authorize (D_LOGIC) + distorsion métrique (D_METRIC) ; ajoute branches de validation (D_CODE mineur). Aucune dette transférée. Réversibilité haute.

## 9. Correction SELF_AUDIT (ajout Fred)
SELF_AUDIT a raté une dépendance RÉELLEMENT consommée (analysis[*].operants). ⇒ (a) il ne peut PAS compter comme certification indépendante ; (b) un inventaire dataflow EXPLICITE doit précéder CHAQUE patch de fermeture de classe. Règle mécanisée : pas de patch de classe sans cette table §2 à jour.
