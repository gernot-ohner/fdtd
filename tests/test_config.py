"""Tests for configuration module."""
import math
import pytest
import scipy.constants as const

import config


class TestSimulationParameters:
    """Tests for SimulationParameters dataclass."""
    
    def test_default_values(self):
        """Test default parameter values."""
        params = config.SimulationParameters()
        assert params.nx == 100
        assert params.ny == 100
        assert params.dx == 0.05
        assert params.dy == 0.05
        assert params.nt == 200
        assert params.pml_config == (10, 1e-6, 3)
    
    def test_custom_values(self):
        """Test custom parameter values."""
        params = config.SimulationParameters(
            nx=50,
            ny=60,
            dx=0.1,
            dy=0.1,
            nt=100
        )
        assert params.nx == 50
        assert params.ny == 60
        assert params.dx == 0.1
        assert params.dy == 0.1
        assert params.nt == 100
    
    def test_derived_parameters(self):
        """Test that derived parameters are calculated correctly."""
        params = config.SimulationParameters(nx=100, ny=200, dx=0.05, dy=0.1)
        assert params.lx == 100 * 0.05
        assert params.ly == 200 * 0.1
    
    def test_dt_calculation(self):
        """Test that dt is calculated using Courant condition."""
        params = config.SimulationParameters(dx=0.05, dy=0.05)
        expected_dt = (const.c * math.sqrt((0.05 ** -2) + (0.05 ** -2))) ** -1
        assert abs(params.dt - expected_dt) < 1e-15
    
    def test_default_source_point(self):
        """Test that source point defaults to center."""
        params = config.SimulationParameters(nx=100, ny=100)
        assert params.source_point == (50, 50)
    
    def test_custom_source_point(self):
        """Test custom source point."""
        params = config.SimulationParameters(
            nx=100,
            ny=100,
            source_point=(25, 75)
        )
        assert params.source_point == (25, 75)
    
    def test_to_list(self):
        """Test conversion to list format."""
        params = config.SimulationParameters()
        param_list = params.to_list()
        assert len(param_list) == 11
        assert param_list[0] == params.nx
        assert param_list[1] == params.ny
        assert param_list[2] == params.lx
        assert param_list[3] == params.ly
        assert param_list[-1] is None  # Source function placeholder


class TestEnums:
    """Tests for enum types."""
    
    def test_action_enum(self):
        """Test Action enum values."""
        assert config.Action.NORMAL.value == "normal"
        assert config.Action.PML.value == "pml"
        assert config.Action.LOSS.value == "loss"
        assert config.Action.COMPARISON.value == "comparison"
        assert config.Action.TIME.value == "time"
        assert config.Action.TRIVIAL.value == "trivial"
        assert config.Action.ALL.value == "all"
    
    def test_pml_type_enum(self):
        """Test PMLType enum values."""
        assert config.PMLType.NO.value == "no"
        assert config.PMLType.BPML.value == "bpml"
        assert config.PMLType.CPML.value == "cpml"
