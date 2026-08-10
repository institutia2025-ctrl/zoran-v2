# -*- coding: utf-8 -*-
"""
GlyphNet ZORAN — moteur de souveraineté structurelle v1.1 CANDIDATE

Statut:
  EXPERIMENTAL / NON_MESURE pour le gain de tokens et la confidentialité.
  Ce module n'est PAS un chiffrement et ne prétend pas remplacer TLS, chiffrement
  au repos, M7/C2, contrôle d'accès ou isolation du runtime.

But borné:
  - encoder une ENVELOPPE STRUCTURELLE fermée de claims sous un dialecte propre
    à une installation ;
  - refuser mécaniquement l'usage quand le runtime local n'est pas attesté ;
  - versionner/rotater la table via une mémoire ZMOS-like ;
  - permettre une validation stricte du flux et détecter un mauvais dialecte.

Point critique:
  Un LLM général ne comprend pas une bijection aléatoire par magie. Pour que
  GlyphNet soit réellement un canal LLM<->moteur, il faut soit:
    (a) un modèle local entraîné/contraint sur le dialecte,
    (b) un adaptateur déterministe qui fait la traduction hors du LLM.
  Tant que ce point n'est pas prouvé, "compression tokens" = NON_MESURE.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from typing import Callable, Optional, Protocol, Any

VERSION = "GLYPHNET-ZORAN-1.1-CANDIDATE"

SYMBOLES_CANONIQUES = (
    "CLAIM", "FACT", "RELATION", "UNCERTAINTY", "ACTION",
    "PASS", "FAIL", "NON_MESURE", "BETA", "DELTA_PHI", "T", "SIGMA", "S",
    "OUVRE", "FERME", "SEP", "ID", "REF", "NEG", "AFF",
)
CLAIM_TYPES = {"CLAIM", "FACT", "RELATION", "UNCERTAINTY", "ACTION"}
POLARITES = {"aff", "neg"}
_RESERVOIR = (
    "🜀🜁🜂🜃🜄🜅🜆🜇🜈🜉🜊🜋🜌🜍🜎🜏"
    "⟐⟡⟢⟣⟤⟥⦿⦾⧉⧫⧭⧮⧯⧰⧱⧲"
    "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊ"
)
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


class ZMOSLike(Protocol):
    _etat: dict
    def ecrire(self, type_: str, titre: str, contenu: dict, authority: str,
               tags: tuple = (), liens: tuple = (), statut: str = "actif",
               object_id: Optional[str] = None) -> dict: ...
    def modifier(self, object_id: str, nouveau_contenu: dict, authority: str,
                 statut: Optional[str] = None) -> dict: ...
    def last_valid(self, object_id: str) -> Optional[dict]: ...


class SouveraineteError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _strict_claim(c: dict) -> dict:
    if not isinstance(c, dict):
        raise SouveraineteError("claim non objet")
    if set(c) != {"type", "id", "polarite"}:
        raise SouveraineteError("schéma claim non fermé")
    typ = c["type"]
    ident = c["id"]
    pol = c["polarite"]
    if typ not in CLAIM_TYPES:
        raise SouveraineteError(f"type interdit: {typ!r}")
    if not isinstance(ident, str) or not _ID_RE.fullmatch(ident):
        raise SouveraineteError("id invalide")
    if pol not in POLARITES:
        raise SouveraineteError("polarité invalide")
    return {"type": typ, "id": ident, "polarite": pol}


class MoteurSouverainete:
    """
    Le vérificateur de runtime est injecté: un simple bool fourni par l'appelant
    n'est pas une preuve de localité.
    """

    def __init__(
        self,
        zmos: ZMOSLike,
        verifier_runtime_local: Callable[[dict], bool],
    ):
        self.z = zmos
        self.verifier_runtime_local = verifier_runtime_local
        self._oid_table = self._table_active_unique()

    def _tables(self) -> list[tuple[str, dict]]:
        out = []
        for oid, vs in self.z._etat.items():
            if vs and vs[0].get("type") == "dialecte_glyphe":
                out.append((oid, vs[-1]))
        return out

    def _table_active_unique(self) -> Optional[str]:
        actifs = []
        for oid, _ in self._tables():
            v = self.z.last_valid(oid)
            if v is not None and v["contenu"].get("actif") is True:
                actifs.append(oid)
        if len(actifs) > 1:
            raise SouveraineteError("plusieurs dialectes actifs: arbitrage requis")
        return actifs[0] if actifs else None

    def _gate(self, runtime_attestation: dict):
        if not isinstance(runtime_attestation, dict):
            raise SouveraineteError("attestation runtime absente")
        if self.verifier_runtime_local(runtime_attestation) is not True:
            raise SouveraineteError("mode souverain refusé: runtime local non attesté")

    def installer_dialecte(
        self,
        authority: str,
        *,
        graine_test: Optional[str] = None,
    ) -> dict:
        if not isinstance(authority, str) or not authority.strip():
            raise SouveraineteError("AUTHORITY absente")

        if self._oid_table is not None:
            old = self.z.last_valid(self._oid_table)
            if old is not None:
                self.z.modifier(
                    self._oid_table,
                    {**old["contenu"], "actif": False},
                    authority=authority,
                    statut="archive",
                )

        pool = list(dict.fromkeys(_RESERVOIR))
        n = len(SYMBOLES_CANONIQUES)
        if len(pool) < n:
            raise SouveraineteError("réservoir insuffisant")

        if graine_test is not None:
            idx = list(range(len(pool)))
            flux = f"TEST-ONLY:{graine_test}"
            for i in range(len(idx) - 1, 0, -1):
                flux = hashlib.sha256(flux.encode("utf-8")).hexdigest()
                j = int(flux, 16) % (i + 1)
                idx[i], idx[j] = idx[j], idx[i]
            pool = [pool[k] for k in idx]
        else:
            secrets.SystemRandom().shuffle(pool)

        bijection = {sym: pool[i] for i, sym in enumerate(SYMBOLES_CANONIQUES)}
        empreinte = _sha(bijection)
        rec = self.z.ecrire(
            "dialecte_glyphe",
            f"dialecte:{empreinte[:12]}",
            {
                "version": VERSION,
                "bijection": bijection,
                "empreinte_dialecte": empreinte,
                "actif": True,
                "security_scope": "OBFUSCATION_STRUCTURELLE_NOT_ENCRYPTION",
            },
            authority=authority,
        )
        self._oid_table = rec["OBJECT_ID"]
        return rec

    def _record(self) -> dict:
        if self._oid_table is None:
            raise SouveraineteError("aucun dialecte actif")
        v = self.z.last_valid(self._oid_table)
        if v is None or v["contenu"].get("actif") is not True:
            raise SouveraineteError("dialecte révoqué/inactif")
        return v

    def empreinte_dialecte(self) -> str:
        return self._record()["contenu"]["empreinte_dialecte"]

    def _bijection(self) -> dict:
        b = self._record()["contenu"]["bijection"]
        if set(b) != set(SYMBOLES_CANONIQUES) or len(set(b.values())) != len(b):
            raise SouveraineteError("table non bijective")
        return b

    def encoder(self, claim_set: list[dict], *, runtime_attestation: dict) -> str:
        self._gate(runtime_attestation)
        if not isinstance(claim_set, list) or not claim_set:
            raise SouveraineteError("CLAIM_SET vide/invalide")
        claims = [_strict_claim(c) for c in claim_set]
        b = self._bijection()

        header = f"GN1:{self.empreinte_dialecte()}:"
        out = [header]
        for c in claims:
            ident_hash = hashlib.sha256(c["id"].encode("utf-8")).hexdigest()[:16]
            out.extend((
                b["OUVRE"], b[c["type"]], b["SEP"], b["ID"], ident_hash,
                b["SEP"], b["NEG"] if c["polarite"] == "neg" else b["AFF"],
                b["FERME"],
            ))
        return "".join(out)

    def parse_strict(self, flux: str, *, runtime_attestation: dict) -> list[dict]:
        self._gate(runtime_attestation)
        if not isinstance(flux, str) or not flux.startswith("GN1:"):
            raise SouveraineteError("flux GlyphNet invalide")
        try:
            _, fingerprint, body = flux.split(":", 2)
        except ValueError as exc:
            raise SouveraineteError("entête GlyphNet invalide") from exc
        if fingerprint != self.empreinte_dialecte():
            raise SouveraineteError("dialecte incompatible")

        b = self._bijection()
        inv = {v: k for k, v in b.items()}
        opens = b["OUVRE"]
        closes = b["FERME"]
        sep = b["SEP"]
        id_marker = b["ID"]

        claims = []
        pos = 0
        while pos < len(body):
            if body[pos] != opens:
                raise SouveraineteError("OUVRE attendu")
            pos += 1

            if pos >= len(body) or body[pos] not in inv or inv[body[pos]] not in CLAIM_TYPES:
                raise SouveraineteError("type claim invalide")
            typ = inv[body[pos]]
            pos += 1

            if body[pos:pos+1] != sep:
                raise SouveraineteError("SEP attendu")
            pos += 1
            if body[pos:pos+1] != id_marker:
                raise SouveraineteError("ID attendu")
            pos += 1

            ident_hash = body[pos:pos+16]
            if len(ident_hash) != 16 or any(c not in "0123456789abcdef" for c in ident_hash):
                raise SouveraineteError("id hash invalide")
            pos += 16

            if body[pos:pos+1] != sep:
                raise SouveraineteError("SEP attendu")
            pos += 1
            if pos >= len(body) or body[pos] not in inv or inv[body[pos]] not in {"AFF", "NEG"}:
                raise SouveraineteError("polarité invalide")
            pol = "neg" if inv[body[pos]] == "NEG" else "aff"
            pos += 1

            if body[pos:pos+1] != closes:
                raise SouveraineteError("FERME attendu")
            pos += 1

            claims.append({"type": typ, "id_hash": ident_hash, "polarite": pol})

        return claims

    def decoder_empreinte(self, flux: str, *, runtime_attestation: dict) -> str:
        self._gate(runtime_attestation)
        self.parse_strict(flux, runtime_attestation=runtime_attestation)
        return _sha({
            "flux": flux,
            "dialecte": self.empreinte_dialecte(),
            "version": VERSION,
        })
