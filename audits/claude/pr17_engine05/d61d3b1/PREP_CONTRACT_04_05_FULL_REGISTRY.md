# PREP_CONTRACT_04_05_FULL_REGISTRY — analyse d'impact READ-ONLY
Finding : GC-05-P1-CANON-REGISTRY-COMPLETENESS (reproduit par Codex Fixer sur 24c64e5c89b8737b6b8ac87e1fb254dcb2ea7cb4).
STATUT : analyse d'impact NON canonique. AUCUN code, AUCUNE branche produit, AUCUN patch, AUCUNE modif de 05.
Rôle : BUILD+PREPARE_MERGE (préparation). Décision d'architecture = Fred.

## 0. Cause racine (confirmée par lecture du code)
- `CANONS.yaml` (racine dépôt) = registre COMPLET, 3 canons V1 (CANON_CONSTRAINT p40 / CANON_STRUCTURE p30 / CANON_INTENT p20). Champs : id, applies_to_frames, applies_to_kinds, priority. **Aucun `version`, aucun `hash`.**
- `load_canon_registry()` (canon_determination.py:369, fail-closed→[]) appelé SEULEMENT par `04.main()`.
- 04 reçoit le registre COMPLET, calcule les canons APPLICABLES par (objet,frame) via `_applicable_canons`, et GÈLE dans sa sortie UNIQUEMENT le sous-référentiel appliqué (`canon_referential.canons` = frozen_list) + `priorities`. Le fingerprint 04 ne couvre QUE ce sous-référentiel.
- 05 reçoit `envelope(00→04)` — donc la sortie DÉJÀ FILTRÉE de 04. 05 reconstruit conflits depuis `canons_selected` + priorités gelées, mais si un canon applicable est retiré SIMULTANÉMENT de `canons_selected` ET du sous-référentiel, la reconstruction reste auto-cohérente → **05 n'a aucune vérité indépendante pour détecter l'omission**. La couverture CSB-PROV-P1-004 vérifie l'univers de PAIRES vs 02, pas la complétude des CANONS applicables par paire.

## 1. Racine de confiance du registre complet
- Fichier : `CANONS.yaml` (racine). Loader : `load_canon_registry()` (impur fin, fail-closed). Normalisation : `_normalize_registry` (dédup par id, priorité max), `_clean_canon`, `_applicable_canons` (filtre frame/kind, tri). **Pas d'objet versionné, pas de hash de registre complet, pas d'orchestrateur.**
- Kinds des objets : produits par 01 (`object_discovery.objects[].kind`) — présents dans envelope(00→04). Frames : 02 (`object_frame_map`). Donc 05 A DÉJÀ accès aux kinds (01) et frames (02) nécessaires pour re-dériver l'applicabilité — il ne lui manque QUE le registre complet + la normalisation partagée.

## 2. Contrat 04 (état actuel + évolution nécessaire)
- Actuel : `run_canon_determination(envelope, registry)` ; sortie = canons_selected, canon_referential{fingerprint(sous-réf), canons(appliqués), priorities}, conflicts, uncanonized, resource_estimate.
- Évolution : engager le registre COMPLET normalisé (séparer explicitement **registre complet** vs **sous-référentiel appliqué**). Champs de sortie candidats : `full_registry_fingerprint` (sha256 du registre complet normalisé), `registry_version`. Normalisation à EXTRAIRE dans un module partagé (source unique).

