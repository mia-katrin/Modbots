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

*/evolve.py*: A script that runs an evolution based on the config file in this directory.
It presupposes several directories and files.

*/xplore_ind.py*: A script that simulates a pickled individual, sent as an argument. Otherwise,
it will use the */bestInd/ind* individual from your last evolutionary run. It also presupposes
a config file.

## If you intend to use this code

Several structures are needed to run this, and the following commands are all run
from */Modbots_top*. First of all, the requirements.txt should all be installed.
Secondly, the modbots package must be installed:

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

You must decide on the number of cores you want to be default for
experiments:

```
echo [YOUR CORES] > experiments/max_cores.txt
```

And lastly, the *example_config.cfg* needs to be altered with your *build_path* and
*log_folder* absolute adresses. The *build_path* address is where you have your
Build. If you use Linux, this will be
*path/to/Modbots_top/LinuxBuild/LinuxBuild.x86_64*.
