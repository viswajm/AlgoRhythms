#!/usr/bin/env bash
set -euo pipefail

BIN=./rqs
OUTDIR=results
mkdir -p "$OUTDIR"

Ns=(1000 5000 10000 50000)
InputTypes=(random sorted reverse nearly_sorted few_distinct)
Variants=(random det_first det_last det_med3)
Trials_small=200
Trials_med=100
Trials_large=30

for n in "${Ns[@]}"; do
  if [ "$n" -le 5000 ]; then trials=$Trials_small
  elif [ "$n" -le 10000 ]; then trials=$Trials_med
  else trials=$Trials_large
  fi

  for input in "${InputTypes[@]}"; do
    for var in "${Variants[@]}"; do
      outfile="$OUTDIR/${var}_${input}_n${n}.csv"
      echo "Running n=$n input=$input var=$var trials=$trials -> $outfile"
      $BIN --n $n --trials $trials --variant $var --input $input --nearly_k 50 --domain 5 > "$outfile"
    done
  done
done

COMBINED="$OUTDIR/combined_results.csv"
head -n1 "$OUTDIR/${Variants[0]}_${InputTypes[0]}_n${Ns[0]}.csv" > "$COMBINED"
for f in $OUTDIR/*.csv; do
  tail -n +2 "$f" >> "$COMBINED"
done

echo "✅ Done. Combined results -> $COMBINED"
