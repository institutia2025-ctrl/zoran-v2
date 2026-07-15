# CONTRACT ENGINE-14 — EXTERNAL EVIDENCE AND FALSIFICATION

## Statut

`SPEC_ONLY` — aucun code avant certification des moteurs `00→13`, validation externe du présent contrat et GO explicite de Fred.

## Identité

```text
COMPONENT_ID = 14_EXTERNAL_EVIDENCE_AND_FALSIFICATION
```

Nom français : **Moteur de preuve externe et de falsification**.

## Finalité

ENGINE-14 prend le relais lorsque ENGINE-13 a reconnu un cadre historique, identifié un delta matériel et constaté que le corpus interne ne contient aucun objet autoritaire suffisant pour valider ou réfuter ce delta.

Le moteur déclenche alors automatiquement une recherche externe, collecte des preuves favorables et défavorables, tente activement de falsifier les hypothèses concurrentes et renvoie une conclusion bornée par le niveau réel de preuve.

L'utilisateur n'a pas à demander séparément une recherche Internet. L'escalade externe fait partie du comportement par défaut.

## Déclenchement canonique

ENGINE-14 s'exécute lorsque les conditions suivantes sont réunies :

```text
historical_frame_identified = true
delta_C_non_empty = true
internal_authoritative_evidence_sufficient = false
delta_material_for_answer = true
```

Dans l'usage ZORAN, la recherche externe est automatique par défaut. L'absence de demande explicite de l'utilisateur ne constitue jamais un veto.

## Chaîne canonique

```text
cadre historique reconnu
→ delta détecté
→ corpus interne insuffisant
→ formulation des hypothèses
→ critères de réfutation définis avant recherche
→ recherche externe automatique
→ qualification des sources
→ collecte de preuves favorables
→ recherche active de contre-preuves
→ tentative de falsification
→ verdict borné
→ proposition d'intégration en quarantaine
```

## Principe de falsification

Le moteur ne doit jamais fonctionner selon la logique :

```text
une source confirme H
→ H est vraie
```

Il doit fonctionner selon la logique :

```text
hypothèse H
→ définir ce qui réfuterait H
→ rechercher des preuves pour H
→ rechercher des preuves contre H
→ tester les critères de réfutation
→ comparer provenance, autorité, date et contradictions
→ conclure avec le niveau réel de preuve
```

Les critères de réfutation doivent être enregistrés avant la collecte des résultats afin d'éviter leur ajustement rétroactif.

## Entrées autoritaires

- `HISTORICAL_DIFFERENTIAL_RESULT` produit par ENGINE-13 ;
- `CURRENT_FRAME_OBJECT` ;
- `DELTA_OBJECT` ;
- `INTERNAL_EVIDENCE_STATUS_OBJECT` ;
- `EXTERNAL_SOURCE_POLICY_OBJECT` versionné ;
- `FALSIFICATION_POLICY_OBJECT` versionné ;
- état temporel de la recherche.

## Recherche externe

Internet est une source de candidats et de preuves externes, jamais une autorité unique indifférenciée.

Le moteur doit pouvoir interroger notamment :

- sources primaires officielles ;
- textes réglementaires et normes ;
- publications scientifiques ;
- documentation technique officielle ;
- données publiques et registres ;
- sources secondaires reconnues lorsque les sources primaires sont absentes ;
- contre-sources pertinentes représentant les hypothèses concurrentes.

## Qualification des sources

Chaque source doit exposer au minimum :

```text
source_id
source_type
authority
publisher_or_author
publication_date
retrieval_timestamp
content_hash
claim_scope
supports_hypotheses
contradicts_hypotheses
known_limitations
```

Une source sans provenance exploitable ne peut pas soutenir un verdict positif.

## Verdicts

```text
EXTERNALLY_SUPPORTED
EXTERNALLY_REFUTED
PARTIALLY_SUPPORTED
CONFLICTING_EXTERNAL_EVIDENCE
NO_RELIABLE_EXTERNAL_EVIDENCE
FALSIFICATION_PASSED
FALSIFICATION_FAILED
INDETERMINATE
BLOCKED
```

### Interprétation

