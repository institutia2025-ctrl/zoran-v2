[AUDIT — ZORAN V2 — BASELINE 05 COUVERTURE 04<->02 — LECTURE SEULE — v2]

Destinataires : ChatGPT GLOBAL_COHERENCE, Codex Session A, Codex Session B.
PR #17, branche fix/baseline-05-coverage-04. SHA A AUDITER: d03b4739762a2daade5604558c3625cb9747a0a8
Historique : cfb7e1d (omission/invention fermes ; ton finding contradiction) -> d03b473 (ce SHA).
Base 9ed679f. CI: success. Tag baseline non mis a jour. SHA GELE apres publication (REX #10).

CORRECTION depuis cfb7e1d (ton finding) :
  Une CONTRADICTION interne de 04 passait : meme paire dans canons_selected ET uncanonized, masquee
  par l'union en set -> couverture==02 OK -> paire comptee resolue -> delta_phi=1.0/authorize_llm=True.
  Fix : listes conservees avant set ; exige AVANT tout calcul : canonized INTER uncanon == vide ;
  aucun doublon dans canons_selected ni uncanonized. Sinon BLOCKED(CD04).

QUESTIONS (falsifiables) — OUI/NON + preuve:
Q1. Une paire a la fois canonisee ET uncanonized est-elle bloquee ?
Q2. Un doublon dans canons_selected ou uncanonized est-il bloque ?
Q3. Omission/invention/02-malforme toujours fermes (non-regression) ?
Q4. Reste-t-il un chemin ou delta_phi/authorize_llm sont gonfles par un 04 incoherent ?
Q5. L'analyse 03 peut-elle gonfler `resolved` (operant_pairs) au-dela des paires canonisees ?
Q6. Faux blocage sur un 04 REEL (pairs disjointes, sans doublon) ? Determinisme/immuabilite ?
Q7. VERDICT: APPROVED, ou ecart falsifiable ?

FORMAT : { "TYPE":"...","SHA":"d03b4739762a2daade5604558c3625cb9747a0a8","VERDICT":"APPROVED"|"FIX_REQUIRED","FINDINGS":[...],"PREUVES":"","CONFIANCE":0.0-1.0 }

DIFF (cfb7e1d -> d03b473), zoran_v2/coherence_engine.py :
==================================================================
diff --git a/zoran_v2/coherence_engine.py b/zoran_v2/coherence_engine.py
index b3bddec..357e9b9 100644
--- a/zoran_v2/coherence_engine.py
+++ b/zoran_v2/coherence_engine.py
@@ -214,15 +214,24 @@ def run_coherence_engine(envelope: dict) -> dict:
         _pair(a.get("object_key"), a.get("frame"))
         for a in analysis if isinstance(a, dict)
     }
-    # Univers des paires = tout ce que 04 a vu (canonisées + non canonisées).
-    canonized_pairs = {
-        _pair(c.get("object_key"), c.get("frame"))
-        for c in canons_selected if isinstance(c, dict)
-    }
-    uncanon_pairs = {
-        _pair(u.get("object_key"), u.get("frame"))
-        for u in uncanonized if isinstance(u, dict)
-    }
+    # Univers des paires = tout ce que 04 a vu (canonisées + non canonisées). On garde les LISTES
+    # avant conversion en set : sinon un doublon (même paire deux fois) ou une CONTRADICTION (paire
+    # à la fois canonisée ET non-canonisée) serait masqué par le set.
+    canonized_pair_list = [_pair(c.get("object_key"), c.get("frame"))
+                           for c in canons_selected if isinstance(c, dict)]
+    uncanon_pair_list = [_pair(u.get("object_key"), u.get("frame"))
+                         for u in uncanonized if isinstance(u, dict)]
+    canonized_pairs = set(canonized_pair_list)
+    uncanon_pairs = set(uncanon_pair_list)
+
+    # CSB-PROV-P1-004 (contradiction interne 04) : une paire ne peut pas être à la fois canonisée ET
+    # non-canonisée, ni apparaître en DOUBLE dans une liste — sinon delta_phi/S seraient faussés
+    # (paire comptée résolue tout en étant déclarée uncanonized). Fail-closed AVANT tout calcul.
+    if (len(canonized_pair_list) != len(canonized_pairs)
+            or len(uncanon_pair_list) != len(uncanon_pairs)
+            or (canonized_pairs & uncanon_pairs)):
+        return _blocked(CD04)
+
     universe = canonized_pairs | uncanon_pairs
 
     # CSB-PROV-P1-004 : l'univers vu par 04 doit COUVRIR EXACTEMENT les couples autoritaires de 02
