"""Configuration dataclasses and enums for FDTD simulation."""
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Tuple
import math
import scipy.constants as const


class Action(Enum):
    """Available simulation actions."""
    NORMAL = "normal"
    PML = "pml"
    LOSS = "loss"
    COMPARISON = "comparison"
    TIME = "time"
    TRIVIAL = "trivial"
    ALL = "all"


class PMLType(Enum):
    """Perfectly Matched Layer implementation types."""
    NO = "no"
    BPML = "bpml"
    CPML = "cpml"


@dataclass
class SimulationParameters:
    """Parameters for FDTD simulation."""
    nx: int = 100  # Number of Yee cells in x direction
    ny: int = 100  # Number of Yee cells in y direction
    dx: float = 0.05  # Discretization constant in x direction (meters)
    dy: float = 0.05  # Discretization constant in y direction (meters)
    nt: int = 200  # Number of time steps
    source_point: Tuple[int, int] = None  # Point where source term is added
    pml_config: Tuple[int, float, int] = (10, 1e-6, 3)  # (thickness, R0, grading parameter)
    
    def __post_init__(self):
        """Calculate derived parameters."""
        if self.source_point is None:
            self.source_point = (int(self.nx / 2), int(self.ny / 2))
        
        self.lx = self.nx * self.dx  # Length in x direction (meters)
        self.ly = self.ny * self.dy  # Length in y direction (meters)
        
        # Calculate time step using Courant condition
        self.dt = (const.c * math.sqrt((self.dx ** -2) + (self.dy ** -2))) ** -1
    
    def to_list(self) -> list:
        """Convert to list format for backward compatibility."""
        return [
            self.nx, self.ny, self.lx, self.ly,
            self.dx, self.dy, self.dt, self.nt,
            self.source_point, self.pml_config, None  # source function added separately
        ]
