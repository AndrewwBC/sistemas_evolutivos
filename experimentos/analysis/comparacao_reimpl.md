# Método original reimplementado × M1-M3

Mesmo framework, treino, população (24) e nº de filhos por geração (12); a fitness é a acurácia de validação. Valores do paper publicado: Tabela I (fitness = acurácia de teste).

## CNN clássica (10 sementes)

| Dataset | Método | n | Teste (melhor rede) | Média pop. (val) | Filhos antes do BP | Params | Espécies (final) |
|---|---|---|---|---|---|---|---|
| MNIST | Paper publicado (Tabela I), com esp. | 10 | 98.13 ± 0.15 | | | | |
| MNIST | Original reimpl., com especiação | 10 | 98.21 ± 0.29 | 94.92 ± 1.54 | 66.80 ± 9.46 | 152k | 6.0 |
| MNIST | Original reimpl., sem especiação | 10 | 98.56 ± 0.17 | 97.82 ± 0.14 | 75.28 ± 5.92 | 776k |  |
| MNIST | M1 steady state aleatório | 10 | 96.11 ± 1.09 | 84.17 ± 8.37 | 18.16 ± 4.38 | 138k |  |
| MNIST | M2 crossover por maioria | 10 | 98.46 ± 0.11 | 97.44 ± 0.66 | 75.99 ± 4.45 | 189k |  |
| MNIST | M3 crossover elitista | 10 | 98.53 ± 0.16 | 97.89 ± 0.33 | 72.74 ± 5.33 | 275k |  |
| Fashion-MNIST | Paper publicado (Tabela I), com esp. | 10 | 88.54 ± 0.70 | | | | |
| Fashion-MNIST | Original reimpl., com especiação | 10 | 89.65 ± 0.34 | 86.46 ± 1.27 | 61.78 ± 4.87 | 200k | 6.0 |
| Fashion-MNIST | Original reimpl., sem especiação | 10 | 90.26 ± 0.21 | 89.45 ± 0.31 | 68.50 ± 2.40 | 835k |  |
| Fashion-MNIST | M1 steady state aleatório | 10 | 84.99 ± 1.92 | 73.75 ± 6.80 | 16.45 ± 3.99 | 132k |  |
| Fashion-MNIST | M2 crossover por maioria | 10 | 90.05 ± 0.30 | 88.61 ± 1.23 | 66.82 ± 4.66 | 247k |  |
| Fashion-MNIST | M3 crossover elitista | 10 | 89.90 ± 0.29 | 88.80 ± 0.89 | 66.75 ± 5.69 | 224k |  |
| SVHN | Paper publicado (Tabela I), com esp. | 10 | 79.86 ± 2.06 | | | | |
| SVHN | Original reimpl., com especiação | 10 | 83.32 ± 1.20 | 79.06 ± 2.85 | 55.82 ± 7.70 | 103k | 6.0 |
| SVHN | Original reimpl., sem especiação | 10 | 86.80 ± 0.80 | 86.17 ± 1.30 | 58.05 ± 7.23 | 712k |  |
| SVHN | M1 steady state aleatório | 10 | 75.39 ± 3.37 | 53.35 ± 6.88 | 13.74 ± 1.20 | 57k |  |
| SVHN | M2 crossover por maioria | 10 | 84.93 ± 1.07 | 85.21 ± 1.69 | 63.70 ± 3.83 | 128k |  |
| SVHN | M3 crossover elitista | 10 | 85.29 ± 0.99 | 85.33 ± 1.51 | 61.40 ± 7.06 | 307k |  |
| CIFAR-10 | Paper publicado (Tabela I), com esp. | 10 | 51.35 ± 3.44 | | | | |
| CIFAR-10 | Original reimpl., com especiação | 10 | 57.34 ± 1.13 | 51.88 ± 2.06 | 36.27 ± 4.77 | 319k | 6.0 |
| CIFAR-10 | Original reimpl., sem especiação | 10 | 61.58 ± 0.45 | 58.85 ± 1.32 | 37.95 ± 4.89 | 748k |  |
| CIFAR-10 | M1 steady state aleatório | 10 | 45.59 ± 3.18 | 35.41 ± 2.60 | 12.05 ± 0.92 | 104k |  |
| CIFAR-10 | M2 crossover por maioria | 10 | 58.62 ± 1.09 | 56.41 ± 1.70 | 44.58 ± 1.63 | 149k |  |
| CIFAR-10 | M3 crossover elitista | 10 | 58.61 ± 0.93 | 56.98 ± 1.45 | 43.36 ± 2.10 | 149k |  |

Mann-Whitney U bicaudal (teste da melhor rede), p ajustado por Holm (24 testes):

