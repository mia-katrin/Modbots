#!/bin/bash

for mode in normal variable growing gradual
do
  echo $mode
  for c in 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82
  do
    python3 make_experiment_configs.py -m $mode -br dec_ctrnn_sine -c $c $c $c $c $c $c $c $c -b 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82
    python3 sbatch_make.py -m $mode -br dec_ctrnn_sine -c $c $c $c $c $c $c $c $c -b 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82
    sleep 1
    sbatch tune_job.sh
    sleep 5
  done
done

##### HEY!!!

#
# For dec_ctrnn_sine, you must have 0.01 0.08 0.16 0.24 0.32 0.48 0.64 0.82 for control
# And normal variable growing gradual
#

##### HEY!!!!
