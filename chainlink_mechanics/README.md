# Chainlink Mechanics

A PyQt6 application for visualizing and analyzing the geometry of chain links arranged in a circular pattern.

## Overview

This tool allows you to interactively design and visualize a chain of links forming a circle. It's particularly useful for mechanical design projects involving chain assemblies, where you need to determine the precise geometry based on constraints like inner diameter, number of links, and individual link lengths.

## Features

- **Interactive Visualization**: Real-time 2D visualization of chain link geometry
- **Customizable Parameters**:
  - Total number of links in the chain
  - Inner diameter of the circle
  - Green link length (special/adjustable link)
  - Red link length (master link)
- **Bidirectional Calculation**: 
  - Adjust inner diameter → calculates required green link length
  - Adjust green link length → calculates required inner diameter
- **Visual Feedback**: Color-coded links (standard/blue, green, red) with connecting lines
- **Automatic Geometry Solving**: Uses numerical methods to solve the circular chain geometry

## Requirements

```bash
pip install PyQt6 numpy pyqtgraph
```

## Usage

Run the application:

```bash
python chainlink_mechanics.py
```

### Controls

- **Total Number of Links**: Enter the total number of links in the chain (default: 22)
- **Inner Diameter Slider**: Adjust the inner diameter (30-200 mm)
- **Green Link Length Slider**: Adjust the special link length (3-20 mm)
- **Red Link Length**: Enter the master link length (default: 6.35 mm)

The application automatically calculates and displays:
- Inner circumference
- Optimal link dimensions for a closed circular chain
- Visual representation of the chain geometry

## Technical Details

The application uses:
- **Chord-to-angle conversion**: Calculates the angular span of each link based on its length
- **Binary search**: Solves for the chain radius when adjusting the green link length
- **PyQtGraph**: Provides high-performance interactive plotting
- **Real-time updates**: All changes are reflected immediately in the visualization

## Use Cases

- Designing custom chain assemblies
- Calculating required link dimensions for circular chain drives
- Educational tool for understanding chain geometry
- Prototyping mechanical linkage systems