| Dataset | Comparação | Δ (pp) | p | p (Holm) |
|---|---|---|---|---|
| MNIST | M2 × orig. c/ esp. | +0.25 | 0.031 | 0.19 |
| MNIST | M2 × orig. s/ esp. | -0.11 | 0.037 | 0.19 |
| MNIST | M3 × orig. c/ esp. | +0.32 | 0.011 | 0.11 |
| MNIST | M3 × orig. s/ esp. | -0.03 | 0.71 | 0.71 |
| MNIST | M1 × orig. c/ esp. | -2.10 | 0.00032 | 0.0049 |
| MNIST | M1 × orig. s/ esp. | -2.45 | 0.00018 | 0.0044 |
| Fashion-MNIST | M2 × orig. c/ esp. | +0.40 | 0.019 | 0.13 |
| Fashion-MNIST | M2 × orig. s/ esp. | -0.21 | 0.14 | 0.28 |
| Fashion-MNIST | M3 × orig. c/ esp. | +0.25 | 0.082 | 0.25 |
| Fashion-MNIST | M3 × orig. s/ esp. | -0.36 | 0.014 | 0.11 |
| Fashion-MNIST | M1 × orig. c/ esp. | -4.66 | 0.00018 | 0.0044 |
| Fashion-MNIST | M1 × orig. s/ esp. | -5.27 | 0.00018 | 0.0044 |
| SVHN | M2 × orig. c/ esp. | +1.61 | 0.0058 | 0.064 |
| SVHN | M2 × orig. s/ esp. | -1.87 | 0.0022 | 0.029 |
| SVHN | M3 × orig. c/ esp. | +1.97 | 0.00077 | 0.011 |
| SVHN | M3 × orig. s/ esp. | -1.51 | 0.0022 | 0.029 |
| SVHN | M1 × orig. c/ esp. | -7.92 | 0.00018 | 0.0044 |
| SVHN | M1 × orig. s/ esp. | -11.41 | 0.00018 | 0.0044 |
| CIFAR-10 | M2 × orig. c/ esp. | +1.28 | 0.045 | 0.19 |
| CIFAR-10 | M2 × orig. s/ esp. | -2.96 | 0.00018 | 0.0044 |
| CIFAR-10 | M3 × orig. c/ esp. | +1.27 | 0.013 | 0.11 |
| CIFAR-10 | M3 × orig. s/ esp. | -2.96 | 0.00018 | 0.0044 |
| CIFAR-10 | M1 × orig. c/ esp. | -11.75 | 0.00018 | 0.0044 |
| CIFAR-10 | M1 × orig. s/ esp. | -15.99 | 0.00018 | 0.0044 |

## CNN moderna, CIFAR-10 (3 sementes)

| Dataset | Método | n | Teste (melhor rede) | Média pop. (val) | Filhos antes do BP | Params | Espécies (final) |
|---|---|---|---|---|---|---|---|
| CIFAR-10 | Paper publicado (Tabela I), com esp. | 10 | 51.35 ± 3.44 | | | | |
| CIFAR-10 | Original reimpl., com especiação | 3 | 68.60 ± 1.66 | 60.67 ± 3.66 | 56.54 ± 2.66 | 128k | 6.0 |
| CIFAR-10 | Original reimpl., sem especiação | 3 | 71.76 ± 1.61 | 69.18 ± 1.88 | 59.25 ± 3.95 | 741k |  |
| CIFAR-10 | M1 steady state aleatório | 3 | 51.55 ± 4.27 | 43.62 ± 4.59 | 20.43 ± 5.85 | 154k |  |
| CIFAR-10 | M2 crossover por maioria | 3 | 74.45 ± 1.22 | 71.52 ± 1.69 | 56.05 ± 3.30 | 227k |  |
| CIFAR-10 | M3 crossover elitista | 3 | 75.20 ± 0.32 | 71.20 ± 2.06 | 57.42 ± 1.49 | 316k |  |

Mann-Whitney U bicaudal (teste da melhor rede), p ajustado por Holm (6 testes):

| Dataset | Comparação | Δ (pp) | p | p (Holm) |
|---|---|---|---|---|
| CIFAR-10 | M2 × orig. c/ esp. | +5.85 | 0.1 | 0.6 |
| CIFAR-10 | M2 × orig. s/ esp. | +2.69 | 0.2 | 0.6 |
| CIFAR-10 | M3 × orig. c/ esp. | +6.60 | 0.1 | 0.6 |
| CIFAR-10 | M3 × orig. s/ esp. | +3.44 | 0.1 | 0.6 |
| CIFAR-10 | M1 × orig. c/ esp. | -17.05 | 0.1 | 0.6 |
| CIFAR-10 | M1 × orig. s/ esp. | -20.21 | 0.1 | 0.6 |

