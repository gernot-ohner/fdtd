"""Wrapper functions for calling different FDTD implementations."""
from typing import List, Tuple, Callable

import numpy as np

import bpml
import common
import cpml
import no_pml


def call_common(nx: int, ny: int, nt: int, dx: float, dy: float, 
                pmlc: Tuple[int, float, int]) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray, List[np.ndarray], np.ndarray]:
    """
    Create common fields and arrays required for PML implementations.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        nt: Number of time steps
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        pmlc: PML configuration tuple (thickness, R0, grading parameter)
        
    Returns:
        Tuple of (fields, eps, mu, sigmas, history)
    """
    fields = common.make_fields(nx, ny)
    eps, mu = common.make_env(nx, ny)
    sigmas = common.make_sigmas(nx, ny)
    sigmas = common.pml(sigmas, pmlc, dx, dy)
    history = np.zeros((nx, ny, nt))
    return fields, eps, mu, sigmas, history


def call_npml(nx: int, ny: int, nt: int, dx: float, dy: float, dt: float,
              p: Tuple[int, int], source: Callable[[int], float]) -> np.ndarray:
    """
    Run simulation without PML.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        nt: Number of time steps
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        p: Source point tuple (x, y)
        source: Source function
        
    Returns:
        Array of shape (nx, ny, nt) containing field history
    """
    fields = common.make_fields(nx, ny)
    constants = no_pml.calculate_constants(dx, dy, dt)
    history = np.zeros((nx, ny, nt))
    return no_pml.evolution(nt, fields, constants, history, p, source)


def call_bpml(nx: int, ny: int, nt: int, dx: float, dy: float, dt: float,
              p: Tuple[int, int], pmlc: Tuple[int, float, int], 
              source: Callable[[int], float], s: float = 0) -> np.ndarray:
    """
    Run simulation with Berenger PML.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        nt: Number of time steps
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        p: Source point tuple (x, y)
        pmlc: PML configuration tuple (thickness, R0, grading parameter)
        source: Source function
        s: Additional conductivity value (default: 0)
        
    Returns:
        Array of shape (nx, ny, nt) containing field history
    """
    fields, eps, mu, sigmas, history = call_common(nx, ny, nt, dx, dy, pmlc)
    
    sigmas = common.add_loss(sigmas, 10, s)
    sigmas[2] *= mu / eps
    sigmas[3] *= mu / eps
    eps, mu, sigmas = common.environment_problem_example(eps, mu, sigmas, dx, dy)
    
    aux_fields = bpml.make_auxiliary_fields(nx, ny)
    constants = bpml.calculate_constants(eps, mu, sigmas, dx, dy, dt)
    
    return bpml.evolution(nt, fields, aux_fields, constants, history, p, source)


def call_cpml(nx: int, ny: int, nt: int, dx: float, dy: float, dt: float,
              p: Tuple[int, int], pmlc: Tuple[int, float, int],
              source: Callable[[int], float]) -> np.ndarray:
    """
    Run simulation with Convolutional PML.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        nt: Number of time steps
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        p: Source point tuple (x, y)
        pmlc: PML configuration tuple (thickness, R0, grading parameter)
        source: Source function
        
    Returns:
        Array of shape (nx, ny, nt) containing field history
    """
    fields, eps, mu, sigmas, history = call_common(nx, ny, nt, dx, dy, pmlc)
    
    eps, mu, sigmas = common.environment_problem_example(eps, mu, sigmas, dx, dy)
    
    aux_fields = cpml.make_auxiliary_fields(nx, ny)
    constants = cpml.calculate_constants(eps, mu, dx, dy, dt)
    aux_constants = cpml.cpml_constants(nx, ny, sigmas, dx, dy, dt)
    
    return cpml.evolution(nt, fields, aux_fields, constants, aux_constants, history, p, source)
