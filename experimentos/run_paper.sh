#!/usr/bin/env bash
# Método original reimplementado (com e sem especiação), numa única GPU.
#   CNN clássica: 4 datasets x 10 sementes -> results/
#   CNN moderna:  CIFAR-10 x 3 sementes    -> results_modern/
# Execuções já concluídas são puladas. Uso: GPU=0 JOBS=20 ./run_paper.sh
cd "$(dirname "$0")"
GPU=${GPU:-0}
JOBS=${JOBS:-20}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p results results_modern logs logs_modern
: > jobs_paper.txt
for s in 0 1 2; do for m in paper_spec paper_nospec; do
  [ -f results_modern/cifar10_${m}_modern_s$s.json ] && grep -q '"final"' results_modern/cifar10_${m}_modern_s$s.json && continue
  echo "cifar10 $m $s modern" >> jobs_paper.txt; done; done
for s in $(seq 0 9); do for d in mnist fashion svhn cifar10; do for m in paper_spec paper_nospec; do
  [ -f results/${d}_${m}_s$s.json ] && grep -q '"final"' results/${d}_${m}_s$s.json && continue
  echo "$d $m $s classic" >> jobs_paper.txt; done; done; done
echo "$(wc -l < jobs_paper.txt) execuções na fila (GPU $GPU, $JOBS em paralelo)"
xargs -P "$JOBS" -L1 bash -c '
  if [ "$3" = modern ]; then extra="--arch modern --augment --out results_modern"; log=logs_modern/$0_$1_modern_s$2.log
  else extra="--out results"; log=logs/$0_$1_s$2.log; fi
  CUDA_VISIBLE_DEVICES='"$GPU"' .venv/bin/python neuroevo.py --dataset $0 --method $1 --seed $2 --gens 100 \
    --mem_frac 0.045 $extra > $log 2>&1 && echo "ok $0 $1 $2 $3" || echo "FALHOU $0 $1 $2 $3"' < jobs_paper.txt
echo "fim: $(date)"
