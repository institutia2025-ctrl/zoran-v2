[AUDIT GLOBAL COHERENCE — ZORAN V2 — ENGINE-08 — LECTURE SEULE — CYCLE 2/2]

Tu es ChatGPT, GLOBAL_COHERENCE_CERTIFIER. Ne produis AUCUN code, AUCUN commit.

CONTEXTE
- ENGINE-08 (08_COHERENCE_2), PR #12. SHA A AUDITER: 82271678a767c2674f29c96493fddc8f847aba29
- Historique: 3974ae8 (GC-08-001/002/003) -> bde03aa (GC-08-004/005) -> 8227167 (ce SHA, cycle 2/2).
- CI: success, 250 passed (Python 3.13). Baseline 00-07 @ 6d3f389.

CORRECTION depuis bde03aa (tes 2 findings) + fermeture complementaire (meme classe, auto-audit) :
- GC-08-004 : S_pre lu et valide FINI (math.isfinite) AVANT la validation 06 ; _validate_request_06
  exige 06.coherence_S fini ET round(.,6) == S de 05 (rejette NaN/+-inf ; chaine 05->06->08 fermee).
- GC-08-005 : `if lrb.get('authorized') is not True: return BLOCKED(ENVELOPE_MALFORMED)` avant tout jugement.
- Complementaire (par coherence, ne pas faire confiance a AUCUN champ de 06) : canons 06 doivent
  tracer au referentiel gele 04 (canons ⊆ {ids 04}) et operants 06 a l'analyse 03 (operants ⊆ {03}).

QUESTIONS D'AUDIT (falsifiables) — OUI/NON + preuve:
Q1. GC-08-004 et GC-08-005 sont-ils reellement fermes ?
Q2. Toute la chaine 03/04/05/06 -> 08 est-elle desormais validee (aucune entree autoritaire non recoupee) ?
Q3. Reste-t-il un champ de 06 (ou 04/05) que 08 utilise SANS recoupement autoritaire ?
Q4. Recoupement coherence_S : la politique d'arrondi (round 6) est-elle correcte, sans faux blocage sur la sortie reelle de 06 ?
Q5. authorized revalide : couvre-t-il les cas non-booleens (1, 'true', None) ?
Q6. Determinisme, formule canonique, verdicts, authorize_09, anti-fuite : inchanges/corrects ?
Q7. Faux blocage sur la sortie REELLE de 06 (canons/operants legitimes ⊆ 04/03, coherence_S==05) ?
Q8. VERDICT: APPROVED, ou ecart falsifiable et localise ?

FORMAT DE VERDICT (JSON):
{ "TYPE":"CHATGPT_GLOBAL_COHERENCE","SHA":"82271678a767c2674f29c96493fddc8f847aba29",
  "VERDICT":"APPROVED"|"FIX_REQUIRED","SCOPE":"engine-08 + frontieres 03/04/05/06/07",
  "FINDINGS":[{"id":"","severite":"","fichier":"","preuve":"","falsifiable":""}],
  "PREUVES":"","CONFIANCE":0.0-1.0 }

DIFF depuis ton dernier verdict (bde03aa -> 8227167), zoran_v2/coherence_2.py :
==================================================================
diff --git a/zoran_v2/coherence_2.py b/zoran_v2/coherence_2.py
index c7c0135..9e58c3c 100644
--- a/zoran_v2/coherence_2.py
+++ b/zoran_v2/coherence_2.py
@@ -33,6 +33,7 @@ panne) :
 """
 from __future__ import annotations
 
+import math
 import re
 import statistics
 
@@ -57,8 +58,11 @@ GOVERNANCE = {
         "NO_MEMORY",
         "RESPONSE_SCHEMA_VALIDATED",
         "REQUEST_06_REVALIDATED_STRICT_FAIL_CLOSED",
+        "REQUEST_06_AUTHORIZED_REVALIDATED",
+        "COHERENCE_S_06_MATCHES_05_FINITE",
+        "CANONS_OPERANTS_06_TRACE_04_03",
         "REFERENTIAL_FINGERPRINT_VERIFIED",
-        "PROVENANCE_TO_04_06",
+        "PROVENANCE_TO_03_04_05_06",
         "NO_PII_FROM_RESPONSE",
         "POST_LLM_ADMISSIBILITY_GATE_BEFORE_09",
         "FAIL_CLOSED",
@@ -192,15 +196,17 @@ def _is_str_list(x) -> bool:
     return isinstance(x, list) and all(isinstance(e, str) for e in x)
 
 
-def _validate_request_06(request, fp04) -> bool:
+def _validate_request_06(request, fp04, s_pre, canon_ids, operant_ids) -> bool:
     """Re-valide la requête AUTORITAIRE 06 avec la MÊME rigueur que la frontière 07 (fail-closed).
 
