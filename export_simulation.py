#!/usr/bin/env python3
"""Export FDTD simulation results to JSON for web visualization."""
import json
import argparse
import sys
from pathlib import Path

import numpy as np

import config
import sources
import callers


def export_simulation(
    sim_params: config.SimulationParameters,
    pml_type: str = "cpml",
    output_path: str = "fdtd-simulation.json"
) -> None:
    """
    Run FDTD simulation and export results to JSON.
    
    Args:
        sim_params: Simulation parameters
        pml_type: PML type ("no", "bpml", or "cpml")
        output_path: Path to output JSON file
    """
    print(f"Running FDTD simulation with {pml_type}...")
    print(f"Grid size: {sim_params.nx}x{sim_params.ny}, Time steps: {sim_params.nt}")
    
    # Get source function
    source = sources.simple_sin_source
    
    # Convert to list format for callers
    params = sim_params.to_list()
    params[-1] = source
    
    # Run simulation
    nx, ny, lx, ly, dx, dy, dt, nt, p, pmlc, _ = params
    
    try:
        if pml_type == "no":
            history = callers.call_npml(nx, ny, nt, dx, dy, dt, p, source)
        elif pml_type == "bpml":
            history = callers.call_bpml(nx, ny, nt, dx, dy, dt, p, pmlc, source, 0)
        elif pml_type == "cpml":
            history = callers.call_cpml(nx, ny, nt, dx, dy, dt, p, pmlc, source)
        else:
            raise ValueError(f"Invalid PML type: {pml_type}. Must be 'no', 'bpml', or 'cpml'")
    except Exception as e:
        print(f"Error running simulation: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate max value for normalization (using absolute values like matplotlib)
    maxval = float(np.max(np.abs(history)))
    print(f"Max absolute value: {maxval}")
    
    # Convert to list format (numpy arrays are not JSON serializable)
    # Transpose to time-major format: (nx, ny, nt) -> (nt, nx, ny)
    # This makes it easier to access frames: data[frameIndex] gives all x,y for that time
    print("Converting to JSON-serializable format...")
    history_abs = np.abs(history)  # Use absolute values like plot_2d does
    # Transpose: (nx, ny, nt) -> (nt, nx, ny)
    history_transposed = np.transpose(history_abs, (2, 0, 1))
    data = history_transposed.tolist()
    
    # Create export structure
    export_data = {
        "nx": int(nx),
        "ny": int(ny),
        "nt": int(nt),
        "maxValue": maxval,
        "dx": float(dx),
        "dy": float(dy),
        "dt": float(dt),
        "sourcePoint": [int(p[0]), int(p[1])],
        "pmlType": pml_type,
        "data": data
    }
    
    # Write to JSON file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(export_data, f)
    
    # Calculate file size
    file_size = output_file.stat().st_size
    print(f"Export complete! File size: {file_size / 1024 / 1024:.2f} MB")


def main():
    """Main entry point for export script."""
    parser = argparse.ArgumentParser(
        description='Export FDTD simulation results to JSON for web visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--pml',
        choices=['no', 'bpml', 'cpml'],
        default='cpml',
        help='PML implementation type (default: cpml)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='fdtd-simulation.json',
        help='Output JSON file path (default: fdtd-simulation.json)'
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
    
    args = parser.parse_args()
    
    # Create simulation parameters
    source_point = None
    if args.source_x is not None and args.source_y is not None:
        source_point = (args.source_x, args.source_y)
    
    sim_params = config.SimulationParameters(
        nx=args.nx,
        ny=args.ny,
        dx=args.dx,
        dy=args.dy,
        nt=args.nt,
        source_point=source_point,
        pml_config=(args.pml_thickness, args.pml_r0, args.pml_grading)
    )
    
    # Export simulation
    export_simulation(sim_params, args.pml, args.output)


if __name__ == "__main__":
    main()

