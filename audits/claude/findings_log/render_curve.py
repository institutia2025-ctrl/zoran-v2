#!/usr/bin/env python3
"""Recompte la courbe findings/moteur depuis FINDINGS_LOG.jsonl (DOCS_ONLY, aucun moteur importé)."""
import json
import pathlib
from collections import Counter, defaultdict

LOG = pathlib.Path(__file__).with_name("FINDINGS_LOG.jsonl")


def load():
    rows = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main():
    rows = load()
    per_engine = Counter(r["engine"] for r in rows)
    reused = defaultdict(int)
    for r in rows:
        if r.get("reused_downstream"):
            reused[r["engine"]] += 1
    order = sorted(per_engine)
    print("moteur | findings | dont garde reutilise aval | provenance")
    for e in order:
        prov = {r.get("provenance", "?") for r in rows if r["engine"] == e}
        print(f"  {e}   |    {per_engine[e]}     |         {reused[e]}          | {','.join(sorted(prov))}")
    print(f"total findings = {len(rows)} ; reutilises aval = {sum(reused.values())}")
    print("courbe (ordre construction 05,08,09,10) = "
          + ", ".join(f"{e}:{per_engine[e]}" for e in order) + "  [10 en reaudit = provisoire]")


if __name__ == "__main__":
    main()
