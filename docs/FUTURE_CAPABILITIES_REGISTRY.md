# FUTURE_CAPABILITIES_REGISTRY — registre autoritaire des capacités différées ZORAN V2

> **STATUT : SOURCE AUTORITAIRE.** Ce registre est la source de vérité de l'existence, de la fonction, du statut
> et des conditions de réactivation de toute capacité ZORAN mise de côté (différée, dormante, hors pipeline ou bloquée).
> Aucune de ces capacités ne dépend plus d'un scratchpad, d'un contexte Claude ou d'une mémoire non canonique.
>
> **RÈGLE (Fred 2026-07-16).** Toute capacité différée, dormante, hors pipeline ou bloquée DOIT être enregistrée ici
> AVANT clôture de sa mission. L'absence d'implémentation ne signifie JAMAIS abandon. Aucune capacité enregistrée ne
> peut être supprimée, renommée ou déclarée caduque sans preuve, audit d'impact global et décision explicite de Fred.

**Pipeline de raisonnement runtime : actuellement certifié et borné ENGINE-00→11 ; ENGINE-11 terminal.**
Toute capacité ci-dessous est HORS de ce pipeline (gouvernance, service auxiliaire, ou branche future). Numérotation
ENGINE au-delà de 11 : NON figée. Ne pas créer de nouveaux numéros ENGINE. Dernière vérification du registre : **2026-07-16**.

---

## Note historique (numéros & alias)

- **« ENGINE-15 » / « ENGINE-16 »** : numéros INFORMELS associés aux fiches **F-025** (COMPLEMENTARY_FRAME_DISCOVERY) et
  **F-026** (CONTROLLED_FRAME_DISPLACEMENT). Numérotation REPORTÉE ; ce ne sont pas des identifiants canoniques.
- **« ENGINE-17 »** : alias **mnésique non vérifié** ; aucune liaison canonique trouvée (recherche complète zoran-v2 +
  zoran main, 2026-07-16 : `NO_BINDING_FOUND`). **Ne pas utiliser comme identifiant.**
- La fonction mémorisée comme **« recherche Internet de cadres »** correspond à la CHAÎNE :
  **F-025 COMPLEMENTARY_FRAME_DISCOVERY → EXTERNAL_EVIDENCE_AND_FALSIFICATION** (deux fonctions distinctes : la
  découverte de cadres est INTERNE et AMONT ; la recherche Internet est le service externe AVAL).
- **Renumérotation tracée** : les ANCIENS moteurs 09/10 (orientés présentation, spec 2026-07-14) ont été déplacés par
  l'ADR-delta (2026-07-15) vers la branche présentation non autoritaire (→ **F-028** / **F-029**) ; les slots 09/10 ont
  été réassignés à STRUCTURED_DECISION / ACTION_ADMISSIBILITY_AND_PLAN (moteurs certifiés actuels).

---

## 1. GOV_COHERENT_EVOLUTION

- **Identifiant sémantique** : `GOV_COHERENT_EVOLUTION`
- **Anciens numéros / alias** : ENGINE-12 ; `12_COHERENT_EVOLUTION` (retiré)
- **Fonction** : non-récurrence et évolution gouvernée — prendre une erreur confirmée, identifier sa classe générale,
  ajouter/renforcer un invariant, produire un guard, produire un test de non-récurrence, vérifier l'impact global,
  soumettre l'évolution à audit, empêcher que la même classe d'erreur réapparaisse.
- **Raison de conservation** : c'est EXACTEMENT le mécanisme qui a fermé les findings des moteurs (ex. les 2 findings
  d'usurpation d'ENGINE-11 : `SELF_ASSERTED_EXTERNAL_PROOF` + `IDENTITY_IMPERSONATION`).
- **Statut actuel** : **ACTIVE_MANUAL_GOVERNANCE** (fonction déjà opérante comme processus, pas comme moteur).
- **Emplacement architectural** : gouvernance HORS pipeline (méta-boucle, multi-transactions, post-confirmation d'erreur).
- **Dépendances** : registre de findings, tests adversariaux, guards, CI, audits indépendants, quarantaine, décision Fred.
- **Verrou principal** : aucun (la fonction fonctionne manuellement). Verrou d'automatisation = besoin d'échelle mesuré.
- **Risques** : automatiser prématurément → auto-apprentissage ou promotion incorrecte d'une règle depuis une mauvaise
  interprétation d'un finding. Forme future obligatoire = **CONSULTATIVE** (propose ; ne modifie jamais le code ; ne
  promeut jamais ; ne merge jamais ; GO Fred final).
