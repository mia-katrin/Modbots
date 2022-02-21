#!/bin/bash

for mode in normal
do
  echo $mode
  for c in 0.01 0.02 0.04 0.08 0.16 0.24 0.32 0.48
  do
    for vs in 1 2 3 4
    do
      if [ $vs -eq 1 ]
      then
        python3 make_experiment_configs.py -m $mode -br copy_sine -c $c $c -b 0.01 0.08
        python3 sbatch_make.py -m $mode -br copy_sine -c $c $c -b 0.01 0.08
      elif [ $vs -eq 2 ]
      then
        python3 make_experiment_configs.py -m $mode -br copy_sine -c $c $c -b 0.16 0.24
        python3 sbatch_make.py -m $mode -br copy_sine -c $c $c -b 0.16 0.24
      elif [ $vs -eq 3 ]
      then
        python3 make_experiment_configs.py -m $mode -br copy_sine -c $c $c -b 0.32 0.48
        python3 sbatch_make.py -m $mode -br copy_sine -c $c $c-b 0.32 0.48
      elif [ $vs -eq 4 ]
      then
        python3 make_experiment_configs.py -m $mode -br copy_sine -c $c $c-b 0.64 0.82
        python3 sbatch_make.py -m $mode -br copy_sine -c $c $c -b 0.64 0.82
      else
        echo "Please kill me"
      fi
      sleep 1
      sbatch tune_job.sh
      sleep 5
    done
  done
done

#python3 run_several.py -l "Variable sine fill 7" -m variable -br sine -c 0.16 0.16 0.16 0.16 -b 0.01 0.08 0.16 0.24
