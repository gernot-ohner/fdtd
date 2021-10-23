import numpy as np


def make_auxiliary_fields(nx, ny):
    """
    Creates fields exclusive to the Berenger PML.
    :param nx: int
    :param ny: int
    :return: List[2 np.ndarrays]
    """
    hzx = np.zeros((nx, ny))
    hzy = np.zeros((nx, ny))
    return [hzx, hzy]


def calculate_constants(eps, mu, sigmas, dx, dy, dt):
    """
    Calculate the constants used in the update equations of ex, ey and hz.
    These constants depend on epsilon, mu and sigma and completely describe the environment.
    :param eps: np.ndarray
    :param mu: np.ndarray
    :param sigmas: List[4 np.ndarrays]
    :param dx: float
    :param dy: float
    :param dt: float
    :return: List[8 np.ndarrays]
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


def evolution(nt, fields, aux_fields, constants, history, sourcepoint, source):
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
