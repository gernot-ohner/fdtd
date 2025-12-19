# FDTD Simulation

A Python implementation of Finite Difference Time Domain (FDTD) electromagnetic wave simulation.

> The finite difference time domain method, in short FDTD, is used to numerically compute
> the propagation of electromagnetic waves, that is, to solve the Maxwell equations for arbitrary
> environments.

![FDTD simulation with various features of low/high permittivity](https://gernot-ohner.github.io/resources/fdtd1.png)

This is a sample image of a FDTD simulation in 2 dimensions.
Features of note:   
- a pulsing point source at `(50, 50)` 
- a [Luneburg lens](https://en.wikipedia.org/wiki/Luneburg_lens) with a focal point around `(20, 90)`
- a "bar" of low (high?) permittivity from `(25, 40)` to `(40, 25)`
- an area of perfect conductivity in the bottom right corner
- an absorbing boundary (otherwise, the limits of the simulation act like perfect reflectors, c.f. the following image)  

![Comparison of 1d simulations with and without absorbing boundary conditions, taken from Ohner 2018](https://gernot-ohner.github.io/resources/abc_explanation_1d.png)

## Features

- **Multiple PML implementations**: Berenger PML (BPML), Convolutional PML (CPML), and no PML
- **Flexible configuration**: Command-line interface with customizable parameters
- **Visualization**: Animated 2D plots and comparison plots
- **Performance benchmarking**: Built-in timing and comparison tools
- **Type hints**: Modern Python with full type annotations

## Installation

### Prerequisites

- Python 3.7 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` (>=1.20.0)
- `scipy` (>=1.7.0)
- `matplotlib` (>=3.4.0)
- `pytest` (>=7.0.0) - for running unit tests
- `pytest-cov` (>=4.0.0) - for test coverage

## Usage

### Command-Line Interface

The simulation can be run from the command line with various options:

```bash
cd src
python main.py <action> [options]
```

### Basic Examples

**Run a normal simulation with BPML:**
```bash
python main.py normal --pml bpml
```

**Run with custom grid size:**
```bash
python main.py normal --pml cpml --nx 150 --ny 150 --nt 300
```

**Compare BPML and CPML:**
```bash
python main.py comparison
```

**Run performance benchmark:**
```bash
python main.py time --repetitions 50
```

**Test PML effectiveness:**
```bash
python main.py pml --pml cpml
```

**Test lossy materials:**
```bash
python main.py loss
```

### Available Actions

- `normal` - Run a standard simulation with visualization
- `pml` - Compare small vs large simulation with PML
- `loss` - Test effect of different conductivity values
- `comparison` - Compare BPML vs CPML implementations
- `time` - Benchmark performance of different PML types
- `trivial` - Benchmark source function overhead
- `all` - Run all tests sequentially

### Command-Line Options

**PML Options:**
- `--pml {no,bpml,cpml}` - PML implementation type (default: bpml)

**Simulation Parameters:**
- `--nx INT` - Number of cells in x direction (default: 100)
- `--ny INT` - Number of cells in y direction (default: 100)
- `--dx FLOAT` - Spatial discretization in x (meters, default: 0.05)
- `--dy FLOAT` - Spatial discretization in y (meters, default: 0.05)
- `--nt INT` - Number of time steps (default: 200)
- `--source-x INT` - Source x position (default: center)
- `--source-y INT` - Source y position (default: center)

**PML Configuration:**
- `--pml-thickness INT` - PML thickness in cells (default: 10)
- `--pml-r0 FLOAT` - PML reflection factor R0 (default: 1e-6)
- `--pml-grading INT` - PML grading parameter (default: 3)

**Test Parameters:**
- `--repetitions INT` - Number of repetitions for timing tests (default: 100)

### Help

For detailed help and examples:
```bash
python main.py --help
python main.py <action> --help
```

## Project Structure

```
src/
├── main.py          # CLI entry point
├── config.py        # Configuration dataclasses and enums
├── sources.py       # Source function definitions
├── common.py        # Common utilities (fields, plotting, environment)
├── callers.py       # Wrapper functions for PML implementations
├── tests.py         # Test and comparison functions
├── no_pml.py        # FDTD without PML
├── bpml.py          # Berenger PML implementation
└── cpml.py          # Convolutional PML implementation
```

## Testing

The project includes a comprehensive unit test suite using pytest.

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_common.py
```

**Run specific test:**
```bash
pytest tests/test_common.py::TestFieldCreation::test_make_fields
```

**Run with coverage report:**
```bash
pytest --cov=src --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Test Structure

The test suite includes:

- **Unit tests** for core functions:
  - `test_sources.py` - Source function tests
  - `test_config.py` - Configuration dataclass tests
  - `test_common.py` - Common utility function tests
  - `test_no_pml.py` - No-PML implementation tests
  - `test_bpml.py` - Berenger PML tests
  - `test_cpml.py` - Convolutional PML tests
  
- **Integration tests**:
  - `test_callers.py` - Integration tests for caller functions

All tests are designed to run quickly and verify correctness of the core FDTD algorithms.

## Code Quality

This project has been modernized with:
- Full type hints throughout
- Proper error handling
- Command-line interface
- Clean separation of concerns
- Comprehensive documentation
- Modern Python best practices
- Comprehensive unit test suite

## License

This code was written for a bachelor thesis in physics. Please respect the original author's work.
