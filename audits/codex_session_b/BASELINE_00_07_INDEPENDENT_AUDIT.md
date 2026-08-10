TIMESTAMP: 2026-07-15T11:27:49.5647934+02:00

# BASELINE 00→07 — audit indépendant Session B

MISSION_ID: `TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1`
AI_ACTOR_ID: `CODEX_SESSION_B`
GUARD_IDS: `SESSION_B_REPORTS_ONLY_V1`, `SHA_UNIQUE_AUDIT_V1`, `FAIL_CLOSED`, `MULTICADRE_ONLY`

## ÉTAT RÉEL

Phase 1 commencée sur l'interface prioritaire 03→04. Deux findings P1 reproductibles sont ouverts. Verdict initial: `FIX_REQUIRED`.

## OBJET AUDITÉ

- REPOSITORY: `institutia2025-ctrl/zoran-v2`
- PR: `N/A — baseline post-merge`
- BASE_SHA: `6d3f3898a5c7352105f07a03098e7fb22d89899f`
- HEAD_SHA: `6d3f3898a5c7352105f07a03098e7fb22d89899f`
- CI_RUN: `29402762441`, job `87310995624`, conclusion `success`
- AUDIT_TIMESTAMP: `2026-07-15T11:27:49.5647934+02:00`
- TAG: `certified/v2-integration-00-07-hardening` résolu sur le HEAD exact

## CADRES UTILISÉS

Correction technique locale; fail-closed adversarial; composition systémique; sécurité/dataflow; déterminisme/replay; cohérence globale; futur probable; contre-exemple minimal.

## PREUVES

- `CARNET_GATE`: PASS 12/12 avant écriture, politique `REPORTS_AND_EVIDENCE_ONLY`.
- Tests ciblés 03+04: `51 passed in 0.46s`.
- CI GitHub du SHA exact: un check `test`, terminé avec `success`.
- Contre-exemples exécutés localement sur le SHA exact: voir `evidence/03_04_COUNTEREXAMPLES.md`.
- Paquet constructeur complet pour `CSB-03-04-P1-001`: `evidence/CSB-03-04-P1-001_REPRO_PACKAGE.md`, avec enveloppe exacte, script autonome et pytest minimal rouge (`1 failed in 0.13s`).

## FINDINGS

1. `CSB-03-04-P1-001`: 04 accepte un simple `{"status":"PASS"}` pour 03 et produit `PASS`, sans vérifier le composant, la version, l'analyse, les opérés ou la cohérence avec 01/02.
2. `CSB-03-04-P1-002`: des clés/IDs non hashables venant d'un amont déclaré PASS provoquent `TypeError` dans 03 et 04 au lieu d'un blocage déterministe.

## CONTRE-EXEMPLES

- Payload 03 minimal, contradictoire ou usurpé → 04 retourne `PASS` et sélectionne un canon.
- `operant.id=[]` applicable → crash de 03.
- `object_key=[]` → crash de 03 et de 04.

Pour `CSB-03-04-P1-001`, la cause est isolée: le payload 03 n'est pas validé au-delà de `status`, tandis que 04 consomme directement les payloads 01/02 pour construire la sélection canonique.

## AUDIT ASSISTÉ PAR ZORAN

`NON_MESURÉ` à cette phase. Aucun résultat ZORAN n'est utilisé pour le verdict initial.

## DIVERGENCES ZORAN / CODEX

`NON_MESURÉ`.

## COHÉRENCE GLOBALE

Le contrat de composition 03→04 n'est pas défendu. Un statut PASS falsifié ou incomplet traverse la frontière et permet à 04 de reconstruire son résultat depuis 01/02 en ignorant la substance de 03. Cela affaiblit le fail-closed global.

## CINÉMATIQUE

Formule: `S = (beta * delta_phi) / (1 + T + sigma)`.

- Proxies: beta=1 direction conforme; delta_phi=4 propriétés observées sur 8; T=2 findings P1; sigma=1 preuve ZORAN-assisted non mesurée.
- `S(t0)=1.00`; historique comparable antérieur non recevable pour Session B.
- `delta S=NON_MESURÉ`, `dS/dt=NON_MESURÉ`, `d2S/dt2=NON_MESURÉ`.
- Scores descriptifs: `S_code=6/10`, `S_logic=4/10`, `S_security=4/10`, `S_systemic=3/10`, `S_future=3/10`.

## FUTUR PROBABLE

Sans validation d'enveloppe aux frontières, les moteurs 08→11 pourront consommer des PASS structurellement faux ou subir des crashes par objets non hashables. La surface augmente avec chaque composition.

## VERROU PRINCIPAL

Absence de validation structurale et sémantique ferme à la frontière 03→04.

## RISQUE PRINCIPAL

Faux PASS global ou arrêt non contrôlé malgré des étapes amont déclarées PASS.

## VERDICT

`FIX_REQUIRED` — aucun P0 observé dans ce lot initial; deux P1 ouverts.

## PROCHAINE ACTION

Transmettre les contre-exemples au constructeur sans proposer de patch produit, puis poursuivre 04→05 indépendamment sur le même SHA tant qu'il reste figé.

LOW_NOISE
MAX_COHERENCE
TRACEABLE_RUNTIME
MULTICADRE_ONLY
