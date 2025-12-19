"""Tests for common utility functions."""
import numpy as np
import pytest
import scipy.constants as const

import common


class TestFieldCreation:
    """Tests for field creation functions."""
    
    def test_make_fields(self):
        """Test field array creation."""
        nx, ny = 10, 20
        fields = common.make_fields(nx, ny)
        
        assert len(fields) == 3
        ex, ey, hz = fields
        
        # Check dimensions (Yee grid staggering)
        assert ex.shape == (nx, ny + 1)
        assert ey.shape == (nx + 1, ny)
        assert hz.shape == (nx, ny)
        
        # Check all zeros initially
        assert np.all(ex == 0)
        assert np.all(ey == 0)
        assert np.all(hz == 0)
    
    def test_make_sigmas(self):
        """Test conductivity array creation."""
        nx, ny = 10, 20
        sigmas = common.make_sigmas(nx, ny)
        
        assert len(sigmas) == 4
        sigmax, sigmay, sigmamx, sigmamy = sigmas
        
        # Check dimensions
        assert sigmax.shape == (nx - 1, ny)
        assert sigmay.shape == (nx, ny - 1)
        assert sigmamx.shape == (nx, ny)
        assert sigmamy.shape == (nx, ny)
        
        # Check all zeros initially
        assert np.all(sigmax == 0)
        assert np.all(sigmay == 0)
        assert np.all(sigmamx == 0)
        assert np.all(sigmamy == 0)
    
    def test_make_env(self):
        """Test environment creation."""
        nx, ny = 10, 20
        eps, mu = common.make_env(nx, ny)
        
        assert eps.shape == (nx, ny)
        assert mu.shape == (nx, ny)
        
        # Should be vacuum values
        assert np.all(eps == const.epsilon_0)
        assert np.all(mu == const.mu_0)


class TestPMLFunctions:
    """Tests for PML-related functions."""
    
    def test_pml_sigma_creation(self):
        """Test PML conductivity assignment."""
        nx, ny = 20, 20
        sigmas = common.make_sigmas(nx, ny)
        pmlc = (5, 1e-6, 3)
        dx, dy = 0.05, 0.05
        
        sigmas = common.pml(sigmas, pmlc, dx, dy)
        
        # PML regions should have non-zero values
        # Check boundaries
        assert np.any(sigmas[0][:5, :] != 0)  # Left boundary
        assert np.any(sigmas[0][-5:, :] != 0)  # Right boundary
        assert np.any(sigmas[1][:, :5] != 0)  # Bottom boundary
        assert np.any(sigmas[1][:, -5:] != 0)  # Top boundary
    
    def test_add_loss(self):
        """Test adding loss to domain."""
        nx, ny = 20, 20
        sigmas = common.make_sigmas(nx, ny)
        w = 5
        s = 0.01
        
        sigmas = common.add_loss(sigmas, w, s)
        
        # Interior should have loss
        assert np.all(sigmas[0][w:-w, w:-w] == s)
        assert np.all(sigmas[1][w:-w, w:-w] == s)
        
        # PML regions should remain unchanged (0 initially)
        # (They'll be set by pml() function separately)


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_meters_to_points(self):
        """Test coordinate conversion."""
        dx, dy = 0.05, 0.1
        meters_x, meters_y = 1.0, 2.0
        
        px, py = common.meters_to_points(meters_x, meters_y, dx, dy)
        
        assert px == 20  # 1.0 / 0.05
        assert py == 20  # 2.0 / 0.1
    
    def test_get_modes(self):
        """Test statistics calculation."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        modes = common.get_modes(data)
        
        assert len(modes) == 3
        assert modes[0] == 1.0  # min
        assert modes[1] == 3.0  # mean
        assert abs(modes[2] - np.std(data)) < 1e-10  # std
    
    def test_compare(self):
        """Test comparison function."""
        data1 = np.array([1.0, 2.0, 3.0])
        data2 = np.array([2.0, 4.0, 6.0])  # 2x data1
        
        results = common.compare([data1, data2])
        
        assert len(results) == 2
        # First should be normalized to 1.0 (base case)
        assert abs(results[0][0] - 1.0) < 1e-10  # min/base
        # Second should be approximately 2x
        assert abs(results[1][0] - 2.0) < 1e-10  # min/base


class TestLunebergLens:
    """Tests for Luneburg lens function."""
    
    def test_luneberg_modifies_eps(self):
        """Test that Luneburg lens modifies permittivity."""
        nx, ny = 20, 20
        eps = np.ones((nx, ny)) * const.epsilon_0
        mx, my = 10, 10
        R = 5
        
        eps_modified = common.luneberg(eps.copy(), mx, my, R)
        
        # Should have different values in lens region
        assert not np.array_equal(eps, eps_modified)
        # Center should be modified
        assert eps_modified[mx, my] != const.epsilon_0
