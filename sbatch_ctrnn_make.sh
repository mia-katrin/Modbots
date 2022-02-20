#!/bin/bash

for mode in normal variable growing gradual
do
  echo $mode
  for c in 0.01 0.02 0.04 0.08 0.16 0.24 0.32 0.48
  do
    python3 make_experiment_configs.py -m $mode -br dec_ctrnn_sine -c $c $c $c $c $c $c $c $c -b 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82
    #python3 sbatch_make.py -m $mode -br dec_ctrnn_sine -c $c $c $c $c $c $c $c $c -b 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82
    #sleep 2
    #sbatch tune_job.sh
    #sleep 10
  done
done

#python3 run_several.py -l "Variable sine fill 7" -m variable -br copy -c 0.01 0.02 -b 0.48 0.64

#python3 sbatch_make.py -br cen_ctrnn -m variable -c 0.01 0.02 -b 0.48 0.64

#sbatch tune_job.sh

#python3 run_several.py -l "Variable sine fill 7" -m variable -br sine -c 0.16 0.16 0.16 0.16 -b 0.01 0.08 0.16 0.24
