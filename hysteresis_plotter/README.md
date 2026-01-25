# Hysteresis Plotter

An interactive PyQt6 application for visualizing and exploring hysteresis loops, commonly used in materials science and engineering to represent stress-strain relationships.

## Overview

This tool provides real-time visualization of hysteresis loops using a hyperbolic tangent (tanh) model. It's designed for educational purposes, materials research, and understanding the behavior of materials under cyclic loading.

## Features

- **Interactive Controls**: Real-time adjustment of hysteresis loop parameters via sliders
- **Customizable Parameters**:
  - **Yield Strength (Ms)**: Maximum stress extent of the hysteresis loop (0.1-2.0)
  - **Plastic Slip (Hc)**: Permanent deformation/offset when stress returns to zero (10-100)
  - **Transition Sharpness (a)**: Controls how abruptly yielding occurs (20-200)
  - **Young's Modulus (E)**: Material stiffness affecting elastic slope (100-300 GPa)
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

- **Yield Strength (M_s)**: Controls the peak stress (vertical extent of the loop)
- **Plastic Slip (H_c)**: Adjusts the permanent deformation and energy dissipation
- **Transition Sharpness (a)**: Changes how abruptly yielding occurs (sharp vs. gradual)
- **Young's Modulus (E)**: Controls the elastic slope of the material

The plot updates instantly as you move any slider, allowing you to explore different material behaviors.

## Technical Details

### Hysteresis Model

The application uses a tanh-based model for stress-strain behavior:

```
strain = Ms * tanh((stress ± Hc) / a) + k * stress
```

Where:
- `Ms` = Yield strength (controls peak stress extent)
- `Hc` = Plastic slip (permanent deformation offset)
- `a` = Transition sharpness (yielding abruptness)
- `k` = Elastic compliance (inverse of Young's Modulus)

### Stress-Strain Relationship

The slope `k` is calculated from Young's Modulus:
```
k = 100 / (E_GPa * 1000)
```

This relates strain (%) to stress (MPa) based on the material's elastic modulus.

## Applications

- **Mechanical Engineering**: Exploring stress-strain relationships in cyclic loading (fatigue, plasticity)
- **Materials Science**: Understanding mechanical hysteresis, yielding, and energy dissipation
- **Education**: Teaching concepts of plastic deformation, elastic recovery, and material properties
- **Structural Analysis**: Visualizing material behavior under repeated loading cycles
- **Research**: Comparing different material behaviors and failure modes

> **Note**: While this tool uses a tanh model originally developed for magnetic hysteresis, the same mathematical form applies to mechanical stress-strain hysteresis loops in materials exhibiting plastic deformation.

## Plot Details

- **X-axis**: Strain (%)
- **Y-axis**: Stress (MPa)
- **Range**: -300 to +600 MPa (tension/compression)
- **Loop Direction**: Ascending (compression → tension) then descending
