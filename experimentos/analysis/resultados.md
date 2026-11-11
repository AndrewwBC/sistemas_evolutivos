# Resultados

Médias ± desvio-padrão (%) entre sementes. 'Filhos antes do BP' = acurácia média dos filhos recém-nascidos, só com os pesos herdados, nas últimas 20 gerações.

| Dataset | Método | n | Teste (campeão final) | Teste (melhor de todos) | Média da pop. (val) | Filhos antes do BP | Parâmetros do campeão |
|---|---|---|---|---|---|---|---|
| MNIST | M1 steady state aleatório | 10 | 96.11 ± 1.09 | 97.50 ± 0.64 | 84.17 ± 8.37 | 18.16 ± 4.38 | 138k |
| MNIST | M2 crossover por maioria | 10 | 98.46 ± 0.11 | 98.47 ± 0.16 | 97.44 ± 0.66 | 75.99 ± 4.45 | 189k |
| MNIST | M3 crossover elitista | 10 | 98.53 ± 0.16 | 98.48 ± 0.09 | 97.89 ± 0.33 | 72.74 ± 5.33 | 275k |
| Fashion-MNIST | M1 steady state aleatório | 10 | 84.99 ± 1.92 | 87.38 ± 1.00 | 73.75 ± 6.80 | 16.45 ± 3.99 | 132k |
| Fashion-MNIST | M2 crossover por maioria | 10 | 90.05 ± 0.30 | 90.08 ± 0.42 | 88.61 ± 1.23 | 66.82 ± 4.66 | 247k |
| Fashion-MNIST | M3 crossover elitista | 10 | 89.90 ± 0.29 | 90.10 ± 0.39 | 88.80 ± 0.89 | 66.75 ± 5.69 | 224k |
| SVHN | M1 steady state aleatório | 10 | 75.39 ± 3.37 | 79.80 ± 1.65 | 53.35 ± 6.88 | 13.74 ± 1.20 | 57k |
| SVHN | M2 crossover por maioria | 10 | 84.93 ± 1.07 | 85.18 ± 0.93 | 85.21 ± 1.69 | 63.70 ± 3.83 | 128k |
| SVHN | M3 crossover elitista | 10 | 85.29 ± 0.99 | 85.58 ± 0.77 | 85.33 ± 1.51 | 61.40 ± 7.06 | 307k |
| CIFAR-10 | M1 steady state aleatório | 10 | 45.59 ± 3.18 | 51.00 ± 2.06 | 35.41 ± 2.60 | 12.05 ± 0.92 | 104k |
| CIFAR-10 | M2 crossover por maioria | 10 | 58.62 ± 1.09 | 59.43 ± 0.77 | 56.41 ± 1.70 | 44.58 ± 1.63 | 149k |
| CIFAR-10 | M3 crossover elitista | 10 | 58.61 ± 0.93 | 59.27 ± 1.08 | 56.98 ± 1.45 | 43.36 ± 2.10 | 149k |

## Mann-Whitney U (bicaudal) — acurácia de teste do campeão final

| Dataset | Comparação | p | Comparação | p | Comparação | p |
|---|---|---|---|---|---|---|
| MNIST | M1 × M2 | 0.000181 | M1 × M3 | 0.000182 | M2 × M3 | 0.307 |
| Fashion-MNIST | M1 × M2 | 0.000183 | M1 × M3 | 0.000182 | M2 × M3 | 0.344 |
| SVHN | M1 × M2 | 0.000183 | M1 × M3 | 0.000183 | M2 × M3 | 0.571 |
| CIFAR-10 | M1 × M2 | 0.000183 | M1 × M3 | 0.000183 | M2 × M3 | 0.97 |

## Comparação com o paper original (Tabela I)

Δ = nosso − paper (com especiação), em pontos percentuais. Melhor rede: no paper, acurácia de teste da melhor rede (selecionada pelo teste); aqui, acurácia de teste do campeão selecionado pela validação.

| Dataset | Abordagem | Melhor rede | Δ | Média da pop. | Δ | Filhos antes do BP | Δ |
|---|---|---|---|---|---|---|---|
| MNIST | Paper (com esp.) | 98.13 ± 0.15 | | 96.80 ± 0.40 | | 95.60 ± 1.80 | |
| MNIST | Paper (sem esp.) | 97.98 ± 0.13 | | 93.70 ± 1.10 | | 72.50 ± 10.70 | |
| MNIST | M1 steady state aleatório | 96.11 ± 1.09 | -2.02 | 84.17 ± 8.37 | -12.63 | 18.16 ± 4.38 | -77.44 |
| MNIST | M2 crossover por maioria | 98.46 ± 0.11 | +0.33 | 97.44 ± 0.66 | +0.64 | 75.99 ± 4.45 | -19.61 |
| MNIST | M3 crossover elitista | 98.53 ± 0.16 | +0.40 | 97.89 ± 0.33 | +1.09 | 72.74 ± 5.33 | -22.86 |
| Fashion-MNIST | Paper (com esp.) | 88.54 ± 0.70 | | 85.30 ± 1.40 | | 82.00 ± 4.30 | |
| Fashion-MNIST | Paper (sem esp.) | 88.44 ± 0.36 | | 83.30 ± 1.10 | | 64.90 ± 7.80 | |
| Fashion-MNIST | M1 steady state aleatório | 84.99 ± 1.92 | -3.55 | 73.75 ± 6.80 | -11.55 | 16.45 ± 3.99 | -65.55 |
| Fashion-MNIST | M2 crossover por maioria | 90.05 ± 0.30 | +1.51 | 88.61 ± 1.23 | +3.31 | 66.82 ± 4.66 | -15.18 |
| Fashion-MNIST | M3 crossover elitista | 89.90 ± 0.29 | +1.36 | 88.80 ± 0.89 | +3.50 | 66.75 ± 5.69 | -15.25 |
| SVHN | Paper (com esp.) | 79.86 ± 2.06 | | 70.20 ± 7.50 | | 66.50 ± 8.00 | |
| SVHN | Paper (sem esp.) | 80.22 ± 0.89 | | 66.50 ± 3.10 | | 44.40 ± 7.40 | |
| SVHN | M1 steady state aleatório | 75.39 ± 3.37 | -4.47 | 53.35 ± 6.88 | -16.85 | 13.74 ± 1.20 | -52.76 |
| SVHN | M2 crossover por maioria | 84.93 ± 1.07 | +5.07 | 85.21 ± 1.69 | +15.01 | 63.70 ± 3.83 | -2.80 |
| SVHN | M3 crossover elitista | 85.29 ± 0.99 | +5.43 | 85.33 ± 1.51 | +15.13 | 61.40 ± 7.06 | -5.10 |
| CIFAR-10 | Paper (com esp.) | 51.35 ± 3.44 | | 43.90 ± 4.80 | | 42.70 ± 5.10 | |
| CIFAR-10 | Paper (sem esp.) | 52.44 ± 0.85 | | 41.90 ± 1.10 | | 32.40 ± 1.80 | |
| CIFAR-10 | M1 steady state aleatório | 45.59 ± 3.18 | -5.76 | 35.41 ± 2.60 | -8.49 | 12.05 ± 0.92 | -30.65 |
| CIFAR-10 | M2 crossover por maioria | 58.62 ± 1.09 | +7.27 | 56.41 ± 1.70 | +12.51 | 44.58 ± 1.63 | +1.88 |
| CIFAR-10 | M3 crossover elitista | 58.61 ± 0.93 | +7.26 | 56.98 ± 1.45 | +13.08 | 43.36 ± 2.10 | +0.66 |
