import numpy as np
import timeit
import common
import scipy.constants as const
import math
import source as src
import matplotlib.pyplot as plt



timesteps = 200
dx = 0.05
dy = 0.05
dt = (const.c * math.sqrt((dx ** -2) + (dy ** -2))) ** -1

def prelim():
    eps = const.epsilon_0
    mu = const.mu_0
    N = 100
    fields = common.make_fields(N, N)
    history = np.zeros((N, N, timesteps))

    q = int(N/2)

    num = 1
    rep = 100
    constants = other_constants(eps, mu, dx, dy, dt)

    def loopycaller():
        loopy(fields, constants, history, N, q)

    def numpylycaller():
        #constants = other_constants(eps, mu, dx, dy, dt)
        numpyly(fields, constants, history, N, q)

    def numpylosscaller():
        #constants = loss_constants(eps, mu, 0, 0, dx, dy, dt)
        numpyly_loss(fields, constants, history, N, q)

    loopytime = timeit.repeat(loopycaller, number = num, repeat = rep)
    numpylytime = timeit.repeat(numpylycaller, number = num, repeat = rep)
    #numpylosstime = timeit.timeit(numpylycaller, number = num) / num
    print(loopytime)
    print(numpylytime)

    loopytime = np.min(loopytime)
    numpylytime = np.min(numpylytime)
    loopytime = loopytime/numpylytime

    loopy_mean = np.mean(loopytime)
    numpyly_mean = np.mean(numpylytime)
    loopy_mean = loopy_mean/numpylytime
    numpyly_mean = numpyly_mean/numpylytime
    print("loopytime mean:", loopy_mean)
    print("numpytime mean:", numpyly_mean)

    loopy_std = np.std(loopytime)
    numpyly_std = np.std(numpylytime)
    loopy_std = loopy_std/numpylytime
    numpyly_std = numpyly_std/numpylytime
    print("loopytime std:", loopy_std)
    print("numpytime std:", numpyly_std)

    numpylytime = 1
    print("loopytime min:", loopytime)
    print("numpytime min:", numpylytime)
    # history = numpyly(fields, constants, history, N, q)
    history = loopy(fields, constants, history, N, q)
    common.plot2d(history, timesteps)

    return [loopytime, numpylytime]
    #return [numpylytime, numpylosstime]

def other_constants(eps, mu, dx, dy, dt):
    cex = dt / (dy*eps)
    cey = dt / (dx*eps)
    chx = dt / (dy*mu)
    chy = dt / (dx*mu)
    return [cex, cey, chx, chy]

def loss_constants(eps, mu, sigma, sigmam, dx, dy, dt):
    cex1 = (2 * eps - sigma * dt) / (2 * eps + sigma * dt)
    cex2 = ((2 * dt) / (2 * eps + sigma * dt)) / dy
    chz1 = (2 * mu - sigmam * dt) / (2 * mu + sigmam * dt)
    chz2 = ((2 * dt) / (2 * mu + sigmam * dt)) / dx
    return [cex1, cex2, chz1, chz2]

def loopy(fields, constants, history, N, q):
    ex, ey, hz = fields
    cex, cey, chx, chy = constants
    for t in range(timesteps):
        for i in range(N):
            for j in range(1, N - 1):
                ex[i, j] = ex[i, j] + cex * (hz[i, j] - hz[i, j - 1])
        for i in range(1, N - 1):
            for j in range(N):
                ey[i, j] = ey[i, j] - cey * (hz[i, j] - hz[i - 1, j])
        for i in range(N):
            for j in range(N):
                hz[i, j] = hz[i, j] + chy * (ex[i, j + 1] - ex[i, j]) - chx * (ey[i + 1, j] - ey[i, j])
        hz[q, q] = src.simple_sin_source(t)
#        for i in range(N):
#            for j in range(N):
#                history[i,j,t] = hz[i,j]
#    return history

prelim()


