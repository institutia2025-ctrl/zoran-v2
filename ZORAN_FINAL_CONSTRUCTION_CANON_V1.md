# ZORAN — PLAN CANONIQUE FINAL DE CONSTRUCTION V1

**Statut : VERROUILLÉ — AUCUNE AUTRE ARCHITECTURE AUTORISÉE**  
**Date de verrouillage : 2026-08-21**  
**Autorité : Fred**  
**Branche mémoire/canon : `codex/zoran-final-canon-v1`**

## 1. Règle absolue

Ce document est l'unique plan de construction à finaliser. Toute ancienne architecture, tout ancien runtime ou toute nouvelle proposition ne peut être utilisé que comme **donneur de brique locale** si son gain est démontré face à ce plan. Il est interdit de réactiver l'ancienne chaîne 00→11 en bloc.

Aucun chat, agent, audit ou session ne doit :
- réinventer l'architecture ;
- remplacer K3 comme noyau logique ;
- laisser un LLM décider d'un fait, cadre, relation, contradiction, action, refus ou niveau de certitude ;
- modifier l'ordre de construction sans défaut bloquant démontré et GO explicite de Fred ;
- considérer l'absence de mémoire conversationnelle comme une excuse pour reconstruire le plan.

## 2. Objectif produit final

Zoran doit :
1. **comprendre** une phrase simple hors ligne ;
2. **répondre** hors ligne depuis son corpus local et ZMOS ;
3. **parler et écouter** via STT/TTS sans donner d'autorité sémantique à la voix ;
4. **chercher sur Internet** quand une donnée actuelle/externe est requise ;
5. transformer toute donnée externe en fait candidat gouverné avant usage ;
6. décider avec un cœur **100 % déterministe** ;
7. utiliser un LLM, s'il existe, uniquement comme verbaliseur facultatif ;
8. produire PASS / FAIL / NON_MESURÉ sans inventer une réponse quand la preuve manque.

## 3. Architecture canonique

```text
MICRO / TEXTE
    ↓
question_raw
    ↓
NORMALISATION DÉTERMINISTE
Unicode / NFC / casse contrôlée
    ↓
NLP.js + ZTRACE
intention / objets / claims / négation / temporalité / modalité
    ↓
BGE-M3 LOCAL
retrieval sémantique de candidats uniquement — jamais autorité
    ↓
CORPUS LOCAL + INDEX ZMOS
    ↓
OBJETS / FAITS / RELATIONS / PROVENANCE
    ↓
INSTANCIATION DES CADRES
    ↓
K3 v1.1
PASS / FAIL / NON_MESURÉ
NON / ET / OU / IMPLIQUE / DIFFÉRENCE
    ↓
JAUGE β ΔΦ T σ seulement si mesurée
    ↓
COHÉRENCE MULTICADRE
locale + générale
    ↓
CONTRADICTIONS / TEMPORALITÉ / CAUSALITÉ
    ↓
BOUSSOLE / CHOIX
    ↓
MPCR / FUTUR probable borné
    ↓
SEMANTIC_DECISION
sens complet scellé avant verbalisation
    ↓
AMYGDALE
VETO / freeze / rollback / refus
    ↓
VERBALISEUR DÉTERMINISTE
    ↓
TEXTE + TTS
    ↓
UI ZORAN
    ↓
MÉMOIRE ZMOS
```

### Internet

```text
Question
→ détection du besoin de donnée externe
→ recherche/acquisition
→ source + URL + date + empreinte
→ extraction
→ fait candidat
→ provenance + contradiction + K3
→ ZMOS
→ même moteur déterministe que hors ligne
```

Internet apporte des **candidats et des faits**, jamais une décision.

## 4. Rôle exact des briques

