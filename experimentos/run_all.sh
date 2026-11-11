#!/usr/bin/env bash
# Roda a grade completa (4 datasets x 3 métodos x SEEDS sementes) nas 2 GPUs.
# Uso: SEEDS=10 JOBS=16 GENS=100 DATASETS="mnist fashion svhn cifar10" ./run_all.sh
#      (JOBS = processos por GPU)
# Execuções já concluídas (json com "final") são puladas, então dá para retomar.
set -euo pipefail
cd "$(dirname "$0")"
SEEDS=${SEEDS:-10}
JOBS=${JOBS:-16}
GENS=${GENS:-100}
DATASETS=${DATASETS:-"mnist fashion svhn cifar10"}
NGPU=$(nvidia-smi -L | wc -l)
PY=.venv/bin/python
mkdir -p results logs

: > jobs.txt
for s in $(seq 0 $((SEEDS - 1))); do
  for d in $DATASETS; do
    for m in steady_random majority elitist; do
      f=results/${d}_${m}_s${s}.json
      if [ -f "$f" ] && grep -q '"final"' "$f"; then continue; fi
      echo "$d $m $s" >> jobs.txt
    done
  done
done
echo "$(wc -l < jobs.txt) execuções na fila, $NGPU GPUs x $JOBS processos"

awk '{print NR-1, $0}' jobs.txt | xargs -P $((JOBS * NGPU)) -L1 bash -c '
  gpu=$(( $0 % '"$NGPU"' ))
  CUDA_VISIBLE_DEVICES=$gpu '"$PY"' neuroevo.py --dataset $1 --method $2 --seed $3 --gens '"$GENS"' \
    > logs/$1_$2_s$3.log 2>&1 && echo "ok $1 $2 $3" || echo "FALHOU $1 $2 $3"'
echo "fim: $(date)"