## 3. Contrat 05 (évolution nécessaire)
- Entrée INDÉPENDANTE du registre complet (pas via la sortie de 04 — sinon pas d'autorité indépendante).
- Recalcul du fingerprint du registre COMPLET (comme 05 recalcule déjà le fingerprint du sous-réf).
- Normalisation PARTAGÉE avec 04 (même module) → pas de divergence.
- Re-dérivation exacte, pour chaque paire (object_key kind@01, frame@02) : canons applicables attendus → reconstruction EXACTE de `canons_selected`, `uncanonized`, `conflicts` ; comparaison stricte à la sortie 04 → détecte omission/invention/altération. Fail-closed → BLOCKED(CD04).

## 4. Call sites (impact réel)
- `run_coherence_engine` : appelé UNIQUEMENT par `tests/test_coherence_engine.py` (+ `main(envelope)`). **Aucun orchestrateur de production.**
- 06/07/08 consomment la SORTIE de 05, ne l'APPELLENT pas → un changement de signature de 05 ne les casse pas (schéma de sortie inchangé, sauf ajout optionnel `full_registry_fingerprint`).
- Migration = fixtures de test 05 + `main` de 05. Surface PETITE.

## 5. Risques
- **Double source de vérité (n°1)** : 04 et 05 dérivent l'applicabilité → RISQUE de divergence. Mitigation OBLIGATOIRE : normalisation + applicabilité dans UN SEUL module (`zoran_v2/canon_registry.py`) importé par 04 ET 05.
- Divergence de normalisation : idem (module unique).
- Dépendance fichier cachée : si 05 charge CANONS.yaml lui-même (dans son main), même schéma que 04 — la fonction PURE reste pure (registre en argument), l'impur est confiné au main.
- Couplage excessif : 05 se couple au registre + kinds(01) + frames(02) (déjà consomme 02). Modéré.
- Rupture de pureté : évitée si registre passé en ARGUMENT.
- Compatibilité anciens payloads : la signature de 05 change (ajout d'un argument/entrée) → migration des fixtures ; pas de compat rétro sur l'ancienne signature.
- Dette transférée : nulle si module partagé ; le changement RÉDUIT la dette (ferme le trou de complétude).

## 6. Deux architectures

### Arch A — Registre complet injecté DIRECTEMENT dans 05
`run_coherence_engine(envelope, registry)` (2e argument, comme 04). `05.main` charge `load_canon_registry()` indépendamment. 05 normalise (module partagé), re-dérive l'applicabilité par paire (kind@01, frame@02), reconstruit canons_selected/uncanonized/conflicts et compare à 04.
- **Indépendance** : VRAIE (05 lit la même racine de confiance que 04, indépendamment).
- + : surface minimale (pas d'orchestrateur à créer) ; pureté préservée (registre en arg).
- − : signature de 05 change → migration fixtures/main ; nécessite le module de normalisation partagé (sinon divergence).

### Arch B — Objet d'engagement/version fourni par l'orchestrateur
Introduire un `RegistryCommitment` versionné {registry_version, full_registry_fingerprint, normalized_full_registry} construit à la racine (loader/orchestrateur) et fourni à 04 ET 05 indépendamment. 05 vérifie la sortie 04 contre le MÊME engagement.
- **Indépendance** : VRAIE (racine unique versionnée, ni 04 ni 05 ne la possèdent seuls).
- + : versioning + hash explicites (utile pour 12_COHERENT_EVOLUTION) ; source de vérité unique et tracée.
- − : nécessite un ORCHESTRATEUR (inexistant aujourd'hui) + un schéma d'engagement + `version`/`hash` ajoutés à CANONS.yaml ; plus de machinerie ; sur-dimensionné pour V1 (3 canons).

## 7. RECOMMANDATION : Arch A (avec module de normalisation partagé), B en cible future
Raisons (MINIMUM-DEBT) : pas d'orchestrateur aujourd'hui ; A ferme le trou avec la surface la plus petite et une VRAIE indépendance ; le seul vrai risque (double source de vérité) est neutralisé par l'extraction d'un module de normalisation UNIQUE. B reste la cible quand l'orchestrateur + le versioning arriveront (12_COHERENT_EVOLUTION en aura besoin) — migration A→B non destructive (A pose déjà le module partagé + le full-registry fingerprint).

- **Périmètre exact** :
  1. NOUVEAU `zoran_v2/canon_registry.py` : `normalize_registry`, `applicable_canons`, `clean_canon`, `full_registry_fingerprint` (extraits de 04, source unique).
  2. 04 : importe le module partagé (comportement inchangé) ; ajoute optionnellement `full_registry_fingerprint`/`registry_version` en sortie (provenance).
  3. 05 : signature `run_coherence_engine(envelope, registry)` ; recompute full fingerprint ; re-dérive applicabilité (kind@01 + frame@02 + registre) ; reconstruit canons_selected/uncanonized/conflicts EXACTS ; compare à 04 → BLOCKED(CD04) sur écart ; `main` charge le registre.
- **Fichiers concernés** : `zoran_v2/canon_registry.py` (new), `zoran_v2/canon_determination.py` (refactor import), `zoran_v2/coherence_engine.py` (signature + re-dérivation), `tests/test_coherence_engine.py` + `tests/test_canon_determination.py` (fixtures/migration), éventuellement `CANONS.yaml` (version, si B partiel).
- **Tests nécessaires** : (a) canon applicable retiré de canons_selected ET du sous-réf → 05 détecte (re-dérivation) → BLOCKED [le contre-exemple exact] ; (b) 04 et module partagé produisent une applicabilité identique ; (c) nominal cohérent → PASS ; (d) full-registry fingerprint ≠ → BLOCKED ; (e) migration des fixtures 05 vers la nouvelle signature ; (f) déterminisme/pureté préservés.
- **Rollback** : branche non fusionnée ; revert ; le module partagé est additif (04 continue de fonctionner).
- **Impact global 04→08** : 04 comportement inchangé (refactor interne) ; 05 gagne l'autorité indépendante ; 06/07 consomment la sortie 05 (schéma stable, +champ optionnel) ; 08 inchangé (utilise le fingerprint du sous-réf 04 ; peut, plus tard, consommer full_registry_fingerprint). Aucun orchestrateur à modifier.
- **Migration des call sites** : uniquement fixtures de test 05 + `05.main` (passer `load_canon_registry()`). 06/08 non impactés (consomment la sortie, pas la signature).

## 8. Questions restant à trancher (Fred)
Q1. Arch A (reco) ou Arch B (orchestrateur+versioning) ?
Q2. CANONS.yaml doit-il recevoir `version` + `hash` maintenant (pré-requis B, utile provenance) ?
Q3. 05 charge-t-il le registre dans son `main` (indépendant, comme 04) ou via un futur orchestrateur ?
Q4. 04 doit-il exposer `full_registry_fingerprint`/`registry_version` en sortie (provenance) dès maintenant ?
Q5. Cette évolution 04→05 est-elle un pré-requis à la certification 05, ou une amélioration parallèle (le finding est-il P1 bloquant le merge) ?
