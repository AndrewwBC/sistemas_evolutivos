#!/usr/bin/env python3
"""Neuroevolução epigenética de CNNs com kernels de formato livre.

Compara três estratégias de reprodução sobre o mesmo framework:

  M1  steady_random  steady state aleatório: a cada nascimento, 2 pais sorteados
                     uniformemente, crossover uniforme sem viés (p=0.5), o filho
                     substitui um indivíduo sorteado uniformemente (os pais são
                     mantidos). Sem elitismo.
  M2  majority       crossover por maioria com k=3 pais (torneio): cada gene
                     estrutural (nº de camadas, stride, nº de kernels, formato de
                     cada kernel) recebe o valor majoritário/mediano; os pesos vêm
                     do pai mais apto entre os que formam a maioria. Filhos
                     substituem os piores.
  M3  elitist        crossover elitista: um pai é sempre o campeão, o outro vem de
                     torneio; uniforme com viés p=0.7 para o campeão. Filhos
                     substituem os piores; o campeão nunca é removido.

Comum aos três (para a comparação isolar a reprodução):
  * genoma em camadas (conv + FC), cada kernel com formato próprio (h x w ímpares),
    mutações estruturais iguais, herança epigenética dos pesos treinados;
  * a cada geração TODAS as redes treinam 1 época em 10% aleatórios do treino;
  * mesmo nº de nascimentos por geração e mesmo orçamento de treino.
"""
import argparse
import copy
import json
import math
import os
import random
import time

import numpy as np
import torch
import torch.nn.functional as F

DEV = "cuda" if torch.cuda.is_available() else "cpu"
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.benchmark = False

MAX_CONV_LAYERS = 6
MAX_KERNELS = 64
MAX_FC_LAYERS = 2
MAX_FC_NEURONS = 256
MIN_K, MAX_K = 1, 7

# Modo "modern" (--arch modern): conv -> BatchNorm -> (+ atalho residual) -> ReLU,
# global average pooling antes da parte densa, redes iniciais maiores, data augmentation,
# AdamW e bf16. A evolução (métodos, mutações, herança epigenética) é a mesma.
MODERN = False
AUGMENT = False
FLIP = False


def set_modern(on):
    global MODERN, MAX_CONV_LAYERS, MAX_KERNELS
    MODERN = on
    if on:
        MAX_CONV_LAYERS, MAX_KERNELS = 12, 160
N_CLASSES = 10
DATASETS = ("mnist", "fashion", "svhn", "cifar10")
METHODS = ("steady_random", "majority", "elitist", "paper_spec", "paper_nospec")


# ----------------------------------------------------------------------------- dados
def load_data(name, root):
    import torchvision as tv

    if name in ("mnist", "fashion"):
        cls = tv.datasets.MNIST if name == "mnist" else tv.datasets.FashionMNIST
        tr, te = cls(root, train=True, download=True), cls(root, train=False, download=True)
        Xtr, Ytr = tr.data.unsqueeze(1), tr.targets
        Xte, Yte = te.data.unsqueeze(1), te.targets
    elif name == "cifar10":
        tr = tv.datasets.CIFAR10(root, train=True, download=True)
        te = tv.datasets.CIFAR10(root, train=False, download=True)
        Xtr, Ytr = torch.from_numpy(tr.data).permute(0, 3, 1, 2), torch.tensor(tr.targets)
        Xte, Yte = torch.from_numpy(te.data).permute(0, 3, 1, 2), torch.tensor(te.targets)
    elif name == "svhn":
        tr = tv.datasets.SVHN(root, split="train", download=True)
        te = tv.datasets.SVHN(root, split="test", download=True)
        Xtr, Ytr = torch.from_numpy(tr.data), torch.from_numpy(tr.labels)
        Xte, Yte = torch.from_numpy(te.data), torch.from_numpy(te.labels)
    else:
        raise ValueError(name)
    Xtr, Xte = Xtr.float() / 255, Xte.float() / 255
    mean, std = Xtr.mean((0, 2, 3), keepdim=True), Xtr.std((0, 2, 3), keepdim=True)
    Xtr, Xte = (Xtr - mean) / std, (Xte - mean) / std
    # split de validação fixo (independe da semente da execução)
    perm = torch.randperm(len(Xtr), generator=torch.Generator().manual_seed(0))
    va, trn = perm[:5000], perm[5000:]
    to = lambda t: t.to(DEV)
    return dict(
        Xtr=to(Xtr[trn]), Ytr=to(Ytr[trn].long()),
        Xva=to(Xtr[va]), Yva=to(Ytr[va].long()),
        Xte=to(Xte), Yte=to(Yte.long()),
        in_shape=tuple(Xtr.shape[1:]),
    )


# ----------------------------------------------------------------------------- genoma
# genoma = {'convs': [{'stride', 'kernels': [{'h','w','W','b'}]}],
#           'fcs':   [{'neurons': [{'W','b'}]}],      # camadas FC ocultas
#           'out':   {'neurons': [...10]}}
# W=None => nó/conexões novas, inicializados no build. Pesos de entrada são
# posicionais: o canal j do kernel corresponde ao j-ésimo nó da camada anterior.

