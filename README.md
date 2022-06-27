# Centralized and Decentralized Control in Modular Robots and Their Effect on Morphology

**Abstract:**
In Evolutionary Robotics, evolutionary algorithms are used to co-optimize morphology and control. However, co-optimizing leads to different challenges: How do you optimize a controller for a body that often changes its number of inputs and outputs? Researchers must then make some choice between centralized or decentralized control. In this article, we study the effects of centralized and decentralized controllers on modular robot performance and morphologies. This is done by implementing one centralized and two decentralized continuous time recurrent neural network controllers, as well as a sine wave controller for a baseline. We found that a decentralized approach that was more independent of morphology size performed significantly better than the other approaches. It also worked well in a larger variety of morphology sizes. In addition, we highlighted the difficulties of implementing centralized control for a changing morphology, and saw that our centralized controller struggled more with early convergence than the other approaches. Our findings indicate that duplicated decentralized networks are beneficial when evolving both the morphology and control of modular robots. Overall, if these findings translate to other robot systems, our results and issues encountered can help future researchers make a choice of control method when co-optimizing morphology and control.

<img src="https://github.com/mia-katrin/Modbots/blob/main/gifs/horse.gif" alt="Horse" width="380" align="left" style="margin: 10px"/>

<img src="https://github.com/mia-katrin/Modbots/blob/main/gifs/spider.gif" alt="Spider" width="380" align="left" style="margin: 10px"/>

<img src="https://github.com/mia-katrin/Modbots/blob/main/gifs/crane.gif" alt="Crane" width="380" align="left" style="margin: 10px"/> 

<img src="https://github.com/mia-katrin/Modbots/blob/main/gifs/round.gif" alt="Round" width="380" align="left" style="margin: 10px"/>

The article can be found at:

*To be added*

Cite as:

```
To be added: Citation and BibTex citation
```

The source code is found in the folder */Modbots_top*.

The code for the controllers is found in */Modbots_top/modbots/modbots/controllers*.

## Gene mutation rates

All probabilities are scaled by the current mutation rate (f.ex global_mut_rate/nr_modules).
They were found through trial and error and are, for the CTRNN, close to the
values that came from examples in the neat-python package.

### CTRNNs:

| Mutation          | Prob. | Options/limits                                       |
|-------------------|-------|------------------------------------------------------|
| Connection add    | 0.2   |
| Connection delete | 0.2   |
| Connection enable | 0.01  | ***True*** False                       |
| Node add          | 0.2   |
| Node delete       | 0.2   |
| Bias              | 0.8   | [-1.0, 1.0]                                          |
| Activation        | 0.2   | sin ***tanh*** sigmoid                |
| Aggregation       | 0.1   | ***sum*** min max mean median product maxabs |
| Weight            | 0.8   | [-1.0, 1.0]                                          |
| Response          | 0.2   | [-1.5, 1.5]                                          |
| Bias replace      | 0.1   |
| Response replace  | 0.1   |
| Weight replace    | 0.1   |

### Sine wave generator:

| Mutation          | Prob. | Options/limits      |
|-------------------|-------|---------------------|
| Amplitude         | 1.0   | [0, 3]              |
| Frequency         | 0.0   | 2.0                 |
| Phase             | 1.0   | [-inf, inf]         |
| Offset            | 1.0   | [-1, 1]             |

A fixed frequency was used to enable better synchronization. This was chosen
after several initial experiments with this controller showed that it was prone
to local optima solutions.