| Brique | S_OBJECTIF /100 | Construction de référence | Statut canonique |
|---|---:|---:|---|
| Normalisation Unicode / question_raw | 99 | 90 % | CORE |
| NLP.js français | 94 | 85 % | CORE |
| ZTRACE objets/claims/négation/temps/modalité | 93 | 72 % | CORE |
| BGE-M3 local retrieval | 94 | 30 % | CORE À BRANCHER |
| Recherche lexicale/exacte secours | 88 | 75 % | CORE OFFLINE |
| Corpus local gouverné | 99 | 30 % | BLOQUANT |
| Index sémantique local | 97 | 30 % | BLOQUANT |
| Objets ZMOS | 98 | 75 % | CORE |
| Reconstruction ZMOS attestée | 99 | 75 % | CORE |
| Mémoire gouvernée V2 | 98 | 75 % | CORE |
| Sélection active ZMOS | 96 | 70 % | CORE |
| Persistance / writer / reprise | 95 | 72 % | CORE |
| Objectification + provenance | 97 | 65 % | CORE |
| Cadres / instanciation | 96 | 62 % | À RASSEMBLER |
| Frame contamination V2 | 92 | 50 % | GREFFE |
| K3 v1.1 | 100 | 90 % | NOYAU |
| Négation K3 | 99 | 90 % | NOYAU |
| ET / OU K3 | 100 | 90 % | NOYAU |
| IMPLIQUE / DIFFÉRENCE | 95 | 88 % | NOYAU |
| Jauge β ΔΦ T σ | 92 | 45 % | À CALIBRER |
| Cohérence locale | 98 | 72 % | CORE |
| Cohérence générale / multicadre | 100 | 58 % | BLOQUANT |
| Contradictions | 99 | 65 % | CORE À FERMER |
| Temporalité | 94 | 45 % | À FERMER |
| Causalité bornée | 96 | 42 % | À FERMER |
| Boussole / choix | 96 | 50 % | À RASSEMBLER |
| Flot | 88 | 40 % | P1 |
| MPCR / futur borné | 93 | 32 % | P1 |
| SEMANTIC_DECISION | 99 | 68 % historique | CORE |
| Scellement / empreinte | 98 | 75 % | CORE |
| Verbaliseur déterministe | 96 | 58 % | CORE À ENRICHIR |
| Amygdale concept/processus | 98 | 30 % | CORE SÉCURITÉ |
| Veto / freeze Amygdale | 99 | 35 % | CORE |
| Rollback Amygdale | 95 | 30 % | CORE |
| STT local | 92 | 50 % | À RACCORDER |
| Wake word Zoran | 84 | 70 % | CONSERVER |
| TTS | 88 | 60 % | À LOCALISER/GELER |
| Acquisition Internet | 98 | 40 % | CORE ONLINE |
| Vérification source | 100 | 40 % | BLOQUANT ONLINE |
| UI visuelle actuelle | 97 | 88 % | CONSERVER |
| NON_MESURÉ visible UI | 98 | 90 % | CORE UI |
| IDs / provenance UI | 96 | 90 % | CORE UI |
| Forum IA | 51 | 75 % | PÉRIPHÉRIQUE |
| Backend LLM actuel comme cœur | 9 | existant | REJET CORE |
| Gemma comme raisonneur | 0 | historique | REJET ABSOLU |
| LLM comme verbaliseur facultatif | 28 | optionnel | HORS CORE |
| ZNS neuronal | 37 | laboratoire | NE PAS GREFFER |
| Ancienne chaîne 00→11 en bloc | 6 | historique | REJET |
| Fonctions locales utiles de 00→11 | 74 | disponibles | DONNEURS UNIQUEMENT |

## 5. Mesure de construction gelée au démarrage

État de référence au verrouillage :

| Porte | Poids | Construction |
|---|---:|---:|
| Compréhension phrases simples offline | 15 | 82 % |
| Corpus + retrieval sémantique local | 15 | 35 % |
| K3 + décision déterministe | 15 | 84 % |
| ZMOS + mémoire persistante | 10 | 72 % |
| Réponse naturelle sans LLM | 10 | 58 % |
| Parole STT + TTS | 8 | 68 % |
| Internet + provenance | 10 | 40 % |
| UI finale | 7 | 88 % |
| Amygdale + sécurité | 5 | 30 % |
| Chaîne E2E + QA réelle | 5 | 30 % |

