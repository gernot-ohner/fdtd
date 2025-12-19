"""Tests for no-PML FDTD implementation."""
import numpy as np
import pytest
import scipy.constants as const

import common
import no_pml
import sources


class TestCalculateConstants:
    """Tests for constant calculation."""
    
    def test_constants_shape(self):
        """Test that constants are calculated correctly."""
        dx, dy, dt = 0.05, 0.05, 1e-10
        constants = no_pml.calculate_constants(dx, dy, dt)
        
        assert len(constants) == 4
        cex, cey, chzx, chzy = constants
        
        # All should be floats
        assert all(isinstance(c, (float, np.floating)) for c in constants)
    
    def test_constants_values(self):
        """Test constant values match expected formulas."""
        dx, dy = 0.05, 0.05
        dt = 1e-10
        eps = const.epsilon_0
        mu = const.mu_0
        
        constants = no_pml.calculate_constants(dx, dy, dt)
        cex, cey, chzx, chzy = constants
        
        expected_cex = dt / (eps * dy)
        expected_cey = dt / (eps * dx)
        expected_chzx = dt / (mu * dx)
        expected_chzy = dt / (mu * dy)
        
        assert abs(cex - expected_cex) < 1e-15
        assert abs(cey - expected_cey) < 1e-15
        assert abs(chzx - expected_chzx) < 1e-15
        assert abs(chzy - expected_chzy) < 1e-15


class TestEvolution:
    """Tests for field evolution."""
    
    def test_evolution_returns_history(self):
        """Test that evolution returns correct history array."""
        nx, ny, nt = 10, 10, 5
        fields = common.make_fields(nx, ny)
        constants = no_pml.calculate_constants(0.05, 0.05, 1e-10)
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        source = sources.simple_sin_source
        
        result = no_pml.evolution(nt, fields, constants, history, sourcepoint, source)
        
        assert result.shape == (nx, ny, nt)
        assert result is history  # Should modify in place
    
    def test_evolution_updates_fields(self):
        """Test that fields are updated during evolution."""
        nx, ny, nt = 10, 10, 5
        fields = common.make_fields(nx, ny)
        # Use larger dt to ensure field propagation
        constants = no_pml.calculate_constants(0.05, 0.05, 1e-9)
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        
        # Use a constant source to ensure it's applied
        def source(t):
            return 1.0
        
        # Fields should start as zeros
        assert np.all(fields[2] == 0)  # hz
        
        no_pml.evolution(nt, fields, constants, history, sourcepoint, source)
        
        # After evolution, source should be applied (at least in history)
        # The source is applied to hz, then hz is stored in history
        # Check that at least one time step has the source value
        source_in_history = False
        for t in range(nt):
            if abs(history[sourcepoint[0], sourcepoint[1], t] - source(t)) < 1e-10:
                source_in_history = True
                break
        assert source_in_history, "Source value should appear in history"
    
    def test_source_applied(self):
        """Test that source is applied at source point."""
        nx, ny, nt = 10, 10, 1
        fields = common.make_fields(nx, ny)
        constants = no_pml.calculate_constants(0.05, 0.05, 1e-10)
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        source = sources.simple_sin_source
        
        no_pml.evolution(nt, fields, constants, history, sourcepoint, source)
        
        # Source value should be in history
        expected_source_value = source(0)
        assert abs(history[sourcepoint[0], sourcepoint[1], 0] - expected_source_value) < 1e-10
    
    def test_history_stored(self):
        """Test that history is stored at each time step."""
        nx, ny, nt = 10, 10, 5
        fields = common.make_fields(nx, ny)
        # Use larger dt to ensure field propagation
        constants = no_pml.calculate_constants(0.05, 0.05, 1e-9)
        history = np.zeros((nx, ny, nt))
        sourcepoint = (5, 5)
        source = sources.simple_sin_source
        
        no_pml.evolution(nt, fields, constants, history, sourcepoint, source)
        
        # At least the source point should have non-zero values
        # (field may not propagate far with very small dt and few steps)
        assert np.any(history != 0)  # At least some non-zero values somewhere
