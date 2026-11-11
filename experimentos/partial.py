#!/usr/bin/env python3
"""Resumo de execuções em andamento (última geração registrada de cada json)."""
import glob
import json
from collections import defaultdict

import numpy as np

PAPER = {"mnist": (98.13, 96.8, 95.6), "fashion": (88.54, 85.3, 82.0), "svhn": (79.86, 70.2, 66.5),
         "cifar10": (51.35, 43.9, 42.7)}
R = defaultdict(list)
for f in glob.glob("results/*.json"):
    try:
        d = json.load(open(f))
    except json.JSONDecodeError:
        continue
    c = d["config"]
    R[(c["dataset"], c["method"])].append(d)
print("finalizadas:", sum("final" in d for v in R.values() for d in v), "de", sum(len(v) for v in R.values()), "iniciadas")
print("| Dataset | Método | n | Geração | Melhor (val) | Média pop. (val) | Filhos antes do BP | Teste final |")
print("|---|---|---|---|---|---|---|---|")
for ds in ["mnist", "fashion", "svhn", "cifar10"]:
    if not any((ds, m) in R for m in ["steady_random", "majority", "elitist"]):
        continue
    p = PAPER[ds]
    print(f"| {ds} | Paper c/ esp. (g100, teste) | 10 | 100 | {p[0]:.2f} | {p[1]:.2f} | {p[2]:.2f} | |")
    for m in ["steady_random", "majority", "elitist"]:
        v = R.get((ds, m), [])
        if not v:
            continue
        gl = [d["gens"][-1] for d in v]
        pre = [np.mean([g["offspring_pre_bp"] for g in d["gens"][-10:] if g["offspring_pre_bp"] is not None]) for d in v]
        test = [d["final"]["champ_test"] for d in v if "final" in d]
        gens = [g["gen"] for g in gl]
        tf = f"{100 * np.mean(test):.2f} (n={len(test)})" if test else "-"
        print(f"| {ds} | {m} | {len(v)} | {min(gens)}–{max(gens)} | {100 * np.mean([g['best'] for g in gl]):.2f} | "
              f"{100 * np.mean([g['mean'] for g in gl]):.2f} | {100 * np.mean(pre):.2f} | {tf} |")
