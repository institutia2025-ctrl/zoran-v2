# HISTORICAL_ALIASES_AND_RENUMBERING — anciens numéros, alias, renumérotations

> But : conserver l'historique des numéros/alias SANS le transformer en vérité numérique. Les identifiants sémantiques
> priment. Ne pas créer de nouveaux numéros ENGINE. Registre : [`FUTURE_CAPABILITIES_REGISTRY.md`](FUTURE_CAPABILITIES_REGISTRY.md).

## Table numéros/alias → fonction
| N°/alias | Statut du numéro | Fonction | Id sémantique | Source |
|---|---|---|---|---|
| ENGINE-12 | figé (spec canonique, reclassé hors pipeline) | non-récurrence / correction gouvernée | `GOV_COHERENT_EVOLUTION` | `specs/CONTRACT_ENGINE_12…` ; PR #41 mergé `5923252` |
| ENGINE-13 | figé (contrat Git) | inférence différentielle historique | `HISTORICAL_DIFFERENTIAL_INFERENCE` | Git `47e5e0a` (branche governance) |
| ENGINE-14 | figé (contrat Git) | **recherche Internet + falsification externe** | `EXTERNAL_EVIDENCE_AND_FALSIFICATION` | Git `b273b7f` + roadmap `a67604f` |
| « 15 » | **INFORMEL, reporté** | découverte de cadres manquants (interne) | `F-025 COMPLEMENTARY_FRAME_DISCOVERY` | scratchpad 2026-07-15 15:27 ; mémoire F-025 |
| « 16 » | **INFORMEL, reporté** | déplacement créatif de cadres | `F-026 CONTROLLED_FRAME_DISPLACEMENT` | scratchpad 2026-07-15 15:28 ; mémoire F-026 |
| « 17 » | **ALIAS MÉMORIEL, non corroboré** | *(cf. ci-dessous)* | — (aucun) | assertion Fred uniquement |
| ancien 09 | **réassigné** (ADR-delta 2026-07-15) | sélection cadre de présentation | `F-028 RESPONSE_FRAME_SELECTION` | scratchpad `ADR_DELTA_09_10` ; mémoire F-028 |
| ancien 10 | **réassigné** (ADR-delta 2026-07-15) | construction réponse finale | `F-029 BUILD_FINAL_RESPONSE` | scratchpad `ADR_DELTA_09_10` ; mémoire F-029 |

Note : les slots **09/10 actuels** = `STRUCTURED_DECISION` / `ACTION_ADMISSIBILITY_AND_PLAN` (moteurs certifiés). Les
anciennes fonctions 09/10 (présentation) ont été déplacées en branche présentation non autoritaire (F-028/F-029).

## L'alias « ENGINE-17 » — statut
**`USER_ASSERTED_HISTORICAL_ALIAS — FUNCTIONALLY_MAPPED — NUMERIC_BINDING_UNCORROBORATED`.**

La mémoire de Fred n'était PAS fausse fonctionnellement : il avait retenu un **mécanisme global** — quand les cadres
sont insuffisants, on cherche des cadres complémentaires, on recherche sur Internet, on explore une évolution probable,
on prépare éventuellement une correction. Ce mécanisme EXISTE dans la conception, mais il a été **découpé** entre
plusieurs capacités. Aucun artefact (scratchpad, mémoire, Git zoran-v2, Git zoran main) ne lie le **numéro** 17 à une
fonction (recherche complète 2026-07-16 : `NO_BINDING_FOUND` côté numéro). **Ne pas utiliser « 17 » comme identifiant.**

### Répartition fonctionnelle du « 17 » (corroborée)
| Composante du souvenir « 17 » | Capacité réelle | Statut |
|---|---|---|
| cadres insuffisants / découverte-prolongement de cadres | `F-025 COMPLEMENTARY_FRAME_DISCOVERY` | dormant (interne, amont) |
| recherche Internet / preuve externe / falsification | `EXTERNAL_EVIDENCE_AND_FALSIFICATION` (ENGINE-14) | différé (service externe isolé) |
| futur probable / évolution probable | cinématique de cohérence | **CONCEPT_CONFIRMED / runtime zoran-v2 NON_IMPLÉMENTÉ** (cf. ci-dessous) |
| préparation d'une correction | `GOV_COHERENT_EVOLUTION` (ENGINE-12) | gouvernance manuelle active |

## « Futur probable » — vérification runtime (2026-07-16)
- **`FUTURE_PROBABILITY_CONCEPT_CONFIRMED`** : concept établi (mémoire `feedback_addendum03_coherence_cinematique_futur.md`
  2026-06-05 ; ordre de décision Faits>Falsification>S>Cinématique>Futur probable ; `predict_next_coherent_state.py`
  existe dans le dépôt zoran main).
- **`CURRENT_ZORAN_V2_RUNTIME_IMPLEMENTATION_UNVERIFIED` → vérifié ABSENT** : le moteur 05/08 certifié de zoran-v2 n'a
  qu'une **cinématique partielle** (`S_pre, S_post, delta_S, trend` ; `zoran_v2/coherence_2.py:21` : « Pas de dS/dt
  (< 3 observations) »). Aucun `future_probability` / `rupture_probability` / `predict_next` dans le runtime zoran-v2.
- **Conclusion** : ne pas affirmer que « futur probable » est actif dans ENGINE-05 actuel. C'est un concept confirmé,
  runtime zoran-v2 = non implémenté (enrichissement futur possible du cœur cohérence, hors périmètre de ce registre).

## Renumérotations détectées (synthèse)
- Anciens 09/10 (présentation) → F-028/F-029 (ADR-delta 2026-07-15) ; slots 09/10 réassignés aux moteurs certifiés actuels.
- Fonction Internet : STABLE à ENGINE-14 dans tous les artefacts ; le « 17 » est une renumérotation mnésique non persistée.
- Numérotation ENGINE au-delà de 11 : **NON figée** (F-024→F-029 = identifiants sémantiques).

Dernière vérification : **2026-07-16**.
