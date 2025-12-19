"""Berenger Perfectly Matched Layer (BPML) implementation."""
from typing import List, Tuple, Callable

import numpy as np


def make_auxiliary_fields(nx: int, ny: int) -> List[np.ndarray]:
    """
    Create auxiliary fields required for Berenger PML.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        
    Returns:
        List containing [hzx, hzy] arrays
    """
    hzx = np.zeros((nx, ny))
    hzy = np.zeros((nx, ny))
    return [hzx, hzy]


def calculate_constants(eps: np.ndarray, mu: np.ndarray, sigmas: List[np.ndarray], 
                       dx: float, dy: float, dt: float) -> List[np.ndarray]:
    """
    Calculate update constants for Berenger PML implementation.
    
    Args:
        eps: Permittivity array
        mu: Permeability array
        sigmas: List of conductivity arrays [sigmax, sigmay, sigmamx, sigmamy]
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        
    Returns:
        List containing [ex1, ex2, ey1, ey2, hzx1, hzx2, hzy1, hzy2]
    """
    sigmax, sigmay, sigmamx, sigmamy = sigmas
    
    eps_shorty = (eps[:, 1:] + eps[:, :-1]) / 2
    eps_shortx = (eps[1:, :] + eps[:-1, :]) / 2
    
    ex1 = (2 * eps_shorty - sigmay * dt) / (2 * eps_shorty + sigmay * dt)
    ex2 = ((2 * dt) / (2 * eps_shorty + sigmay * dt)) / dy
    ey1 = (2 * eps_shortx - sigmax * dt) / (2 * eps_shortx + sigmax * dt)
    ey2 = ((2 * dt) / (2 * eps_shortx + sigmax * dt)) / dx
    hzx1 = (2 * mu - sigmamx * dt) / (2 * mu + sigmamx * dt)
    hzy1 = (2 * mu - sigmamy * dt) / (2 * mu + sigmamy * dt)
    hzx2 = ((2 * dt) / (2 * mu + sigmamx * dt)) / dx
    hzy2 = ((2 * dt) / (2 * mu + sigmamy * dt)) / dy
    
    return [ex1, ex2, ey1, ey2, hzx1, hzx2, hzy1, hzy2]


def evolution(nt: int, fields: List[np.ndarray], aux_fields: List[np.ndarray], 
              constants: List[np.ndarray], history: np.ndarray, 
              sourcepoint: Tuple[int, int], source: Callable[[int], float]) -> np.ndarray:
    """
    Evolve electromagnetic fields using Berenger PML.
    
    Args:
        nt: Number of time steps
        fields: List containing [Ex, Ey, Hz] arrays
        aux_fields: List containing [hzx, hzy] auxiliary arrays
        constants: List containing update constants
        history: Array to store field history, shape (nx, ny, nt)
        sourcepoint: Tuple (x, y) where source is applied
        source: Source function taking time step and returning value
        
    Returns:
        Array containing field history
    """
    ex, ey, hz = fields
    hzx, hzy = aux_fields
    ex1, ex2, ey1, ey2, hzx1, hzx2, hzy1, hzy2 = constants
    
    for t in range(nt):
        hzx = hzx1 * hzx - hzx2 * (ey[1:, :] - ey[:-1, :])
        hzy = hzy1 * hzy + hzy2 * (ex[:, 1:] - ex[:, :-1])
        hz = hzx + hzy
        hz[sourcepoint] = source(t)
        
        ex[:, 1:-1] = ex1 * ex[:, 1:-1] + ex2 * (hz[:, 1:] - hz[:, :-1])
        ey[1:-1, :] = ey1 * ey[1:-1, :] - ey2 * (hz[1:, :] - hz[:-1, :])
        
        history[:, :, t] = hz
    
    return history
