"""Common utilities for FDTD simulation."""
import math
from typing import List, Tuple

import matplotlib.animation as anim
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import scipy.constants as const


def make_fields(nx: int, ny: int) -> List[np.ndarray]:
    """
    Create the electromagnetic fields Ex, Ey and Hz required for simulation.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        
    Returns:
        List containing [Ex, Ey, Hz] arrays
    """
    ex = np.zeros((nx, ny + 1))
    ey = np.zeros((nx + 1, ny))
    hz = np.zeros((nx, ny))
    return [ex, ey, hz]


def make_sigmas(nx: int, ny: int) -> List[np.ndarray]:
    """
    Create empty arrays for electric and magnetic conductivities.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        
    Returns:
        List containing [sigmax, sigmay, sigmamx, sigmamy] arrays
    """
    sigmax = np.zeros((nx - 1, ny))
    sigmay = np.zeros((nx, ny - 1))
    sigmamx = np.zeros((nx, ny))
    sigmamy = np.zeros((nx, ny))
    return [sigmax, sigmay, sigmamx, sigmamy]


def luneberg(eps: np.ndarray, mx: int, my: int, R: int) -> np.ndarray:
    """
    Modify permittivity to create a Luneburg lens at position (mx, my) of radius R.
    
    Currently unused but kept for potential future use.
    
    Args:
        eps: Permittivity array
        mx: x position of lens center
        my: y position of lens center
        R: Radius of lens
        
    Returns:
        Modified permittivity array
    """
    for qx in range(mx - R, mx + R):
        for qy in range(my - R, my + R):
            r = int(math.sqrt((qx - mx) ** 2 + (qy - my) ** 2))
            if r > R:
                continue
            eps[qx, qy] *= 2 - (r / R) ** 2
    return eps


def add_loss(sigmas: List[np.ndarray], w: int, s: float) -> List[np.ndarray]:
    """
    Add constant electrical conductivity to grid points excluding PML region.
    
    Args:
        sigmas: List of conductivity arrays [sigmax, sigmay, sigmamx, sigmamy]
        w: PML thickness in cells
        s: Conductivity value (S/m)
        
    Returns:
        Modified sigmas list
    """
    sigmas[0][w:-w, w:-w] = s
    sigmas[1][w:-w, w:-w] = s
    return sigmas