def new_kernel(h=None, w=None):
    return {"h": h or random.choice([1, 3, 5]), "w": w or random.choice([1, 3, 5]), "W": None, "b": None}


def new_neuron():
    return {"W": None, "b": None}


def random_genome():
    if MODERN:
        n = random.randint(3, 5)
        convs = [{"stride": 2 if i in (1, 3) else 1,
                  "kernels": [new_kernel() for _ in range(random.randint(32, 96))]} for i in range(n)]
        fcs = [{"neurons": [new_neuron() for _ in range(random.randint(64, 128))]}] if random.random() < 0.5 else []
        return {"convs": convs, "fcs": fcs, "out": {"neurons": [new_neuron() for _ in range(N_CLASSES)]}}
    convs = []
    for i in range(random.choice([1, 2])):
        convs.append({
            "stride": random.choice([1, 2]) if i == 0 else 1,
            "kernels": [new_kernel() for _ in range(random.randint(4, 12))],
        })
    fcs = [{"neurons": [new_neuron() for _ in range(random.randint(32, 64))]}] if random.random() < 0.5 else []
    return {"convs": convs, "fcs": fcs, "out": {"neurons": [new_neuron() for _ in range(N_CLASSES)]}}


def conv_out_shape(g, in_shape):
    C, H, W = in_shape
    for L in g["convs"]:
        s = L["stride"]
        H, W, C = (H - 1) // s + 1, (W - 1) // s + 1, len(L["kernels"])
    return C, H, W


def n_params(g, in_shape):
    C, H, W = in_shape
    n = 0
    for L in g["convs"]:
        n += sum(C * k["h"] * k["w"] + (2 if MODERN else 1) for k in L["kernels"])
        s = L["stride"]
        H, W, C = (H - 1) // s + 1, (W - 1) // s + 1, len(L["kernels"])
    D = C if MODERN else C * H * W
    for L in g["fcs"] + [g["out"]]:
        N = len(L["neurons"])
        n += D * N + N
        D = N
    return n


def arch_str(g):
    parts = []
    for L in g["convs"]:
        shapes = {}
        for k in L["kernels"]:
            key = f"{k['h']}x{k['w']}"
            shapes[key] = shapes.get(key, 0) + 1
        sh = ",".join(f"{v}*{s}" for s, v in sorted(shapes.items(), key=lambda t: -t[1]))
        parts.append(f"C{len(L['kernels'])}/s{L['stride']}[{sh}]")
    parts += [f"F{len(L['neurons'])}" for L in g["fcs"]]
    return " > ".join(parts + ["out10"])


# ----------------------------------------------------------------------------- fenótipo
def fit_channels(W, C):
    """Ajusta a 1ª dimensão (canais de entrada) por corte ou zeros no fim."""
    c0 = W.shape[0]
    if c0 == C:
        return W
    if c0 > C:
        return W[:C]
    return torch.cat([W, W.new_zeros((C - c0,) + tuple(W.shape[1:]))], 0)


def fit_kernel(W, h, w):
    """Corta/completa com zeros, centralizado, as duas últimas dimensões."""
    _, h0, w0 = W.shape
    out = W.new_zeros(W.shape[0], h, w)
    ch, cw = min(h, h0), min(w, w0)
    oh, ow, ih, iw = (h - ch) // 2, (w - cw) // 2, (h0 - ch) // 2, (w0 - cw) // 2
    out[:, oh:oh + ch, ow:ow + cw] = W[:, ih:ih + ch, iw:iw + cw]
    return out


def adapt_fc(W, in_sh):
    if W is None or W.dim() != len(in_sh):
        return None
    if len(in_sh) == 3 and tuple(W.shape[1:]) != tuple(in_sh[1:]):
        return None  # mudança espacial (stride) => conexões reiniciadas
    return fit_channels(W, in_sh[0])


