# Mechagodzilla Scaler

A Python/Tkinter tool for visualizing and scaling the Mechagodzilla 3D model (Ready Player One version).

## Features
- **Dual View**: Front and Side profiles of the OBJ model.
- **Skeleton Overlay**: Draggable joint points to visualize measuring points.
- **Scaling Calculator**: Adjust total height to see resulting dimensions and limb lengths in cm and studs.
- **Persistence**: Remembers joint positions relative to the model (stored in `skeleton_config.json` next to the model file).

## Usage
Run the script with the path to your OBJ file:

```powershell
python mech_scaler.py "path/to/model.obj"
```

If no argument is provided, it defaults to the project path in `d:\VaultZero\Systems\000 Works In Progress\Mechagodzilla\...`.