-    08 utilise 06 comme source de vérité des cibles attendues : une source mal validée peut
-    produire une certification post-LLM FAUSSE (GC-08-001/002/003). Impose : schéma racine EXACT,
-    instruction_kind + pii_policy canoniques, fingerprint 06 == fingerprint 04, cibles = liste
-    non vide au schéma EXACT, object_public_id opaque `OBJ-nnnn`, kind_public/frame str, canons &
-    operants listes de STR UNIQUEMENT (pas de conteneur falsy normalisé), AUCUN doublon
-    (object_public_id, frame) ni canon/opérant dupliqué, et aucune clé interne / séparateur (fuite).
+    08 utilise 06 comme source de vérité des cibles attendues : on ne fait confiance à AUCUN champ
+    de 06 — une source mal validée fausserait la certification post-LLM (GC-08-001..005). Impose :
+    schéma racine EXACT, instruction_kind + pii_policy canoniques, fingerprint 06 == fingerprint 04,
+    coherence_S 06 FINI ET == S de 05 (arrondi canonique, GC-08-004), cibles = liste non vide au
+    schéma EXACT, object_public_id opaque `OBJ-nnnn`, kind_public/frame str, canons & operants listes
+    de STR UNIQUEMENT tracant a l'amont (canons ⊆ ids 04 gelés, operants ⊆ opérants 03), AUCUN
+    doublon (object_public_id, frame) ni canon/opérant dupliqué, `frames` racine == frames des cibles,
+    et aucune clé interne / séparateur (fuite).
     """
     if _has_internal_leak(request):
         return False
@@ -212,8 +218,9 @@ def _validate_request_06(request, fp04) -> bool:
         return False
     if request.get("referential_fingerprint") != fp04:  # fingerprint 06 DOIT == 04 gelé
         return False
-    s = request.get("coherence_S")
-    if not (s is None or (isinstance(s, (int, float)) and not isinstance(s, bool))):
+    s = request.get("coherence_S")  # GC-08-004 : fini ET == S autoritaire de 05 (chaîne 05->06 fermée)
+    if not (isinstance(s, (int, float)) and not isinstance(s, bool)
+            and math.isfinite(s) and round(float(s), 6) == s_pre):
         return False
     if not _is_str_list(request.get("frames")):
         return False
@@ -238,8 +245,10 @@ def _validate_request_06(request, fp04) -> bool:
             return False
         if len(set(canons)) != len(canons) or len(set(operants)) != len(operants):  # doublon canon/opérant
             return False
-    # Cohérence root<->cibles : `frames` racine DOIT être exactement l'ensemble des frames des cibles
-    # (invariant 06). Sinon requête incohérente -> fail-closed.
+        # Provenance amont : chaque canon ∈ référentiel 04 gelé, chaque opérant ∈ analyse 03.
+        if not (set(canons) <= canon_ids and set(operants) <= operant_ids):
+            return False
+    # Cohérence root<->cibles : `frames` racine DOIT être exactement l'ensemble des frames des cibles.
     if set(request["frames"]) != {t["frame"] for t in targets}:
         return False
     return True
@@ -261,18 +270,34 @@ def run_coherence_2(envelope: dict) -> dict:
     if ex.get("executed") is not True:
         return _blocked(NOT_EXECUTED)
 
-    # 3) Fingerprint 04 autoritaire.
+    # 3) Fingerprint 04 autoritaire + VOCABULAIRE autoritaire (ids de canons 04 gelés, opérants 03).
     cd = envelope["canon_determination"]
     referential = cd.get("canon_referential")
     fingerprint = referential.get("fingerprint") if isinstance(referential, dict) else None
     if not (isinstance(fingerprint, str) and fingerprint):
         return _blocked(FINGERPRINT_MISSING)
+    canon_ids = {c["id"] for c in (referential.get("canons") or [])
+                 if isinstance(c, dict) and isinstance(c.get("id"), str)}
+    oa = envelope["operants_operes"]
+    operant_ids = {op for a in (oa.get("analysis") or []) if isinstance(a, dict)
+                   for op in (a.get("operants") or []) if isinstance(op, str)}
+
+    # 4) S_pre depuis 05 — validé FINI, AVANT la validation 06 (recoupement coherence_S, GC-08-004).
+    ce = envelope["coherence_engine"]
+    coherence5 = ce.get("coherence")
+    s_raw = coherence5.get("S") if isinstance(coherence5, dict) else None
+    if not (isinstance(s_raw, (int, float)) and not isinstance(s_raw, bool) and math.isfinite(s_raw)):
+        return _blocked(ENVELOPE_MALFORMED)
+    s_pre = round(float(s_raw), 6)
 
-    # 4) Requête 06 AUTORITAIRE : re-validée STRICTEMENT (fail-closed), pas de confiance à 07.
-    #    Une source attendue mal validée fausserait la certification post-LLM (GC-08-001/002/003).
+    # 5) Requête 06 AUTORITAIRE : autorisation RÉELLE (GC-08-005) + re-validation STRICTE (fail-closed),
+    #    sans confiance à 07. On ne fait confiance à AUCUN champ de 06 : coherence_S==05, canons⊆04,
+    #    operants⊆03, fingerprint==04 -> chaîne 05→06→08 fermée (GC-08-001..005).
     lrb = envelope["llm_request_build"]
+    if lrb.get("authorized") is not True:
+        return _blocked(ENVELOPE_MALFORMED)
     request = lrb.get("llm_request")
-    if not _validate_request_06(request, fingerprint):
+    if not _validate_request_06(request, fingerprint, s_pre, canon_ids, operant_ids):
         return _blocked(ENVELOPE_MALFORMED)
     # Cibles attendues, clef (object_public_id, frame). L'unicité est déjà garantie par la validation.
     expected = {
@@ -280,14 +305,6 @@ def run_coherence_2(envelope: dict) -> dict:
         for t in request["targets"]
     }
 
-    # 5) S_pre depuis 05.
-    ce = envelope["coherence_engine"]
-    coherence5 = ce.get("coherence")
-    if not (isinstance(coherence5, dict) and isinstance(coherence5.get("S"), (int, float))
-            and not isinstance(coherence5.get("S"), bool)):
-        return _blocked(ENVELOPE_MALFORMED)
-    s_pre = round(float(coherence5["S"]), 6)
-
     # ---- status PASS : on JUGE la réponse (une mauvaise réponse -> REJECT, jamais BLOCKED) ----
     return _judge(ex.get("response"), request, expected, fingerprint, s_pre)
 
