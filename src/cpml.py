"""Convolutional Perfectly Matched Layer (CPML) implementation."""
from typing import List, Tuple, Callable

import numpy as np
import scipy.constants as const


def make_auxiliary_fields(nx: int, ny: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Create auxiliary fields required for CPML.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        
    Returns:
        Tuple containing (pex, pey, phx, phy) arrays
    """
    pex = np.zeros((nx - 1, ny))
    pey = np.zeros((nx, ny - 1))
    phx = np.zeros((nx, ny))
    phy = np.zeros((nx, ny))
    return pex, pey, phx, phy


def calculate_constants(eps: np.ndarray, mu: np.ndarray, dx: float, dy: float, dt: float) -> List[np.ndarray]:
    """
    Calculate update constants for CPML implementation.
    
    Args:
        eps: Permittivity array
        mu: Permeability array
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        
    Returns:
        List containing [cex, cey, chx, chy, px, py, pm]
    """
    kx = 1
    ky = 1
    
    cex = dt / (ky * dy * eps)
    cey = dt / (kx * dx * eps)
    chx = dt / (ky * dy * mu)
    chy = dt / (kx * dx * mu)
    cex = (cex[:, 1:] + cex[:, :-1]) / 2
    cey = (cey[1:, :] + cey[:-1, :]) / 2
    
    pe = dt / eps
    pm = dt / mu
    px = (pe[:, 1:] + pe[:, :-1]) / 2
    py = (pe[1:, :] + pe[:-1, :]) / 2
    
    return [cex, cey, chx, chy, px, py, pm]


def cpml_constants(nx: int, ny: int, sigmas: List[np.ndarray], dx: float, dy: float, dt: float) -> List[np.ndarray]:
    """
    Calculate CPML-specific constants for auxiliary field updates.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        sigmas: List of conductivity arrays [sigmax, sigmay, sigmamx, sigmamy]
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        dt: Time discretization
        
    Returns:
        List containing [aex, aey, ahx, ahy, bex, bey, bhx, bhy]
    """
    k = 1
    
    alpha_x = np.ones((nx - 1, ny))
    alpha_y = np.ones((nx, ny - 1))
    alpha_mx = np.ones((nx, ny))
    alpha_my = np.ones((nx, ny))
    
    # Set up alpha values for PML region (10 cells)
    for i in range(10):
        alpha_x[i, :] = (i + 1) / 10
        alpha_x[-i - 1, :] = (i + 1) / 10
        alpha_mx[i, :] = (i + 1) / 10
        alpha_mx[-i - 1, :] = (i + 1) / 10
        alpha_y[:, i] = (i + 1) / 10
        alpha_y[:, -i - 1] = (i + 1) / 10
        alpha_my[:, i] = (i + 1) / 10
        alpha_my[:, -i - 1] = (i + 1) / 10
    
    bex = np.exp(-(sigmas[0] / (k + alpha_x)) * (dt / const.epsilon_0))
    bey = np.exp(-(sigmas[1] / (k + alpha_y)) * (dt / const.epsilon_0))
    bhx = np.exp(-(sigmas[2] / (k + alpha_mx)) * (dt / const.epsilon_0))
    bhy = np.exp(-(sigmas[3] / (k + alpha_my)) * (dt / const.epsilon_0))
    
    aex = (bex - 1) / dx
    aey = (bey - 1) / dy
    ahx = (bhx - 1) / dx
    ahy = (bhy - 1) / dy
    
    return [aex, aey, ahx, ahy, bex, bey, bhx, bhy]


def evolution(nt: int, fields: List[np.ndarray], aux_fields: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
              constants: List[np.ndarray], aux_constants: List[np.ndarray], history: np.ndarray,
              sourcepoint: Tuple[int, int], source: Callable[[int], float]) -> np.ndarray:
    """
    Evolve electromagnetic fields using CPML.
    
    Args:
        nt: Number of time steps
        fields: List containing [Ex, Ey, Hz] arrays
        aux_fields: Tuple containing (pex, pey, phx, phy) auxiliary arrays
        constants: List containing main update constants
        aux_constants: List containing CPML auxiliary constants
        history: Array to store field history, shape (nx, ny, nt)
        sourcepoint: Tuple (x, y) where source is applied
        source: Source function taking time step and returning value
        
    Returns:
        Array containing field history
    """
    ex, ey, hz = fields
    pex, pey, phx, phy = aux_fields
    cex, cey, chy, chx, px, py, pm = constants
    aex, aey, ahx, ahy, bex, bey, bhx, bhy = aux_constants
    
    for t in range(nt):
        phy = bhy * phy + ahy * (ex[:, 1:] - ex[:, :-1])
        phx = bhx * phx + ahx * (ey[1:, :] - ey[:-1, :])
        
        hz = hz - chy * (ey[1:, :] - ey[:-1, :]) + chx * (ex[:, 1:] - ex[:, :-1]) + pm * (phy - phx)
        hz[sourcepoint] = source(t)
        
        pey = bey * pey + aey * (hz[:, 1:] - hz[:, :-1])
        pex = bex * pex + aex * (hz[1:, :] - hz[:-1, :])
        
        ex[:, 1:-1] = ex[:, 1:-1] + cex * (hz[:, 1:] - hz[:, :-1]) + px * pey
        ey[1:-1, :] = ey[1:-1, :] - cey * (hz[1:, :] - hz[:-1, :]) - py * pex
        
        history[:, :, t] = hz
    
    return history
