# -*- coding: utf-8 -*-
"""Falsificateurs GlyphNet v1.1 — indépendants de ZMOS produit."""
from __future__ import annotations
import copy
import json

from moteur_souverainete import (
    MoteurSouverainete,
    SouveraineteError,
)

class FakeZMOS:
    def __init__(self):
        self._etat = {}
        self.n = 0

    def ecrire(self, type_, titre, contenu, authority, tags=(), liens=(),
               statut="actif", object_id=None):
        self.n += 1
        oid = object_id or f"OID-{self.n}"
        rec = {
            "OBJECT_ID": oid,
            "VERSION_ID": f"V-{self.n}",
            "type": type_,
            "titre": titre,
            "contenu": copy.deepcopy(contenu),
            "AUTHORITY": authority,
            "statut": statut,
        }
        self._etat.setdefault(oid, []).append(rec)
        return rec

    def modifier(self, object_id, nouveau_contenu, authority, statut=None):
        old = self._etat[object_id][-1]
        return self.ecrire(
            old["type"], old["titre"], nouveau_contenu, authority,
            statut=old["statut"] if statut is None else statut,
            object_id=object_id,
        )

    def last_valid(self, object_id):
        if object_id not in self._etat:
            return None
        v = self._etat[object_id][-1]
        return v if v["statut"] == "actif" else None


def attest_local(proof):
    return proof == {"provider": "ollama-local", "attested": True}

LOCAL = {"provider": "ollama-local", "attested": True}
CLOUD = {"provider": "cloud", "attested": False}
CS = [
    {"type": "CLAIM", "id": "c1", "polarite": "aff"},
    {"type": "FACT", "id": "f1", "polarite": "neg"},
]

R = {}

z = FakeZMOS()
m = MoteurSouverainete(z, attest_local)
m.installer_dialecte("fred", graine_test="inst-A")

try:
    m.encoder(CS, runtime_attestation=CLOUD)
    R["G1_gate_cloud"] = False
except SouveraineteError:
    R["G1_gate_cloud"] = True

flux = m.encoder(CS, runtime_attestation=LOCAL)
parsed = m.parse_strict(flux, runtime_attestation=LOCAL)
R["G2_roundtrip_structurel"] = (
    [x["type"] for x in parsed] == ["CLAIM", "FACT"]
    and [x["polarite"] for x in parsed] == ["aff", "neg"]
)

z2 = FakeZMOS()
m2 = MoteurSouverainete(z2, attest_local)
m2.installer_dialecte("fred", graine_test="inst-B")
try:
    m2.parse_strict(flux, runtime_attestation=LOCAL)
    R["G3_cross_dialect_refuse"] = False
except SouveraineteError:
    R["G3_cross_dialect_refuse"] = True

R["G4_distincts"] = m.empreinte_dialecte() != m2.empreinte_dialecte()

old_oid = m._oid_table
old_fp = m.empreinte_dialecte()
m.installer_dialecte("fred", graine_test="inst-A-rot2")
R["G5_rotation_archive"] = (
    m.empreinte_dialecte() != old_fp
    and z.last_valid(old_oid) is None
)

try:
    m.encoder(
        [{"type": "CLAIM", "id": "c2", "polarite": "maybe"}],
        runtime_attestation=LOCAL,
    )
    R["G6_polarite_fermee"] = False
except SouveraineteError:
    R["G6_polarite_fermee"] = True

try:
    m.encoder(
        [{"type": "CLAIM", "id": "c2", "polarite": "aff", "texte": "secret"}],
        runtime_attestation=LOCAL,
    )
    R["G7_schema_ferme"] = False
except SouveraineteError:
    R["G7_schema_ferme"] = True

bad = flux[:-1]
try:
    m.parse_strict(bad, runtime_attestation=LOCAL)
    R["G8_flux_tronque_refuse"] = False
except SouveraineteError:
    R["G8_flux_tronque_refuse"] = True

emp = m.decoder_empreinte(
    m.encoder(CS, runtime_attestation=LOCAL),
    runtime_attestation=LOCAL,
)
R["G9_empreinte_validee"] = (
    len(emp) == 64 and all(c in "0123456789abcdef" for c in emp)
)

print(json.dumps(R, indent=2, ensure_ascii=False))
ok = all(R.values())
print(f"=== GLYPHNET : {sum(R.values())}/{len(R)} VERTS ===",
      "✅ CANDIDAT" if ok else "🔴 FIX_REQUIRED")
raise SystemExit(0 if ok else 1)
