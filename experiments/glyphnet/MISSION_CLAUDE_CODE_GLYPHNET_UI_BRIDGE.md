# MISSION CLAUDE CODE — GLYPHNET + RACCORDEMENT UI ↔ ZORAN V3

## Autorité
Fred autorise Claude Code à travailler **uniquement dans les clones de travail locaux**. Les dépôts/branches gelés restent lecture seule. Aucun merge, déploiement ou publication sans GO distinct.

## Sources GitHub de cette mission
- Dépôt moteur : `institutia2025-ctrl/zoran-v2`
- Branche de mission : `audit/glyphnet-sovereignty-v1`
- Dossier candidat : `experiments/glyphnet/`

## Objectif général
1. Contre-auditer le candidat GlyphNet v1.1.
2. Ne l'intégrer que s'il conserve strictement les invariants V3.
3. Raccorder ensuite l'interface ZORAN de travail au moteur V3 réel via une frontière API fermée.
4. Ne jamais rebrancher l'UI directement sur un LLM décisionnel.

---

# PHASE A — PRÉFLIGHT LOCAL

Avant toute écriture, relever :
- chemin exact du dépôt moteur local ;
- remote, branche, HEAD, worktree ;
- chemin exact du clone UI de travail ;
- remote, branche, HEAD, worktree ;
- statut du dépôt UI gelé ;
- runtime Python/Node réellement utilisés ;
- services locaux actifs et ports ;
- état exact de `SEMANTIC_DECISION_V1` et du raccord 05B→06 ;
- présence de ZMOS/M7/C2 réellement utilisables en amont/aval.

Si un dépôt de travail est sale avec modifications étrangères non attribuables : `BLOCKED_PRECONDITION`. Ne pas reset/stash/clean.

---

# PHASE B — CONTRE-AUDIT GLYPHNET

Le candidat est **expérimental**. Ne pas accepter les mots « chiffrement », « confidentialité prouvée », « compression prouvée » ou « souveraineté cryptographique ».

Vérifier au minimum :

1. Gate local : une attestation non locale ou absente refuse mécaniquement GlyphNet.
2. Le gate n'est pas un booléen librement fourni par l'appelant final ; la preuve locale doit venir du runtime/configuration gouvernée.
3. Schéma claim fermé : `{type,id,polarite}` uniquement dans cette V1.1.
4. Polarité inconnue => refus, jamais conversion implicite en AFF.
5. Mauvais dialecte => refus explicite, jamais parse partiel.
6. Flux tronqué/corrompu => refus fail-closed.
7. Une rotation archive réellement l'ancien dialecte et ne laisse qu'un actif.
8. Plusieurs dialectes actifs => refus/arbitrage requis.
9. La graine reproductible est TEST-ONLY ; en production, aucun seed prédictible.
10. Un attaquant ayant accès à la table peut décoder : GlyphNet n'est pas un substitut au chiffrement.
11. Mesurer séparément : taille bytes, tokens du modèle local réel, latence encode/decode, coût vs JSON compact / CBOR / MessagePack.
12. Vérifier si le LLM local comprend effectivement le canal. Un LLM général ne connaît pas une bijection aléatoire sans adaptation ; si aucune preuve n'existe, `LLM_GLYPH_UNDERSTANDING = NON_MESURE`.

Exécuter `experiments/glyphnet/test_falsificateur_souverainete.py` puis ajouter seulement les falsificateurs justifiés par des défauts réellement reproduits.

### Condition d'intégration GlyphNet
`APPROVED_FOR_EXPERIMENTAL_WIRING` seulement si :
- tests verts ;
- aucune dérive sémantique ;
- aucune modification de verdict/claim/modalité ;
- local attestation gouvernée ;
- rotation/replay conformes à ZMOS réel ;
- limites documentées.

Sinon : `FIX_REQUIRED` et arrêt de l'intégration.

### Placement autorisé
GlyphNet est un **codec périphérique** autour du `CLAIM_SET`/verbaliseur local. Il n'est pas :
- un moteur A/B/C ;
- une autorité ;
- un substitut à ZMOS/M7/C2 ;
- un moyen de modifier les décisions.

