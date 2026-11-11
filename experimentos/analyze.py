#!/usr/bin/env python3
"""Agrega results/*.json: tabela (markdown) + curvas por dataset e método."""
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

RES = sys.argv[1] if len(sys.argv) > 1 else "results"
OUT = sys.argv[2] if len(sys.argv) > 2 else "analysis"
DATASETS = ["mnist", "fashion", "svhn", "cifar10"]
METHODS = ["steady_random", "majority", "elitist"]
LABEL = {"steady_random": "M1 steady state aleatório", "majority": "M2 crossover por maioria",
         "elitist": "M3 crossover elitista"}
DLABEL = {"mnist": "MNIST", "fashion": "Fashion-MNIST", "svhn": "SVHN", "cifar10": "CIFAR-10"}

runs = defaultdict(list)
for f in sorted(glob.glob(os.path.join(RES, "*.json"))):
    d = json.load(open(f))
    if "final" in d:
        c = d["config"]
        runs[(c["dataset"], c["method"])].append(d)
os.makedirs(OUT, exist_ok=True)


def ms(xs, pct=True):
    xs = np.asarray(xs, float) * (100 if pct else 1)
    return f"{xs.mean():.2f} ± {xs.std(ddof=1) if len(xs) > 1 else 0:.2f}"


rows = ["| Dataset | Método | n | Teste (campeão final) | Teste (melhor de todos) | Média da pop. (val) | Filhos antes do BP | Parâmetros do campeão |",
        "|---|---|---|---|---|---|---|---|"]
summary = {}
for d in DATASETS:
    for m in METHODS:
        R = runs.get((d, m), [])
        if not R:
            continue
        test = [r["final"]["champ_test"] for r in R]
        best = [r["final"]["best_ever_test"] for r in R]
        meanv = [r["gens"][-1]["mean"] for r in R]
        pre = [np.mean([g["offspring_pre_bp"] for g in r["gens"][-20:] if g["offspring_pre_bp"] is not None]) for r in R]
        par = [r["final"]["champ_params"] for r in R]
        summary[(d, m)] = dict(test=test, pre=pre)
        rows.append(f"| {DLABEL[d]} | {LABEL[m]} | {len(R)} | {ms(test)} | {ms(best)} | {ms(meanv)} | {ms(pre)} | "
                    f"{np.mean(par)/1e3:.0f}k |")

lines = ["# Resultados", "", "Médias ± desvio-padrão (%) entre sementes. "
         "'Filhos antes do BP' = acurácia média dos filhos recém-nascidos, só com os pesos herdados, "
         "nas últimas 20 gerações.", ""] + rows

try:
    from scipy.stats import mannwhitneyu
    lines += ["", "## Mann-Whitney U (bicaudal) — acurácia de teste do campeão final", "",
              "| Dataset | Comparação | p | Comparação | p | Comparação | p |", "|---|---|---|---|---|---|---|"]
    for d in DATASETS:
        cells = []
        for a, b in [("steady_random", "majority"), ("steady_random", "elitist"), ("majority", "elitist")]:
            if (d, a) in summary and (d, b) in summary and len(summary[(d, a)]["test"]) > 1:
                p = mannwhitneyu(summary[(d, a)]["test"], summary[(d, b)]["test"]).pvalue
                cells += [f"M{METHODS.index(a)+1} × M{METHODS.index(b)+1}", f"{p:.3g}"]
        if cells:
            lines.append(f"| {DLABEL[d]} | " + " | ".join(cells) + " |")
except ImportError:
    pass

