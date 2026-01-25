# Hysteresis Plotter

An interactive PyQt6 application for visualizing and exploring hysteresis loops, commonly used in materials science and engineering to represent stress-strain relationships.

## Overview

This tool provides real-time visualization of hysteresis loops using a hyperbolic tangent (tanh) model. It's designed for educational purposes, materials research, and understanding the behavior of materials under cyclic loading.

## Features

- **Interactive Controls**: Real-time adjustment of hysteresis loop parameters via sliders
- **Customizable Parameters**:
  - **Saturation (Ms)**: Maximum magnetization/strain (0.1-2.0)
  - **Coercivity (Hc)**: Field required to reduce magnetization to zero (10-100)
  - **Squareness (a)**: Controls the sharpness of the loop transitions (20-200)
  - **Young's Modulus (E)**: Material stiffness affecting loop slope (100-300 GPa)
- **Professional Visualization**: 
  - Centered axes with grid
  - Smooth curve rendering
  - Labeled stress (MPa) and strain (%) axes
- **Mathematical Model**: Uses tanh-based hysteresis model for realistic loop shapes

## Requirements

```bash
pip install PyQt6 numpy pyqtgraph
```

## Usage

Run the application:

```bash
python hysteresis_plotter.py
```

### Controls

Adjust the sliders to modify the hysteresis loop in real-time:

- **Saturation (M_s)**: Controls the maximum extent of the loop
- **Coercivity (H_c)**: Adjusts the width of the loop (energy dissipation)
- **Squareness (a)**: Changes how "square" or "rounded" the loop appears
- **Young's Modulus (E)**: Affects the slope of the loop ends

The plot updates instantly as you move any slider, allowing you to explore different material behaviors.

## Technical Details

### Hysteresis Model

The application uses a tanh-based model:

```
x = Ms * tanh((y ± Hc) / a) + k * y
```

Where:
- `Ms` = Saturation magnetization/strain
- `Hc` = Coercivity
- `a` = Squareness parameter
- `k` = Slope factor (derived from Young's Modulus)

### Stress-Strain Relationship

The slope `k` is calculated from Young's Modulus:
```
k = 100 / (E_GPa * 1000)
```

This relates strain (%) to stress (MPa) based on the material's elastic modulus.

## Applications

- **Materials Science**: Understanding magnetic hysteresis and mechanical behavior
- **Education**: Teaching concepts of energy dissipation and material properties
- **Engineering**: Exploring stress-strain relationships in cyclic loading
- **Research**: Visualizing and comparing different material behaviors

## Plot Details

- **X-axis**: Strain (%)
- **Y-axis**: Stress (MPa)
- **Range**: -300 to +600 MPa (tension/compression)
- **Loop Direction**: Ascending (compression → tension) then descending
