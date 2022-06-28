# Source code

Contact *mia.kvalsund@gmail.com* for questions.  

### General info:

This source code was created as a part of Mia-Katrin Kvalsund's master thesis.
It therefore contains extra functionality outside of what the experiments in the
article require, as this is part of a larger exploration of landscape traversal
when co-optimizing morphology and control in modular robots.

Other functionalities: Variable sizes of modules, different encodings employing
these variable sizes, an additional, unused controller, and several scripts to
generate result graphs and data.

In addition, there is code intended to have easily switchable
environments, including a stair, maze and winding corridor environments. These
were not used in the thesis and therefore are not fully functionable.

## Files and explanations

Here are the major files when considering the functionality described in the article:

*/LinuxBuild*: The Build of the environment for Linux.

*/Modbots_v2*: The source code for the Unity project, Assets and C# code.

*/modbots*: A package containing the body, controllers, evaluation, utils, plotting.
This package contains all major functionality (Python-side) apart from the script
that runs an evolution.

In this folder, the most important files are

*/evolve.py*: A script that runs an evolution based on the config file in this directory, or a given config file as an argument. Beware that if documentation is true in the config file,
several files will be generated. Otherwise, you will get plots and the final individual
will be saved in *bestInd/ind*.
It presupposes several directories and files.

*/xplore_ind.py*: A script that simulates a pickled individual file, sent as an argument. Otherwise,
it will use the */bestInd/ind* individual from your last evolutionary run. You can also generate a random individual with the *--gene random* argument, using the default or given config. This file presupposes
a config file unless one is given.

## If you intend to use this code

Several structures are needed to run this, and the following commands are all run
from */Modbots_top*.

First of all, without a build you have no simulator. If you are using Linux,
a build is provided in LinuxBuild. In all other cases, you must
yourself create the build using Unity Editor, the */Modbots_v2/Assets* folder,
and using the ML-Agents package.

The *example_config.cfg* needs to be altered with your *build_path* and
*log_folder* absolute adresses. The *build_path* address is where you have your
Build. If you use Linux, this will be
*path/to/Modbots_top/LinuxBuild/LinuxBuild.x86_64*.

Secondly, the requirements.txt and the modbots package should all be installed:

```
pip3 install -r requirements.txt
pip3 install -e modbots
```

I recommend installing modbots with editing (-e) so that if you make changes you
do not need to reinstall.

Then files to run and track experiments are needed:

```
mkdir log_folder
mkdir experiments
touch experiments/all_statements.txt
echo "{}" > experiments/valid_intervals
echo "0" > experiments/runNr.txt
mkdir bestInd
```

Lastly, you must decide on the number of cores you want to be default for
experiments:

```
echo [YOUR CORES] > experiments/max_cores.txt
```
Note that this last command is likely unnecessary, however to avoid issues it is
good to include. To change number of cores you should instead use the config file.