class Pheno:
    """Rede PyTorch montada a partir do genoma; os kernels de uma camada são
    empilhados num bloco Hmax x Wmax com máscara fixa (zeros fora do formato).
    No modo moderno: conv (sem bias) -> BatchNorm -> + atalho residual -> ReLU,
    e global average pooling antes das camadas densas."""

    def __init__(self, g, in_shape):
        self.g = g
        self.training = False
        C, H, W = in_shape
        self.convs = []
        for l, L in enumerate(g["convs"]):
            ks = L["kernels"]
            K, Hm, Wm = len(ks), max(k["h"] for k in ks), max(k["w"] for k in ks)
            Wt = torch.zeros(K, C, Hm, Wm, device=DEV)
            bt = torch.zeros(K, device=DEV)
            mask = torch.zeros(K, 1, Hm, Wm, device=DEV)
            bn = torch.zeros(4, K, device=DEV)  # gamma, beta, running_mean, running_var
            bn[0], bn[3] = 1.0, 1.0
            offs = []
            for i, k in enumerate(ks):
                oh, ow = (Hm - k["h"]) // 2, (Wm - k["w"]) // 2
                offs.append((oh, ow))
                mask[i, 0, oh:oh + k["h"], ow:ow + k["w"]] = 1
                if k["W"] is None:
                    w0 = torch.randn(C, k["h"], k["w"], device=DEV) * math.sqrt(2 / (C * k["h"] * k["w"]))
                else:
                    w0 = fit_channels(k["W"], C)
                    bt[i] = k["b"]
                if MODERN and k.get("bn") is not None:
                    bn[:, i] = k["bn"]
                Wt[i, :, oh:oh + k["h"], ow:ow + k["w"]] = w0
            gamma, beta = bn[0].clone().requires_grad_(), bn[1].clone().requires_grad_()
            rm, rv = bn[2].clone(), bn[3].clone()
            self.convs.append(dict(W=Wt.requires_grad_(), b=bt.requires_grad_(), mask=mask, s=L["stride"],
                                   pad=(Hm // 2, Wm // 2), offs=offs, gamma=gamma, beta=beta, rm=rm, rv=rv,
                                   res=MODERN and l > 0))
            s = L["stride"]
            H, W, C = (H - 1) // s + 1, (W - 1) // s + 1, K
        in_sh = (C,) if MODERN else (C, H, W)
        self.fcs = []
        layers = g["fcs"] + [g["out"]]
        for j, L in enumerate(layers):
            ns = L["neurons"]
            D = int(np.prod(in_sh))
            Wt = torch.zeros(len(ns), D, device=DEV)
            bt = torch.zeros(len(ns), device=DEV)
            gain = 1.0 if j == len(layers) - 1 else 2.0
            for i, n in enumerate(ns):
                w0 = adapt_fc(n["W"], in_sh)
                if w0 is None:
                    w0 = torch.randn(in_sh, device=DEV) * math.sqrt(gain / D)
                elif n["b"] is not None:
                    bt[i] = n["b"]
                Wt[i] = w0.reshape(-1)
            self.fcs.append([Wt.requires_grad_(), bt.requires_grad_(), in_sh])
            in_sh = (len(ns),)

    def params(self):
        if MODERN:
            ps = [p for c in self.convs for p in (c["W"], c["gamma"], c["beta"])]
        else:
            ps = [p for c in self.convs for p in (c["W"], c["b"])]
        return ps + [p for f in self.fcs for p in f[:2]]

    @staticmethod
    def shortcut(x, K, s):
        """Atalho residual sem parâmetros: subamostra pelo stride e corta/completa canais."""
        if s > 1:
            x = x[:, :, ::s, ::s]
        C = x.shape[1]
        if C > K:
            return x[:, :K]
        if C < K:
            return F.pad(x, (0, 0, 0, 0, 0, K - C))
        return x

    def forward(self, x):
        for c in self.convs:
            if MODERN:
                y = F.conv2d(x, c["W"] * c["mask"], None, c["s"], c["pad"])
                y = F.batch_norm(y, c["rm"], c["rv"], c["gamma"], c["beta"], self.training, 0.1, 1e-5)
                if c["res"]:
                    y = y + self.shortcut(x, y.shape[1], c["s"])
                x = F.relu(y)
            else:
                x = F.relu(F.conv2d(x, c["W"] * c["mask"], c["b"], c["s"], c["pad"]))
        x = x.mean((2, 3)) if MODERN else x.flatten(1)
        for j, (Wt, bt, _) in enumerate(self.fcs):
            x = F.linear(x, Wt, bt)
            if j < len(self.fcs) - 1:
                x = F.relu(x)
        return x

    @torch.no_grad()
    def writeback(self):
        """Grava os pesos treinados de volta no genoma (herança epigenética)."""
        for c, L in zip(self.convs, self.g["convs"]):
            for i, (k, (oh, ow)) in enumerate(zip(L["kernels"], c["offs"])):
                k["W"] = c["W"][i, :, oh:oh + k["h"], ow:ow + k["w"]].detach().clone()
                k["b"] = c["b"][i].detach().clone()
                if MODERN:
                    k["bn"] = torch.stack([c["gamma"][i], c["beta"][i], c["rm"][i], c["rv"][i]]).detach().clone()
        for (Wt, bt, in_sh), L in zip(self.fcs, self.g["fcs"] + [self.g["out"]]):
            for i, n in enumerate(L["neurons"]):
                n["W"] = Wt[i].detach().reshape(in_sh).clone()
                n["b"] = bt[i].detach().clone()


def augment(x):
    """Recorte aleatório com padding 4 (+ espelhamento horizontal se FLIP), por amostra, na GPU."""
    B, C, H, W = x.shape
    xp = F.pad(x, (4, 4, 4, 4))
    i = torch.randint(0, 9, (B,), device=x.device)
    j = torch.randint(0, 9, (B,), device=x.device)
    rows = (i[:, None] + torch.arange(H, device=x.device))[:, None, :, None]
    cols = (j[:, None] + torch.arange(W, device=x.device))[:, None, None, :]
    out = xp[torch.arange(B, device=x.device)[:, None, None, None],
             torch.arange(C, device=x.device)[None, :, None, None], rows, cols]
    if FLIP:
        flip = torch.rand(B, device=x.device) < 0.5
        out = torch.where(flip[:, None, None, None], out.flip(3), out)
    return out


def train_epoch(g, data, frac, bs, lr):
    ph = Pheno(g, data["in_shape"])
    ph.training = True
    X, Y = data["Xtr"], data["Ytr"]
    idx = torch.randperm(len(X), device=DEV)[: int(frac * len(X))]
    if MODERN:
        opt = torch.optim.AdamW(ph.params(), lr=lr, weight_decay=5e-4)
    else:
        opt = torch.optim.Adam(ph.params(), lr=lr)
    for i in range(0, len(idx), bs):
        b = idx[i:i + bs]
        xb = augment(X[b]) if AUGMENT else X[b]
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=MODERN and DEV == "cuda"):
            loss = F.cross_entropy(ph.forward(xb).float(), Y[b])
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    ph.writeback()


