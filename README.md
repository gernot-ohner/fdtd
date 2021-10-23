# FDTD simulation 
For my bachelor thesis in physics, I investigated FDTD simulations using Python

> The finite difference time domain method, in short FDTD, is used to numerically compute
the propagation of electromagnetic waves, that is, to solve the Maxwell equations for arbitrary
environments.

![FDTD simulation with various features of low/high permittivity](https://gernot-ohner.github.io/resources/fdtd1.png)

This is a sample image of a FDTD simulation in 2 dimensions.
Features of note:   
- a pulsing point source at `(50, 50)` 
- a [luneburg lens](https://en.wikipedia.org/wiki/Luneburg_lens) with a focal point around `(20, 90)`
- a "bar" of low (high?) permittivity from `(25, 40)` to `(40, 25)`
- an area of perfect conductivity in the bottom right corner
- an absorbing boundary (otherwise, the limits of the simulation act like perfect reflectors, c.f. the following image)  

![Comparison of 1d simulations with and without absorbing boundary conditions, taken from Ohner 2018](https://gernot-ohner.github.io/resources/abc_explanation_1d.png)


## Usage

`python main.py`

