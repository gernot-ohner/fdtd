'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { FDTDSimulationData, FDTDVisualizerProps } from '../types/fdtd';

/**
 * Color mapping functions for different colormaps
 * These approximate matplotlib colormaps
 */
const colormaps: Record<string, (value: number) => string> = {
  viridis: (t: number) => {
    // Approximate viridis colormap
    const r = Math.floor(68 + (253 - 68) * t);
    const g = Math.floor(1 + (231 - 1) * t);
    const b = Math.floor(84 + (37 - 84) * t);
    return `rgb(${r},${g},${b})`;
  },
  plasma: (t: number) => {
    // Approximate plasma colormap
    const r = Math.floor(13 + (240 - 13) * t);
    const g = Math.floor(8 + (249 - 8) * t);
    const b = Math.floor(135 + (33 - 135) * t);
    return `rgb(${r},${g},${b})`;
  },
  inferno: (t: number) => {
    // Approximate inferno colormap
    const r = Math.floor(0 + (252 - 0) * t);
    const g = Math.floor(0 + (141 - 0) * t);
    const b = Math.floor(4 + (89 - 4) * t);
    return `rgb(${r},${g},${b})`;
  },
  magma: (t: number) => {
    // Approximate magma colormap
    const r = Math.floor(0 + (252 - 0) * t);
    const g = Math.floor(0 + (253 - 0) * t);
    const b = Math.floor(4 + (191 - 4) * t);
    return `rgb(${r},${g},${b})`;
  },
  hot: (t: number) => {
    // Hot colormap (black -> red -> yellow -> white)
    if (t < 0.33) {
      const s = t / 0.33;
      return `rgb(${Math.floor(255 * s)},0,0)`;
    } else if (t < 0.66) {
      const s = (t - 0.33) / 0.33;
      return `rgb(255,${Math.floor(255 * s)},0)`;
    } else {
      const s = (t - 0.66) / 0.34;
      return `rgb(255,255,${Math.floor(255 * s)})`;
    }
  },
  cool: (t: number) => {
    // Cool colormap (cyan -> magenta)
    const r = Math.floor(255 * t);
    const g = Math.floor(255 * (1 - t));
    const b = 255;
    return `rgb(${r},${g},${b})`;
  },
};

/**
 * FDTD Visualization Component
 * 
 * Displays an animated 2D heatmap of FDTD simulation results using HTML5 Canvas.
 * Similar to matplotlib's animated imshow visualization.
 */
export default function FDTDVisualizer({
  dataPath,
  initialSpeed = 1.0,
  autoPlay = true,
  width = 600,
  height = 600,
  colorScheme = 'viridis',
}: FDTDVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [data, setData] = useState<FDTDSimulationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [lastFrameTime, setLastFrameTime] = useState(0);
  const [speed, setSpeed] = useState(initialSpeed);

  // Load simulation data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(dataPath);
        if (!response.ok) {
          throw new Error(`Failed to load simulation data: ${response.statusText}`);
        }
        const jsonData: FDTDSimulationData = await response.json();
        setData(jsonData);
        setCurrentFrame(0);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load simulation data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [dataPath]);

  // Render a single frame to canvas
  const renderFrame = useCallback(
    (frameIndex: number) => {
      if (!data || !canvasRef.current) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const { nx, ny, maxValue, data: fieldData } = data;
      const frame = fieldData[frameIndex];
      if (!frame) return;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Calculate cell size
      const cellWidth = width / nx;
      const cellHeight = height / ny;

      // Get colormap function
      const colorMap = colormaps[colorScheme] || colormaps.viridis;

      // Draw each cell
      for (let x = 0; x < nx; x++) {
        for (let y = 0; y < ny; y++) {
          const value = frame[x][y];
          // Normalize value to [0, 1]
          const normalized = Math.min(1.0, Math.max(0.0, value / maxValue));
          const color = colorMap(normalized);

          ctx.fillStyle = color;
          ctx.fillRect(y * cellWidth, x * cellHeight, cellWidth, cellHeight);
        }
      }
    },
    [data, width, height, colorScheme]
  );

  // Animation loop
  useEffect(() => {
    if (!data || !isPlaying) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    const animate = (timestamp: number) => {
      // Control animation speed
      const frameInterval = 50 / speed; // 50ms base interval divided by speed
      if (timestamp - lastFrameTime >= frameInterval) {
        setCurrentFrame((prev) => {
          const next = (prev + 1) % data.nt;
          renderFrame(next);
          return next;
        });
        setLastFrameTime(timestamp);
      }
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [data, isPlaying, speed, lastFrameTime, renderFrame]);

  // Render initial frame when data loads
  useEffect(() => {
    if (data && !isPlaying) {
      renderFrame(currentFrame);
    }
  }, [data, currentFrame, isPlaying, renderFrame]);

  // Handle play/pause
  const togglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  // Handle frame navigation
  const goToFrame = (frame: number) => {
    if (!data) return;
    const clamped = Math.max(0, Math.min(data.nt - 1, frame));
    setCurrentFrame(clamped);
    renderFrame(clamped);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div>Loading simulation data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center text-red-500" style={{ width, height }}>
        <div>Error: {error}</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="fdtd-visualizer">
      <div className="canvas-container" style={{ marginBottom: '1rem' }}>
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          style={{
            border: '1px solid #ccc',
            display: 'block',
            maxWidth: '100%',
            height: 'auto',
          }}
        />
      </div>
      <div className="controls" style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          onClick={togglePlay}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1rem',
            cursor: 'pointer',
            backgroundColor: isPlaying ? '#ef4444' : '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
          }}
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={() => goToFrame(currentFrame - 1)}
            disabled={currentFrame === 0}
            style={{
              padding: '0.25rem 0.5rem',
              cursor: currentFrame === 0 ? 'not-allowed' : 'pointer',
              opacity: currentFrame === 0 ? 0.5 : 1,
            }}
          >
            ←
          </button>
          <span>
            Frame {currentFrame + 1} / {data.nt}
          </span>
          <button
            onClick={() => goToFrame(currentFrame + 1)}
            disabled={currentFrame === data.nt - 1}
            style={{
              padding: '0.25rem 0.5rem',
              cursor: currentFrame === data.nt - 1 ? 'not-allowed' : 'pointer',
              opacity: currentFrame === data.nt - 1 ? 0.5 : 1,
            }}
          >
            →
          </button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label htmlFor="speed-control">Speed:</label>
          <input
            id="speed-control"
            type="range"
            min="0.1"
            max="3"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            style={{ width: '100px' }}
          />
          <span>{speed.toFixed(1)}x</span>
        </div>
        <div style={{ fontSize: '0.875rem', color: '#666' }}>
          Grid: {data.nx}×{data.ny} | PML: {data.pmlType}
        </div>
      </div>
    </div>
  );
}