- **Conditions de réactivation (mesurables)** : trop de findings pour traitement manuel ; **récidive d'une classe
  déclarée fermée** (détectable via `FINDINGS_LOG.jsonl` champ `reused_downstream`) ; oubli fréquent de guards/tests ;
  délai d'audit bloquant ; contradictions entre registres de findings ; besoin mesuré de génération auto de guards.
- **Instrument d'alerte précoce (déjà actif)** : `audits/claude/findings_log/FINDINGS_LOG.jsonl` (PR #37).
- **Décision Fred** : ENGINE-12 runtime = **DO_NOT_BUILD** ; fonction conservée et active comme gouvernance ; automatisation dormante.
- **GO_CODE** : ❌ non.
- **Sources / traces** : `specs/CONTRACT_ENGINE_12_COHERENT_EVOLUTION.md` (canonique, reclassé) ; reframe **PR #41** mergé `5923252` ; `AGENTS.md` (règle de non-récurrence).
- **Dernière vérification** : 2026-07-16.

---

## 2. HISTORICAL_DIFFERENTIAL_INFERENCE

- **Identifiant sémantique** : `HISTORICAL_DIFFERENTIAL_INFERENCE` (forme cible : `HISTORICAL_DIFFERENTIAL_CONTEXT_SERVICE`)
- **Anciens numéros / alias** : ENGINE-13 ; `13_HISTORICAL_DIFFERENTIAL_INFERENCE`
- **Fonction** : ne pas repartir de zéro — retrouver une situation historique comparable, vérifier sa provenance,
  comparer cadres anciens/actuels, conserver uniquement les conclusions encore valides, identifier le delta, recalculer
  seulement ce qui a changé, BLOQUER si versions ou preuves incomparables. Formule : `R_t = R_previous_valid + F(delta_C) - I(delta_C)`.
- **Raison de conservation** : mémoire longue, continuité inter-session, reconstruction, réduction du recalcul, cohérence
  dans le temps, exploitation réelle de l'histoire ZMOS.