def make_env(nx: int, ny: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create environment with vacuum permittivity and permeability.
    
    Args:
        nx: Number of cells in x direction
        ny: Number of cells in y direction
        
    Returns:
        Tuple of (permittivity array, permeability array)
    """
    eps = np.ones((nx, ny)) * const.epsilon_0
    mu = np.ones((nx, ny)) * const.mu_0
    return eps, mu


def pml(sigmas: List[np.ndarray], pmlc: Tuple[int, float, int], dx: float, dy: float) -> List[np.ndarray]:
    """
    Fill conductivity arrays with PML values using polynomial grading.
    
    Args:
        sigmas: List of conductivity arrays to fill
        pmlc: PML configuration tuple (thickness, R0 reflection factor, grading parameter)
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        
    Returns:
        Modified sigmas list with PML values
    """
    w, r0, m = pmlc
    delta = np.sqrt((dx ** 2 + dy ** 2) / 2)
    sigmamax = -math.log(r0) * (m + 1) * const.epsilon_0 * const.c / (2 * w * delta)
    wp = w + 1
    
    for q in range(w):
        sigmas[0][q, :] = wp - 0.5 - q
        sigmas[0][-q - 1, :] = wp - 0.5 - q
        sigmas[1][:, q] = wp - 0.5 - q
        sigmas[1][:, -q - 1] = wp - 0.5 - q
        sigmas[2][q, :] = wp - q
        sigmas[2][-q - 1, :] = wp - q
        sigmas[3][:, q] = wp - q
        sigmas[3][:, -q - 1] = wp - q
    
    sigmas[0] = sigmamax * (sigmas[0] / w) ** m
    sigmas[1] = sigmamax * (sigmas[1] / w) ** m
    sigmas[2] = sigmamax * (sigmas[2] / w) ** m
    sigmas[3] = sigmamax * (sigmas[3] / w) ** m
    
    return sigmas


def get_modes(data: np.ndarray) -> List[float]:
    """
    Calculate minimum, mean and standard deviation of data.
    
    Args:
        data: Input array
        
    Returns:
        List containing [minimum, mean, std]
    """
    return [np.min(data), np.mean(data), np.std(data)]


def meters_to_points(meters_x: float, meters_y: float, dx: float, dy: float) -> Tuple[int, int]:
    """
    Convert physical coordinates (meters) to grid cell coordinates.
    
    Args:
        meters_x: x coordinate in meters
        meters_y: y coordinate in meters
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        
    Returns:
        Tuple of (x_cell, y_cell)
    """
    return int(meters_x / dx), int(meters_y / dy)


def add_loss_half(sigmas: List[np.ndarray]) -> List[np.ndarray]:
    """
    Make half the computational domain lossy with conductivity 0.01 S/m.
    
    Used for creating specific test scenarios.
    
    Args:
        sigmas: List of conductivity arrays
        
    Returns:
        Modified sigmas list
    """
    y = int(sigmas[0].shape[1] / 2)
    sigmas[0][:, y:] = 0.01
    sigmas[1][:, y:] = 0.01
    return sigmas


def compare(data_sets: List[np.ndarray]) -> List[np.ndarray]:
    """
    Compare multiple datasets by computing min/mean/std relative to first dataset.
    
    Args:
        data_sets: List of numpy arrays to compare
        
    Returns:
        List of arrays containing [min/base, mean/base, std/base] for each dataset
    """
    base_case = np.min(data_sets[0])
    results = [get_modes(data) / base_case for data in data_sets]
    return results


def modify_env(eps: np.ndarray, mu: np.ndarray, sigmas: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """
    Modify environment by adding loss to half the domain.
    
    Args:
        eps: Permittivity array
        mu: Permeability array
        sigmas: List of conductivity arrays
        
    Returns:
        Tuple of (eps, mu, sigmas)
    """
    sigmas = add_loss_half(sigmas)
    return eps, mu, sigmas


def environment_problem_example(eps: np.ndarray, mu: np.ndarray, sigmas: List[np.ndarray], 
                                dx: float, dy: float) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """
    Modify environment according to a specific problem setup.
    
    Creates:
    - Perfect conductor in bottom right corner
    - Diagonal plate of perfect conductor
    - Circular region with high permittivity and loss
    
    Args:
        eps: Permittivity array
        mu: Permeability array
        sigmas: List of conductivity arrays
        dx: Spatial discretization in x direction
        dy: Spatial discretization in y direction
        
    Returns:
        Tuple of (eps, mu, sigmas)
    """
    # Perfect conductor in bottom right corner
    pecx, pecy = meters_to_points(2.2, 3, dx, dy)
    sigmas[2][-pecx:, -pecy:] = 1e9
    sigmas[3][-pecx:, -pecy:] = 1e9
    
    # Diagonal plate
    plate_x1, plate_y1 = meters_to_points(2.1, 1.1, dx, dy)
    plate_x2, plate_y2 = meters_to_points(1.1, 2.1, dx, dy)
    qx = plate_x1 - plate_x2
    for i in range(0, qx):
        sigmas[2][plate_x2 + i, plate_y2 - i] = 1e9
        sigmas[3][plate_x2 + i, plate_y2 - i] = 1e9
    
    # Circular region with high permittivity
    bx, by = meters_to_points(1.6, 4.1, dx, dy)
    rx, ry = meters_to_points(0.5, 0.5, dx, dy)
    radius = int(np.sqrt(rx ** 2 / 2 + ry ** 2 / 2))
    
    for qx in range(bx - rx, bx + rx):
        for qy in range(by - ry, by + ry):
            r = int(math.sqrt((qx - bx) ** 2 + (qy - by) ** 2))
            if r > radius:
                continue
            sigmas[2][qx, qy] = 0.01
            sigmas[3][qx, qy] = 0.01
            eps[qx, qy] *= 4
    
    return eps, mu, sigmas


def plot_2d(data: np.ndarray, nt: int) -> None:
    """
    Plot animated 2D color plot of simulation data.
    
    Args:
        data: Array of shape (nx, ny, nt) containing field values
        nt: Number of time steps to animate
    """
    plt.style.use('classic')
    maxval = np.max(data)
    print(f"maxval: {maxval}")
    fig = plt.figure()
    ims = []
    for i in range(nt):
        im = plt.imshow(np.fabs(data[:, :, i]), norm=colors.Normalize(0.0, maxval))
        ims.append([im])
    animation = anim.ArtistAnimation(fig, ims, interval=50)
    plt.show()


def plot_snaps(names: List[str], labels: List[str], data: List[np.ndarray]) -> None:
    """
    Plot multiple 1D snapshots with labels and legend.
    
    Args:
        names: List of names for legend
        labels: List of [xlabel, ylabel]
        data: List of 1D arrays to plot
    """
    for i in range(len(names)):
        plt.plot(data[i], label=names[i])
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    plt.legend()
    plt.show()