@torch.no_grad()
def accuracy(g, X, Y, in_shape, bs=None):
    bs = bs or (1024 if MODERN else 4096)
    ph = Pheno(g, in_shape)
    correct = torch.zeros((), device=DEV)
    for i in range(0, len(X), bs):
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=MODERN and DEV == "cuda"):
            out = ph.forward(X[i:i + bs])
        correct += (out.argmax(1) == Y[i:i + bs]).sum()
    return (correct / len(X)).item()


# ----------------------------------------------------------------------------- mutação
def del_input(nodes, idx):
    for n in nodes:
        if n["W"] is not None and n["W"].shape[0] > idx:
            n["W"] = torch.cat([n["W"][:idx], n["W"][idx + 1:]], 0)


def consumers_of_conv(g, l):
    if l + 1 < len(g["convs"]):
        return g["convs"][l + 1]["kernels"]
    return (g["fcs"][0] if g["fcs"] else g["out"])["neurons"]


def consumers_of_fc(g, j):
    return g["fcs"][j + 1]["neurons"] if j + 1 < len(g["fcs"]) else g["out"]["neurons"]


def m_add_kernel(g, in_ch):
    ls = [L for L in g["convs"] if len(L["kernels"]) < MAX_KERNELS]
    if not ls:
        return False
    random.choice(ls)["kernels"].append(new_kernel())  # canal novo nos consumidores = 0
    return True


def m_remove_kernel(g, in_ch):
    ls = [l for l, L in enumerate(g["convs"]) if len(L["kernels"]) > 1]
    if not ls:
        return False
    l = random.choice(ls)
    i = random.randrange(len(g["convs"][l]["kernels"]))
    g["convs"][l]["kernels"].pop(i)
    del_input(consumers_of_conv(g, l), i)
    return True


def m_resize_kernel(g, in_ch):
    """A mutação do paper: redimensiona UM kernel em uma dimensão (±2, mantém ímpar)."""
    if not g["convs"]:
        return False
    k = random.choice(random.choice(g["convs"])["kernels"])
    dim = random.choice(["h", "w"])
    new = k[dim] + random.choice([-2, 2])
    if not MIN_K <= new <= MAX_K:
        return False
    k[dim] = new
    if k["W"] is not None:
        k["W"] = fit_kernel(k["W"], k["h"], k["w"])
    return True


def m_add_conv_layer(g, in_ch):
    if len(g["convs"]) >= MAX_CONV_LAYERS:
        return False
    pos = random.randint(0, len(g["convs"]))
    C = in_ch if pos == 0 else len(g["convs"][pos - 1]["kernels"])
    ks = []
    for c in range(C):  # inicialização identidade (preserva a função, Net2Net)
        W = torch.zeros(C, 3, 3, device=DEV)
        W[c, 1, 1] = 1.0
        ks.append({"h": 3, "w": 3, "W": W, "b": torch.zeros((), device=DEV),
                   "bn": torch.tensor([1.0, 0.0, 0.0, 1.0], device=DEV) if MODERN else None})
    g["convs"].insert(pos, {"stride": 1, "kernels": ks})
    return True


def m_remove_conv_layer(g, in_ch):
    if len(g["convs"]) <= (1 if MODERN else 0):
        return False
    g["convs"].pop(random.randrange(len(g["convs"])))
    return True


def m_stride(g, in_ch):
    if not g["convs"]:
        return False
    L = random.choice(g["convs"])
    L["stride"] = 2 if L["stride"] == 1 else 1
    return True


def m_add_fc_neuron(g, in_ch):
    ls = [L for L in g["fcs"] if len(L["neurons"]) < MAX_FC_NEURONS]
    if not ls:
        return False
    random.choice(ls)["neurons"].append(new_neuron())
    return True


def m_remove_fc_neuron(g, in_ch):
    ls = [j for j, L in enumerate(g["fcs"]) if len(L["neurons"]) > 1]
    if not ls:
        return False
    j = random.choice(ls)
    i = random.randrange(len(g["fcs"][j]["neurons"]))
    g["fcs"][j]["neurons"].pop(i)
    del_input(consumers_of_fc(g, j), i)
    return True