- `EXTERNALLY_SUPPORTED` : preuves externes fiables soutiennent le delta après tentative de réfutation non concluante ;
- `EXTERNALLY_REFUTED` : au moins un critère de réfutation déterminant est satisfait ;
- `PARTIALLY_SUPPORTED` : une partie seulement du delta est soutenue ;
- `CONFLICTING_EXTERNAL_EVIDENCE` : sources fiables incompatibles non départagées ;
- `NO_RELIABLE_EXTERNAL_EVIDENCE` : recherche exécutée sans source recevable ;
- `INDETERMINATE` : données ou règles insuffisantes pour conclure ;
- `BLOCKED` : entrée, politique, provenance ou exécution malformée.

## Sortie canonique minimale

```json
{
  "component": "14_EXTERNAL_EVIDENCE_AND_FALSIFICATION",
  "status": "PASS",
  "trigger": {
    "historical_frame_identified": true,
    "delta_unresolved": true,
    "internal_authoritative_evidence_sufficient": false,
    "external_search_automatic": true
  },
  "hypotheses": [],
  "falsification_criteria": [],
  "external_evidence": {
    "supporting": [],
    "contradicting": [],
    "source_assessments": [],
    "unresolved_conflicts": []
  },
  "falsification": {
    "attempted": true,
    "result": "INDETERMINATE"
  },
  "verdict": "INDETERMINATE",
  "answer_effect": "AUGMENT_HISTORICAL_RESPONSE",
  "corpus_action": "PROPOSE_QUARANTINE_OBJECT"
}
```

## Intégration au corpus

Aucune information trouvée sur Internet ne devient automatiquement canonique.

Cycle obligatoire :

```text
EXTERNAL_CANDIDATE
→ PROVENANCE_VERIFIED
→ FALSIFICATION_ATTEMPTED
→ QUARANTINE
→ REPLAY
→ EXTERNAL_AUDIT
→ CANON_PROPOSAL
```

Fred reste l'autorité de promotion canonique.

## Règles fail-closed

- aucune recherche confirmatoire seule ;
- aucun verdict positif sans tentative documentée de contre-preuve ;
- aucun score global ne compense une source autoritaire réfutante ;
- aucune source sans date ou provenance suffisante ne devient autoritaire ;
- aucune intégration automatique au canon ;
- aucune réécriture rétroactive des critères de falsification ;
- aucune certitude artificielle lorsque les sources fiables divergent ;
- aucune demande supplémentaire à l'utilisateur uniquement pour autoriser une recherche Internet ordinaire.

## Tests adversariaux minimaux

- une seule source confirmatoire disponible ;
- source officielle contredite par une publication plus récente ;
- contenu dupliqué par plusieurs sites présenté comme plusieurs preuves ;
- source sans date ;
- source citant circulairement une autre source ;
- preuve favorable forte et contre-preuve faible ;
- contre-preuve autoritaire satisfaisant un critère de réfutation ;
- hypothèses concurrentes non exclusives ;
- changement de résultat après modification rétroactive des critères ;
- corpus interne suffisant mais recherche externe tout de même déclenchée ;
- aucune source fiable ;
- accès externe en échec technique ;
- donnée externe proposée directement au canon ;
- recherche produisant une conclusion hors du périmètre du delta.

## Critères de certification

ENGINE-14 est certifiable uniquement si :

- le déclenchement automatique est déterministe ;
- les hypothèses et critères de réfutation précèdent la recherche ;
- les preuves favorables et défavorables sont recherchées ;
- la provenance et la temporalité sont traçables ;
- les verdicts sont reproductibles sur un corpus figé ;
- les sources dupliquées ne gonflent pas artificiellement la preuve ;
- une réfutation autoritaire ne peut pas être masquée par une majorité de sources faibles ;
- aucune preuve externe n'entre directement dans le canon ;
- la réponse finale distingue faits externes, contradictions, incertitudes et inférences.

## Position

```text
12_COHERENT_EVOLUTION
→ 13_HISTORICAL_DIFFERENTIAL_INFERENCE
→ 14_EXTERNAL_EVIDENCE_AND_FALSIFICATION
→ EXTERNAL_INDEPENDENT_CERTIFICATION_BY_CLAUDE
```

ENGINE-13 calcule ce qui a changé par rapport à l'histoire. ENGINE-14 recherche automatiquement ce que le corpus interne ne permet pas de trancher et tente de le falsifier.
