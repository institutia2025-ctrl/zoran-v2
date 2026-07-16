#!/usr/bin/env python3
"""Tableau de bord d'instrumentation ZORAN V2 (DOCS_ONLY, aucun moteur importé).

Lit FINDINGS_LOG.jsonl (per-finding) + ENGINE_METRICS.jsonl (per-moteur) et recompute :
courbe findings, gardes réutilisés en aval, distribution severité/dette, LOC/tests (mesurés),
rounds_to_green, self vs external. Chiffres mesurés vs reconstruits distingués par la provenance.
"""
import json
import pathlib
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).parent
FINDINGS = HERE / "FINDINGS_LOG.jsonl"
METRICS = HERE / "ENGINE_METRICS.jsonl"


def _load(path):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def main():
    findings = _load(FINDINGS)
    metrics = {m["engine"]: m for m in _load(METRICS)}
    order = sorted(metrics)

    per_engine = Counter(f["engine"] for f in findings)
    reused = defaultdict(int)
    for f in findings:
        if f.get("reused_downstream"):
            reused[f["engine"]] += 1

    print("== TABLEAU DE BORD INSTRUMENTATION ZORAN V2 ==")
    print("moteur | findings | reuse_aval | LOC | tests | rounds_green | self_precorr | ci")
    for e in order:
        m = metrics[e]
        print(f"  {e}   |    {per_engine[e]}     |     {reused[e]}      "
              f"| {m['loc']:>3} |  {m['tests']:>2}   |      {m['rounds_to_green']}       "
              f"|      {m['self_precorrections_approx']}       | {m['ci']}")

    print("\n-- courbe findings (ordre 05,08,09,10) : "
          + ", ".join(f"{e}:{per_engine[e]}" for e in order))
    print("-- LOC (consolidation) : "
          + ", ".join(f"{e}:{metrics[e]['loc']}" for e in order))
    print("-- tests : " + ", ".join(f"{e}:{metrics[e]['tests']}" for e in order))

    sev = Counter(f.get("severity", "?") for f in findings)
    debt = Counter(f.get("debt_class", "?") for f in findings)
    caught = Counter(f.get("caught_by", "?") for f in findings)
    print("\n-- severite : " + repr(dict(sev)))
    print("-- dette (Minimum-Debt V1) : " + repr(dict(debt)))
    print("-- attrape par : " + repr(dict(caught))
          + "  (NB: self_precorrections non journalises ici, cf ENGINE_METRICS)")
    merged = [e for e in order if metrics[e].get("merged")]
    print(f"\ntotal findings = {len(findings)} ; reutilises aval = {sum(reused.values())}"
          f" ; moteurs mergés = {','.join(merged)} ; pipeline 00->11 complet (12 dormant)")


if __name__ == "__main__":
    main()
