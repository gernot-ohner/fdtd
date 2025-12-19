"""Source functions for FDTD simulation."""
import numpy as np
from typing import Protocol


class SourceFunction(Protocol):
    """Protocol for source functions."""
    def __call__(self, time_step: int) -> float:
        """Return source value at given time step."""
        ...


def simple_sin_source(time_step: int) -> float:
    """
    Simple sinusoidal source function.
    
    Args:
        time_step: Current time step
        
    Returns:
        Source value at the given time step
    """
    return np.sin(time_step / 5)


def null_source(time_step: int) -> float:
    """
    Null source function (returns 0).
    
    Designed to mimic a real source as closely as possible for benchmarking.
    
    Args:
        time_step: Current time step (unused)
        
    Returns:
        Always returns 0.0
    """
    return time_step * 0
