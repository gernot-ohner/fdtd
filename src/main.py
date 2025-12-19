#!/usr/bin/env python3
"""Main entry point for FDTD simulation with command-line interface."""
import argparse
import sys
from typing import Callable

import matplotlib.pyplot as plt

import config
import sources
import tests

plt.rc('font', family='serif', size=14)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='FDTD (Finite Difference Time Domain) electromagnetic wave simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run normal simulation with BPML
  python main.py normal --pml bpml
  
  # Run with custom grid size
  python main.py normal --pml cpml --nx 150 --ny 150
  
  # Run comparison test
  python main.py comparison
  
  # Run performance benchmark
  python main.py time --repetitions 50
        """
    )
    
    parser.add_argument(
        'action',
        choices=['normal', 'pml', 'loss', 'comparison', 'time', 'trivial', 'all'],
        help='Type of simulation/test to run'
    )
    
    parser.add_argument(
        '--pml',
        choices=['no', 'bpml', 'cpml'],
        default='bpml',
        help='PML implementation type (default: bpml)'
    )
    
    # Simulation parameters
    parser.add_argument('--nx', type=int, default=100, help='Number of cells in x direction (default: 100)')
    parser.add_argument('--ny', type=int, default=100, help='Number of cells in y direction (default: 100)')
    parser.add_argument('--dx', type=float, default=0.05, help='Spatial discretization in x (meters, default: 0.05)')
    parser.add_argument('--dy', type=float, default=0.05, help='Spatial discretization in y (meters, default: 0.05)')
    parser.add_argument('--nt', type=int, default=200, help='Number of time steps (default: 200)')
    
    # Source parameters
    parser.add_argument('--source-x', type=int, help='Source x position (default: center)')
    parser.add_argument('--source-y', type=int, help='Source y position (default: center)')
    
    # PML parameters
    parser.add_argument('--pml-thickness', type=int, default=10, help='PML thickness in cells (default: 10)')
    parser.add_argument('--pml-r0', type=float, default=1e-6, help='PML reflection factor R0 (default: 1e-6)')
    parser.add_argument('--pml-grading', type=int, default=3, help='PML grading parameter (default: 3)')
    
    # Test parameters
    parser.add_argument('--repetitions', type=int, default=100, help='Number of repetitions for timing tests (default: 100)')
    
    return parser


def get_source_function() -> Callable[[int], float]:
    """Get source function (currently only simple_sin_source available)."""
    return sources.simple_sin_source


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create simulation parameters
    sim_params = config.SimulationParameters(
        nx=args.nx,
        ny=args.ny,
        dx=args.dx,
        dy=args.dy,
        nt=args.nt,
        source_point=(args.source_x, args.source_y) if args.source_x and args.source_y else None,
        pml_config=(args.pml_thickness, args.pml_r0, args.pml_grading)
    )
    
    # Get source function
    source = get_source_function()
    
    # Convert to list format for backward compatibility with tests
    params = sim_params.to_list()
    params[-1] = source  # Replace None with actual source function
    
    # Run requested action
    try:
        if args.action == "normal":
            tests.normal_test(params, args.pml)
        elif args.action == "pml":
            tests.pml_test(params, args.pml)
        elif args.action == "loss":
            tests.loss_test(params)
        elif args.action == "comparison":
            tests.comparison_test(params)
        elif args.action == "time":
            tests.time_test(params, rep=args.repetitions, num=1)
        elif args.action == "trivial":
            tests.time_trivial(params, rep=args.repetitions, num=1)
        elif args.action == "all":
            print("Running all tests...")
            tests.normal_test(params, "cpml")
            tests.normal_test(params, "bpml")
            tests.normal_test(params, "no")
            tests.pml_test(params, "cpml")
            tests.pml_test(params, "bpml")
            tests.loss_test(params)
            tests.comparison_test(params)
            tests.time_test(params, 1)
            tests.time_trivial(params, 1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
