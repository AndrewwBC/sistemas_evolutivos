#!/usr/bin/env bash
# CNN moderna, CIFAR-10: completa 10 sementes (0-9) para os 5 métodos, numa única GPU.
# Execuções já concluídas são puladas. Uso: GPU=0 JOBS=18 ./run_modern10.sh
cd "$(dirname "$0")"
GPU=${GPU:-0}
JOBS=${JOBS:-18}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p results_modern logs_modern
: > jobs_modern10.txt
for s in $(seq 0 9); do for m in steady_random majority elitist paper_spec paper_nospec; do
  f=results_modern/cifar10_${m}_modern_s$s.json
  [ -f "$f" ] && grep -q '"final"' "$f" && continue
  echo "$m $s" >> jobs_modern10.txt; done; done
echo "$(wc -l < jobs_modern10.txt) execuções na fila (GPU $GPU, $JOBS em paralelo)"
xargs -P "$JOBS" -L1 bash -c 'CUDA_VISIBLE_DEVICES='"$GPU"' .venv/bin/python neuroevo.py --dataset cifar10 \
  --method $0 --seed $1 --gens 100 --arch modern --augment --mem_frac 0.045 --out results_modern \
  > logs_modern/cifar10_$0_modern_s$1.log 2>&1 && echo "ok $0 $1" || echo "FALHOU $0 $1"' < jobs_modern10.txt
echo "fim: $(date)"
