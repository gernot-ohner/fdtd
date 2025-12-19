"""Pytest configuration and fixtures."""
import sys
from pathlib import Path

# Add src directory to path so we can import modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
import pytest
import scipy.constants as const

import config
import sources


@pytest.fixture
def small_sim_params():
    """Small simulation parameters for fast tests."""
    return config.SimulationParameters(
        nx=20,
        ny=20,
        dx=0.05,
        dy=0.05,
        nt=10,
        source_point=(10, 10),
        pml_config=(5, 1e-6, 3)
    )


@pytest.fixture
def default_sim_params():
    """Default simulation parameters."""
    return config.SimulationParameters()


@pytest.fixture
def simple_source():
    """Simple source function."""
    return sources.simple_sin_source


@pytest.fixture
def null_source_func():
    """Null source function."""
    return sources.null_source
