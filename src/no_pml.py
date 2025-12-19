"""FDTD implementation without Perfectly Matched Layer (PML)."""
from typing import List, Tuple, Callable

import numpy as np
import scipy.constants as const


def calculate_constants(dx: float, dy: float, dt: float) -> List[float]:
    """
    Calculate update constants for vacuum environment.
    
    Args:
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        
    Returns:
        List containing [cex, cey, chzx, chzy]
    """
    eps = const.epsilon_0
    mu = const.mu_0
    
    cex = dt / (eps * dy)
    cey = dt / (eps * dx)
    chzx = dt / (mu * dx)
    chzy = dt / (mu * dy)
    
    return [cex, cey, chzx, chzy]


def evolution(nt: int, fields: List[np.ndarray], constants: List[float], 
              history: np.ndarray, sourcepoint: Tuple[int, int], 
              source: Callable[[int], float]) -> np.ndarray:
    """
    Evolve electromagnetic fields using matrix-based FDTD without PML.
    
    Args:
        nt: Number of time steps
        fields: List containing [Ex, Ey, Hz] arrays
        constants: List containing [cex, cey, chzx, chzy]
        history: Array to store field history, shape (nx, ny, nt)
        sourcepoint: Tuple (x, y) where source is applied
        source: Source function taking time step and returning value
        
    Returns:
        Array containing field history
    """
    ex, ey, hz = fields
    cex, cey, chzx, chzy = constants
    
    for t in range(nt):
        hz = hz - chzx * (ey[1:, :] - ey[:-1, :]) + chzy * (ex[:, 1:] - ex[:, :-1])
        hz[sourcepoint] = source(t)
        ex[:, 1:-1] = ex[:, 1:-1] + cex * (hz[:, 1:] - hz[:, :-1])
        ey[1:-1, :] = ey[1:-1, :] - cey * (hz[1:, :] - hz[:-1, :])
        history[:, :, t] = hz
    
    return history
