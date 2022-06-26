# Centralized and Decentralized Control in Modular Robots and Their Effect on Morphology

**Abstract:**
In Evolutionary Robotics, evolutionary algorithms are used to co-optimize morphology and control. However, co-optimizing leads to different challenges: How do you optimize a controller for a body that often changes its number of inputs and outputs? Researchers must then make some choice between centralized or decentralized control. In this article, we study the effects of centralized and decentralized controllers on modular robot performance and morphologies. This is done by implementing one centralized and two decentralized continuous time recurrent neural network controllers, as well as a sine wave controller for a baseline. We found that a decentralized approach that was more independent of morphology size performed significantly better than the other approaches. It also worked well in a larger variety of morphology sizes. In addition, we highlighted the difficulties of implementing centralized control for a changing morphology, and saw that our centralized controller struggled more with early convergence than the other approaches. Our findings indicate that duplicated decentralized networks are beneficial when evolving both the morphology and control of modular robots. Overall, if these findings translate to other robot systems, our results and issues encountered can help future researchers make a choice of control method when co-optimizing morphology and control.

The article can be found at:

*To be added*

Cite as:

```
To be added: Citation and BibTex citation
```


### Gene mutation rates

#### CTRNNs:

$$
\begin{aligned}{c|c|c}
\hline
Mutation & Prob. & Options/limits  \\\hline
Connection add & 0.2 \\
Connection delete & 0.2 \\
Connection enable & 0.01 & \underline{\textbf{True}} False \\
Node add & 0.2 \\
Node delete & 0.2 \\
Bias & 0.8 & [-1.0, 1.0] \\
Activation & 0.2 & sin \underline{\textbf{tanh}} sigmoid \\
Aggregation & 0.1 & \underline{\textbf{sum}} min max mean median product \\
& & maxabs \\
Weight & 0.8 & [-1.0, 1.0] \\
Response & 0.2 & [-1.5, 1.5] \\
Bias replace & 0.1 \\
Response replace & 0.1 \\
Weight replace & 0.1 \\
\hline
\end{aligned}
$$
