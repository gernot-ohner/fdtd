"""Tests for Convolutional PML implementation."""
import numpy as np
import pytest

import cpml
import common


class TestAuxiliaryFields:
    """Tests for auxiliary field creation."""
    
    def test_make_auxiliary_fields(self):
        """Test auxiliary field creation."""
        nx, ny = 10, 20
        aux_fields = cpml.make_auxiliary_fields(nx, ny)
        
        assert len(aux_fields) == 4
        pex, pey, phx, phy = aux_fields
        
        assert pex.shape == (nx - 1, ny)
        assert pey.shape == (nx, ny - 1)
        assert phx.shape == (nx, ny)
        assert phy.shape == (nx, ny)
        assert np.all(pex == 0)
        assert np.all(pey == 0)
        assert np.all(phx == 0)
        assert np.all(phy == 0)


class TestCalculateConstants:
    """Tests for constant calculation."""
    
    def test_constants_shape(self):
        """Test that constants have correct shape."""
        nx, ny = 10, 10
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        dx, dy, dt = 0.05, 0.05, 1e-10
        
        constants = cpml.calculate_constants(eps, mu, dx, dy, dt)
        
        assert len(constants) == 7
        cex, cey, chx, chy, px, py, pm = constants
        
        # Check shapes
        assert cex.shape == (nx, ny - 1)
        assert cey.shape == (nx - 1, ny)
        assert chx.shape == (nx, ny)
        assert chy.shape == (nx, ny)
        assert px.shape == (nx, ny - 1)
        assert py.shape == (nx - 1, ny)
        assert pm.shape == (nx, ny)


class TestCPMLConstants:
    """Tests for CPML-specific constants."""
    
    def test_cpml_constants_shape(self):
        """Test CPML constants have correct shape."""
        nx, ny = 20, 20
        sigmas = common.make_sigmas(nx, ny)
        dx, dy, dt = 0.05, 0.05, 1e-10
        
        constants = cpml.cpml_constants(nx, ny, sigmas, dx, dy, dt)
        
        assert len(constants) == 8
        aex, aey, ahx, ahy, bex, bey, bhx, bhy = constants
        
        # Check shapes
        assert aex.shape == (nx - 1, ny)
        assert aey.shape == (nx, ny - 1)
        assert ahx.shape == (nx, ny)
        assert ahy.shape == (nx, ny)
        assert bex.shape == (nx - 1, ny)
        assert bey.shape == (nx, ny - 1)
        assert bhx.shape == (nx, ny)
        assert bhy.shape == (nx, ny)


class TestEvolution:
    """Tests for field evolution."""
    
    def test_evolution_returns_history(self):
        """Test that evolution returns correct history."""
        # Use larger grid to avoid PML index issues
        nx, ny, nt = 30, 30, 5
        fields = common.make_fields(nx, ny)
        aux_fields = cpml.make_auxiliary_fields(nx, ny)
        
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        constants = cpml.calculate_constants(eps, mu, 0.05, 0.05, 1e-10)
        
        sigmas = common.make_sigmas(nx, ny)
        aux_constants = cpml.cpml_constants(nx, ny, sigmas, 0.05, 0.05, 1e-10)
        
        history = np.zeros((nx, ny, nt))
        sourcepoint = (15, 15)
        
        def source(t):
            return 1.0 if t == 0 else 0.0
        
        result = cpml.evolution(nt, fields, aux_fields, constants, aux_constants, 
                                history, sourcepoint, source)
        
        assert result.shape == (nx, ny, nt)
        assert result is history
    
    def test_source_applied(self):
        """Test that source is applied."""
        # Use larger grid to avoid PML index issues
        nx, ny, nt = 30, 30, 1
        fields = common.make_fields(nx, ny)
        aux_fields = cpml.make_auxiliary_fields(nx, ny)
        
        eps = np.ones((nx, ny)) * 1.0
        mu = np.ones((nx, ny)) * 1.0
        constants = cpml.calculate_constants(eps, mu, 0.05, 0.05, 1e-10)
        
        sigmas = common.make_sigmas(nx, ny)
        aux_constants = cpml.cpml_constants(nx, ny, sigmas, 0.05, 0.05, 1e-10)
        
        history = np.zeros((nx, ny, nt))
        sourcepoint = (15, 15)
        source_value = 2.0
        
        def source(t):
            return source_value
        
        cpml.evolution(nt, fields, aux_fields, constants, aux_constants, 
                      history, sourcepoint, source)
        
        # Source should be in history
        assert abs(history[sourcepoint[0], sourcepoint[1], 0] - source_value) < 1e-10
