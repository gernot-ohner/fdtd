import numpy as np
import scipy.constants as const


def make_auxiliary_fields(nx, ny):
    """
    Creates fields exclusive to the CPML.
    :param nx: int
    :param ny: int
    :return: List[4 np.ndarrays]
    """
    pex = np.zeros((nx - 1, ny))
    pey = np.zeros((nx, ny - 1))
    phx = np.zeros((nx, ny))
    phy = np.zeros((nx, ny))
    return pex, pey, phx, phy


def calculate_constants(eps, mu, dx, dy, dt):
    """
    Calculate the constants used in the update equations of ex, ey and hz.
    These constants depend on epsilon, mu and sigma and completely describe the environment.
    :param eps: np.ndarray
    :param mu: np.ndarray
    :param dx: float
    :param dy: float
    :param dt: float
    :return: List[7 np.ndarrays]
    """
    kx = 1
    ky = 1

    cex = dt / (ky*dy*eps)
    cey = dt / (kx*dx*eps)
    chx = dt / (ky*dy*mu)
    chy = dt / (kx*dx*mu)
    cex = (cex[:, 1:] + cex[:, :-1]) / 2
    cey = (cey[1:, :] + cey[:-1, :]) / 2

    pe = dt / eps
    pm = dt / mu
    px = (pe[:, 1:] + pe[:, :-1]) / 2
    py = (pe[1:, :] + pe[:-1, :]) / 2

    return [cex, cey, chx, chy, px, py, pm]


def cpml_constants(nx, ny, sigmas, dx, dy, dt):
    """
    Calculate the constants used in the update equations of pex, pey, phx, phy
    These constants depend on epsilon, mu and sigma and completely describe the environment.
    :param nx: int
    :param ny: int
    :param sigmas: List[4 np.ndarrays]
    :param dx: float
    :param dy: float
    :param dt: float
    :return: List[8 np.ndarrays]
    """
    k = 1

    alpha_x = np.ones((nx-1, ny))
    alpha_y = np.ones((nx, ny-1))
    alpha_mx = np.ones((nx, ny))
    alpha_my = np.ones((nx, ny))

    for i in range(10):
        alpha_x[i, :] = (i + 1) / 10
        alpha_x[-i - 1, :] = (i + 1) / 10
        alpha_mx[i, :] = (i + 1) / 10
        alpha_mx[-i - 1, :] = (i + 1) / 10
        alpha_y[:, i] = (i + 1) / 10
        alpha_y[:, -i - 1] = (i + 1) / 10
        alpha_my[:, i] = (i + 1) / 10
        alpha_my[:, -i - 1] = (i + 1) / 10

    bex = np.exp(-(sigmas[0]/(k + alpha_x)) * (dt / const.epsilon_0))
    bey = np.exp(-(sigmas[1]/(k + alpha_y)) * (dt / const.epsilon_0))
    bhx = np.exp(-(sigmas[2]/(k + alpha_mx)) * (dt / const.epsilon_0))
    bhy = np.exp(-(sigmas[3]/(k + alpha_my)) * (dt / const.epsilon_0))

    aex = (bex - 1) / dx
    aey = (bey - 1) / dy
    ahx = (bhx - 1) / dx
    ahy = (bhy - 1) / dy

    return [aex, aey, ahx, ahy, bex, bey, bhx, bhy]


def evolution(nt, fields, aux_fields, constants, aux_constants, history, sourcepoint, source):
    """
    Calculate the behavior of the situation determined by the "constants" and "aux_constants".
    A source determined by the function "source" excites the field at point "sourcepoint".
    The value of "hz" at each timestep is stored in "history" which is then returned.
    :param nt: int
    :param fields: List[3 np.ndarrays]
    :param aux_fields: List[4 np.ndarrays]
    :param constants: List[7 np.ndarrays]
    :param aux_constants: List[8 np.ndarrays]
    :param history: np.ndarray of size [nx, ny, nt]
    :param sourcepoint: Tuple(float, float)
    :param source: function
    :return: np.ndarray of size [nx, ny, nt]
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
