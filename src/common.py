import math

import matplotlib.animation as anim
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import scipy.constants as const
from typing import *


def make_fields(nx, ny):
    """
    Creates the fields Ex, Ey and Hz required for every simulation as numpy arrays of desired size
    :param nx: int
    :param ny: int
    :return: List[np.ndrarray, np.ndarray, np.ndarray]
    """
    ex = np.zeros((nx, ny + 1))
    ey = np.zeros((nx + 1, ny))
    hz = np.zeros((nx, ny))
    return [ex, ey, hz]


def make_sigmas(nx, ny):
    """
    Creates the empty numpy arrays containing the electric and magnetic conductivities
    :param nx: int
    :param ny: int
    :return: List[np.ndrarray, np.ndarray, np.ndarray, np.ndarray]
    """
    sigmax = np.zeros((nx - 1, ny))
    sigmay = np.zeros((nx, ny - 1))
    sigmamx = np.zeros((nx, ny))
    sigmamy = np.zeros((nx, ny))
    return [sigmax, sigmay, sigmamx, sigmamy]


def luneberg(eps, mx, my, R):
    """
    Modifies the permittivity to create a Luneberg lens at position (mx,my) of radius R
    Returns the a matrix containing the new permittivities.
    Currently unused.
    :param eps: np.ndarray
    :param mx: int
    :param my: int
    :param R: int
    :return: np.ndarray
    """

    for qx in range(mx - R, mx + R):
        for qy in range(my - R, my + R):
            r = int(math.sqrt((qx - mx) ** 2 + (qy - my) ** 2))
            if r > R:
                continue
            eps[qx, qy] *= 2 - (r / R) ** 2

    return eps


def add_loss(sigmas, w, s):
    """
    Adds a constant electrical conductivity of magnitude "s" on all points in the grid except the PML of thickness w
    :param sigmas: List[4 np.ndarrays]
    :param w: int
    :param s: float
    :return:
    """
    sigmas[0][w:-w, w:-w] = s
    sigmas[1][w:-w, w:-w] = s
    return sigmas


def make_env(nx, ny):
    """
    Creates
    :param nx: int
    :param ny: int
    :return: np.ndarray, np.ndarray
    """
    eps = np.ones((nx, ny)) * const.epsilon_0
    mu = np.ones((nx, ny)) * const.mu_0
    return eps, mu


def pml(sigmas, pmlc, dx, dy):
    """
    Fills the given numpy arrays with appropriate conductivities for a perfectly matched layer with grading
    :param sigmas: List[np.ndarrays]
    :param pmlc: Tuple(float, float, float)
    :param dx: float
    :param dy: float
    :return:
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


def get_modes(data):
    """
    Calculate minimum, mean and standard deviation of the given data.
    :param data: np.ndarray
    :return: List[float, float, float]
    """
    return [np.min(data), np.mean(data), np.std(data)]


def meters_to_points(meters_x, meters_y, dx, dy):
    """
    Convert a tuple of meters to a tuple of cells using the discretization parameters.
    :param meters_x: float
    :param meters_y: float
    :param dx: float
    :param dy: float
    :return: Tuple(float, float)
    """
    return int(meters_x / dx), int(meters_y / dy)


def add_loss_half(sigmas):
    """
    Simple function that makes half the computational domain lossy with conductivity sigma = 0.01 S/m. Used
    Used for the creation of Fig. 3.8 a) and b).
    :param sigmas: List[4 np.ndarrays]
    :return:
    """
    y = int(sigmas[0].shape[1] / 2)
    sigmas[0][:, y:] = 0.01
    sigmas[1][:, y:] = 0.01

    return sigmas


def compare(data_sets: List):
    """
    Receive a list of multiple numpy arrays. Compute their min, mean and std using function get_modes()
    Use minimum of first numpy array as base case. Represent all results as multiples of this base case.
    Return the result
    :param data_sets: List[np.ndarray]
    :return:
    """
    base_case = np.min(data_sets[0])
    results = [get_modes(data) / base_case for data in data_sets]
    return results


def modify_env(eps, mu, sigmas):
    # modify the environment as in Problem 9.9
    # eps, mu, sigmas = common.sigmaenv1(eps, mu, sigmas, dx, dy)
    # eps, mu, sigmas = common.sigmaenv2(eps, mu, sigmas)
    # eps, mu = common.different_env(eps, mu)
    sigmas = add_loss_half(sigmas)
    return eps, mu, sigmas


def environment_problem_example(eps, mu, sigmas, dx, dy):
    """
    Modified the fields eps, mu and sigmas according to the problem posed by Fig. 3.9 a) and returns them.
    :param eps: np.ndarray
    :param mu: np.ndarray
    :param sigmas: List[4 np.ndarrays]
    :param dx: float
    :param dy: float
    :return:
    """
    pecx, pecy = meters_to_points(2.2, 3, dx, dy)
    sigmas[2][-pecx:, -pecy:] = 1e9
    sigmas[3][-pecx:, -pecy:] = 1e9

    plate_x1, plate_y1 = meters_to_points(2.1, 1.1, dx, dy)
    plate_x2, plate_y2 = meters_to_points(1.1, 2.1, dx, dy)
    qx = plate_x1 - plate_x2
    for i in range(0, qx):
        sigmas[2][plate_x2 + i, plate_y2 - i] = 1e9
        sigmas[3][plate_x2 + i, plate_y2 - i] = 1e9

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


def plot_2d(data, nt):
    """
    Plot an animated color plot of the received data "data" for "nt" time steps
    :param data: np.ndarray[nx, ny, nt]
    :param nt: int
    """
    plt.style.use('classic')
    maxval = np.max(data)
    print("maxval: ", maxval)
    fig = plt.figure()
    ims = []
    for i in range(nt):
        im = plt.imshow(np.fabs(data[:, :, i]), norm=colors.Normalize(0.0, maxval))
        ims.append([im])
    animation = anim.ArtistAnimation(fig, ims, interval=50)
    plt.show()


def plot_snaps(names: List, labels: List, data: List):
    """
    Recieve and plot multiple numpy arrays with appropriate axis labels and legend
    :param names: List[string]
    :param labels: List[string]
    :param data: List[np.ndarray]
    """
    for i in range(len(names)):
        plt.plot(data[i], label=names[i])
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    plt.legend()
    plt.show()
