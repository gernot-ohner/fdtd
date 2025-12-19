"""Integration tests for caller functions."""
import numpy as np
import pytest

import callers
import sources


class TestCallNoPML:
    """Tests for call_npml function."""
    
    def test_call_npml_returns_history(self):
        """Test that call_npml returns correct history shape."""
        nx, ny, nt = 20, 20, 10
        dx, dy = 0.05, 0.05
        dt = 1e-10
        p = (10, 10)
        source = sources.simple_sin_source
        
        history = callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
        
        assert history.shape == (nx, ny, nt)
        assert isinstance(history, np.ndarray)
    
    def test_call_npml_with_null_source(self):
        """Test call_npml with null source."""
        nx, ny, nt = 20, 20, 5
        dx, dy = 0.05, 0.05
        dt = 1e-10
        p = (10, 10)
        source = sources.null_source
        
        history = callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
        
        # Should still run without error
        assert history.shape == (nx, ny, nt)


class TestCallBPML:
    """Tests for call_bpml function."""
    
    def test_call_bpml_returns_history(self):
        """Test that call_bpml returns correct history shape."""
        # Use larger grid to avoid environment_problem_example index errors
        nx, ny, nt = 100, 100, 10
        dx, dy = 0.05, 0.05
        dt = 1e-10
        p = (50, 50)
        pmlc = (5, 1e-6, 3)
        source = sources.simple_sin_source
        
        history = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
        
        assert history.shape == (nx, ny, nt)
        assert isinstance(history, np.ndarray)
    
    def test_call_bpml_with_conductivity(self):
        """Test call_bpml with additional conductivity."""
        # Use larger grid to avoid environment_problem_example index errors
        nx, ny, nt = 100, 100, 5
        dx, dy = 0.05, 0.05
        dt = 1e-10
        p = (50, 50)
        pmlc = (5, 1e-6, 3)
        source = sources.simple_sin_source
        s = 0.01
        
        history = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source, s)
        
        assert history.shape == (nx, ny, nt)


class TestCallCPML:
    """Tests for call_cpml function."""
    
    def test_call_cpml_returns_history(self):
        """Test that call_cpml returns correct history shape."""
        # Use larger grid to avoid environment_problem_example index errors
        nx, ny, nt = 100, 100, 10
        dx, dy = 0.05, 0.05
        dt = 1e-10
        p = (50, 50)
        pmlc = (5, 1e-6, 3)
        source = sources.simple_sin_source
        
        history = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
        
        assert history.shape == (nx, ny, nt)
        assert isinstance(history, np.ndarray)


class TestCallCommon:
    """Tests for call_common function."""
    
    def test_call_common_returns_all_fields(self):
        """Test that call_common returns all required fields."""
        nx, ny, nt = 20, 20, 10
        dx, dy = 0.05, 0.05
        pmlc = (5, 1e-6, 3)
        
        fields, eps, mu, sigmas, history = callers.call_common(nx, ny, nt, dx, dy, pmlc)
        
        # Check fields
        assert len(fields) == 3
        ex, ey, hz = fields
        assert ex.shape == (nx, ny + 1)
        assert ey.shape == (nx + 1, ny)
        assert hz.shape == (nx, ny)
        
        # Check environment
        assert eps.shape == (nx, ny)
        assert mu.shape == (nx, ny)
        
        # Check sigmas
        assert len(sigmas) == 4
        
        # Check history
        assert history.shape == (nx, ny, nt)
    
    def test_call_common_pml_applied(self):
        """Test that PML is applied in call_common."""
        nx, ny, nt = 20, 20, 10
        dx, dy = 0.05, 0.05
        pmlc = (5, 1e-6, 3)
        
        fields, eps, mu, sigmas, history = callers.call_common(nx, ny, nt, dx, dy, pmlc)
        
        # PML regions should have non-zero conductivity
        assert np.any(sigmas[0] != 0)  # Should have PML values
        assert np.any(sigmas[1] != 0)
        assert np.any(sigmas[2] != 0)
        assert np.any(sigmas[3] != 0)
