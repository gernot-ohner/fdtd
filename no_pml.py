import scipy.constants as const


def calculate_constants(dx, dy, dt):
    """
    Calculates the constants used in the updates equations for a vacuum.
    :param dx: float
    :param dy: float
    :param dt: float
    :return: List[4 floats]
    """
    eps = const.epsilon_0
    mu = const.mu_0

    cex = dt / (eps * dy)
    cey = dt / (eps * dx)
    chzx = dt / (mu * dx)
    chzy = dt / (mu * dy)

    return [cex, cey, chzx, chzy]


def evolution(nt, fields, constants, history, sourcepoint, source):
    """
    Calculate the behavior of the situation determined by the "constants" with a matrix implementation without a pml.
    A source determined by the function "source" excites the field at point "sourcepoint".
    The value of "hz" at each timestep is stored in "history" which is then returned.
    :param nt: int
    :param fields: List[3 np.ndarrays]
    :param constants: List[4 floats]
    :param history: np.ndarray of size (nx, ny, nt)
    :param sourcepoint: Tuple(float, float)
    :param source: function
    :return:
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


def loop_evolution(nx, ny, nt, fields, constants, history, sourcepoint, source):
    """
    Calculate the behavior of the situation determined by the "constants" with a loop implementation.
    A source determined by the function "source" excites the field at point "sourcepoint".
    The value of "hz" at each timestep is stored in "history" which is then returned.
    :param nx: int
    :param ny: int
    :param nt: int
    :param fields: List[3 np.ndarrays]
    :param constants: List[4 floats]
    :param history: np.ndarray of size (nx, ny, nt)
    :param sourcepoint: Tuple(float, float)
    :param source: function
    :return:
    """
    ex, ey, hz = fields
    cex, cey, chx, chy = constants
    for t in range(nt):
        for i in range(nx):
            for j in range(1, ny - 1):
                ex[i, j] = ex[i, j] + cex * (hz[i, j] - hz[i, j - 1])
        for i in range(1, nx - 1):
            for j in range(ny):
                ey[i, j] = ey[i, j] - cey * (hz[i, j] - hz[i - 1, j])
        for i in range(nx):
            for j in range(ny):
                hz[i, j] = hz[i, j] + chy * (ex[i, j + 1] - ex[i, j]) - chx * (ey[i + 1, j] - ey[i, j])
        hz[sourcepoint] = source(t)
        for i in range(nx):
            for j in range(ny):
                history[i,j,t] = hz[i,j]
    return history
