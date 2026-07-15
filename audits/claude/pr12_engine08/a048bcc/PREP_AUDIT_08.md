# PRÉPARATION READ-ONLY — AUDIT ENGINE-08 (08_COHERENCE_2)
STATUT : préparation d'audit, NON canonique, AUCUN verdict de certification. Aucune modif PR#12,
aucun commit/branche/merge. HEAD GitHub exact PR#12 = a048bcc1d2d86e5d5f9c773a829ec80545b920ec
(= 37f40b1 + fix CODEX_FIXER « bind fingerprint authority to engine 05 » ; base integration/v2-canonical,
mergeState CLEAN, CI success). Rôle : BUILD+PREPARE_MERGE.
NOTE : **H1 (frontière 04→08, fingerprint) est désormais FERMÉ** par `a048bcc` (finding
GC-08-P1-FINGERPRINT-CHAIN-05-04) : 08 exige `04.canon_referential.fingerprint == 05.coherence.referential_fingerprint`
(str non vides) AVANT validation 06 et authorize_09, sinon BLOCKED. Les risques H2–H7 ci-dessous restent à auditer.

## 1. Rôle de 08 (rappel)
2e passe de cohérence POST-LLM, déterministe, NO_LLM, anti-relecture texte brut, anti-fuite récursive.
Valide la réponse 07 contre 06 (cibles attendues) + 04 (référentiel gelé) + 05 (S_pre), émet verdict
{BLOCKED, REJECT, QUARANTINE, ACCEPT} + authorize_09 (True ssi ACCEPT).

## 2. MATRICE DATAFLOW (preuve → producteur → contrat → sortie influencée → validation existante → trou potentiel → risque transfert 09)