# --- comparação com a Tabela I de Hadjiivanov & Blair (2021): média ± dp em 10 execuções,
# após 100 gerações. ATENÇÃO: no paper a fitness é a acurácia no TESTE (Seção III-B),
# então os números dele são otimistas; aqui a seleção usa validação e o teste é medido só no fim.
PAPER = {  # dataset: {variante: (melhor, média da pop., filhos antes do BP)}
    "mnist":   {"com esp.": ((98.13, 0.15), (96.8, 0.4), (95.6, 1.8)), "sem esp.": ((97.98, 0.13), (93.7, 1.1), (72.5, 10.7))},
    "svhn":    {"com esp.": ((79.86, 2.06), (70.2, 7.5), (66.5, 8.0)), "sem esp.": ((80.22, 0.89), (66.5, 3.1), (44.4, 7.4))},
    "fashion": {"com esp.": ((88.54, 0.70), (85.3, 1.4), (82.0, 4.3)), "sem esp.": ((88.44, 0.36), (83.3, 1.1), (64.9, 7.8))},
    "cifar10": {"com esp.": ((51.35, 3.44), (43.9, 4.8), (42.7, 5.1)), "sem esp.": ((52.44, 0.85), (41.9, 1.1), (32.4, 1.8))},
}
lines += ["", "## Comparação com o paper original (Tabela I)", "",
          "Δ = nosso − paper (com especiação), em pontos percentuais. Melhor rede: no paper, acurácia de teste "
          "da melhor rede (selecionada pelo teste); aqui, acurácia de teste do campeão selecionado pela validação.", "",
          "| Dataset | Abordagem | Melhor rede | Δ | Média da pop. | Δ | Filhos antes do BP | Δ |",
          "|---|---|---|---|---|---|---|---|"]
fmt = lambda t: f"{t[0]:.2f} ± {t[1]:.2f}"
for d in DATASETS:
    if not any((d, m) in runs for m in METHODS):
        continue
    ref = PAPER[d]["com esp."]
    for var, vals in PAPER[d].items():
        lines.append(f"| {DLABEL[d]} | Paper ({var}) | {fmt(vals[0])} | | {fmt(vals[1])} | | {fmt(vals[2])} | |")
    for m in METHODS:
        R = runs.get((d, m))
        if not R:
            continue
        ours = [
            100 * np.array([r["final"]["champ_test"] for r in R]),
            100 * np.array([r["gens"][-1]["mean"] for r in R]),
            100 * np.array(summary[(d, m)]["pre"]),
        ]
        cells = []
        for x, p in zip(ours, ref):
            sd = x.std(ddof=1) if len(x) > 1 else 0
            cells += [f"{x.mean():.2f} ± {sd:.2f}", f"{x.mean() - p[0]:+.2f}"]
        lines.append(f"| {DLABEL[d]} | {LABEL[m]} | " + " | ".join(cells) + " |")

open(os.path.join(OUT, "resultados.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit(0)

metrics = [("best", "Melhor da população (val)"), ("mean", "Média da população (val)"),
           ("offspring_pre_bp", "Filhos antes do BP (val)"), ("mean_params", "Parâmetros (média da pop.)")]
ds = [d for d in DATASETS if any((d, m) in runs for m in METHODS)]
if not ds:
    sys.exit(0)
fig, axes = plt.subplots(len(metrics), len(ds), figsize=(4.2 * len(ds), 3.2 * len(metrics)), squeeze=False)
colors = {"steady_random": "#d1495b", "majority": "#2e86ab", "elitist": "#3b8b3b"}
for j, d in enumerate(ds):
    for i, (key, title) in enumerate(metrics):
        ax = axes[i][j]
        for m in METHODS:
            R = runs.get((d, m))
            if not R:
                continue
            G = min(len(r["gens"]) for r in R)
            Y = np.array([[np.nan if r["gens"][g][key] is None else r["gens"][g][key] for g in range(G)] for r in R])
            mu, sd = np.nanmean(Y, 0), np.nanstd(Y, 0)
            x = np.arange(G)
            ax.plot(x, mu, color=colors[m], lw=1.6, label=LABEL[m])
            ax.fill_between(x, mu - sd, mu + sd, color=colors[m], alpha=0.15, lw=0)
        if i == 0:
            ax.set_title(DLABEL[d])
        if j == 0:
            ax.set_ylabel(title)
        if i == len(metrics) - 1:
            ax.set_xlabel("geração")
        ax.grid(alpha=0.3)
axes[0][0].legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "curvas.png"), dpi=130)
print("salvo", os.path.join(OUT, "curvas.png"))
