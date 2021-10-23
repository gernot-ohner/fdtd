import numpy as np

import bpml
import common
import cpml
import no_pml


def call_common(nx, ny, nt, dx, dy, pmlc):
    """
    Creates fields that are common to all implementations according to the given arguments
    :param nx: int
    :param ny: int
    :param nt: int
    :param dx: float
    :param dy: float
    :param pmlc: Tuple(float, float, float)
    :return:
    """
    fields = common.make_fields(nx, ny)
    eps, mu = common.make_env(nx, ny)
    sigmas = common.make_sigmas(nx, ny)
    sigmas = common.pml(sigmas, pmlc, dx, dy)
    history = np.zeros((nx, ny, nt))
    return fields, eps, mu, sigmas, history


def call_npml(nx, ny, nt, dx, dy, dt, p, source):
    """
    Calls a simulation without a PML according to the given arguments.
    :param nx: int
    :param ny: int
    :param nt: int
    :param dx: float
    :param dy: float
    :param dt: float
    :param p: Tuple(float, float)
    :param source: function
    :return: np.ndarray of size (nx, ny, nt)
    """
    fields = common.make_fields(nx, ny)
    constants = no_pml.calculate_constants(dx, dy, dt)
    history = np.zeros((nx, ny, nt))
    return no_pml.evolution(nt, fields, constants, history, p, source)


def call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source, s=0):
    """
    Calls a simulation with a berenger PML according to the given arguments.
    :param nx: int
    :param ny: int
    :param nt: int
    :param dx: float
    :param dy: float
    :param dt: float
    :param p: Tuple(float, float)
    :param pmlc: Tuple(float, float, float)
    :param source: function
    :param s: float
    :return: np.ndarray of size (nx, ny, nt)
    """
    fields, eps, mu, sigmas, history = call_common(nx, ny, nt, dx, dy, pmlc)

    sigmas = common.add_loss(sigmas, 10, s)
    sigmas[2] *= mu / eps
    sigmas[3] *= mu / eps
    eps, mu, sigmas = common.environment_problem_example(eps, mu, sigmas, dx, dy)

    aux_fields = bpml.make_auxiliary_fields(nx, ny)
    constants = bpml.calculate_constants(eps, mu, sigmas, dx, dy, dt)

    return bpml.evolution(nt, fields, aux_fields, constants, history, p, source)


def call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source):
    """
    Calls a simulation with a convolutional PML according to the given arguments.
    :param nx: int
    :param ny: int
    :param nt: int
    :param dx: float
    :param dy: float
    :param dt: float
    :param p: Tuple(float, float)
    :param pmlc: Tuple(float, float, float)
    :param source: function
    :return: np.ndarray of size (nx, ny, nt)
    """
    fields, eps, mu, sigmas, history = call_common(nx, ny, nt, dx, dy, pmlc)

    eps, mu, sigmas = common.environment_problem_example(eps, mu, sigmas, dx, dy)
    #eps, mu, sigmas = common.modify_env(eps, mu, sigmas)

    aux_fields = cpml.make_auxiliary_fields(nx, ny)
    constants = cpml.calculate_constants(eps, mu, dx, dy, dt)
    aux_constants = cpml.cpml_constants(nx, ny, sigmas, dx, dy, dt)

    return cpml.evolution(nt, fields, aux_fields, constants, aux_constants, history, p, source)
