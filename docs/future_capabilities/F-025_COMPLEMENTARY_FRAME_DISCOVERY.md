# F-025 — FUTURE_COMPLEMENTARY_FRAME_DISCOVERY — fiche capacité durable

- **Identifiant sémantique** : `FUTURE_COMPLEMENTARY_FRAME_DISCOVERY`
- **Anciens numéros / alias** : F-025 ; **« 15 » (informel, reporté)**. Composante « découverte/prolongement de cadres » du souvenir « 17 ».
- **Description fonctionnelle** : étant donné un problème P et ses cadres présents F(P), produire les CADRES COMPLÉMENTAIRES
  MANQUANTS + les BONNES questions falsifiables AVANT toute recherche. Ne cherche pas la réponse : cherche le bon ESPACE DE
  QUESTIONS. 5 critères de sélection d'une question (introduit un cadre/variable absent · distingue ≥2 hypothèses · produit un
  test possible · non-redondante · réduit l'incertitude). Intuition = candidat tracé, JAMAIS une conclusion. **Découverte INTERNE**
  (LLM génère / déterministe valide-filtre-trace) ; **pas** la recherche Internet (celle-ci = EXTERNAL_EVIDENCE, aval).
- **Raison de conservation** : sans elle, la recherche externe chercherait dans un MAUVAIS espace de questions.
- **Statut** : `FUTURE_DORMANT · NON_CANONICAL · NO_CODE · POST_CERTIFICATION_00_11 · HORS_CHEMIN_CRITIQUE`.
- **Position architecturale** : branche RESEARCH, AMONT de EXTERNAL_EVIDENCE_AND_FALSIFICATION. **Fonctionnellement AVANT le 14** (d'où la confusion « 15 après 14 »).
- **Inputs prévus** : problème + cadres présents F(P) + angles morts.
- **Outputs prévus** : cadres complémentaires candidats + questions (statuts `QUESTION_FALSIFIABLE / DISCRIMINANTE /
  COMPLEMENTAIRE / REDONDANTE / NON_TESTABLE / HORS_PERIMETRE`) priorisées et tracées.
- **Dépendances** : F-024 (routeur, RESEARCH) ; branche RESEARCH.
- **Incompatibilités** : ne propage pas une intuition vers 05/08 sans hypothèse→falsification ; non-déterminisme gouverné
  (le LLM ne canonise rien, ne verdicte pas).
- **Risques** : propager une intuition comme vérité ; explosion combinatoire (borner le budget cadres/questions).
- **Conditions mesurables de réactivation** : cas de production où le raisonnement échoue par CADRE MANQUANT (mesuré).
- **Interdictions** : aucun code sans GO Fred ; intuition ≠ conclusion ; questions non testables non retenues comme hypothèses.
- **GO_CODE actuel** : ❌ non.
- **Sources historiques** : `scratchpad/15_COMPLEMENTARY_FRAME_DISCOVERY.md` (2026-07-15 15:27) ; mémoire F-025.
- **Dernière vérification** : 2026-07-16.
- **Relation avec les autres capacités** : aval de F-024 ; **AMONT de EXTERNAL_EVIDENCE_AND_FALSIFICATION (14)**. Distincte de la recherche Internet.
