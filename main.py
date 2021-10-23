import math

import matplotlib.pyplot as plt
import scipy.constants as const
from typing import *

import tests
import source as src

plt.rc('font', family='serif', size=14)

num = 1  # number is set to one as we want no averaging to take place before we calculate the minimum computation time


def __init__():
    # These strings should be changed according to what you want the program to do.
    action = "normal"  # options are: normal, pml, loss, comparison, time
    pml = "bpml"  # options are: no, bpml, cpml

    # Specify the parameters of the computation here
    nx = 100  # number of Yee cells in x direction
    ny = 100  # number of Yee cells in y direction
    dx = 0.05  # discretization constant in x direction
    dy = 0.05  # discretization constant in y direction
    lx = nx * dx  # product gives length in x direction in meters
    ly = ny * dy  # product gives length in x direction in meters
    dt = (const.c * math.sqrt((dx ** -2) + (dy ** -2))) ** -1  #
    nt = 200  # number of time steps for which the computation is run
    pmlc = (10, 1e-6, 3)  # (thickness of the PML in cells, desired reflection factor R0, grading parameter)
    p = (int(nx / 2), int(ny / 2))  # point where the source term is added
    source = src.simple_sin_source

    params = [nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, source]  # package the parameters in a list

    if action == "normal":
        tests.normal_test(params, pml)
    elif action == "pml":
        tests.pml_test(params, pml)
    elif action == "loss":
        tests.loss_test(params)
    elif action == "comparison":
        tests.comparison_test(params)
    elif action == "time":
        tests.time_test(params, 1)
    elif action == "trivial":
        tests.time_trivial(params, 1)
    elif action == "all":
        tests.normal_test(params, "cpml")
        tests.normal_test(params, "bpml")
        tests.normal_test(params, "no")
        tests.pml_test(params, "cpml")
        tests.pml_test(params, "bpml")
        tests.loss_test(params)
        tests.comparison_test(params)
        tests.time_test(params, 1)
        tests.time_trivial(params, 1)
    else:
        print("choose an action")


__init__()
