"""Tests for source functions."""
import numpy as np
import pytest

import sources


class TestSimpleSinSource:
    """Tests for simple_sin_source function."""
    
    def test_returns_float(self):
        """Source should return a float value."""
        result = sources.simple_sin_source(0)
        assert isinstance(result, (float, np.floating))
    
    def test_sinusoidal_behavior(self):
        """Source should produce sinusoidal values."""
        t0 = sources.simple_sin_source(0)
        t5 = sources.simple_sin_source(5)
        t10 = sources.simple_sin_source(10)
        
        # Should be approximately sin(0), sin(1), sin(2)
        assert abs(t0 - np.sin(0)) < 1e-10
        assert abs(t5 - np.sin(1)) < 1e-10
        assert abs(t10 - np.sin(2)) < 1e-10
    
    def test_continuous(self):
        """Source should be continuous."""
        t1 = sources.simple_sin_source(1)
        t2 = sources.simple_sin_source(2)
        # Values should change smoothly
        assert abs(t2 - t1) < 1.0  # Reasonable bound for sin


class TestNullSource:
    """Tests for null_source function."""
    
    def test_returns_zero(self):
        """Null source should always return 0."""
        for t in [0, 1, 10, 100, 1000]:
            result = sources.null_source(t)
            assert result == 0.0
    
    def test_returns_float(self):
        """Null source should return a float."""
        result = sources.null_source(0)
        assert isinstance(result, (float, np.floating))
