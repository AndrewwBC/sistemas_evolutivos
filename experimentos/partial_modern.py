#!/usr/bin/env python3
"""Parcial da CNN moderna (results_modern/) contra a clássica (results/) no CIFAR-10, na mesma geração."""
import glob
import json
from collections import defaultdict

import numpy as np

LAB = {"steady_random": "M1 steady state", "majority": "M2 maioria", "elitist": "M3 elitista"}
mod, cla = defaultdict(list), defaultdict(list)
for f in glob.glob("results_modern/*.json"):
    d = json.load(open(f))
    mod[d["config"]["method"]].append(d)
for f in glob.glob("results/cifar10_*.json"):
    d = json.load(open(f))
    cla[d["config"]["method"]].append(d)

pm = lambda x: f"{np.mean(x):.2f} ± {np.std(x, ddof=1):.2f}" if len(x) > 1 else f"{np.mean(x):.2f}"
print("| Método | Geração | Moderna: melhor (val) | Clássica, mesma geração | Clássica, g100 | "
      "Moderna: média pop. | Clássica: média pop., mesma ger. | Moderna: filhos antes do BP | Params moderna | Teste final moderna |")
print("|---|---|---|---|---|---|---|---|---|---|")
for m in ["steady_random", "majority", "elitist"]:
    v = mod[m]
    g = min(len(d["gens"]) for d in v) - 1
    b = [100 * d["gens"][g]["best"] for d in v]
    mu = [100 * d["gens"][g]["mean"] for d in v]
    pre = [100 * np.mean([x["offspring_pre_bp"] for x in d["gens"][max(1, g - 9):g + 1]
                          if x["offspring_pre_bp"] is not None]) for d in v]
    par = [d["gens"][g]["mean_params"] / 1e3 for d in v]
    cb = [100 * d["gens"][g]["best"] for d in cla[m]]
    cm = [100 * d["gens"][g]["mean"] for d in cla[m]]
    cf = [100 * d["gens"][-1]["best"] for d in cla[m]]
    tst = [100 * d["final"]["champ_test"] for d in v if "final" in d]
    gens = sorted(len(d["gens"]) - 1 for d in v)
    print(f"| {LAB[m]} | {g} (até {gens[-1]}) | {pm(b)} | {pm(cb)} | {pm(cf)} | {pm(mu)} | {pm(cm)} | "
          f"{pm(pre)} | {np.mean(par):.0f}k | {pm(tst) if tst else '-'} |")