def m_add_fc_layer(g, in_ch):
    if len(g["fcs"]) >= MAX_FC_LAYERS:
        return False
    if g["fcs"]:  # identidade após a última oculta
        N = len(g["fcs"][-1]["neurons"])
        ns = []
        for i in range(N):
            W = torch.zeros(N, device=DEV)
            W[i] = 1.0
            ns.append({"W": W, "b": torch.zeros((), device=DEV)})
        g["fcs"].append({"neurons": ns})
    else:
        g["fcs"].append({"neurons": [new_neuron() for _ in range(32)]})
    return True


def m_remove_fc_layer(g, in_ch):
    if not g["fcs"]:
        return False
    g["fcs"].pop(random.randrange(len(g["fcs"])))
    return True


MUTATIONS = [
    (m_add_kernel, 0.18), (m_remove_kernel, 0.10), (m_resize_kernel, 0.25),
    (m_add_conv_layer, 0.07), (m_remove_conv_layer, 0.04), (m_stride, 0.03),
    (m_add_fc_neuron, 0.12), (m_remove_fc_neuron, 0.07),
    (m_add_fc_layer, 0.08), (m_remove_fc_layer, 0.06),
]


def mutate(g, in_ch, extra_p=0.5):
    n_target = 1 + int(random.random() < extra_p)
    done, tries = 0, 0
    fns, ws = zip(*MUTATIONS)
    while done < n_target and tries < 30:
        tries += 1
        if random.choices(fns, ws)[0](g, in_ch):
            done += 1
    return g


# ----------------------------------------------------------------------------- crossovers
def clone_struct(x):
    return copy.deepcopy(x)


def uni_nodes(na, nb, p):
    out = []
    for i in range(max(len(na), len(nb))):
        if i < len(na) and i < len(nb):
            out.append(clone_struct(na[i] if random.random() < p else nb[i]))
        elif i < len(na):
            if random.random() < p:
                out.append(clone_struct(na[i]))
        elif random.random() < 1 - p:
            out.append(clone_struct(nb[i]))
    if not out:
        out.append(clone_struct((na or nb)[0]))
    return out


def uni_layers(La, Lb, p, key, extra=None):
    out = []
    for i in range(max(len(La), len(Lb))):
        a = La[i] if i < len(La) else None
        b = Lb[i] if i < len(Lb) else None
        if a is not None and b is not None:
            layer = {key: uni_nodes(a[key], b[key], p)}
            if extra:
                layer[extra] = (a if random.random() < p else b)[extra]
            out.append(layer)
        elif a is not None:
            if random.random() < p:
                out.append(clone_struct(a))
        elif random.random() < 1 - p:
            out.append(clone_struct(b))
    return out


def uniform_crossover(A, B, p=0.5):
    """Uniforme nó a nó. p = probabilidade de cada gene vir de A."""
    return {
        "convs": uni_layers(A["convs"], B["convs"], p, "kernels", extra="stride"),
        "fcs": uni_layers(A["fcs"], B["fcs"], p, "neurons"),
        "out": {"neurons": uni_nodes(A["out"]["neurons"], B["out"]["neurons"], p)},
    }


