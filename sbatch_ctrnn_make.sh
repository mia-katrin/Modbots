#!/bin/bash

for mode in normal variable growing gradual
do
  echo $mode
  for c in 0.01 0.02 0.04 0.08 0.16 0.24 0.32 0.48
  do
    for vs in 1 2
    do
      if [ $vs = 2 ]
      then
        echo $c "0.32 0.48 0.64 0.82"
        python3 make_experiment_configs.py -m $mode -br cen_ctrnn -c $c $c $c $c -b 0.32 0.48 0.64 0.82
      else
        echo $c "0.01 0.08 0.16 0.24"
        python3 make_experiment_configs.py -m $mode -br cen_ctrnn -c $c $c $c $c -b 0.01 0.08 0.16 0.24
      fi
    done
  done
done

#python3 make_experiment_configs.py -m variable -br copy -c 0.01 0.02 -b 0.48 0.64
#python3 run_several.py -l "Test run_several" -m variable -br copy -c 0.01 0.02 -b 0.48 0.64

#python3 make_experiment_configs.py
#python3 sbatch_make.py -b cen_ctrnn -m variable

#sbatch tune_job.sh