| Preuve | Producteur | Contrat | Sortie influencée | Validation 08 | Trou potentiel | Transfert 09 |
|---|---|---|---|---|---|---|
| status 00→07 | 00-07 | ==PASS | BLOCKED | exact ==PASS | 01/02 non re-validés en profondeur (confiance à 04/06 amont) | faible |
| 07.executed | 07 | ==True | BLOCKED(NOT_EXECUTED) | exact | — | — |
| 04.fingerprint | 04 | str non vide | BLOCKED(FINGERPRINT_MISSING) | non vide str | **NON RECALCULÉ** (05 recalcule le sha256 ; 08 non) | **H1** : 04 tampéré, fp string conservé → 08 fait confiance |
| 04.canons[*].id | 04 | ids gelés | vocab canon_ids → valid 06 + réponse | filtre dict+id str (`or []`) | **skip silencieux** (REX #6) ; divergence vs 05 (fail-closed) | conservateur (fail-closed en aval) |
| 03.analysis[*].operants | 03 | opérants | vocab operant_ids → valid 06 | filtre (`or []`) | skip silencieux idem | conservateur |
| 05.coherence.S | 05 | fini | s_pre → coherence_S recoupé, cinematic, gate delta_s | fini + arrondi 6 | 08 ne recalcule pas S de 05 (confiance) | S_pre faux → ACCEPT/QUARANTINE biaisé |
| 06.authorized | 06 | ==True | BLOCKED | exact | — | — |
| 06.llm_request | 06 | schéma FIGÉ | `expected` → toutes métriques | _validate_request_06 (racine exacte, instruction_kind, pii_policy, fp==04, coherence_S==s_pre, targets schéma, opid `OBJ-\d{4,}`, canons⊆04, operants⊆03, no dup, frames root==cibles, anti-fuite) | très complet ; kind_public str non contrôlé sémantiquement | faible |
| 07.response | 07 (transport LLM) | RESPONSE_STRUCTURED_ANALYSIS_V1 | verdict + métriques | anti-fuite récursif, _schema_ok strict, fp==04, cibles/canons/operants ⊆ attendus | voir H3/H5 (sémantique complétude) | S_post/verdict → 09 |

## 3. Preuves influençant chaque SORTIE
- **BLOCKED** : status 00→07, 07.executed, 04.fingerprint présent, 05.S fini, 06.authorized, 06.request valide.
- **REJECT** : fuite interne réponse ; _schema_ok faux ; response.fingerprint≠04 ; violations CRITIQUES {CANON/OPERANT/FRAME_NOT_EXPECTED, UNKNOWN_TARGET, SCHEMA_INVALID, FINGERPRINT_MISMATCH, PII_LEAK} ; conflicts ; results vides.
- **QUARANTINE** : non critique MAIS (delta_phi<1.0 OU delta_s<0).
- **ACCEPT** : non critique ET delta_phi==1.0 ET delta_s>=0.
- **authorize_09** : == (verdict==ACCEPT).
- **coherence_post** : delta_phi=complete_targets/n_targets ; tension=(violations+conflicts)/n_targets ; sigma=CV(canon_findings_count) ; S_post=β·delta_phi/(1+T+σ).

## 4. RISQUES / CONTRE-EXEMPLES ADVERSARIAUX PROPOSÉS (à jouer par l'auditeur — NON codés ici)
- **H1 — fingerprint 04 non recalculé** : 04 avec canons modifiés mais `fingerprint` string inchangé, 06+réponse échoient le même string → 08 ACCEPTE. (05 recalcule le sha256 ; 08 devrait re-vérifier ou documenter qu'il s'appuie sur 05 — REX #1 « status PASS ≠ preuve ».) **Frontière la plus intéressante à auditer.**
- **H2 — skip silencieux vocab** : 04 `{"id":123}` (id non-str) → écarté silencieusement de canon_ids. Fail-closed en aval (06 bloque si canon manquant) mais asymétrie vs 05 (REX #6).
- **H3 — gate delta_s>=0 mélange deux définitions de S** : S_pre (05 : paires canonisées∩opérants) et S_post (08 : cibles réponse complètes) mesurent des choses différentes ; delta_s>=0 comme condition ACCEPT peut sur-QUARANTINER une réponse parfaite si S_post<S_pre structurellement. **Question de contrat.**
- **H4 — sigma métrique seulement** : n'affecte pas authorize_09 (seuls delta_phi+delta_s gatent) ; distorsion S_post publiée → propagée à 09/cinematic.
- **H5 — reason_code CONSTRAINT_BLOCKED/CANON_CONFLICT comptent l'opérant COUVERT** : seul INSUFFICIENT_EVIDENCE marque incomplet. Une cible peut être « complète » avec des opérants CONSTRAINT_BLOCKED → ACCEPT. **Question de contrat** (intentionnel ?).
- **H6 — transfert 09** : 09 doit revalider `verdict==ACCEPT ⇔ authorize_09` (ne pas faire confiance au flag) + fingerprint chain + ne consommer que l'ensemble ACCEPTé. CE : sortie 08 tampérée `authorize_09=True, verdict=REJECT`.
- **H7 — anti-fuite** : vérifier que `_has_internal_leak` couvre bien clés+valeurs récursif + `\x1f` (semble complet ; à confirmer sur payload imbriqué profond).

## 5. FRONTIÈRES 04→06→07→08 (provenance)
- 05→06 : `06.coherence_S == round(05.S,6)` (GC-08-004) ✓ re-vérifié.
- 04→06 : `06.fingerprint==04`, `canons⊆04 ids`, `operants⊆03` ✓ re-vérifié.
- 06→07→08 : 08 compare la réponse 07 à `expected` (06) — cibles/canons/opérants ⊆ attendus, unicité, fingerprint réponse==04 ✓.
- **Point faible** : 04→08 direct — le fingerprint 04 n'est pas RECALCULÉ par 08 (seulement comparé comme string). Chaîne dépend de 05 ayant recalculé. **À auditer (H1).**

## 6. DÉPENDANCES 08→09
- 09 GATÉ par `authorize_09` (ACCEPT only). REJECT/QUARANTINE/BLOCKED → 09 fail-closed.
- 09 consommera : verdict, coherence_post{delta_phi,tension,sigma,S_post}, cinematic{S_pre,S_post,delta_S,trend}, violations/conflicts/missing/unknown, referential_fingerprint, + probablement 07.response ADMISE + 06.expected.
- 09 DEVRA revalider (ne pas faire confiance) : cohérence verdict↔authorize_09, fingerprint==04, cibles⊆06, anti-fuite, anti-relecture (héritage 08).

## 7. MATRICE NON CANONIQUE — 3 RÔLES POSSIBLES POUR 09 (aucun choisi ; à trancher par Fred)

| Critère | (a) DÉCISION STRUCTURÉE | (b) SYNTHÈSE DE RÉPONSE | (c) SÉLECTION D'ACTION |
|---|---|---|---|
| Fonction | émettre une décision typée (admis/rejeté/à réviser) + justification tracée | agréger la réponse ADMISE en livrable structuré (render_format) | choisir une/des action(s) parmi un ensemble admissible |
| Entrées 08 | verdict + coherence_post + violations | 07.response admise + 06.expected + coherence_post | 07.response + catalogue d'actions + coherence_post |
| Sortie | objet décision {verdict, motifs, S} | document/rendu structuré traçable | action(s) sélectionnée(s) + justification |
| Déterministe | oui (map verdict→décision) | oui (transformation structurée) | oui SI catalogue clos ; risque si ouvert |
| NO_LLM | oui | oui | oui |
| Risque principal | redondance avec 08 (que fait 09 de plus que le verdict ?) | fuite/invention si re-génère du contenu | invention d'action hors catalogue ; provenance action |
| Univers autoritaire | verdict 08 | cibles ADMISES (06/07) | catalogue d'actions défini en amont |
| Adhérence pipeline | prépare 10/11 (trace) | prépare rendu utilisateur | prépare exécution/effet |

## 8. QUESTIONS CONTRACTUELLES RESTANT À TRANCHER (Fred)
Q1. H3 : `delta_s>=0` est-il le bon gate ACCEPT vu que S_pre et S_post mesurent des espaces différents ?
Q2. H5 : CONSTRAINT_BLOCKED / CANON_CONFLICT doivent-ils compter l'opérant comme COUVERT (donc cible complète) ?
Q3. H1 : 08 doit-il RECALCULER le fingerprint 04 (comme 05) ou s'appuyer contractuellement sur 05 ?
Q4. Rôle de 09 (a/b/c ci-dessus) → conditionne tout l'audit 09.
Q5. 09 reçoit-il 07.response admise + 06.expected, ou seulement la sortie de 08 ?
Q6. kind_public transporté : contrôle sémantique requis (anti-PII) au niveau 09 ?