def median_int(vals):
    return sorted(vals)[len(vals) // 2]


def mode_fittest(vals):
    """Valor mais frequente; empate => o do pai mais apto (vals em ordem de fitness)."""
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    top = max(cnt.values())
    return next(v for v in vals if cnt[v] == top)


def maj_nodes(lists, key):
    n = median_int([len(l) for l in lists]) if len(lists) >= 3 else len(lists[0])
    out = []
    for i in range(n):
        cands = [l[i] for l in lists if i < len(l)]
        if key is None:
            out.append(clone_struct(cands[0]))
        else:
            v = mode_fittest([key(c) for c in cands])
            out.append(clone_struct(next(c for c in cands if key(c) == v)))
    return out


def majority_crossover(P):
    """P: pais em ordem decrescente de fitness (k ímpar)."""
    convs = []
    for i in range(median_int([len(p["convs"]) for p in P])):
        have = [p["convs"][i] for p in P if i < len(p["convs"])]
        convs.append({
            "stride": mode_fittest([L["stride"] for L in have]),
            "kernels": maj_nodes([L["kernels"] for L in have], key=lambda k: (k["h"], k["w"])),
        })
    fcs = []
    for i in range(median_int([len(p["fcs"]) for p in P])):
        have = [p["fcs"][i] for p in P if i < len(p["fcs"])]
        fcs.append({"neurons": maj_nodes([L["neurons"] for L in have], key=None)})
    return {"convs": convs, "fcs": fcs, "out": clone_struct(P[0]["out"])}


# ----------------------------------------------------------------------------- seleção / reprodução
def tournament(pop, k, exclude=()):
    cands = [i for i in range(len(pop)) if i not in exclude]
    return max(random.sample(cands, min(k, len(cands))), key=lambda i: pop[i]["fit"])


def make_child(g, data, in_ch):
    c = mutate(g, in_ch)
    c["fit_pre"] = accuracy(c, data["Xva"], data["Yva"], data["in_shape"])  # antes do BP
    c["fit"] = c["fit_pre"]
    c["age"] = 0
    return c


def reproduce(pop, method, births, data, args):
    in_ch = data["in_shape"][0]
    born = []
    if method == "steady_random":
        for _ in range(births):
            ia, ib = random.sample(range(len(pop)), 2)
            c = make_child(uniform_crossover(pop[ia], pop[ib], 0.5), data, in_ch)
            j = random.choice([i for i in range(len(pop)) if i not in (ia, ib)])
            pop[j] = c  # substituição aleatória; o filho já pode ser pai no próximo nascimento
            born.append(c)
    elif method == "majority":
        for _ in range(births):
            idx = []
            for _ in range(args.k_parents):
                idx.append(tournament(pop, args.tour, exclude=idx))
            P = sorted((pop[i] for i in idx), key=lambda g: -g["fit"])
            born.append(make_child(majority_crossover(P), data, in_ch))
        worst = sorted(range(len(pop)), key=lambda i: pop[i]["fit"])[:births]
        for j, c in zip(worst, born):
            pop[j] = c
    elif method == "elitist":
        champ = max(range(len(pop)), key=lambda i: pop[i]["fit"])
        for _ in range(births):
            ib = tournament(pop, args.tour, exclude=[champ])
            born.append(make_child(uniform_crossover(pop[champ], pop[ib], args.elite_p), data, in_ch))
        worst = sorted((i for i in range(len(pop)) if i != champ), key=lambda i: pop[i]["fit"])[:births]
        for j, c in zip(worst, born):
            pop[j] = c
    elif method in ("paper_spec", "paper_nospec"):
        born = reproduce_paper(pop, births, data, args, speciation=(method == "paper_spec"))
    else:
        raise ValueError(method)
    return born


# ----------------------------------------------------------------------------- método original
# Reimplementação de Hadjiivanov & Blair (2021), Seções II-B e III, no mesmo framework:
# calibração (eq. 2), especiação por genoma, seleção proporcional ao fitness relativo,
# crossover nó a nó ponderado pelo fitness, similaridade (eq. 7-8) sem especiação e
# culling ponderado por idade/(f_r * c_r) (eq. 9). Treino, população e nº de filhos
# por geração são os mesmos dos métodos M1-M3.

def genome_key(g):
    """Espécie: mesmo nº de camadas de cada tipo e mesmo nº de nós em cada camada."""
    return (tuple(len(L["kernels"]) for L in g["convs"]), tuple(len(L["neurons"]) for L in g["fcs"]))


def logistic_rel(vals):
    v = np.asarray(vals, float)
    mu, sd = v.mean(), v.std()
    if sd < 1e-12:
        return np.full(len(v), 0.5)
    return 1 / (1 + np.exp(-(v - mu) / sd))


def species_groups(pop, speciation):
    if not speciation:
        return [list(range(len(pop)))]
    d = {}
    for i, g in enumerate(pop):
        d.setdefault(genome_key(g), []).append(i)
    return list(d.values())


def calibrate(pop, groups, in_shape):
    fr, cr = np.zeros(len(pop)), np.zeros(len(pop))
    for idx in groups:
        fr[idx] = logistic_rel([pop[i]["fit"] for i in idx])
        cr[idx] = logistic_rel([n_params(pop[i], in_shape) for i in idx])
    return fr, cr


def similarity(A, B):
    """Eq. 7-8: interseção de nós camada a camada (mesmo tipo) / união."""
    O = sum(min(len(a["kernels"]), len(b["kernels"])) for a, b in zip(A["convs"], B["convs"]))
    O += sum(min(len(a["neurons"]), len(b["neurons"])) for a, b in zip(A["fcs"], B["fcs"]))
    O += N_CLASSES
    n = lambda g: sum(len(L["kernels"]) for L in g["convs"]) + sum(len(L["neurons"]) for L in g["fcs"]) + N_CLASSES
    return O / (n(A) + n(B) - O)


def paper_nodes(na, nb, p, fa, fb):
    out = []
    for i in range(max(len(na), len(nb))):
        if i < len(na) and i < len(nb):
            out.append(clone_struct(na[i] if random.random() < p else nb[i]))
        elif i < len(na):
            if random.random() < fa:  # excesso herdado com prob. = fitness do pai maior
                out.append(clone_struct(na[i]))
        elif random.random() < fb:
            out.append(clone_struct(nb[i]))
    if not out:
        out.append(clone_struct((na or nb)[0]))
    return out


def paper_layers(La, Lb, p, fa, fb, key, extra=None):
    out = []
    for i in range(max(len(La), len(Lb))):
        a = La[i] if i < len(La) else None
        b = Lb[i] if i < len(Lb) else None
        if a is not None and b is not None:
            layer = {key: paper_nodes(a[key], b[key], p, fa, fb)}
            if extra:
                layer[extra] = (a if random.random() < p else b)[extra]
            out.append(layer)
        elif a is not None:
            if random.random() < fa:
                out.append(clone_struct(a))
        elif random.random() < fb:
            out.append(clone_struct(b))
    return out


def paper_crossover(A, B, fa, fb):
    p = fa / (fa + fb) if fa + fb > 0 else 0.5
    return {
        "convs": paper_layers(A["convs"], B["convs"], p, fa, fb, "kernels", extra="stride"),
        "fcs": paper_layers(A["fcs"], B["fcs"], p, fa, fb, "neurons"),
        "out": {"neurons": paper_nodes(A["out"]["neurons"], B["out"]["neurons"], p, fa, fb)},
    }


def strip(g):
    return clone_struct({"convs": g["convs"], "fcs": g["fcs"], "out": g["out"]})


def mutate_species(g, in_ch, present, max_species, extra_p=0.5):
    """Mutação com limite de espécies: uma mutação que criaria uma espécie nova é
    rejeitada quando o limite já foi atingido (Seção V do paper)."""
    n_target = 1 + int(random.random() < extra_p)
    done, tries = 0, 0
    fns, ws = zip(*MUTATIONS)
    k0 = genome_key(g)
    while done < n_target and tries < 30:
        tries += 1
        g2 = clone_struct(g)
        if not random.choices(fns, ws)[0](g2, in_ch):
            continue
        k = genome_key(g2)
        if k == k0 or k in present or len(present) < max_species:
            g, k0 = g2, k
            present.add(k)
            done += 1
    return g


def weighted_pick(idx, w, exclude=None):
    cand = [i for i in idx if i != exclude]
    p = np.array([w[i] for i in cand], float)
    p = p / p.sum() if p.sum() > 0 else np.full(len(cand), 1 / len(cand))
    return cand[np.random.choice(len(cand), p=p)]


def reproduce_paper(pop, births, data, args, speciation):
    in_ch, in_shape = data["in_shape"][0], data["in_shape"]
    groups = species_groups(pop, speciation)
    fr, cr = calibrate(pop, groups, in_shape)
    champs = {max(idx, key=lambda i: pop[i]["fit"]) for idx in groups}
    present = {genome_key(g) for g in pop}
    max_sp = args.species_max if speciation else 10 ** 9
    sizes = np.array([len(idx) for idx in groups], float)
    born = []
    for _ in range(births):
        if speciation:  # crossover só dentro da espécie
            idx = groups[np.random.choice(len(groups), p=sizes / sizes.sum())]
            if len(idx) == 1:
                child = strip(pop[idx[0]])
            else:
                ia = weighted_pick(idx, fr)
                ib = weighted_pick(idx, fr, exclude=ia)
                child = paper_crossover(pop[ia], pop[ib], fr[ia], fr[ib])
        else:  # qualquer par; crossover ocorre com probabilidade = similaridade
            child = None
            for _ in range(10):
                ia = weighted_pick(groups[0], fr)
                ib = weighted_pick(groups[0], fr, exclude=ia)
                if random.random() < similarity(pop[ia], pop[ib]):
                    child = paper_crossover(pop[ia], pop[ib], fr[ia], fr[ib])
                    break
            if child is None:
                child = strip(pop[ia] if pop[ia]["fit"] >= pop[ib]["fit"] else pop[ib])
        c = mutate_species(child, in_ch, present, max_sp)
        c["fit_pre"] = accuracy(c, data["Xva"], data["Yva"], in_shape)
        c["fit"], c["age"] = c["fit_pre"], 0
        born.append(c)
    # culling: filhos novos e campeões de cada espécie sobrevivem; os demais são
    # removidos um a um, sorteados com peso age / (f_r * c_r) (eq. 9)
    n_old = len(pop)
    allpop = pop + born
    cand = [i for i in range(n_old) if i not in champs]
    w = {i: pop[i]["age"] / max(fr[i] * cr[i], 1e-6) for i in cand}
    removed = set()
    while len(allpop) - len(removed) > args.pop and cand:
        i = weighted_pick(cand, w)
        removed.add(i)
        cand.remove(i)
    pop[:] = [g for i, g in enumerate(allpop) if i not in removed]
    return born


def init_population(args):
    if args.method != "paper_spec":
        return [random_genome() for _ in range(args.pop)]
    # espécies iniciais: estruturas aleatórias distintas; membros com a mesma estrutura
    templates, keys = [], set()
    while len(templates) < args.species_init:
        t = random_genome()
        if genome_key(t) not in keys:
            templates.append(t)
            keys.add(genome_key(t))
    pop = []
    for i in range(args.pop):
        t = templates[i % len(templates)]
        pop.append({
            "convs": [{"stride": L["stride"], "kernels": [new_kernel() for _ in L["kernels"]]} for L in t["convs"]],
            "fcs": [{"neurons": [new_neuron() for _ in L["neurons"]]} for L in t["fcs"]],
            "out": {"neurons": [new_neuron() for _ in range(N_CLASSES)]},
        })
    return pop


# ----------------------------------------------------------------------------- loop
def run(args):
    global AUGMENT, FLIP
    set_modern(args.arch == "modern")
    if args.mem_frac and DEV == "cuda":  # teto de memória por processo (servidor compartilhado)
        torch.cuda.set_per_process_memory_fraction(args.mem_frac)
    AUGMENT = args.augment
    FLIP = args.augment and args.dataset == "cifar10"
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    data = load_data(args.dataset, args.data)
    in_shape = data["in_shape"]
    os.makedirs(args.out, exist_ok=True)
    tag = "" if args.arch == "classic" else f"_{args.arch}"
    out_path = os.path.join(args.out, f"{args.dataset}_{args.method}{tag}_s{args.seed}.json")
    log = {"config": vars(args), "gens": []}

    pop = init_population(args)
    for g in pop:
        g["age"] = 0
    best_ever, best_ever_fit = None, -1.0
    born = []
    t0 = time.time()
    for gen in range(args.gens):
        for g in pop:  # aprendizado "em vida": todas treinam 1 época em 10% dos dados
            train_epoch(g, data, args.frac, args.bs, args.lr)
            g["fit"] = accuracy(g, data["Xva"], data["Yva"], in_shape)
            g["age"] += 1
        fits = [g["fit"] for g in pop]
        champ = pop[int(np.argmax(fits))]
        if champ["fit"] > best_ever_fit:
            best_ever_fit, best_ever = champ["fit"], copy.deepcopy(champ)
        params = [n_params(g, in_shape) for g in pop]
        shapes = {}
        for g in pop:
            for L in g["convs"]:
                for k in L["kernels"]:
                    key = f"{k['h']}x{k['w']}"
                    shapes[key] = shapes.get(key, 0) + 1
        entry = {
            "gen": gen, "time": round(time.time() - t0, 1),
            "best": max(fits), "mean": float(np.mean(fits)), "median": float(np.median(fits)),
            "offspring_pre_bp": float(np.mean([c["fit_pre"] for c in born])) if born else None,
            "mean_params": float(np.mean(params)), "champ_params": n_params(champ, in_shape),
            "mean_conv_layers": float(np.mean([len(g["convs"]) for g in pop])),
            "mean_kernels": float(np.mean([sum(len(L["kernels"]) for L in g["convs"]) for g in pop])),
            "n_distinct_archs": len({arch_str(g) for g in pop}),
            "n_species": len({genome_key(g) for g in pop}),
            "kernel_shapes": shapes, "champ_arch": arch_str(champ),
        }
        log["gens"].append(entry)
        print(f"[{args.dataset}/{args.method}/s{args.seed}] g{gen:03d} best={entry['best']:.4f} "
              f"mean={entry['mean']:.4f} pre_bp={entry['offspring_pre_bp']} "
              f"params={entry['mean_params']:.0f} t={entry['time']}s | {entry['champ_arch']}", flush=True)
        if gen < args.gens - 1:
            born = reproduce(pop, args.method, args.births, data, args)
        with open(out_path + ".tmp", "w") as f:
            json.dump(log, f)
        os.replace(out_path + ".tmp", out_path)

    final_champ = pop[int(np.argmax([g["fit"] for g in pop]))]
    log["final"] = {
        "champ_val": final_champ["fit"],
        "champ_test": accuracy(final_champ, data["Xte"], data["Yte"], in_shape),
        "champ_params": n_params(final_champ, in_shape),
        "champ_arch": arch_str(final_champ),
        "best_ever_val": best_ever_fit,
        "best_ever_test": accuracy(best_ever, data["Xte"], data["Yte"], in_shape),
        "best_ever_arch": arch_str(best_ever),
        "total_time": round(time.time() - t0, 1),
    }
    print("FINAL", json.dumps(log["final"]), flush=True)
    with open(out_path + ".tmp", "w") as f:
        json.dump(log, f)
    os.replace(out_path + ".tmp", out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=DATASETS)
    ap.add_argument("--method", choices=METHODS)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--pop", type=int, default=24)
    ap.add_argument("--births", type=int, default=12, help="filhos por geração (igual nos 3 métodos)")
    ap.add_argument("--gens", type=int, default=100)
    ap.add_argument("--frac", type=float, default=0.1, help="fração do treino usada por época")
    ap.add_argument("--bs", type=int, default=128)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--tour", type=int, default=3, help="tamanho do torneio (M2, M3)")
    ap.add_argument("--k_parents", type=int, default=3, help="nº de pais no crossover por maioria")
    ap.add_argument("--elite_p", type=float, default=0.7, help="viés para o campeão (M3)")
    ap.add_argument("--species_init", type=int, default=3, help="espécies iniciais (paper_spec)")
    ap.add_argument("--species_max", type=int, default=6, help="limite de espécies (paper_spec)")
    ap.add_argument("--data", default=os.path.expanduser("~/data"))
    ap.add_argument("--out", default="results")
    ap.add_argument("--arch", choices=("classic", "modern"), default="classic")
    ap.add_argument("--augment", action="store_true", help="recorte aleatório (+ flip no CIFAR-10)")
    ap.add_argument("--mem_frac", type=float, default=None, help="fração máxima da memória da GPU por processo")
    ap.add_argument("--prepare", action="store_true", help="só baixa os datasets")
    args = ap.parse_args()
    if args.prepare:
        for d in DATASETS:
            load_data(d, args.data)
            print("ok", d, flush=True)
        return
    run(args)


if __name__ == "__main__":
    main()