**Construction globale de référence : 62 %**  
**Reste : 38 %**  
**Incertitude initiale : ±6 points**

Cette jauge n'est pas la formule scientifique S. `S = (β × ΔΦ)/(1+T+σ)` reste NON_MESURÉ tant que les proxys ne sont pas calibrés sur un protocole gelé.

## 6. Ordre de construction verrouillé

1. BGE-M3
2. corpus / index
3. NLP.js + ZTRACE
4. ZMOS
5. cadres
6. K3
7. cohérence multicadre
8. semantic decision
9. verbaliseur
10. voix
11. Internet
12. UI
13. Amygdale
14. test intégral

Aucune étape ne doit être sautée silencieusement. Une brique déjà avancée peut être conservée, mais son raccord à la chaîne canonique doit être prouvé.

## 7. Plan de chats de référence

Estimation centrale : **10 chats de travail**, fourchette **8–12**.

| Chat | Porte terminale |
|---:|---|
| 1 | Cartographie exacte + versions les plus avancées de chaque brique |
| 2 | BGE-M3 local persistant + index + latence + déterminisme |
| 3 | NLP.js + ZTRACE + BGE-M3 → objets ZMOS |
| 4 | ZMOS canonique + mémoire + reprise + provenance |
| 5 | Cadres + K3 + négation + contradiction + cohérence locale/générale |
| 6 | Temporalité + causalité + boussole + SEMANTIC_DECISION |
| 7 | Verbaliseur déterministe naturel + formes de réponse |
| 8 | Micro/STT + TTS + UI conforme |
| 9 | Internet gouverné + sources + objectification |
| 10 | E2E offline + online + voix + mémoire + tests + gel SHA |

Un chat n'est jamais clos sur du simple texte : il doit produire un état vérifiable `PASS / FAIL / NON_MESURÉ`, avec coordonnées de preuve quand elles existent.

## 8. Protocole mémoire obligatoire à chaque chat

Au début de **chaque** chat Zoran :
1. lire ce canon ;
2. lire `zmos_memory/ZORAN_FINAL_PLAN_V1.zmos.json` ;
3. lire `zmos_memory/ZORAN_BUILD_TRACKER_V1.json` ;
4. effectuer un audit 360° des acquis, manques, contradictions, versions, SHA et tests disponibles ;
5. identifier l'étape du plan en cours ;
6. refuser toute dérive vers une architecture alternative.

À la fin de **chaque** chat :
1. consigner le delta réel ;
2. mettre à jour le pourcentage de construction uniquement avec preuve ;
3. enregistrer les briques PASS / FAIL / NON_MESURÉ ;
4. inscrire le prochain verrou exact ;
5. écrire les coordonnées dépôt / branche / SHA / artefacts / tests si elles existent ;
6. enregistrer les inconnus ;
7. refaire un audit 360° avant clôture ;
8. préserver le plan inchangé.

## 9. Invariants de mémoire

- Aucun fait de construction ne doit dépendre uniquement du contexte conversationnel.
- Le contexte de chat est un cache ; **ZMOS/canon est l'autorité persistante**.
- Toute information non écrite dans la mémoire Zoran après un changement significatif est considérée comme `NON_PERSISTÉE`.
- Aucun pourcentage ne monte sans preuve.
- Aucun ancien résultat ne devient courant par simple récence d'un message.
- Toute divergence entre chat et mémoire canonique se résout en faveur de la mémoire canonique, sauf GO explicite de Fred.

## 10. Condition de fin

Zoran est finalisé uniquement si la même chaîne prouve :
- compréhension offline ;
- retrieval local ;
- mémoire ZMOS ;
- K3 et cohérence multicadre ;
- décision sémantique avant verbalisation ;
- réponse naturelle sans raisonnement LLM ;
- écoute et parole ;
- Internet gouverné ;
- UI ;
- Amygdale/veto ;
- E2E reproductible ;
- absence de voie probabiliste décisionnelle.

Tant qu'une porte reste NON_MESURÉE ou FAIL, le système n'est pas déclaré terminé.
