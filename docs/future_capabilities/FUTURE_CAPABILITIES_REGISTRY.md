# FUTURE_CAPABILITIES_REGISTRY — registre central autoritaire des capacités différées ZORAN V2

> **SOURCE DE VÉRITÉ.** L'existence, la fonction, le statut et les conditions de réactivation de toute capacité ZORAN
> mise de côté (différée, dormante, hors pipeline, déplacée ou bloquée) sont définis ici et dans les fiches durables de
> ce dossier. Aucune de ces capacités ne dépend plus d'une mémoire personnelle, d'un contexte de session, d'un résumé
> de compaction, d'un scratchpad non versionné, d'une mémoire privée Claude, ou d'un ancien numéro de moteur.

## Principe canonique (Fred 2026-07-16)
« Toute capacité différée, dormante, hors pipeline, déplacée ou bloquée doit être enregistrée dans le registre des
capacités futures. Avant toute mission susceptible de correspondre à l'une de ces capacités, l'agent doit relire le
registre, exhumer les fiches concernées et déclarer explicitement leur impact. L'absence d'implémentation ne signifie
jamais abandon. » → Protocole d'exhumation obligatoire : [`EXHUMATION_PROTOCOL.md`](EXHUMATION_PROTOCOL.md).

## Cadre invariant
- Pipeline de raisonnement runtime : **actuellement certifié et borné ENGINE-00→11 ; ENGINE-11 terminal.** (Révisable
  seulement par nouvelle décision architecturale + recertification — jamais « définitif ».)
- Toute capacité ci-dessous est HORS de ce pipeline (gouvernance, service auxiliaire, ou branche future).
- **Les identifiants sémantiques priment sur les anciens numéros.** Ne pas créer de nouveaux numéros ENGINE.
- Aucune capacité ne peut être supprimée, renommée ou déclarée caduque sans preuve + audit d'impact global + décision Fred.
- Aucun `GO_CODE` n'est implicite.

## Index des capacités (fiches durables)
| Id sémantique | Anciens n°/alias | Statut | Fiche |
|---|---|---|---|
| `GOV_COHERENT_EVOLUTION` | ENGINE-12 | ACTIVE_MANUAL_GOVERNANCE | [GOV_COHERENT_EVOLUTION.md](GOV_COHERENT_EVOLUTION.md) |
| `HISTORICAL_DIFFERENTIAL_INFERENCE` | ENGINE-13 | NECESSARY_FOR_TARGET / DEFERRED | [HISTORICAL_DIFFERENTIAL_INFERENCE.md](HISTORICAL_DIFFERENTIAL_INFERENCE.md) |
| `EXTERNAL_EVIDENCE_AND_FALSIFICATION` | ENGINE-14 | IMPORTANT_AUXILIARY / DEFERRED | [EXTERNAL_EVIDENCE_AND_FALSIFICATION.md](EXTERNAL_EVIDENCE_AND_FALSIFICATION.md) |
| `FUTURE_MODE_ROUTER` | F-024 | FUTURE_DORMANT | [F-024_MODE_ROUTER.md](F-024_MODE_ROUTER.md) |
| `FUTURE_COMPLEMENTARY_FRAME_DISCOVERY` | F-025 · « 15 » informel | FUTURE_DORMANT | [F-025_COMPLEMENTARY_FRAME_DISCOVERY.md](F-025_COMPLEMENTARY_FRAME_DISCOVERY.md) |
| `FUTURE_CONTROLLED_FRAME_DISPLACEMENT` | F-026 · « 16 » informel | FUTURE_DORMANT | [F-026_CONTROLLED_FRAME_DISPLACEMENT.md](F-026_CONTROLLED_FRAME_DISPLACEMENT.md) |
| `FUTURE_RELEVANCE_AND_NOISE_FILTER` | F-027 | FUTURE_DORMANT | [F-027_RELEVANCE_AND_NOISE_FILTER.md](F-027_RELEVANCE_AND_NOISE_FILTER.md) |
| `FUTURE_RESPONSE_FRAME_SELECTION` | F-028 · ancien 09 | FUTURE_DORMANT | [F-028_RESPONSE_FRAME_SELECTION.md](F-028_RESPONSE_FRAME_SELECTION.md) |
| `FUTURE_BUILD_FINAL_RESPONSE` | F-029 · ancien 10 | FUTURE_DORMANT | [F-029_BUILD_FINAL_RESPONSE.md](F-029_BUILD_FINAL_RESPONSE.md) |

Table historique des numéros/alias et renumérotations : [`HISTORICAL_ALIASES_AND_RENUMBERING.md`](HISTORICAL_ALIASES_AND_RENUMBERING.md).

## Note « futur probable » (vérifiée runtime 2026-07-16)
`FUTURE_PROBABILITY_CONCEPT_CONFIRMED` (mémoire addendum03 2026-06-05 ; `predict_next_coherent_state.py` dans zoran main) —
mais **`CURRENT_ZORAN_V2_RUNTIME_IMPLEMENTATION = NON_IMPLÉMENTÉ`** : le moteur 05/08 actuel n'a qu'une cinématique
partielle (`S_pre, S_post, delta_S, trend` ; `coherence_2.py:21` mentionne explicitement « Pas de dS/dt »). Pas de
`future_probability`/`rupture_probability`/`predict_next` dans le runtime zoran-v2. Ne pas affirmer que c'est actif en 05.

## Ordre FONCTIONNEL (≠ ordre numérique)
`13 histoire différentielle → F-025 cadres manquants → 14 Internet+falsification → quarantaine/audit → 12 correction gouvernée`.
La numérotation mécanique 13→14→15 induit en erreur : **F-025 (« 15 » informel) intervient fonctionnellement AVANT 14.**

## Rappel automatique futur (dormant, non construit)
Un `DEFERRED_CAPABILITY_RELEVANCE_GUARD` central (hors pipeline, consultatif, sans réseau, déterministe, rejouable) est
PROPOSÉ pour signaler, à partir des traces closes 00→11, quand une capacité différée aurait été pertinente. Il ne
construit ni n'active rien. Conception et conditions dans [`EXHUMATION_PROTOCOL.md`](EXHUMATION_PROTOCOL.md) §Guard.
**Statut : conçu, NON construit ; GO_CODE = non.**

Dernière vérification du registre : **2026-07-16**.
