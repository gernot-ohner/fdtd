/**
 * TypeScript type definitions for FDTD simulation data.
 * 
 * These types match the JSON structure exported by export_simulation.py
 */

export interface FDTDSimulationData {
  /** Number of cells in x direction */
  nx: number;
  /** Number of cells in y direction */
  ny: number;
  /** Number of time steps */
  nt: number;
  /** Maximum absolute value in the dataset (for normalization) */
  maxValue: number;
  /** Spatial discretization in x direction (meters) */
  dx: number;
  /** Spatial discretization in y direction (meters) */
  dy: number;
  /** Time discretization (seconds) */
  dt: number;
  /** Source point coordinates [x, y] */
  sourcePoint: [number, number];
  /** PML type used: "no", "bpml", or "cpml" */
  pmlType: string;
  /** 3D array of field values: data[t][x][y] (time-major format for efficient frame access) */
  data: number[][][];
}

export interface FDTDVisualizerProps {
  /** Path to the JSON data file (relative to public folder) */
  dataPath: string;
  /** Initial animation speed multiplier (1.0 = normal speed) */
  initialSpeed?: number;
  /** Whether to auto-play on mount */
  autoPlay?: boolean;
  /** Canvas width in pixels (default: 600) */
  width?: number;
  /** Canvas height in pixels (default: 600) */
  height?: number;
  /** Color scheme name */
  colorScheme?: 'viridis' | 'plasma' | 'inferno' | 'magma' | 'hot' | 'cool';
}

