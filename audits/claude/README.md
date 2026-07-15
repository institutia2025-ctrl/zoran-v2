# Paquets d'audit — CLAUDE (builder → demandes d'audit)

Archivage dans le dépôt des **bundles d'audit** que Claude a produits pour chaque SHA soumis à
certification (ferme le défaut documentaire : pointeurs `scratchpad/…` non présents dans le checkout).

Chaque fichier contient, pour un SHA précis : le cadrage, le diff intégral audité, et les **questions
falsifiables** posées aux certificateurs (ChatGPT GLOBAL_COHERENCE + Codex Session A/B).

| Fichier | Finding | SHA | État |
|---|---|---|---|
| `CSB-META-P1-003_01-unicode_bdf022a.md` | Unicode NFC (01) | `bdf022a` | CERTIFIED + mergé (`7493c75`) |
| `CSB-03-04_baseline-03-04_8d69646.md` | 03→04 fail-closed | `8d69646` (→ `711acbd`) | CERTIFIED + mergé (`9ed679f`) |
| `CSB-PROV-P1-004_05-coverage_d03b473.md` | couverture/contradiction 04→05 | `d03b473` | en audit (gelé) |
| `engine-08_coherence-2_8227167.md` | engine-08 (coherence_2) | `8227167` | en audit |

NB : ces bundles sont des **demandes d'audit** (preuves + questions), distinctes des rapports de
verdict des certificateurs (côté Codex/ChatGPT) et des preuves reproductibles de Session B
(`audits/codex_session_b/`). Docs-only, aucun impact produit.