---

# PHASE C — RACCORDEMENT UI ↔ ZORAN V3

## Architecture cible

```text
UI locale
  ↓ POST /zoran/run
A — STRUCTURATION
  ↓
B — Ω∞ COHERENCE CORE
  ↓
C1 — DÉCISION / PLAN
  ↓
CLAIM_SET scellé
  ↓
D — verbaliseur confiné (local si GlyphNet activé)
  ↓
C2 — autorisation d'action éventuelle
  ↓
E — ZMOS / trace
  ↓
réponse structurée UI
```

## Interdit critique
Ne pas raccorder l'UI au vieux `runtime.py` 00→11 comme autorité finale si Gemma/LLM y décide encore une partie du sens. Le LLM ne peut être qu'un périphérique de formulation.

## Contrat API minimal
Créer une frontière locale fermée, par exemple `POST /zoran/run`.

### Entrée
- `request_id`
- `question_raw`
- `user_context_ref` (référence, pas mémoire brute)
- `ui_mode`
- `requested_action` éventuelle

### Sortie
- `request_id`
- `status`: `PASS | FAIL | NON_MESURE | REFUSED`
- `semantic_decision_hash`
- `claim_set_hash`
- `local_coherence`
- `general_coherence`
- `surface_text`
- `trace_id`
- `action_state`: `NONE | PROPOSED | AUTHORIZED | REFUSED`
- `errors[]` structurées

Aucune donnée UI ne doit pouvoir injecter directement `PASS`, un hash, une autorisation ou un verdict.

## Fail-close
- moteur indisponible => UI affiche indisponibilité, pas fallback vers un LLM libre ;
- décision NON_MESURE => UI affiche NON_MESURE ;
- verbaliseur invalide => refus de surface, décision sémantique inchangée ;
- action sans C2 => jamais exécutée ;
- timeout => trace structurée, pas décision inventée.

## Tests E2E minimaux
1. question normale PASS ;
2. NON_MESURE rendu tel quel ;
3. contradiction globale => FAIL/REFUSED ;
4. backend arrêté => aucun fallback LLM ;
5. surface LLM ajoute un claim => rejet ;
6. même entrée/config => mêmes hashes de décision/claims ;
7. action proposée sans autorisation => non exécutée ;
8. action autorisée => trace ZMOS ;
9. GlyphNet cloud/non-local demandé => refus du codec, fonctionnement clair standard conservé ;
10. GlyphNet local activé => décision identique avec/sans codec.

---

# PHASE D — UI

Dans le clone UI de travail uniquement :
- raccorder `app/page.tsx` / couche réseau au endpoint local ;
- conserver l'expérience visuelle existante ;
- afficher PASS/FAIL/NON_MESURE sans inventer de score ;
- rattacher chaque message à `request_id/trace_id` ;
- ne jamais exposer la table GlyphNet ;
- ne jamais afficher les clés API ou secrets ;
- ne pas toucher au dépôt UI gelé.

---

# PREUVES TERMINALES

Produire un rapport avec :
- dépôt/branche/SHA moteur ;
- dépôt/branche/SHA UI ;
- fichiers modifiés ;
- commandes exactes ;
- tests GlyphNet ;
- tests moteur ;
- tests UI ;
- tests E2E ;
- hashes de décision avec/sans GlyphNet ;
- preuve d'invariance décisionnelle ;
- preuve dépôt UI gelé inchangé ;
- risques résiduels ;
- verdict unique.

## Verdicts autorisés
- `DONE — READY_FOR_EXTERNAL_REVIEW`
- `FIX_REQUIRED`
- `BLOCKED_PRECONDITION`
- `BLOCKED_MAJOR`

## Git
Commits locaux sur branches de travail autorisés. Aucun merge/déploiement. Push uniquement sur branche d'audit/travail si nécessaire pour contre-audit ; jamais sur une branche gelée.
