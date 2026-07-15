[AUDIT — ZORAN V2 — BASELINE 01 UNICODE NFC — LECTURE SEULE]
Destinataires : ChatGPT GLOBAL_COHERENCE, Codex Session A, Codex Session B.
PR #19, branche fix/baseline-01-unicode-nfc. SHA A AUDITER: bdf022a953dc2b853ba80236a83b4f157fec7c6e
Historique : 95afe8d (value NFC) -> bdf022a (+ kind NFC, fermeture de classe). Base 9ed679f.
CI success (231 passed). INDEPENDANT de 05 (gele d03b473) et 08 (8227167). SHA GELE apres publication.

CORRECTION (CSB-META-P1-003) — Unicode NFC de l'IDENTITE textuelle complete (object_key = kind + SEP + value) :
- value : _normalize = unicodedata.normalize('NFC', " ".join(value.split()).casefold()).
- kind  : object_key = NFC(kind.strip()) + SEP + normalized ; kind stocke = forme NFC.
Deux chaines canoniquement equivalentes (precompose vs decompose, sur value OU kind) -> meme object_key
-> dedup 01. Politique NFC (REX #15) ; NFKC ecarte (compatibilites non repliees par casefold restent distinctes).
Repro exact rouge->vert.

QUESTIONS (falsifiables) — OUI/NON + preuve:
Q1. Formes equivalentes de VALUE -> meme object_key (dedup) ?
Q2. Formes equivalentes de KIND -> meme object_key (dedup) ? (fermeture de classe)
Q3. Sortie (normalized, kind) toujours en forme NFC ?
Q4. NFC ne fusionne PAS a tort des objets distincts (compatibilites NFKC hors casefold, ex. fullwidth) ?
Q5. Non-regression ASCII / provenance / dedup / ordre / determinisme / immuabilite ?
Q6. Reste-t-il un champ d'identite textuelle non normalise ? (value + kind couverts ; autre ?)
Q7. Impact aval : object_key reste str opaque, contrat inchange pour 03..08 ? (04 matche kind NFC vs registre ASCII : ok)
Q8. VERDICT: APPROVED, ou ecart falsifiable ?

FORMAT : { "TYPE":"...","SHA":"bdf022a953dc2b853ba80236a83b4f157fec7c6e","VERDICT":"APPROVED"|"FIX_REQUIRED","FINDINGS":[...],"PREUVES":"","CONFIANCE":0.0-1.0 }

DIFF (9ed679f -> bdf022a), zoran_v2/object_discovery.py :
==================================================================
diff --git a/zoran_v2/object_discovery.py b/zoran_v2/object_discovery.py
index c58fbe5..035b19a 100644
--- a/zoran_v2/object_discovery.py
+++ b/zoran_v2/object_discovery.py
@@ -9,6 +9,8 @@ fail-closed (candidat non ancrable -> dropped, jamais inventé).
 """
 from __future__ import annotations
 
+import unicodedata
+
 COMPONENT_ID = "01_OBJECT_DISCOVERY"
 VERSION = "1.0.0"
 
@@ -22,6 +24,7 @@ GOVERNANCE = {
     "GUARD_IDS": [
         "STRUCTURED_ONLY",
         "NO_INVENTION",
+        "TEXT_IDENTITY_UNICODE_NFC",
         "FAIL_CLOSED",
         "DETERMINISTIC",
         "NO_LLM",
@@ -34,7 +37,7 @@ GOVERNANCE = {
     "VALIDATION": "tests deterministes pytest + CI Python 3.13",
     "ROLLBACK": "git : branche non fusionnee dans seed-bootstrap ; git revert du commit",
     "DETECTION_MODIF": "SHA git + CI GitHub Actions",
-    "ALERTE": "status=BLOCKED si 00!=PASS ; dropped[] pour tout candidat non admissible (jamais silencieux)",
+    "ALERTE": "status=BLOCKED si 00!=PASS ; dropped[] pour tout candidat non admissible (jamais silencieux) ; identite textuelle normalisee Unicode NFC (formes equivalentes -> meme object_key)",
     "ANTI_REGRESSION": "tests non-invention + dedup + ordre + fail-closed + gouvernance ; CI bloque le merge",
 }
 
@@ -68,7 +71,10 @@ def _normalize(value):
     if isinstance(value, bool):
         return None  # un booléen n'est pas un objet-valeur
     if isinstance(value, str):
-        n = " ".join(value.split()).casefold()
+        # CSB-META-P1-003 : identité textuelle CANONIQUE. Normalisation Unicode NFC (REX #15, NFC par
+        # défaut) pour que deux chaînes canoniquement équivalentes (formes précomposée/décomposée)
+        # produisent le MÊME object_key. NFC appliqué APRÈS casefold pour recomposer la sortie.
+        n = unicodedata.normalize("NFC", " ".join(value.split()).casefold())
         return n or None
     if isinstance(value, (int, float)):
         return repr(value)
@@ -146,7 +152,10 @@ def run_object_discovery(envelope: dict) -> dict:
             _drop(i, cand, "provenance_unverified")
             continue
 
-        key = f"{kind.strip()}{_SEP}{normalized}"
+        # CSB-META-P1-003 : le `kind` fait partie de l'identite (object_key) -> il doit AUSSI etre
+        # normalise Unicode NFC (sinon deux kinds canoniquement equivalents = deux object_key).
+        kind_n = unicodedata.normalize("NFC", kind.strip())
+        key = f"{kind_n}{_SEP}{normalized}"
         off = prov.get("in_text", {}).get("offset") if "in_text" in prov else None
         if key in by_key:
             by_key[key]["provenance"].append(prov)
@@ -154,7 +163,7 @@ def run_object_discovery(envelope: dict) -> dict:
                 by_key[key]["order"] = off
         else:
             by_key[key] = {
-                "object_key": key, "kind": kind.strip(),
+                "object_key": key, "kind": kind_n,
                 "normalized": normalized, "provenance": [prov], "order": off,
             }
 