- **Statut actuel** : **NECESSARY_FOR_TARGET_PRODUCT / IMPLEMENTATION_DEFERRED**
  (réserve d'audit : nécessité pour la cible ASSERTÉE, non encore MESURÉE par benchmark).
- **Emplacement architectural** : **service auxiliaire AVANT pipeline** (`ZMOS historique → service différentiel →
  contexte historique figé → pipeline 00→11`). Jamais une porte après 11.
- **Dépendances** : interface historique ZMOS autoritaire (objets historiques versionnés, transactions closes, cadres
  engagés, provenance, hashes, temporalité, relations entre états, politique de sélection historique).
- **Verrou principal** : **interface historique ZMOS autoritaire (inexistante à ce jour)**.
- **Risques** : réutiliser une conclusion non valable, une version postérieure, ou un historique falsifié. Attaques à
  couvrir : histoire future présentée comme passée · provenance falsifiée · versions incomparables · similarité
  superficielle · conclusion périmée réutilisée · sélection historique biaisée.
- **Conditions de réactivation (mesurables)** : interface ZMOS autoritaire DISPONIBLE **et** coût de recalcul mesuré
  justifiant le service.
- **Action actuelle (Fred)** : contrat à rebaser (supprimer le prérequis void « 00→12 certifié » → « post-cert 00→11 +
  interface ZMOS ») et sortir de la numérotation runtime. **Caveat auditeur** : ne PAS geler le point de contact ZMOS
  tant que l'interface n'existe pas (gel contre producteur fantôme = dette) → viser `READY_EXCEPT_ZMOS_BINDING`.
- **Décision Fred** : construire pour la cible produit, comme service auxiliaire ; code interdit avant nouveau GO Fred.
- **GO_CODE** : ❌ non (bloqué sur interface ZMOS).
- **Sources / traces** : `specs/CONTRACT_ENGINE_13_HISTORICAL_DIFFERENTIAL_INFERENCE.md` (branche `governance/add-engine-13-historical-differential`, commit `47e5e0a`).
- **Dernière vérification** : 2026-07-16.

---

## 3. EXTERNAL_EVIDENCE_AND_FALSIFICATION

- **Identifiant sémantique** : `EXTERNAL_EVIDENCE_AND_FALSIFICATION`
- **Anciens numéros / alias** : ENGINE-14 ; `14_EXTERNAL_EVIDENCE_AND_FALSIFICATION`
- **Fonction** : recherche externe (Internet) automatique + falsification active quand le corpus interne ne permet pas de
  trancher un delta matériel ; collecter preuves favorables ET défavorables, tester des critères de réfutation définis
  AVANT la recherche, conclure avec le niveau réel de preuve.
- **Raison de conservation** : capacité auxiliaire importante pour dépasser les limites du corpus interne (escalade + falsification).
- **Statut actuel** : **IMPORTANT_AUXILIARY_SERVICE / IMPLEMENTATION_DEFERRED**.
- **Emplacement architectural** : **service externe ISOLÉ**, jamais dans le cœur déterministe. Résultats obligatoirement
  FIGÉS, HASHÉS, mis en QUARANTAINE et AUDITÉS avant tout usage ; promotion canon = GO Fred. AVAL de F-025.
- **Dépendances** : F-025 (COMPLEMENTARY_FRAME_DISCOVERY) en amont ; politique de sources versionnée ; politique de falsification versionnée.
- **Verrou principal** : **incompatibilité avec le cœur** — introduit réseau + non-déterminisme. **Aucun accès Internet
  direct depuis le pipeline 00→11.** Le service doit être physiquement isolé du cœur déterministe (invariant `NO_NETWORK`).
- **Risques** : authenticité/spoofing des sources externes (classe `SELF_ASSERTED_PROOF` amplifiée), citation circulaire,
  duplication présentée comme multiple, non-reproductibilité du live web (mitigée par corpus figé + hash + timestamps).
- **Conditions de réactivation (mesurables)** : cas de production RÉCURRENTS de corpus interne insuffisant **et** design
  d'un service externe isolé prouvé (retrieval isolé du cœur, replay sur corpus figé) **et** GO Fred.
- **Décision Fred** : service externe isolé ; jamais dans le pipeline 00→11 ; implémentation différée.
- **GO_CODE** : ❌ non.
- **Sources / traces** : `specs/CONTRACT_ENGINE_14_EXTERNAL_EVIDENCE_AND_FALSIFICATION.md` (branche `governance/add-engine-13-historical-differential`, commit `b273b7f`).
- **Dernière vérification** : 2026-07-16.

---

## Architecture ramifiée future (modes cognitifs) — F-024 → F-029

> Statut commun : **FUTURE_DORMANT · NON_CANONICAL · NO_CODE · POST_CERTIFICATION_00_11 · HORS_CHEMIN_CRITIQUE.**
> Numérotation ENGINE **NON figée** (identifiants sémantiques F-0xx). Aucun GO_CODE implicite. Régime des branches
> RESEARCH/CREATIVE : LLM = GÉNÉRATEUR de candidats ; couche DÉTERMINISTE = VALIDE + FILTRE + TRACE (le LLM ne canonise
> rien, ne produit aucun verdict de vérité). Graphe cible :
>
> ```
> pipeline 00→11 → HISTORICAL_DIFFERENTIAL_INFERENCE → FUTURE_MODE_ROUTER (F-024)
>    ├─ RESEARCH  → COMPLEMENTARY_FRAME_DISCOVERY (F-025) → EXTERNAL_EVIDENCE_AND_FALSIFICATION
>    ├─ STANDARD  → raisonnement standard existant
>    └─ CREATIVE  → CONTROLLED_FRAME_DISPLACEMENT (F-026) → CREATIVE_NON_TRUTH_OUTPUT (terminal isolé)
> branche PRÉSENTATION (non autoritaire) : RESPONSE_FRAME_SELECTION (F-028) → BUILD_FINAL_RESPONSE (F-029) → RELEVANCE_AND_NOISE_FILTER (F-027) → utilisateur
> ```

### 4. F-024 — `FUTURE_MODE_ROUTER`
- **Fonction** : nœud EXPLICITE de routage épistémique (RESEARCH / CREATIVE / STANDARD_REASONING) ; visible, contestable,
  tracé ; propose un mode mais le mode demandé par l'utilisateur PRIME ; ne déduit jamais silencieusement un mode sensible.
- **Raison de conservation** : sans routeur explicite, le changement de régime épistémique serait une fonction cachée.
- **Statut** : FUTURE_DORMANT · **Emplacement** : nœud de routage post-13, amont des branches · **Dépendances** : F-025/F-026 (les branches qu'il route).
- **Verrou** : activation des branches RESEARCH/CREATIVE · **Risques** : déduction silencieuse d'un mode sensible.
- **Réactivation (mesurable)** : décision de construire au moins une branche non-standard (RESEARCH ou CREATIVE).
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : `scratchpad/PIPELINE_BRANCHED_ARCHITECTURE.md` (Option 2, Fred 2026-07-15) ; mémoire `project_futures_registry.md` F-024. · **Dernière vérif** : 2026-07-16.

### 5. F-025 — `FUTURE_COMPLEMENTARY_FRAME_DISCOVERY`
- **Anciens alias** : « ENGINE-15 » (informel, reporté).
- **Fonction** : trouver les cadres complémentaires MANQUANTS + les BONNES questions falsifiables AVANT toute recherche
  (5 critères : introduit un cadre/variable absent · distingue ≥2 hypothèses · produit un test possible · non-redondant ·
  réduit l'incertitude). Verdicts : QUESTION_FALSIFIABLE / DISCRIMINANTE / COMPLEMENTAIRE / REDONDANTE / NON_TESTABLE / HORS_PERIMETRE.
  Intuition = candidat tracé, JAMAIS une conclusion. AMONT de EXTERNAL_EVIDENCE_AND_FALSIFICATION.
- **Raison de conservation** : sans elle, la recherche externe chercherait dans un MAUVAIS espace de questions.
- **Statut** : FUTURE_DORMANT · **Emplacement** : branche RESEARCH, amont de la recherche externe · **Dépendances** : F-024 (routeur) ; branche RESEARCH.
- **Verrou** : activation de la branche RESEARCH · **Risques** : propager une intuition comme vérité ; explosion combinatoire (borner le budget).
- **Réactivation (mesurable)** : cas de production où le raisonnement échoue par CADRE MANQUANT (mesuré).
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : `scratchpad/15_COMPLEMENTARY_FRAME_DISCOVERY.md` ; mémoire F-025. · **Dernière vérif** : 2026-07-16.

### 6. F-026 — `FUTURE_CONTROLLED_FRAME_DISPLACEMENT`
- **Anciens alias** : « ENGINE-16 » (informel, reporté).
- **Fonction** : déplacement/collision VOLONTAIRE de cadres (objet O de son cadre F0 vers F1) pour produire des
  PROPOSITIONS créatives — pas une vérité, des POSSIBILITÉS. Incohérence INTENTIONNELLE, tracée, réversible.
  Productivité RELATIVE à un brief ; validation artistique HUMAINE.
- **Raison de conservation** : capacité créative/divergente distincte du raisonnement scientifique.
- **Statut** : FUTURE_DORMANT · **Emplacement** : branche CREATIVE **TERMINALE ISOLÉE** · **Dépendances** : F-024 (routeur).
- **Verrou** : invariant `CREATIVE_NON_TRUTH` (une sortie créative n'entre JAMAIS dans 05/08, ne modifie jamais les canons,
  ne devient jamais preuve, ne rejoint jamais le journal de vérité sans reclassement explicite).
- **Risques** : rupture d'invariant non déclarée (= bug) ; contamination de la branche scientifique.
- **Réactivation (mesurable)** : demande explicite d'un usage créatif/artistique.
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : `scratchpad/16_CONTROLLED_FRAME_DISPLACEMENT.md` ; mémoire F-026. · **Dernière vérif** : 2026-07-16.

### 7. F-027 — `FUTURE_RELEVANCE_AND_NOISE_FILTER`
- **Fonction** : filtre de SORTIE (dernier nœud avant l'utilisateur) : retire tout élément qui ne modifie NI la
  compréhension NI la décision NI l'action → réponse MINIMALE SUFFISANTE. **Fail-safe INVERSÉ** : au doute → PRÉSERVER
  (le sur-filtrage est le risque n°1). Liste blanche JAMAIS supprimée : sécurité, gouvernance, alerte bloquante, légal,
  consentement, provenance, demande explicite. Statuts : NOISE_REDUCED / MINIMAL_SUFFICIENT / CRITICAL_CONTEXT_PRESERVED / OVERFILTERING_RISK.
- **Raison de conservation** : formalise la loi ZORAN « token economy / minimal suffisant » comme nœud tracé et réversible.
- **Statut** : FUTURE_DORMANT · **Emplacement** : branche PRÉSENTATION, nœud terminal (n'altère jamais le CONTENU décisionnel, seulement le bruit) · **Dépendances** : couche présentation (F-028/F-029) ou indépendante.
- **Verrou** : aucun dur (utilitaire) · **Risques** : SUR-FILTRAGE (supprimer un élément critique) → doit lever `OVERFILTERING_RISK`, jamais silencieux.
- **Réactivation (mesurable)** : sorties trop verbeuses mesurées / coût token présentation mesuré.
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : `scratchpad/FUTURE_RELEVANCE_AND_NOISE_FILTER.md` ; mémoire F-027. · **Dernière vérif** : 2026-07-16.

### 8. F-028 — `FUTURE_RESPONSE_FRAME_SELECTION`
- **Anciens alias** : **ANCIEN moteur 09** (spec 2026-07-14), déplacé par l'ADR-delta (2026-07-15) en branche présentation non autoritaire.
- **Fonction** : sélection du cadre de PRÉSENTATION de la réponse (rendu utilisateur), HORS chaîne décision/action. Ne
  modifie ni verdict, ni décision, ni plan ; ne canonise rien.
- **Raison de conservation** : couche présentation UX ; distincte du STRUCTURED_DECISION (09 actuel).
- **Statut** : FUTURE_DORMANT · **Emplacement** : branche PRÉSENTATION non autoritaire (amont de F-029) · **Dépendances** : sortie de 10/11 (rendu), ADR dédié.
- **Verrou** : ADR dédié + couche présentation · **Risques** : confondre présentation et décision (doit rester non autoritaire).
- **Réactivation (mesurable)** : décision de construire la couche présentation utilisateur.
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : `scratchpad/ADR_DELTA_09_10_PIPELINE.md` ; mémoire F-028. · **Dernière vérif** : 2026-07-16.

### 9. F-029 — `FUTURE_BUILD_FINAL_RESPONSE`
- **Anciens alias** : **ANCIEN moteur 10** (spec 2026-07-14), déplacé par le même ADR-delta en branche présentation non autoritaire.
- **Fonction** : construction de la réponse finale utilisateur (aval de F-028), rendu non autoritaire.
- **Raison de conservation** : couche présentation UX ; distincte de ACTION_ADMISSIBILITY_AND_PLAN (10 actuel).
- **Statut** : FUTURE_DORMANT · **Emplacement** : branche PRÉSENTATION non autoritaire (aval de F-028, amont de F-027) · **Dépendances** : F-028, ADR dédié.
- **Verrou** : idem F-028 · **Risques** : idem F-028.
- **Réactivation (mesurable)** : décision de construire la couche présentation utilisateur.
- **Décision Fred** : conservé, dormant · **GO_CODE** : ❌ · **Sources** : ADR-delta 2026-07-15 ; mémoire F-029. · **Dernière vérif** : 2026-07-16.

---

## Invariants du registre
- Aucune capacité ici n'est un moteur runtime du pipeline certifié 00→11 (qui reste terminal à 11).
- Aucune ne peut être supprimée / renommée / déclarée caduque sans preuve + audit d'impact global + décision Fred.
- Aucun GO_CODE n'est implicite : chaque implémentation exige un GO Fred explicite et scopé.
- Ne pas créer de nouveaux numéros ENGINE ; les identifiants sémantiques (GOV_*, FUTURE_*, F-0xx) font foi.
