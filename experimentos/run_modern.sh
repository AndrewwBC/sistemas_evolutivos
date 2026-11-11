#!/usr/bin/env bash
# Teste rápido do modo moderno: CIFAR-10, 3 métodos x 3 sementes, 100 gerações.
# Roda tudo numa única GPU (GPU=0 por padrão), com teto de memória por processo,
# para não disputar memória com outros usuários do servidor.
cd "$(dirname "$0")"
GPU=${GPU:-0}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p results_modern logs_modern
for s in 0 1 2; do for m in steady_random majority elitist; do echo "$m $s"; done; done |
  xargs -P 9 -L1 bash -c 'CUDA_VISIBLE_DEVICES='"$GPU"' .venv/bin/python neuroevo.py --dataset cifar10 \
    --method $0 --seed $1 --gens 100 --arch modern --augment --mem_frac 0.1 --out results_modern \
    > logs_modern/cifar10_$0_s$1.log 2>&1 && echo "ok $0 $1" || echo "FALHOU $0 $1"'
echo "fim: $(date)"
