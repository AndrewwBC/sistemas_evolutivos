#!/usr/bin/env python3
"""CIFAR-10: curva de erro da melhor rede, CNN clássica (tracejada) x moderna (contínua), por método."""
import glob
import json
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

METHODS = [("steady_random", "M1 steady state aleatório", "#d1495b"),
           ("majority", "M2 crossover por maioria", "#2e86ab"),
           ("elitist", "M3 crossover elitista", "#3b8b3b")]
runs = defaultdict(list)
for arch, pat in (("classic", "results/cifar10_*.json"), ("modern", "results_modern/*.json")):
    for f in glob.glob(pat):
        d = json.load(open(f))
        if "final" in d:
            runs[(arch, d["config"]["method"])].append([g["best"] for g in d["gens"]])

fig, ax = plt.subplots(figsize=(8, 5))
for m, lab, col in METHODS:
    for arch, ls, alpha in (("classic", "--", 0.10), ("modern", "-", 0.18)):
        E = 100 * (1 - np.array(runs[(arch, m)]))
        mu, sd = E.mean(0), E.std(0, ddof=1)
        x = np.arange(1, E.shape[1] + 1)
        name = f"{lab} — {'CNN moderna' if arch == 'modern' else 'CNN clássica'} (n={len(E)})"
        ax.plot(x, mu, color=col, ls=ls, lw=2 if arch == "modern" else 1.4, label=name)
        ax.fill_between(x, mu - sd, mu + sd, color=col, alpha=alpha, lw=0)
ax.axhline(100 - 51.35, color="#444", ls=":", lw=1.5, label="Paper original (final, g100)")
ax.set_xlabel("Geração")
ax.set_ylabel("Erro da melhor rede (%) — validação")
ax.set_title("CIFAR-10: CNN clássica × CNN moderna")
ax.set_xlim(1, 100)
ax.set_ylim(20, 65)
ax.grid(alpha=0.3)
ax.legend(fontsize=7.5, loc="upper right")
fig.tight_layout()
os.makedirs("analysis", exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(f"analysis/cifar10_classica_vs_moderna.{ext}", dpi=150)
print("salvo analysis/cifar10_classica_vs_moderna.png")
