"""Tests for Berenger PML implementation."""
import numpy as np
import pytest

import bpml
import common


class TestAuxiliaryFields:
    """Tests for auxiliary field creation."""
    
    def test_make_auxiliary_fields(self):
        """Test auxiliary field creation."""
        nx, ny = 10, 20
        aux_fields = bpml.make_auxiliary_fields(nx, ny)
        
        assert len(aux_fields) == 2
        hzx, hzy = aux_fields
        
        assert hzx.shape == (nx, ny)
        assert hzy.shape == (nx, ny)
        assert np.all(hzx == 0)
        assert np.all(hzy == 0)


class TestCalculateConstants:
    """Tests for constant calculation."""
    
    def test_constants_shape(self):
        """Test that constants have correct shape."""
        nx, ny = 10, 10
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        sigmas = common.make_sigmas(nx, ny)
        dx, dy, dt = 0.05, 0.05, 1e-10
        
        constants = bpml.calculate_constants(eps, mu, sigmas, dx, dy, dt)
        
        assert len(constants) == 8
        ex1, ex2, ey1, ey2, hzx1, hzx2, hzy1, hzy2 = constants
        
        # Check shapes
        assert ex1.shape == (nx, ny - 1)
        assert ex2.shape == (nx, ny - 1)
        assert ey1.shape == (nx - 1, ny)
        assert ey2.shape == (nx - 1, ny)
        assert hzx1.shape == (nx, ny)
        assert hzx2.shape == (nx, ny)
        assert hzy1.shape == (nx, ny)
        assert hzy2.shape == (nx, ny)
    
    def test_constants_with_loss(self):
        """Test constants calculation with conductivity."""
        nx, ny = 10, 10
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        sigmas = common.make_sigmas(nx, ny)
        sigmas[0][:] = 0.01  # Add some conductivity
        dx, dy, dt = 0.05, 0.05, 1e-10
        
        constants = bpml.calculate_constants(eps, mu, sigmas, dx, dy, dt)
        
        # Should still return 8 constants
        assert len(constants) == 8


class TestEvolution:
    """Tests for field evolution."""
    
    def test_evolution_returns_history(self):
        """Test that evolution returns correct history."""
        nx, ny, nt = 10, 10, 5
        fields = common.make_fields(nx, ny)
        aux_fields = bpml.make_auxiliary_fields(nx, ny)
        
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        sigmas = common.make_sigmas(nx, ny)
        constants = bpml.calculate_constants(eps, mu, sigmas, 0.05, 0.05, 1e-10)
        
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        
        def source(t):
            return 1.0 if t == 0 else 0.0
        
        result = bpml.evolution(nt, fields, aux_fields, constants, history, sourcepoint, source)
        
        assert result.shape == (nx, ny, nt)
        assert result is history
    
    def test_source_applied(self):
        """Test that source is applied."""
        nx, ny, nt = 10, 10, 1
        fields = common.make_fields(nx, ny)
        aux_fields = bpml.make_auxiliary_fields(nx, ny)
        
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        sigmas = common.make_sigmas(nx, ny)
        constants = bpml.calculate_constants(eps, mu, sigmas, 0.05, 0.05, 1e-10)
        
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        source_value = 2.0
        
        def source(t):
            return source_value
        
        bpml.evolution(nt, fields, aux_fields, constants, history, sourcepoint, source)
        
        # Source should be in history
        assert abs(history[sourcepoint[0], sourcepoint[1], 0] - source_value) < 1e-10
