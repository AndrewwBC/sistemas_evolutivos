#!/usr/bin/env python3
"""Curva de erro (100 - acurácia da melhor rede) ao longo das gerações, por método.
Linha = média das sementes; faixa = ± desvio-padrão; tracejado = erro final do paper (Tabela I).
Uso: python plot_curva_erro.py [results] [analysis]"""
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
METHODS = [("steady_random", "M1 steady state aleatório", "#d1495b"),
           ("majority", "M2 crossover por maioria", "#2e86ab"),
           ("elitist", "M3 crossover elitista", "#3b8b3b")]
PAPER_BEST = {"mnist": 98.13, "fashion": 88.54, "svhn": 79.86, "cifar10": 51.35}  # com especiação

runs = defaultdict(list)
for f in glob.glob(os.path.join(RES, "*.json")):
    d = json.load(open(f))
    if "final" in d:
        runs[(d["config"]["dataset"], d["config"]["method"])].append([g["best"] for g in d["gens"]])

fig, axes = plt.subplots(1, 4, figsize=(17, 4.4))
for ax, (d, dl) in zip(axes, DATASETS):
    for m, lab, col in METHODS:
        E = 100 * (1 - np.array(runs[(d, m)]))  # sementes x gerações
        mu, sd = E.mean(0), E.std(0, ddof=1)
        x = np.arange(1, E.shape[1] + 1)
        ax.plot(x, mu, color=col, lw=2, label=lab)
        ax.fill_between(x, mu - sd, mu + sd, color=col, alpha=0.15, lw=0)
    ax.axhline(100 - PAPER_BEST[d], color="#444", ls="--", lw=1.3, label="Paper original (final, g100)")
    ax.set_title(dl)
    ax.set_xlabel("Geração")
    ax.set_xlim(1, 100)
    ax.grid(alpha=0.3)
    # zoom na região interessante: do erro inicial até um pouco abaixo do melhor final
    finals = [100 * (1 - np.array(runs[(d, m)]))[:, -1].mean() for m, _, _ in METHODS]
    lo = min(finals + [100 - PAPER_BEST[d]])
    hi = max(100 * (1 - np.array(runs[(d, m)]))[:, 2].mean() for m, _, _ in METHODS)
    ax.set_ylim(max(0, lo - 0.25 * (hi - lo)), hi + 0.15 * (hi - lo))
axes[0].set_ylabel("Erro da melhor rede (%)")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, fontsize=10, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1))
os.makedirs(OUT, exist_ok=True)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, f"curva_erro.{ext}"), dpi=150)
print("salvo", os.path.join(OUT, "curva_erro.png"))
