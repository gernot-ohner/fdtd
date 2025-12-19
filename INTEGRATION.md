# FDTD Simulation Integration Guide for Next.js

This guide explains how to integrate the FDTD simulation visualization into your Next.js website.

## Files Created

1. **`export_simulation.py`** - Python script to export simulation data as JSON
2. **`components/FDTDVisualizer.tsx`** - React component for visualization
3. **`types/fdtd.ts`** - TypeScript type definitions

## Step 1: Export Simulation Data

Run the export script to generate JSON data:

```bash
cd /Users/gernotohner/dev/personal/fdtd
python export_simulation.py --pml cpml --nx 100 --ny 100 --nt 200 --output ../your-nextjs-project/public/data/fdtd-simulation.json
```

Or use default parameters:
```bash
python export_simulation.py --output ../your-nextjs-project/public/data/fdtd-simulation.json
```

**Note:** Adjust the output path to point to your Next.js project's `public` folder.

## Step 2: Copy Files to Next.js Project

Copy the following files to your Next.js project:

1. **Component**: Copy `components/FDTDVisualizer.tsx` to your Next.js `components/` folder
2. **Types**: Copy `types/fdtd.ts` to your Next.js `types/` folder (or adjust import paths)

## Step 3: Update Import Paths

If your Next.js project structure differs, update the import in `FDTDVisualizer.tsx`:

```typescript
// Change this line in FDTDVisualizer.tsx:
import { FDTDSimulationData, FDTDVisualizerProps } from '../types/fdtd';

// To match your project structure, e.g.:
import { FDTDSimulationData, FDTDVisualizerProps } from '@/types/fdtd';
```

## Step 4: Use the Component

Add the component to any Next.js page:

```typescript
// app/simulation/page.tsx (App Router) or pages/simulation.tsx (Pages Router)
import FDTDVisualizer from '@/components/FDTDVisualizer';

export default function SimulationPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">FDTD Simulation</h1>
      <FDTDVisualizer 
        dataPath="/data/fdtd-simulation.json"
        initialSpeed={1.0}
        autoPlay={true}
        width={800}
        height={800}
        colorScheme="viridis"
      />
    </div>
  );
}
```

## Component Props

- `dataPath` (required): Path to JSON file relative to `public/` folder
- `initialSpeed` (optional): Animation speed multiplier (default: 1.0)
- `autoPlay` (optional): Auto-start animation (default: true)
- `width` (optional): Canvas width in pixels (default: 600)
- `height` (optional): Canvas height in pixels (default: 600)
- `colorScheme` (optional): Colormap name - 'viridis', 'plasma', 'inferno', 'magma', 'hot', 'cool' (default: 'viridis')

## Features

- **Animated visualization**: Smooth animation of electromagnetic wave propagation
- **Play/Pause controls**: Start and stop animation
- **Frame navigation**: Step through frames manually
- **Speed control**: Adjust animation speed (0.1x to 3x)
- **Multiple colormaps**: Choose from 6 different color schemes
- **Responsive**: Canvas scales to container width

## Performance Considerations

- **File size**: Large simulations (e.g., 200x200x500) can produce 50-100MB JSON files
- **Recommendations**:
  - Use smaller grid sizes for web (100x100 or 150x150)
  - Reduce time steps if file size is an issue
  - Vercel automatically compresses static assets (gzip)
  - Consider downsampling for display if needed

## Example: Multiple Simulations

You can export multiple simulations with different parameters:

```bash
# Small, fast simulation
python export_simulation.py --nx 80 --ny 80 --nt 150 --output ../project/public/data/fdtd-small.json

# Larger, more detailed simulation
python export_simulation.py --nx 150 --ny 150 --nt 300 --output ../project/public/data/fdtd-large.json
```

Then use different components for each:

```typescript
<FDTDVisualizer dataPath="/data/fdtd-small.json" width={400} height={400} />
<FDTDVisualizer dataPath="/data/fdtd-large.json" width={800} height={800} />
```

## Troubleshooting

**Issue**: Component shows "Loading..." indefinitely
- **Solution**: Check that the JSON file exists in `public/data/` and the path is correct

**Issue**: Animation is choppy
- **Solution**: Reduce grid size or time steps, or lower animation speed

**Issue**: File too large
- **Solution**: Use smaller simulation parameters or compress the JSON file

**Issue**: TypeScript errors
- **Solution**: Ensure `types/fdtd.ts` is in the correct location and import paths match your project structure

## Next Steps

- Customize colormaps to match your site's theme
- Add more interactive controls (zoom, pan, etc.)
- Implement WebGL rendering for larger grids
- Add export functionality for individual frames

