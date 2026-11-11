#!/usr/bin/env python3
"""Barras de erro por método (média ± dp entre sementes) + cada execução como ponto.
Uso: python plot_erro.py [results] [analysis]"""
import glob
import json
import os
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RES = sys.argv[1] if len(sys.argv) > 1 else "results"
OUT = sys.argv[2] if len(sys.argv) > 2 else "analysis"
DATASETS = [("mnist", "MNIST"), ("fashion", "Fashion-MNIST"), ("svhn", "SVHN"), ("cifar10", "CIFAR-10")]
METHODS = [("steady_random", "M1\nsteady state\naleatório", "#d1495b"),
           ("majority", "M2\nmaioria", "#2e86ab"),
           ("elitist", "M3\nelitista", "#3b8b3b")]
PAPER = {  # Tabela I: melhor rede, média ± dp (10 execuções)
    "mnist": [(98.13, 0.15), (97.98, 0.13)], "fashion": [(88.54, 0.70), (88.44, 0.36)],
    "svhn": [(79.86, 2.06), (80.22, 0.89)], "cifar10": [(51.35, 3.44), (52.44, 0.85)],
}
PAPER_LAB = ["Original\ncom\nespeciação", "Original\nsem\nespeciação"]

runs = defaultdict(list)
for f in glob.glob(os.path.join(RES, "*.json")):
    d = json.load(open(f))
    if "final" in d:
        runs[(d["config"]["dataset"], d["config"]["method"])].append(
            (d["config"]["seed"], 100 * d["final"]["champ_test"]))

rng = np.random.default_rng(0)
fig, axes = plt.subplots(1, 4, figsize=(17, 4.6))
for ax, (d, dl) in zip(axes, DATASETS):
    x = 0
    ticks, labels = [], []
    for (mu, sd), lab in zip(PAPER[d], PAPER_LAB):
        ax.errorbar(x, mu, yerr=sd, fmt="s", color="#555", ecolor="#555", capsize=6, ms=7, lw=1.6)
        ticks.append(x); labels.append(lab); x += 1
    ax.axvline(x - 0.5, color="#bbb", lw=0.8, ls="--")
    for m, lab, col in METHODS:
        v = np.array([a for _, a in sorted(runs[(d, m)])])
        ax.scatter(x + rng.uniform(-0.17, 0.17, len(v)), v, s=18, color=col, alpha=0.55, lw=0, zorder=2)
        ax.errorbar(x, v.mean(), yerr=v.std(ddof=1), fmt="o", color=col, ecolor=col, capsize=6, ms=8,
                    lw=1.8, zorder=3, mec="white", mew=0.8)
        ticks.append(x); labels.append(lab); x += 1
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_title(dl)
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(-0.6, x - 0.4)
axes[0].set_ylabel("Acurácia de teste da melhor rede (%)")
fig.suptitle("Variação entre execuções (10 sementes): média ± desvio-padrão; pontos = execuções individuais",
             fontsize=11)
fig.tight_layout()
os.makedirs(OUT, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"erro_por_metodo.{ext}"), dpi=150)
print("salvo", os.path.join(OUT, "erro_por_metodo.png"))
for d, dl in DATASETS:
    for m, lab, _ in METHODS:
        v = [a for _, a in sorted(runs[(d, m)])]
        print(f"{dl:14s} {m:14s} min={min(v):.2f} max={max(v):.2f} amplitude={max(v)-min(v):.2f}")
