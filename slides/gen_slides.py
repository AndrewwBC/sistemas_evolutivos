#!/usr/bin/env python3
"""Gera os fragmentos de slides do paper 'Epigenetic evolution of deep convolutional models'."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

BLUE, NAVY, INK, MUTED, SKY, PALE, ORANGE = "#00408F", "#002A5C", "#14202E", "#54677D", "#B5DCF1", "#EAF4FB", "#F7A600"
FOOTER = '<div class="footer"><img src="assets/ufpel-marca.svg" alt="Universidade Federal de Pelotas"></div>'
FOOTER_DARK = '<div class="footer"><img src="assets/ufpel-marca-white.svg" alt="Universidade Federal de Pelotas"></div>'
ARROW_DEFS = f'''<defs><marker id="{{id}}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker></defs>'''


def arrow_defs(i):
    return ARROW_DEFS.replace("{id}", i)


def light(n, kicker, heading, body):
    return f'''<!-- SLIDE {n} -->
<section class="slide">
  <div class="content">
    <div class="kicker">{kicker}</div>
    <h2 class="heading" data-asset="heading">{heading}</h2>
    <div class="body">
{body}
    </div>
  </div>
  {FOOTER}
</section>
'''


def kernel(cx, cy, w, h, cell, fill=SKY, center=NAVY, stroke="#fff", added=None):
    """Kernel w×h (colunas×linhas) centrado em (cx,cy). added: set de (i,j) pintados de laranja."""
    s = []
    x0, y0 = cx - w * cell / 2, cy - h * cell / 2
    for j in range(h):
        for i in range(w):
            f = fill
            if added and (i, j) in added:
                f = ORANGE
            if i == w // 2 and j == h // 2 and center:
                f = center
            s.append(f'<rect x="{x0 + i*cell:.1f}" y="{y0 + j*cell:.1f}" width="{cell}" height="{cell}" fill="{f}" stroke="{stroke}" stroke-width="1.5"/>')
    return "\n".join(s)


def node_note(asset, kicker, text):
    return f'''<div data-asset="{asset}" style="border-left:3px solid {BLUE}; padding:4px 0 4px 20px;">
          <div class="kicker" style="margin-bottom:6px;">{kicker}</div>
          <div style="font-size:18px; line-height:1.45;">{text}</div>
        </div>'''


slides = {}

# ---------------------------------------------------------------- 01 título
slides["01-title"] = f'''<!-- SLIDE 1 — título -->
<section class="slide dark">
  <img class="hero-img" src="assets/ufpel-hero-bg.jpg" alt="">
  <div class="hero-veil"></div>
  <svg class="flow-lines" style="right:0; top:80px;" width="420" height="300" viewBox="0 0 420 300" fill="none">
    <path d="M420 40 C 300 40, 280 110, 160 110 L 0 110" stroke="rgba(181,220,241,.5)" stroke-width="1.2"/>
    <path d="M420 170 C 330 170, 310 230, 210 230 L 60 230" stroke="rgba(255,255,255,.35)" stroke-width="1.2"/>
    <circle cx="160" cy="110" r="4" fill="#B5DCF1"/>
    <rect x="206" y="226" width="8" height="8" fill="#00408F"/>
  </svg>
  <div class="content" style="display:flex; flex-direction:column;">
    <img data-asset="marca" src="assets/ufpel-marca-white.svg" alt="Universidade Federal de Pelotas" style="height:88px; width:auto; align-self:flex-start;">
    <div style="flex:1"></div>
    <div style="max-width:980px;">
      <span class="chip" data-asset="kicker-chip">Leitura de paper · Neuroevolução</span>
      <h1 class="title" data-asset="title" style="margin-top:22px; font-size:64px;">Evolução <span class="em">epigenética</span> de redes convolucionais profundas</h1>
      <p class="lead" data-asset="subtitle" style="margin-top:18px;">Hadjiivanov &amp; Blair · UNSW Sydney · arXiv:2104.05411 (2021)</p>
    </div>
    <div data-asset="meta" style="margin-top:36px; font-size:15px; color:rgba(255,255,255,.75);">
      Andrew Borges Campos &nbsp;·&nbsp; Universidade Federal de Pelotas &nbsp;·&nbsp; Novembro de 2026
    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- 02 agenda
items = [
    ("Contexto", "Neuroevolução e uma revisão rápida de CNNs"),
    ("O método", "Cortex, crossover em camadas e kernels de formato livre"),
    ("Experimentos", "Configuração, resultados e o papel da especiação"),
    ("Leitura crítica", "O que o paper prova e o que fica em aberto"),
]
agenda = "\n".join(
    f'''      <div class="agenda-item"><div class="a-num">{i}</div><div><div class="a-name">{a}</div><div class="a-note">{b}</div></div></div>'''
    for i, (a, b) in enumerate(items, 1))
slides["02-agenda"] = light(2, "Roteiro", 'O que vamos <span class="em">ver</span>', f'''      <div class="agenda" data-asset="agenda">
{agenda}
      </div>''')

# ---------------------------------------------------------------- 03 resumo
ic_kernels = f'''<svg viewBox="0 0 62 62" width="62" height="62">
  <rect x="25" y="4" width="12" height="54" rx="2" fill="#fff" stroke="{INK}" stroke-width="2"/>
  <rect x="4" y="25" width="54" height="12" rx="2" fill="#fff" stroke="{INK}" stroke-width="2"/>
  <rect x="17" y="17" width="28" height="28" rx="2" fill="none" stroke="{BLUE}" stroke-width="3"/>
  <rect x="26" y="26" width="10" height="10" fill="{NAVY}"/>
</svg>'''
ic_cross = f'''<svg viewBox="0 0 62 62" width="62" height="62">
  <rect x="4" y="6" width="14" height="14" rx="2" fill="{BLUE}"/>
  <rect x="4" y="24" width="14" height="14" rx="2" fill="{BLUE}"/>
  <rect x="44" y="6" width="14" height="14" rx="2" fill="#fff" stroke="{INK}" stroke-width="2"/>
  <rect x="44" y="24" width="14" height="14" rx="2" fill="#fff" stroke="{INK}" stroke-width="2"/>
  <path d="M11 38 C 11 50, 31 44, 31 52 M51 38 C 51 50, 31 44, 31 52" fill="none" stroke="{INK}" stroke-width="2"/>
  <rect x="24" y="50" width="7" height="9" fill="{BLUE}"/><rect x="31" y="50" width="7" height="9" fill="#fff" stroke="{INK}" stroke-width="1.5"/>
</svg>'''
ic_code = f'''<svg viewBox="0 0 62 62" width="62" height="62">
  <rect x="4" y="10" width="54" height="42" rx="6" fill="#fff" stroke="{INK}" stroke-width="2"/>
  <path d="M22 24 l-8 7 8 7 M40 24 l8 7 -8 7" fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="34" y1="21" x2="28" y2="41" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>
</svg>'''
feats = [
    (ic_kernels, "Kernels de formato livre", "Cada kernel tem sua própria largura e altura (1×7, 3×3, 5×5…) <b>dentro da mesma camada</b>, com uma mutação que redimensiona kernels individuais."),
    (ic_cross, "Crossover em camadas", "Camadas viram cromossomos e kernels viram genes: o filho herda <b>kernels inteiros, com pesos</b>, sem precisar “consertar” a rede."),
    (ic_code, "PyCortex", "Plataforma open source sobre <b>PyTorch</b>: cada indivíduo evoluído já é um modelo PyTorch válido, treinável com backprop."),
]
fg = "\n".join(f'''        <div class="feature"><div class="tile">{ic}</div><div class="f-name">{n}</div><div class="f-text">{t}</div></div>''' for ic, n, t in feats)
slides["03-resumo"] = light(3, "Visão geral", 'O paper em <span class="em">30 segundos</span>', f'''      <p class="lead" data-asset="lead" style="margin-bottom:44px; max-width:1040px;">Uma <b style="color:{INK};">população de CNNs</b> evolui a sua estrutura ao longo de gerações; os pesos são treinados com backprop e <b style="color:{INK};">herdados pelos filhos</b>. Três contribuições:</p>
      <div class="feature-grid" data-asset="features">
{fg}
      </div>''')

# ---------------------------------------------------------------- 04 neuroevolução
hyb = f'''<svg class="diagram" data-asset="diagram" width="500" height="360" viewBox="0 0 500 360">
  {arrow_defs("arr4")}
  <rect x="10" y="10" width="480" height="140" rx="20" fill="{PALE}" stroke="{SKY}" stroke-width="1.5"/>
  <text x="34" y="44" style="font-size:13px; font-weight:600; letter-spacing:.08em; fill:{MUTED};">EVOLUÇÃO · BUSCA GLOBAL</text>
  <text x="34" y="78" style="font-size:20px; font-weight:700; fill:{BLUE};">Estrutura</text>
  <text x="34" y="106" style="font-size:15px; fill:{INK};">nº de camadas, nº de kernels,</text>
  <text x="34" y="128" style="font-size:15px; fill:{INK};">formato de cada kernel, stride</text>
  <g transform="translate(372,80)">
    <circle cx="0" cy="-30" r="9" fill="{BLUE}"/><circle cx="-28" cy="12" r="9" fill="{SKY}" stroke="{INK}" stroke-width="1.2"/>
    <circle cx="28" cy="12" r="9" fill="{SKY}" stroke="{INK}" stroke-width="1.2"/><circle cx="0" cy="40" r="9" fill="#fff" stroke="{INK}" stroke-width="1.2"/>
    <circle cx="56" cy="-24" r="9" fill="#fff" stroke="{INK}" stroke-width="1.2"/><circle cx="-56" cy="-18" r="9" fill="{BLUE}"/>
  </g>
  <circle cx="250" cy="180" r="20" fill="#fff" stroke="{INK}" stroke-width="1.5"/>
  <text x="250" y="188" text-anchor="middle" style="font-size:24px; font-weight:600;">+</text>
  <rect x="10" y="210" width="480" height="140" rx="20" fill="{NAVY}"/>
  <text x="34" y="244" style="font-size:13px; font-weight:600; letter-spacing:.08em; fill:{SKY};">BACKPROP · AJUSTE LOCAL</text>
  <text x="34" y="278" style="font-size:20px; font-weight:700; fill:#fff;">Pesos</text>
  <text x="34" y="306" style="font-size:15px; fill:#fff;">gradiente descendente (Adadelta)</text>
  <text x="34" y="328" style="font-size:15px; fill:#fff;">sobre os pesos herdados</text>
  <path d="M360 300 C 380 250, 420 330, 440 280 S 470 300, 470 300" fill="none" stroke="{SKY}" stroke-width="2.5"/>
  <circle cx="440" cy="280" r="5" fill="{SKY}"/>
</svg>'''
slides["04-neuroevolucao"] = light(4, "Contexto", 'Neuroevolução: <span class="em">evoluir</span> a rede em vez de projetá-la', f'''      <div class="cols wide-left" style="align-items:center;">
        <ul class="bullets" data-asset="bullets">
          <li><b>Neuroevolução (NE)</b> = otimizar a estrutura e/ou os pesos de redes neurais com algoritmos evolutivos: população, mutação, crossover e seleção.</li>
          <li>Começou com redes pequenas (pole balancing, labirintos). <b>NEAT</b> (2002) popularizou evoluir topologias protegendo inovações com <b>especiação</b>.</li>
          <li>Tendência recente, que o paper segue: a evolução busca a <b>arquitetura</b>, o backprop ajusta os <b>pesos</b> — um otimizador híbrido.</li>
        </ul>
{hyb}
      </div>''')

# ---------------------------------------------------------------- 05 CNN
def conv_panel(ox, title, stride, pad, caption):
    s = [f'<g transform="translate({ox},0)">', f'<text x="176" y="18" text-anchor="middle" style="font-size:15px; font-weight:600;">{title}</text>']
    n = 7
    centers = [68 + 36 * j for j in range(n)]
    if pad:
        for x in (14, 302):
            s.append(f'<rect x="{x+2}" y="152" width="32" height="32" rx="5" fill="#fff" stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="4 3"/>')
            s.append(f'<text x="{x+18}" y="174" text-anchor="middle" style="font-size:13px; fill:{MUTED};">0</text>')
    for c in centers:
        s.append(f'<rect x="{c-16}" y="152" width="32" height="32" rx="5" fill="{SKY}" stroke="{INK}" stroke-width="1.3"/>')
    outs = [centers[j] for j in range(0 if pad else 1, n if pad else n - 1, stride)]
    # janela do primeiro kernel
    wc = outs[0]
    s.append(f'<path d="M{outs[0]-16} 76 L{wc-54} 150 L{wc+54} 150 L{outs[0]+16} 76 Z" fill="{BLUE}" fill-opacity=".10"/>')
    s.append(f'<rect x="{wc-55}" y="149" width="110" height="38" rx="7" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
    if stride == 2:
        w2 = outs[1]
        s.append(f'<rect x="{w2-55}" y="145" width="110" height="46" rx="7" fill="none" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    for i, c in enumerate(outs):
        f = BLUE if i == 0 else "#fff"
        s.append(f'<rect x="{c-16}" y="42" width="32" height="32" rx="5" fill="{f}" stroke="{BLUE}" stroke-width="1.6"/>')
    s.append(f'<text x="176" y="222" text-anchor="middle" style="font-size:15px; fill:{MUTED};">{caption}</text>')
    s.append("</g>")
    return "\n".join(s)

conv = "\n".join([
    conv_panel(0, "K = 3 · S = 1 · P = 0", 1, False, "saída menor: 5 valores"),
    conv_panel(392, "K = 3 · S = 2 · P = 0", 2, False, "stride 2: pula posições → 3"),
    conv_panel(784, "K = 3 · S = 1 · P = 1", 1, True, "padding: saída = entrada (7)"),
])
slides["05-cnn"] = light(5, "Contexto", 'Revisão rápida: <span class="em">kernel</span>, stride e padding', f'''      <svg class="diagram" data-asset="diagram" width="1136" height="236" viewBox="0 0 1136 236">
{conv}
      </svg>
      <div class="cols" style="margin-top:36px; gap:40px;">
        {node_note("note-cnn", "Como funciona", "Cada kernel desliza sobre a entrada e produz um <b>mapa de resposta</b>. Camadas conv extraem features; camadas FC classificam.")}
        {node_note("note-conv", "A convenção que o paper quebra", "Todos os kernels de uma camada têm o mesmo D×W×H: o tamanho do kernel vira <b>atributo da camada</b>.")}
      </div>''')

# ---------------------------------------------------------------- 05a arquitetura MLP × CNN
def img_box(x, y, s=70):
    out = [f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{PALE}" stroke="{SKY}" stroke-width="1.5"/>']
    for k in range(1, 5):
        out.append(f'<line x1="{x+k*s/5}" y1="{y}" x2="{x+k*s/5}" y2="{y+s}" stroke="#fff" stroke-width="1"/>')
        out.append(f'<line x1="{x}" y1="{y+k*s/5}" x2="{x+s}" y2="{y+k*s/5}" stroke="#fff" stroke-width="1"/>')
    return "\n".join(out)

def column(x, y0, n, c=10):
    return "\n".join(f'<rect x="{x}" y="{y0+k*c}" width="12" height="{c}" fill="{SKY}" stroke="#fff" stroke-width="1"/>' for k in range(n))

def dense(xa, ya, xb, yb):
    return "\n".join(f'<line x1="{xa}" y1="{a}" x2="{xb}" y2="{b}" stroke="{SKY}" stroke-width="1.1"/>' for a in ya for b in yb)

def neurons(x, ys, fill="#fff"):
    st = INK if fill == "#fff" else fill
    return "\n".join(f'<circle cx="{x}" cy="{y}" r="8" fill="{fill}" stroke="{st}" stroke-width="1.4"/>' for y in ys)

def stack(x, y, s, n, off):
    return "\n".join(f'<rect x="{x+k*off}" y="{y-k*off}" width="{s}" height="{s}" rx="3" fill="{"#fff" if k else PALE}" stroke="{BLUE}" stroke-width="1.4"/>' for k in range(n - 1, -1, -1))

def lbl_(x, y, t):
    return f'<text x="{x}" y="{y}" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">{t}</text>'

def annot(x, y, lines):
    out = []
    for i, t in enumerate(lines):
        w = "700; fill:" + BLUE if i == 0 else "400; fill:" + INK
        out.append(f'<text x="{x}" y="{y+i*22}" style="font-size:15px; font-weight:{w};">{t}</text>')
    return "\n".join(out)

# linha 1 — MLP
r1_col = [25 + 20 * k for k in range(7)]
r1_d1, r1_d2, r1_o = [45, 65, 85, 105, 125], [55, 75, 95, 115], [65, 85, 105]
# linha 2 — CNN
r2_col = [235 + 18 * k for k in range(6)]
r2_fc, r2_o = [247, 269, 291, 313], [258, 280, 302]
arq = f'''<svg class="diagram" data-asset="diagram" width="1136" height="386" viewBox="0 0 1136 386">
  {arrow_defs("arr5a")}
  <text x="0" y="92" style="font-size:22px; font-weight:700; fill:{BLUE};">MLP</text>
  {img_box(110, 50)}
  <line x1="190" y1="85" x2="224" y2="85" class="d-edge" marker-end="url(#arr5a)"/>
  {dense(247, r1_col, 372, r1_d1)}{dense(388, r1_d1, 512, r1_d2)}{dense(528, r1_d2, 642, r1_o)}
  {column(235, 20, 13)}
  {neurons(380, r1_d1)}{neurons(520, r1_d2)}{neurons(650, r1_o, NAVY)}
  {lbl_(145, 175, "imagem")}{lbl_(241, 175, "vetor 784")}{lbl_(380, 175, "densa")}{lbl_(520, 175, "densa")}{lbl_(650, 175, "saída")}
  {annot(790, 62, ["Tudo é camada densa", "cada neurônio vê a entrada inteira;", "a imagem vira vetor e a vizinhança", "entre pixels se perde"])}

  <line x1="0" y1="200" x2="1136" y2="200" stroke="#D5E3EF" stroke-width="1.5"/>

  <text x="0" y="287" style="font-size:22px; font-weight:700; fill:{BLUE};">CNN</text>
  {img_box(110, 245)}
  <line x1="150" y1="262" x2="250" y2="276" class="d-edge-dash"/><line x1="150" y1="282" x2="250" y2="284" class="d-edge-dash"/>
  {stack(230, 258, 64, 4, 7)}
  <rect x="130" y="262" width="20" height="20" fill="{BLUE}" fill-opacity=".18" stroke="{BLUE}" stroke-width="2"/>
  <rect x="250" y="276" width="8" height="8" fill="{BLUE}"/>
  <line x1="325" y1="285" x2="358" y2="285" class="d-edge" marker-end="url(#arr5a)"/>
  {stack(370, 266, 48, 6, 6)}
  <line x1="458" y1="285" x2="488" y2="285" class="d-edge" marker-end="url(#arr5a)"/>
  {dense(512, r2_col, 592, r2_fc)}{dense(608, r2_fc, 682, r2_o)}
  {column(500, 230, 10)}
  {neurons(600, r2_fc)}{neurons(690, r2_o, NAVY)}
  {lbl_(145, 346, "imagem")}{lbl_(270, 346, "conv 1")}{lbl_(405, 346, "conv 2")}{lbl_(506, 346, "vetor")}{lbl_(600, 346, "densa")}{lbl_(690, 346, "saída")}
  <path d="M226 356 v7 h226 v-7" fill="none" stroke="{BLUE}" stroke-width="1.5"/>
  <text x="339" y="381" text-anchor="middle" style="font-size:14px; font-weight:600; fill:{BLUE};">extração de features (kernels)</text>
  <path d="M494 356 v7 h210 v-7" fill="none" stroke="{BLUE}" stroke-width="1.5"/>
  <text x="599" y="381" text-anchor="middle" style="font-size:14px; font-weight:600; fill:{BLUE};">classificação = uma MLP</text>
  {annot(790, 252, ["Kernels locais e compartilhados", "poucos pesos e o mesmo detector", "em toda a imagem; cada kernel", "gera um mapa de resposta"])}
</svg>'''
slides["05a-arquitetura"] = light(6, "Contexto", 'MLP × CNN: a <span class="em">arquitetura</span> completa', f'''{arq}
      <div class="callout" data-asset="callout" style="margin-top:20px;">
        <b>Uma CNN = extrator de features + uma MLP no final.</b> O paper evolui as duas partes, mas sem pooling: só camadas conv e FC.
      </div>''')

# ---------------------------------------------------------------- 05b kernel = neurônio
def grid(x0, y0, n, m, c, fill="#fff", stroke=INK, hl=None, hlfill=BLUE):
    out = []
    for j in range(m):
        for i in range(n):
            f = hlfill if hl and (i, j) in hl else fill
            out.append(f'<rect x="{x0+i*c}" y="{y0+j*c}" width="{c}" height="{c}" fill="{f}" stroke="{stroke}" stroke-width="1.2"/>')
    return "\n".join(out)

ins = [(40, 80, "x₁", "w₁"), (40, 130, "x₂", "w₂"), (40, 180, "x₃", "w₃"), (40, 230, "x₄", "w₄")]
mlp = []
for x, y, t, w in ins:
    mlp.append(f'<line x1="{x+16}" y1="{y}" x2="200" y2="155" stroke="{SKY}" stroke-width="2"/>')
for x, y, t, w in ins:
    mlp.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{SKY}" stroke="{INK}" stroke-width="1.3"/><text x="{x}" y="{y+5}" text-anchor="middle" style="font-size:14px;">{t}</text>')
    mlp.append(f'<text x="128" y="{y + (155-y)*0.5 - 4:.0f}" text-anchor="middle" style="font-size:13px; fill:{BLUE}; font-weight:600;">{w}</text>')
kw = [["-1", "0", "1"]] * 3
kern_txt = "\n".join(f'<text x="{724+13+i*26}" y="{99+18+j*26}" text-anchor="middle" style="font-size:12px; fill:{INK};">{kw[j][i]}</text>' for j in range(3) for i in range(3))
mlp_s = "\n".join(mlp)
kn = f'''<svg class="diagram" data-asset="diagram" width="1136" height="296" viewBox="0 0 1136 296">
  {arrow_defs("arr5b")}
  <text x="210" y="22" text-anchor="middle" style="font-size:16px; font-weight:700;">MLP: um neurônio</text>
  {mlp_s}
  <circle cx="230" cy="155" r="30" fill="#fff" stroke="{BLUE}" stroke-width="2.5"/><text x="230" y="163" text-anchor="middle" style="font-size:22px; fill:{BLUE};">Σ</text>
  <line x1="262" y1="155" x2="292" y2="155" class="d-edge" marker-end="url(#arr5b)"/>
  <rect x="296" y="133" width="44" height="44" rx="10" fill="{NAVY}"/><text x="318" y="161" text-anchor="middle" style="font-size:17px; fill:#fff; font-style:italic;">f</text>
  <line x1="342" y1="155" x2="372" y2="155" class="d-edge" marker-end="url(#arr5b)"/>
  <circle cx="394" cy="155" r="18" fill="{BLUE}"/><text x="394" y="161" text-anchor="middle" style="font-size:15px; fill:#fff;">h</text>
  <text x="210" y="286" text-anchor="middle" style="font-size:16px; fill:{MUTED};">h = f( w · x + b ) — vê a entrada inteira</text>

  <line x1="468" y1="10" x2="468" y2="290" stroke="#D5E3EF" stroke-width="1.5"/>

  <text x="808" y="22" text-anchor="middle" style="font-size:16px; font-weight:700;">CNN: um kernel</text>
  <text x="588" y="52" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">desliza pela imagem →</text>
  {grid(510, 60, 6, 6, 26, fill=PALE, stroke="#fff")}
  <rect x="536" y="86" width="78" height="78" rx="4" fill="{BLUE}" fill-opacity=".14" stroke="{BLUE}" stroke-width="3"/>
  <text x="588" y="244" text-anchor="middle" style="font-size:14px; fill:{MUTED};">imagem · janela 3×3</text>
  <text x="692" y="146" text-anchor="middle" style="font-size:24px; fill:{MUTED};">×</text>
  {grid(724, 99, 3, 3, 26, fill=SKY, stroke="#fff")}
  {kern_txt}
  <text x="763" y="244" text-anchor="middle" style="font-size:14px; fill:{MUTED};">kernel = pesos</text>
  <line x1="812" y1="138" x2="842" y2="138" class="d-edge" marker-end="url(#arr5b)"/>
  <circle cx="872" cy="138" r="26" fill="#fff" stroke="{BLUE}" stroke-width="2.5"/><text x="872" y="146" text-anchor="middle" style="font-size:20px; fill:{BLUE};">Σ</text>
  <line x1="900" y1="138" x2="922" y2="138" class="d-edge" marker-end="url(#arr5b)"/>
  <rect x="926" y="118" width="40" height="40" rx="10" fill="{NAVY}"/><text x="946" y="144" text-anchor="middle" style="font-size:16px; fill:#fff; font-style:italic;">f</text>
  <line x1="968" y1="138" x2="994" y2="138" class="d-edge" marker-end="url(#arr5b)"/>
  {grid(1000, 86, 4, 4, 26, fill="#fff", stroke=BLUE, hl={(1, 1)})}
  <text x="1052" y="244" text-anchor="middle" style="font-size:14px; fill:{MUTED};">mapa de resposta</text>
  <text x="808" y="286" text-anchor="middle" style="font-size:16px; fill:{MUTED};">y[i,j] = f( kernel · janela[i,j] + b ) — vê uma janela por vez</text>
</svg>'''
notes_kn = "\n        ".join([
    node_note("note-fixos", "Pesos fixos no forward", "O <b>mesmo kernel</b> é usado em todas as posições. Os pesos só mudam no backprop, entre um lote e outro."),
    node_note("note-resposta", "Uma resposta por posição", "Soma ponderada <b>janela × pesos</b> + bias, depois a ativação: um valor do mapa."),
    node_note("note-paper", "No paper", "<b>Nó = kernel</b>: adicionar um kernel é adicionar um neurônio; o crossover herda kernels inteiros."),
])
slides["05b-kernel-neuronio"] = light(6, "Contexto", 'O kernel é um <span class="em">neurônio</span> que desliza', f'''{kn}
      <div class="cols" style="grid-template-columns:1fr 1fr 1fr; gap:36px; margin-top:28px;">
        {notes_kn}
      </div>''')

# ---------------------------------------------------------------- 06 Cortex
P = {1: (30, 40), 2: (30, 110), 3: (30, 180), 4: (120, 70), 5: (120, 150), 6: (210, 110)}
E = [(1, 4), (2, 4), (2, 5), (3, 5), (1, 5), (4, 6), (5, 6), (3, 6)]
W = {(1, 4): 4, (2, 4): 1.4, (2, 5): 2.6, (3, 5): 1, (1, 5): 3.2, (4, 6): 4.6, (5, 6): 1.8, (3, 6): 1.2}

def net(ox, mode):
    s = [f'<g transform="translate({ox},20)">', f'<rect x="-14" y="0" width="268" height="220" rx="16" fill="#fff" stroke="#D5E3EF" stroke-width="1.5"/>']
    if mode >= 1:
        for a, b in E:
            (x1, y1), (x2, y2) = P[a], P[b]
            if mode == 1:
                s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="5 4"/>')
            else:
                s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE}" stroke-width="{W[(a,b)]}" stroke-opacity=".85"/>')
    for k, (x, y) in P.items():
        s.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{SKY if mode < 2 else "#fff"}" stroke="{INK}" stroke-width="1.4"/>')
        s.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" style="font-size:14px; font-weight:600;">{k}</text>')
    s.append("</g>")
    return "\n".join(s)

lbl = lambda x, t, d: f'<text x="{x}" y="270" text-anchor="middle" style="font-size:18px; font-weight:700; fill:{BLUE};">{t}</text><text x="{x}" y="294" text-anchor="middle" style="font-size:14px; fill:{MUTED};">{d}</text>'
cortex = f'''<svg class="diagram" data-asset="diagram" width="1060" height="304" viewBox="0 0 1060 304">
  {arrow_defs("arr6")}
  {net(24, 0)}
  <line x1="300" y1="130" x2="380" y2="130" class="d-edge" marker-end="url(#arr6)"/>
  <text x="340" y="116" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">+ conexões</text>
  {net(410, 1)}
  <line x1="686" y1="130" x2="766" y2="130" class="d-edge" marker-end="url(#arr6)"/>
  <text x="726" y="116" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">+ pesos</text>
  {net(796, 2)}
  {lbl(144, "Genoma", "esqueleto de nós ordenados")}
  {lbl(530, "Genótipo", "conexões, ainda sem pesos")}
  {lbl(916, "Fenótipo", "a rede real, com pesos")}
</svg>'''
slides["06-cortex"] = light(6, "O método · Base", 'O framework Cortex: genoma, genótipo e <span class="em">fenótipo</span>', f'''      <div style="display:flex; justify-content:center;">
{cortex}
      </div>
      <div class="cols" style="margin-top:30px; gap:40px;">
        {node_note("note-especiacao", "Especiação", "Redes com o <b>mesmo genoma</b> formam uma espécie e só competem entre si — mutações recentes ganham tempo para amadurecer.")}
        {node_note("note-epigenetico", "Por que “epigenética”", "Os pesos aprendidos durante a “vida” dos pais são <b>herdados sem alteração</b> pelos filhos (evolução lamarckiana).")}
      </div>''')

# ---------------------------------------------------------------- 07 crossover
def layered(ox, colors, label, sub):
    sizes = [4, 3, 2]
    sq, gap, col = 30, 10, 62
    H = 4 * sq + 3 * gap
    s = [f'<g transform="translate({ox},30)">']
    pos = []
    for li, n in enumerate(sizes):
        h = n * sq + (n - 1) * gap
        y0 = (H - h) / 2
        pos.append([(li * col, y0 + k * (sq + gap)) for k in range(n)])
    for li in range(2):
        for (x1, y1) in pos[li]:
            for (x2, y2) in pos[li + 1]:
                s.append(f'<line x1="{x1+sq}" y1="{y1+sq/2}" x2="{x2}" y2="{y2+sq/2}" stroke="#D5E3EF" stroke-width="1.2"/>')
    for li, layer in enumerate(pos):
        for k, (x, y) in enumerate(layer):
            c = colors[li][k]
            f = BLUE if c == "a" else ORANGE
            s.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" rx="6" fill="{f}"/>')
    w = 2 * col + sq
    s.append(f'<text x="{w/2}" y="{H+36}" text-anchor="middle" style="font-size:16px; font-weight:700;">{label}</text>')
    s.append(f'<text x="{w/2}" y="{H+58}" text-anchor="middle" style="font-size:13px; fill:{MUTED};">{sub}</text>')
    s.append("</g>")
    return "\n".join(s)

xo = f'''<svg class="diagram" data-asset="diagram" width="620" height="350" viewBox="0 0 620 350">
  {arrow_defs("arr7")}
  {layered(10, ["aaaa", "aaa", "aa"], "Pai 1", "fitness relativo 0,7")}
  <text x="198" y="116" text-anchor="middle" style="font-size:28px; fill:{MUTED};">×</text>
  {layered(232, ["bbbb", "bbb", "bb"], "Pai 2", "fitness relativo 0,4")}
  <line x1="408" y1="110" x2="452" y2="110" class="d-edge" marker-end="url(#arr7)"/>
  {layered(464, ["abaa", "aab", "ba"], "Filho", "genes dos dois pais")}
  <rect x="10" y="300" width="14" height="14" rx="3" fill="{BLUE}"/><text x="32" y="312" style="font-size:13px; fill:{MUTED};">gene do pai 1</text>
  <rect x="140" y="300" width="14" height="14" rx="3" fill="{ORANGE}"/><text x="162" y="312" style="font-size:13px; fill:{MUTED};">gene do pai 2</text>
  <text x="10" y="340" style="font-size:13px; fill:{MUTED};">coluna = camada (cromossomo) · quadrado = kernel (gene)</text>
</svg>'''
slides["07-crossover"] = light(7, "O método · Contribuição 1", 'Crossover em camadas: kernels como <span class="em">genes</span>', f'''      <div class="cols" style="grid-template-columns: 620px 1fr; gap:48px; align-items:center;">
{xo}
        <ul class="bullets" data-asset="bullets" style="font-size:17px;">
          <li><b>Gene indivisível</b> = um nó (kernel) com todas as suas conexões de entrada e pesos.</li>
          <li>Com especiação, os pais têm as mesmas camadas e tamanhos → o filho é <b>sempre funcional</b>, sem adicionar nem podar conexões.</li>
          <li>Cada gene vem de um pai com probabilidade proporcional ao seu <b>fitness relativo</b>.</li>
          <li>Sem especiação: a similaridade <i>s</i> = O / (N<sub>i</sub> + N<sub>j</sub> − O) decide quem cruza; o excedente vem do pai maior.</li>
        </ul>
      </div>''')

# ---------------------------------------------------------------- 08 kernels heterogêneos
def kernel_row(ox, oy, shapes, cell, gap, title):
    s = [f'<g transform="translate({ox},{oy})">']
    total = sum(w for w, h in shapes) * cell + gap * (len(shapes) - 1)
    s.append(f'<text x="{total/2}" y="-92" text-anchor="middle" style="font-size:16px; font-weight:700;">{title}</text>')
    s.append(f'<line x1="-16" y1="0" x2="{total+16}" y2="0" stroke="{BLUE}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    x = 0
    for w, h in shapes:
        cx = x + w * cell / 2
        s.append(kernel(cx, 0, w, h, cell))
        s.append(f'<text x="{cx}" y="{7*cell/2+30}" text-anchor="middle" style="font-size:15px; font-weight:600; fill:{MUTED};">{w}×{h}</text>')
        x += w * cell + gap
    s.append("</g>")
    return "\n".join(s), total

cell = 15
ra, wa = kernel_row(0, 0, [(7, 7)] * 4, cell, 22, "Convencional: o formato é da camada")
rb, wb = kernel_row(0, 0, [(3, 3), (1, 7), (5, 5), (7, 1), (3, 5), (7, 7)], cell, 26, "Proposto: o formato é de cada kernel")
kh = f'''<svg class="diagram" data-asset="diagram" width="1136" height="300" viewBox="0 0 1136 300">
  <g transform="translate(20,150)">{ra}</g>
  <line x1="{wa+70}" y1="20" x2="{wa+70}" y2="290" stroke="#D5E3EF" stroke-width="1.5"/>
  <g transform="translate({1136 - wb - 20},150)">{rb}</g>
</svg>'''
slides["08-kernels"] = light(8, "O método · Contribuição 2", 'A ideia central: kernels de <span class="em">formatos diferentes</span> na mesma camada', f'''{kh}
      <div class="callout" data-asset="callout" style="margin-top:28px;">
        <b>Como cabe num tensor só:</b> W e H são sempre ímpares, então todos os kernels se alinham pelo <b>elemento central</b> (escuro) e são empilhados antes da convolução. Inspiração: o módulo Inception, que já mistura 1×1, 3×3 e 5×5.
      </div>''')

# ---------------------------------------------------------------- 09 por que
c = 18
def cross_ill():
    s = [kernel(90, 90, 7, 7, c, fill="#fff", center=None, stroke="#D5E3EF")]
    s.append(kernel(90, 90, 1, 7, c, fill=BLUE, center=NAVY))
    s.append(kernel(90, 90, 7, 1, c, fill=BLUE, center=NAVY))
    return "\n".join(s)
def ring_ill():
    s = [kernel(90, 90, 7, 7, c, fill=BLUE, center=None)]
    s.append(kernel(90, 90, 5, 5, c, fill="#fff", center=None, stroke="#D5E3EF"))
    s.append(f'<rect x="{90-c/2}" y="{90-c/2}" width="{c}" height="{c}" fill="{SKY}" stroke="#fff" stroke-width="1.5"/>')
    return "\n".join(s)
def ctx_ill():
    s = [kernel(90, 90, 9, 9, 16, fill=PALE, center=None, stroke="#fff")]
    s.append(kernel(90, 90, 3, 3, 16, fill=BLUE, center=NAVY))
    return "\n".join(s)
ills = [
    (cross_ill(), "Detector de cruz", "1×7 + 7×1", "Kernels longos e finos detectam <b>bordas nítidas</b> sem “poluição” dos vizinhos; um par ortogonal detecta cruzamentos."),
    (ring_ill(), "Detector de contorno", "7×7 − 5×5", "A diferença entre dois kernels concêntricos responde ao que <b>envolve o centro</b> — numa única camada."),
    (ctx_ill(), "Contexto", "9×9 junto de 3×3", "Kernels grandes dão <b>contexto</b> aos detalhes finos dos pequenos, já disponível para a camada seguinte."),
]
fg = "\n".join(f'''        <div class="feature" data-asset="feature-{i}">
          <svg class="diagram" width="180" height="180" viewBox="0 0 180 180" style="display:block; margin:0 auto 18px;">{svg}</svg>
          <div class="f-name">{n}</div>
          <div style="font-size:14px; font-weight:600; color:{MUTED}; margin:-4px 0 10px;">{k}</div>
          <div class="f-text">{t}</div>
        </div>''' for i, (svg, n, k, t) in enumerate(ills, 1))
slides["09-porque"] = light(9, "O método · Motivação", 'Por que misturar formatos <span class="em">ajudaria</span>?', f'''      <div class="feature-grid" data-asset="features" style="gap:56px;">
{fg}
      </div>
      <p data-asset="note" style="margin-top:30px; text-align:center; font-size:15px; color:{MUTED};">Argumento dos autores — o paper <b style="color:{INK};">não testa</b> essa hipótese isoladamente (a análise dos kernels ficou para trabalho futuro).</p>''')

# ---------------------------------------------------------------- 10 mutações
cm = 20
add_w = {(0, j) for j in range(5)} | {(4, j) for j in range(5)}
add_h = {(i, 0) for i in range(3)} | {(i, 6) for i in range(3)}
mut = f'''<svg class="diagram" data-asset="diagram" width="500" height="380" viewBox="0 0 500 380">
  {arrow_defs("arr10")}
  {kernel(70, 180, 3, 5, cm)}
  <text x="70" y="{180+50+30}" text-anchor="middle" style="font-size:16px; font-weight:700;">3×5</text>
  <path d="M120 160 C 190 160, 220 90, 300 90" class="d-edge" marker-end="url(#arr10)"/>
  <text x="196" y="96" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">largura +2</text>
  <path d="M120 200 C 190 200, 220 280, 330 280" class="d-edge" marker-end="url(#arr10)"/>
  <text x="200" y="272" text-anchor="middle" style="font-size:13px; font-weight:500; fill:{MUTED};">altura +2</text>
  {kernel(380, 90, 5, 5, cm, added=add_w)}
  <text x="380" y="166" text-anchor="middle" style="font-size:16px; font-weight:700;">5×5</text>
  {kernel(390, 270, 3, 7, cm, added=add_h)}
  <text x="450" y="276" style="font-size:16px; font-weight:700;">3×7</text>
  <rect x="20" y="350" width="14" height="14" fill="{SKY}"/><text x="40" y="362" style="font-size:13px; fill:{MUTED};">original</text>
  <rect x="120" y="350" width="14" height="14" fill="{ORANGE}"/><text x="140" y="362" style="font-size:13px; fill:{MUTED};">adicionado</text>
  <rect x="240" y="350" width="14" height="14" fill="{NAVY}"/><text x="260" y="362" style="font-size:13px; fill:{MUTED};">centro preservado</text>
</svg>'''
slides["10-mutacoes"] = light(10, "O método · Operadores", 'Como a estrutura <span class="em">muta</span>', f'''      <div class="cols" style="grid-template-columns: 500px 1fr; gap:56px; align-items:center;">
{mut}
        <ul class="bullets" data-asset="bullets" style="font-size:17px;">
          <li><b>Kernel:</b> cresce ou encolhe W ou H em 2 — continua ímpar e o centro é preservado. Limites: 1×1 até metade da entrada.</li>
          <li><b>Stride:</b> ±1 em W ou H. Rara, porque muda o tamanho de todas as camadas acima.</li>
          <li><b>Padding:</b> não muta; vale ⌊maior kernel / 2⌋, então a saída mantém o tamanho da entrada.</li>
          <li><b>Nós e camadas:</b> adicionar/remover kernels e camadas (conv ou FC).</li>
          <li>Probabilidade de cada mutação ∝ 1 / conexões afetadas. Formato inicial com p ∝ e<sup>−W·H</sup>: <b>começa pequeno</b>.</li>
        </ul>
      </div>''')

# ---------------------------------------------------------------- 11 geração
steps = [
    ("icon-gear", "Treino e avaliação", "Backprop (Adadelta) em <b>10% aleatórios</b> do treino; fitness = acurácia no teste."),
    ("icon-chart", "Calibração", "Fitness relativo f<sub>r</sub> = σ((f − μ) / σ<sub>f</sub>) ∈ (0, 1), usado como probabilidade."),
    ("icon-diamond", "Evolução", "Mutações estruturais + crossover; pais sorteados ∝ fitness relativo, dentro da espécie."),
    ("icon-shield", "Culling", "Acima do limite, remove redes com p ∝ idade / (f<sub>r</sub> · complexidade). Filhos e campeões ficam."),
]
st = "\n".join(f'''        <div class="step"><div class="st-num">Etapa 0{i}</div><div class="tile"><svg><use href="#{ic}"/></svg></div><div class="st-name">{n}</div><div class="st-text">{t}</div></div>''' for i, (ic, n, t) in enumerate(steps, 1))
slides["11-geracao"] = light(11, "O método · Algoritmo", 'Uma geração, passo a <span class="em">passo</span>', f'''      <div class="steps" data-asset="steps">
{st}
      </div>
      <div class="callout" data-asset="callout" style="margin-top:48px;">
        <b>Ciclo repetido por 100 gerações.</b> Início com especiação: 8 espécies, a primeira mínima (só a camada de saída olhando a entrada) e as outras geradas por mutações aleatórias.
      </div>''')

# ---------------------------------------------------------------- 12 setup
stats = [
    ("Datasets", "4", "MNIST e Fashion-MNIST (cinza) · SVHN e CIFAR-10 (RGB natural)"),
    ("Execuções × gerações", "10 × 100", "por experimento, com e sem especiação"),
    ("Do treino por época", "10%", "sorteados por rede: nenhuma rede vê o dataset inteiro"),
    ("Redes na população", "64 → 111", "inicial → máximo, uma CPU por rede"),
]
ss = "\n".join(f'''        <div class="stat"><div class="s-label">{a}</div><div class="s-value" style="font-size:58px;">{b}</div><div class="s-note">{c_}</div></div>''' for a, b, c_ in stats)
slides["12-setup"] = light(12, "Experimentos", 'Configuração dos <span class="em">experimentos</span>', f'''      <div class="stats" data-asset="stats" style="gap:36px;">
{ss}
      </div>
      <div class="callout" data-asset="callout" style="margin-top:56px;">
        <b>Detalhes:</b> só camadas conv e FC (sem pooling) · batch 128 · pesos iniciais N(0; 0,1) · 8 espécies iniciais, no máximo 16 · cada filho é avaliado no teste <b>antes de qualquer treino</b>.
      </div>''')

# ---------------------------------------------------------------- 13 resultados (dark)
def chart(asset, title, a, b, cap):
    return f'''        <figure class="chart" data-asset="{asset}">
          <div style="font-size:16px; font-weight:600; color:#fff; margin-bottom:8px;">{title}</div>
          <canvas data-chart width="530" height="300"></canvas>
          <script type="application/json">
          {{
            "type": "bar",
            "data": {{
              "labels": ["MNIST", "SVHN", "Fashion-MNIST", "CIFAR-10"],
              "datasets": [
                {{ "label": "Com especiação", "data": {a} }},
                {{ "label": "Sem especiação", "data": {b} }}
              ]
            }},
            "options": {{ "scales": {{ "y": {{ "min": 0, "max": 100, "title": {{ "display": true, "text": "acurácia no teste (%)" }} }} }} }}
          }}
          </script>
          <figcaption style="color:rgba(255,255,255,.6);">{cap} Média de 10 execuções, geração 100.</figcaption>
        </figure>'''

slides["13-resultados"] = f'''<!-- SLIDE 13 — resultados (dark) -->
<section class="slide dark" data-theme="dark">
  <div class="content">
    <div class="kicker">Experimentos · Resultados</div>
    <h2 class="heading" data-asset="heading" style="color:#fff;">O efeito da especiação aparece nos <span class="em">filhos</span></h2>
    <div class="body">
      <div class="cols" style="gap:48px;">
{chart("chart-best", "Melhor rede da população", "[98.13, 79.86, 88.54, 51.35]", "[97.98, 80.22, 88.44, 52.44]", "Praticamente empatado — em SVHN e CIFAR-10, sem especiação fica até à frente.")}
{chart("chart-offspring", "Filhos recém-nascidos, antes do backprop", "[95.6, 66.5, 82.0, 42.7]", "[72.5, 44.4, 64.9, 32.4]", "Com especiação, os filhos nascem 10 a 23 p.p. melhores.")}
      </div>
    </div>
  </div>
  {FOOTER_DARK}
</section>
'''

# ---------------------------------------------------------------- 14 leitura crítica
slides["14-critica"] = light(14, "Leitura crítica", 'O que o paper <span class="em">mostra</span> — e o que falta', f'''      <div class="cols" style="gap:48px; align-items:stretch;">
        <div class="card-insight" data-asset="insight" style="padding:34px 40px;">
          <div class="c-kicker">O achado principal</div>
          <div style="font-size:19px; line-height:1.55;">Nenhuma rede viu o dataset inteiro, mas a população viu. Filhos acertam <span class="em" style="font-weight:700;">~96% no MNIST sem treino</span> — só é possível se o crossover <b>transfere features aprendidas</b> pelos pais.</div>
          <div style="font-size:16px; line-height:1.5; margin-top:18px; color:rgba(255,255,255,.75);">Especiação alinha os genes no crossover: filhos melhores (95,6% vs 72,5% no MNIST), mas redes que quase não crescem.</div>
        </div>
        <div data-asset="limitacoes">
          <div class="kicker" style="margin-bottom:14px;">Limitações</div>
          <ul class="bullets" style="font-size:17px;">
            <li><b>Redes pequenas</b> (~10⁵ parâmetros): CIFAR-10 fica em ~55%. O limite de 16 espécies travou mutações estruturais.</li>
            <li>Kernels de formato livre <b>sem ablação</b>: não se mede se ajudam de fato.</li>
            <li>Fitness = acurácia <b>no conjunto de teste</b>: a seleção “enxerga” o teste, o que infla os números.</li>
            <li>Só 10 execuções, <b>sem teste estatístico</b> — os próprios autores pedem mais experimentos.</li>
          </ul>
        </div>
      </div>''')

# ---------------------------------------------------------------- 15 fechamento
slides["15-fechamento"] = f'''<!-- SLIDE 15 — fechamento -->
<section class="slide dark">
  <img class="hero-img" src="assets/ufpel-hero-bg.jpg" alt="">
  <div class="hero-veil"></div>
  <div class="content" style="display:flex; flex-direction:column;">
    <img data-asset="marca" src="assets/ufpel-marca-white.svg" alt="Universidade Federal de Pelotas" style="height:80px; width:auto; align-self:flex-start;">
    <div style="flex:1"></div>
    <h1 class="title" data-asset="closing-title" style="font-size:72px;">Para <span class="em">aprofundar</span></h1>
    <div data-asset="contact" style="margin-top:32px; font-size:17px; line-height:1.75; color:rgba(255,255,255,.85); max-width:980px;">
      Hadjiivanov, A.; Blair, A. <i>Epigenetic evolution of deep convolutional models.</i> arXiv, 2021 · <span style="color:#B5DCF1;">arxiv.org/abs/2104.05411</span><br>
      Código: PyCortex · <span style="color:#B5DCF1;">gitlab.com/cantordust/pycortex</span><br>
      Base: Stanley &amp; Miikkulainen (2002), NEAT · Szegedy et al. (2015), Inception
    </div>
  </div>
</section>
'''

for i, name in enumerate(sorted(slides), 1):
    (OUT / f"{i:02d}-{name.split('-', 1)[1]}.html").write_text(slides[name], encoding="utf-8")
print(f"{len(slides)} slides escritos em {OUT}")
