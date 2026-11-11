#!/usr/bin/env python3
"""Compara M1-M3 com o método original reimplementado no mesmo framework (e com a Tabela I).
Gera analysis/comparacao_reimpl.md e analysis/curva_erro_reimpl.{png,pdf}."""
import glob
import json
import os
from collections import defaultdict

import numpy as np
from scipy.stats import mannwhitneyu

DATASETS = [("mnist", "MNIST"), ("fashion", "Fashion-MNIST"), ("svhn", "SVHN"), ("cifar10", "CIFAR-10")]
METHODS = [("paper_spec", "Original reimpl., com especiação", "#6c6c6c", "-"),
           ("paper_nospec", "Original reimpl., sem especiação", "#a9a9a9", "-"),
           ("steady_random", "M1 steady state aleatório", "#d1495b", "-"),
           ("majority", "M2 crossover por maioria", "#2e86ab", "-"),
           ("elitist", "M3 crossover elitista", "#3b8b3b", "-")]
PUB = {"mnist": ((98.13, 0.15), (97.98, 0.13)), "fashion": ((88.54, 0.70), (88.44, 0.36)),
       "svhn": ((79.86, 2.06), (80.22, 0.89)), "cifar10": ((51.35, 3.44), (52.44, 0.85))}


def load(pattern):
    R = defaultdict(list)
    for f in glob.glob(pattern):
        d = json.load(open(f))
        if "final" in d:
            R[(d["config"]["dataset"], d["config"]["method"])].append(d)
    return R


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0
    for r, i in enumerate(order):
        run = max(run, (len(ps) - r) * ps[i])
        adj[i] = min(1, run)
    return adj


pm = lambda x: f"{np.mean(x):.2f} ± {np.std(x, ddof=1):.2f}" if len(x) > 1 else f"{np.mean(x):.2f}"
lines = []


def table(R, title, datasets):
    lines.extend([f"## {title}", "",
                  "| Dataset | Método | n | Teste (melhor rede) | Média pop. (val) | Filhos antes do BP | Params | Espécies (final) |",
                  "|---|---|---|---|---|---|---|---|"])
    tests = []
    for d, dl in datasets:
        a, b = PUB[d]
        lines.append(f"| {dl} | Paper publicado (Tabela I), com esp. | 10 | {a[0]:.2f} ± {a[1]:.2f} | | | | |")
        for m, lab, _, _ in METHODS:
            v = R.get((d, m), [])
            if not v:
                continue
            t = [100 * x["final"]["champ_test"] for x in v]
            mu = [100 * x["gens"][-1]["mean"] for x in v]
            pre = [100 * np.mean([g["offspring_pre_bp"] for g in x["gens"][-20:]]) for x in v]
            par = np.mean([x["final"]["champ_params"] for x in v]) / 1e3
            sp = [x["gens"][-1].get("n_species") for x in v]
            sp = f"{np.mean(sp):.1f}" if sp[0] is not None and m == "paper_spec" else ""
            lines.append(f"| {dl} | {lab} | {len(v)} | {pm(t)} | {pm(mu)} | {pm(pre)} | {par:.0f}k | {sp} |")
        for m in ("majority", "elitist", "steady_random"):
            for ref in ("paper_spec", "paper_nospec"):
                x = [100 * r["final"]["champ_test"] for r in R.get((d, m), [])]
                y = [100 * r["final"]["champ_test"] for r in R.get((d, ref), [])]
                if len(x) > 1 and len(y) > 1:
                    tests.append((dl, m, ref, np.mean(x) - np.mean(y), mannwhitneyu(x, y).pvalue))
    if tests:
        adj = holm(np.array([t[4] for t in tests]))
        short = {"majority": "M2", "elitist": "M3", "steady_random": "M1",
                 "paper_spec": "orig. c/ esp.", "paper_nospec": "orig. s/ esp."}
        lines.extend(["", f"Mann-Whitney U bicaudal (teste da melhor rede), p ajustado por Holm ({len(tests)} testes):", "",
                      "| Dataset | Comparação | Δ (pp) | p | p (Holm) |", "|---|---|---|---|---|"])
        for (dl, m, ref, dd, p), pa in zip(tests, adj):
            lines.append(f"| {dl} | {short[m]} × {short[ref]} | {dd:+.2f} | {p:.2g} | {pa:.2g} |")
    lines.append("")


classic = load("results/*.json")
modern = load("results_modern/*.json")
lines.append("# Método original reimplementado × M1-M3")
lines.append("")
lines.append("Mesmo framework, treino, população (24) e nº de filhos por geração (12); a fitness é a acurácia "
             "de validação. Valores do paper publicado: Tabela I (fitness = acurácia de teste).")
lines.append("")
table(classic, "CNN clássica (10 sementes)", DATASETS)
table(modern, "CNN moderna, CIFAR-10 (3 sementes)", [("cifar10", "CIFAR-10")])
os.makedirs("analysis", exist_ok=True)
open("analysis/comparacao_reimpl.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 5, figsize=(21, 4.4))
panels = [(classic, d, dl + " (clássica)") for d, dl in DATASETS] + [(modern, "cifar10", "CIFAR-10 (moderna)")]
for ax, (R, d, title) in zip(axes, panels):
    for m, lab, col, ls in METHODS:
        v = R.get((d, m))
        if not v:
            continue
        E = 100 * (1 - np.array([[g["best"] for g in x["gens"]] for x in v]))
        mu, sd = E.mean(0), E.std(0, ddof=1)
        x = np.arange(1, E.shape[1] + 1)
        ax.plot(x, mu, color=col, ls=ls, lw=2, label=lab)
        ax.fill_between(x, mu - sd, mu + sd, color=col, alpha=0.13, lw=0)
    ax.axhline(100 - PUB[d][0][0], color="#444", ls=":", lw=1.3, label="Paper publicado (final, g100)")
    ax.set_title(title)
    ax.set_xlabel("Geração")
    ax.set_xlim(1, 100)
    ax.grid(alpha=0.3)
    fin = [100 * (1 - np.mean([x["gens"][-1]["best"] for x in R[(d, m)]])) for m, *_ in METHODS if (d, m) in R]
    early = [100 * (1 - np.mean([x["gens"][2]["best"] for x in R[(d, m)]])) for m, *_ in METHODS if (d, m) in R]
    lo, hi = min(fin + [100 - PUB[d][0][0]]), max(early)
    ax.set_ylim(max(0, lo - 0.25 * (hi - lo)), hi + 0.1 * (hi - lo))
axes[0].set_ylabel("Erro da melhor rede (%) — validação")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=6, fontsize=10, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"analysis/curva_erro_reimpl.{ext}", dpi=150)
print("salvo analysis/curva_erro_reimpl.png")
