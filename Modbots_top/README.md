# Source code

Contact *mia.kvalsund@gmail.com* for questions.  

### General info:

This source code was created as a part of Mia-Katrin Kvalsund's master thesis.
It therefore contains extra functionality outside of what the experiments in the
article require, as this is part of a larger exploration of landscape traversal
when co-optimizing morphology and control in modular robots.

Other functionalities: Variable sizes of modules, different encodings employing
these variable sizes, and an additional, unused controller.

In addition, there is code intended to have easily switchable
environments, including a stair, maze and winding corridor environments. These
were not used in the thesis and therefore are not fully functionable.

## Files and explanations

*/LinuxBuild*: The Build of the environment for Linux.

*/Modbots_v2*: The source code for the Unity project.

*/analyze_project*: Tools to analyze determinism, populations, etc.

*/defunct_tools*: Scripts to run runs and keep track of runs on servers.

*/modbots*: A package containing the morphology, controllers, evaluation, utils, etc.
