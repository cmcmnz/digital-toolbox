# Mechagodzilla Scaler

A Python/Tkinter tool for visualizing and scaling the Mechagodzilla 3D model (Ready Player One version).

## Features
- **Dual View**: Front and Side profiles of the OBJ model.
- **Skeleton Overlay**: Draggable joint points to visualize measuring points.
- **Scaling Calculator**: Adjust total height to see resulting dimensions and limb lengths in cm and studs.
- **Persistence**: Remembers joint positions relative to the model (stored in `skeleton_config.json` next to the model file).

## Requirements
- **Python 3.x**
- **Tkinter** (Usually included with Python)

## Usage
1.  Place your `.obj` model file in the **same folder** as `mech_scaler.py`.
2.  Run the script providing the filename:

```powershell
python mech_scaler.py model.obj
```

If no file is specified, the script will print usage instructions and exit.

**Note**: The script will generate/read a `skeleton_config.json` file in the same directory to save your joint positions.
