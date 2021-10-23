import numpy as np


def simple_sin_source(n):
    """
    :param n: int
    :return: float
    """
    return np.sin(n / 5)


def null_source(n):
    """
    Returns 0. Designed to mimic a real source as closely as possible - thus the unnecessary argument
    and equally unnecessary multiplication operation
    :param n: int
    :return: float
    """
    return n * 0
