
import tkinter as tk
from tkinter import ttk, Canvas
import sys
import os
import math
import json

class MechScalerApp:
    def __init__(self, root, obj_path):
        self.root = root
        self.root.title("Mechagodzilla Scaler v2.0 - 3D Dual View")
        self.root.geometry("1400x800")
        
        self.obj_path = obj_path
        self.vertices = []
        self.model_dims = (0, 0, 0) # w, h, d
        self.model_bounds = (0, 0, 0, 0, 0, 0) # min_x, max_x, etc
        
        # Scale Settings
        self.target_height_cm = tk.DoubleVar(value=60.0)
        self.mesh_visibility = tk.IntVar(value=50) # 0-100
        self.pixels_per_mm = 0.5
        self.dragged_joint = None
        
        self.load_data()
        
        # Skeleton Definitions: (x_ratio, y_ratio, z_ratio)
        # Ratios 0.0-1.0 relative to bounding box
        self.skeleton_ratios = {
            "Hip": (0.45, 0.45, 0.5),
            "Knee": (0.55, 0.25, 0.5),
            "Ankle": (0.45, 0.05, 0.5),
            "Shoulder": (0.60, 0.70, 0.5),
            "Elbow": (0.65, 0.55, 0.5),
            "Wrist": (0.75, 0.50, 0.5),
            "Head": (0.85, 0.85, 0.5),
            "NeckBase": (0.65, 0.75, 0.5),
            "TailBase": (0.35, 0.45, 0.5),
            "TailMid": (0.20, 0.30, 0.5),
            "TailTip": (0.05, 0.10, 0.5)
        }
        
        self.load_config() 
        
        self.bones = [
            ("Femur", "Hip", "Knee"),
            ("Tibia", "Knee", "Ankle"),
            ("Spine", "Hip", "Shoulder"),
            ("Neck", "Shoulder", "Head"),
            ("Humerus", "Shoulder", "Elbow"),
            ("Radius", "Elbow", "Wrist"),
            ("Tail Upper", "Hip", "TailMid"),
            ("Tail Lower", "TailMid", "TailTip")
        ]
        
        self.current_joints = {} # Stores real-world Model Unit coords (x,y,z)
        
        self.setup_ui()
        self.update_calculations()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Sidebar (Controls) ---
        control_panel = ttk.Frame(main_frame, padding=10, width=250)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(control_panel, text="Target Height (cm)", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Scale(control_panel, from_=10, to=200, variable=self.target_height_cm, command=self.on_slider_change).pack(fill=tk.X, pady=5)
        
        ttk.Label(control_panel, text="Mesh Visibility", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        ttk.Scale(control_panel, from_=0, to=100, variable=self.mesh_visibility, command=self.on_slider_change).pack(fill=tk.X, pady=5)
        
        self.lbl_dims = ttk.Label(control_panel, text="", font=("Consolas", 10), justify=tk.LEFT)
        self.lbl_dims.pack(anchor=tk.W, pady=10)
        
        ttk.Label(control_panel, text="LIMB LENGTHS (3D):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,5))
        self.lbl_limbs = ttk.Label(control_panel, text="", font=("Consolas", 10), justify=tk.LEFT)
        self.lbl_limbs.pack(anchor=tk.W)
        
        # --- Visualization Area ---
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Split into Side View / Front View
        self.paned = ttk.PanedWindow(viz_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Side View Frame
        f_side = ttk.Labelframe(self.paned, text="Side View (Length vs Height)")
        self.paned.add(f_side, weight=2)
        self.canvas_side = Canvas(f_side, bg="#eaeaea")
        self.canvas_side.pack(fill=tk.BOTH, expand=True)
        
        # Front View Frame
        f_front = ttk.Labelframe(self.paned, text="Front View (Width vs Height)")
        self.paned.add(f_front, weight=1)
        self.canvas_front = Canvas(f_front, bg="#e0e0e0")
        self.canvas_front.pack(fill=tk.BOTH, expand=True)
        
        # Bind Events
        self.canvas_side.bind("<Configure>", self.on_resize)
        self.canvas_front.bind("<Configure>", self.on_resize)
        
        # Mouse Interaction
        # We need to know WHICH canvas
        self.canvas_side.bind("<ButtonPress-1>", lambda e: self.on_click(e, "side"))
        self.canvas_side.bind("<B1-Motion>", lambda e: self.on_drag(e, "side"))
        self.canvas_side.bind("<ButtonRelease-1>", self.on_release)
        
        self.canvas_front.bind("<ButtonPress-1>", lambda e: self.on_click(e, "front"))
        self.canvas_front.bind("<B1-Motion>", lambda e: self.on_drag(e, "front"))
        self.canvas_front.bind("<ButtonRelease-1>", self.on_release)

    def load_data(self):
        print(f"Loading {self.obj_path}...")
        self.edges = set() # Store tuples of (v1_idx, v2_idx)
        
        try:
            with open(self.obj_path, 'r') as f:
                for line in f:
                    parts = line.split()
                    if not parts: continue
                    
                    if parts[0] == 'v':
                        try:
                            # OBJ: v x y z
                            self.vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                        except ValueError: continue
                    
                    elif parts[0] == 'f':
                        # f v1 v2 v3 ...
                        # OBJ indices are 1-based
                        v_indices = []
                        for p in parts[1:]:
                            # format can be v/vt/vn or just v
                            v_idx = int(p.split('/')[0]) - 1
                            v_indices.append(v_idx)
                        
                        # Create edges
                        for i in range(len(v_indices)):
                            i1 = v_indices[i]
                            i2 = v_indices[(i+1) % len(v_indices)] # Wrap around
                            # Store unordered tuple
                            edge = tuple(sorted((i1, i2)))
                            self.edges.add(edge)
                            
        except FileNotFoundError:
            # Dummy
            self.vertices = [(0,0,0), (100,100,50), (200,50,-50)]

        if not self.vertices: sys.exit(1)
            
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]

        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.min_z, self.max_z = min(zs), max(zs)
        
        self.model_dims = (self.max_x-self.min_x, self.max_y-self.min_y, self.max_z-self.min_z)
        
        # Optimization: if too many edges, sample them to avoid freezing Tkinter
        print(f"Loaded {len(self.vertices)} vertices and {len(self.edges)} edges.")
        if len(self.edges) > 5000:
            import random
            print("Reducing edges for display performance...")
            self.edges = random.sample(list(self.edges), 5000)

    def on_slider_change(self, event):
        self.update_calculations()
        
    def on_resize(self, event):
        self.draw_views()

    def update_calculations(self):
        target_mm = self.target_height_cm.get() * 10
        _, model_h, _ = self.model_dims
        if model_h == 0: return

        self.scale_factor = target_mm / model_h
        
        # Calculate real-world joint positions (Model Units)
        for name, (rx, ry, rz) in self.skeleton_ratios.items():
            mx = self.min_x + (rx * (self.max_x - self.min_x))
            my = self.min_y + (ry * (self.max_y - self.min_y))
            mz = self.min_z + (rz * (self.max_z - self.min_z))
            self.current_joints[name] = (mx, my, mz)

        # Update Labels
        scaled_h = model_h * self.scale_factor
        scaled_w = self.model_dims[0] * self.scale_factor
        scaled_d = self.model_dims[2] * self.scale_factor
        
        self.lbl_dims.config(text=f"Height: {scaled_h/10:.1f} cm\nLength: {scaled_w/10:.1f} cm\nWidth:  {scaled_d/10:.1f} cm")
        
        # Limb Lengths
        txt = ""
        for bone, start, end in self.bones:
            p1 = self.current_joints[start]
            p2 = self.current_joints[end]
            dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
            dist_mm = dist * self.scale_factor
            txt += f"{bone}: {dist_mm/10:.1f}cm ({dist_mm/8:.1f}s)\n"
        self.lbl_limbs.config(text=txt)
        
        self.draw_views()

    def draw_views(self):
        self.draw_canvas(self.canvas_side, "side")
        self.draw_canvas(self.canvas_front, "front")

    def draw_canvas(self, canvas, view_type):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        floor_y = h - 50
        origin_x = w/2 if view_type == "front" else 100
        
        # Calculate Mesh Color based on visibility
        # 0 = Invisible, 100 = #8888ff
        vis = self.mesh_visibility.get()
        if vis <= 5:
            mesh_color = None # Don't draw
        else:
            # Interpolate alpha? Tkinter doesn't do alpha easily.
            # We interpolate color towards background (#eaeaea or #e0e0e0)
            # Simple hex lerp
            bg_val = 234 if view_type == 'side' else 224 # eaeaea vs e0e0e0
            target_r, target_g, target_b = 136, 136, 255 # 8888ff
            
            # alpha 0.0 to 1.0
            alpha = vis / 100.0
            
            r = int(bg_val + (target_r - bg_val) * alpha)
            g = int(bg_val + (target_g - bg_val) * alpha)
            b = int(bg_val + (target_b - bg_val) * alpha)
            
            mesh_color = f"#{r:02x}{g:02x}{b:02x}"
            
        # Floor
        canvas.create_line(0, floor_y, w, floor_y, width=2)
        
        # --- Grid ---
        grid_mm = 16 * 8.0
        grid_px = grid_mm * self.pixels_per_mm
        
        num_h_lines = int(floor_y / grid_px) + 1
        for i in range(1, num_h_lines):
            y = floor_y - (i * grid_px)
            canvas.create_line(0, y, w, y, fill="#cccccc", width=1, dash=(4, 4))
            
        # Vertical lines
        num_v_lines_r = int((w - origin_x) / grid_px) + 1
        for i in range(1, num_v_lines_r):
            x = origin_x + (i * grid_px)
            canvas.create_line(x, 0, x, h, fill="#cccccc", width=1, dash=(4, 4))
        num_v_lines_l = int(origin_x / grid_px) + 1
        for i in range(1, num_v_lines_l):
            x = origin_x - (i * grid_px)
            canvas.create_line(x, 0, x, h, fill="#cccccc", width=1, dash=(4, 4))

        # Minifig
        minifig_h = 40 * self.pixels_per_mm
        canvas.create_rectangle(origin_x-10, floor_y-minifig_h, origin_x+10, floor_y, fill="red")
        
        # Draw Mesh Lines
        if mesh_color:
            z_center = (self.max_z + self.min_z) / 2
            
            # Draw Edges (limited/sampled)
            # Optimized draw: calculate projected points first?
            # Drawing thousands of lines is slow.
            
            # Use a generator/loop
            for v1_idx, v2_idx in self.edges:
                # Vertex 1
                vx1, vy1, vz1 = self.vertices[v1_idx]
                sy1 = (vy1 - self.min_y) * self.scale_factor
                py1 = floor_y - (sy1 * self.pixels_per_mm)
                
                # Vertex 2
                vx2, vy2, vz2 = self.vertices[v2_idx]
                sy2 = (vy2 - self.min_y) * self.scale_factor
                py2 = floor_y - (sy2 * self.pixels_per_mm)

                if view_type == "side":
                    sx1 = (vx1 - self.min_x) * self.scale_factor
                    px1 = origin_x + 50 + (sx1 * self.pixels_per_mm)
                    
                    sx2 = (vx2 - self.min_x) * self.scale_factor
                    px2 = origin_x + 50 + (sx2 * self.pixels_per_mm)
                else:
                    sz1 = (vz1 - z_center) * self.scale_factor
                    px1 = origin_x + (sz1 * self.pixels_per_mm)
                    
                    sz2 = (vz2 - z_center) * self.scale_factor
                    px2 = origin_x + (sz2 * self.pixels_per_mm)
                
                canvas.create_line(px1, py1, px2, py2, fill=mesh_color)
            
        # Draw Skeleton
        joint_px = {}
        for name, (mx, my, mz) in self.current_joints.items():
             sy = (my - self.min_y) * self.scale_factor
             py = floor_y - (sy * self.pixels_per_mm)
             
             if view_type == "side":
                 sx = (mx - self.min_x) * self.scale_factor
                 px = origin_x + 50 + (sx * self.pixels_per_mm)
             else:
                 z_center = (self.max_z + self.min_z) / 2
                 sz = (mz - z_center) * self.scale_factor
                 px = origin_x + (sz * self.pixels_per_mm)
            
             joint_px[name] = (px, py)
             canvas.create_oval(px-4, py-4, px+4, py+4, fill="orange", outline="black", tags=name)
             
        for bone, s, e in self.bones:
            p1 = joint_px[s]
            p2 = joint_px[e]
            canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="green", width=3)

    # --- Interaction ---
    def on_click(self, event, view_type):
        canvas = event.widget
        # Simple hit test
        closest = None
        min_dist = 20
        
        # We need to reuse the projection logic to find px,py of joints
        # Or just store them in draw? Storing in draw is cleaner but let's recompute for simplicity
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        floor_y = h - 50
        origin_x = w/2 if view_type == "front" else 100
        
        for name, (mx, my, mz) in self.current_joints.items():
             sy = (my - self.min_y) * self.scale_factor
             py = floor_y - (sy * self.pixels_per_mm)
             
             if view_type == "side":
                 sx = (mx - self.min_x) * self.scale_factor
                 px = origin_x + 50 + (sx * self.pixels_per_mm)
             else:
                 z_center = (self.max_z + self.min_z) / 2
                 sz = (mz - z_center) * self.scale_factor
                 px = origin_x + (sz * self.pixels_per_mm)
             
             dist = math.sqrt((event.x-px)**2 + (event.y-py)**2)
             if dist < min_dist:
                 closest = name
                 min_dist = dist
        
        self.dragged_joint = closest

    def on_drag(self, event, view_type):
        if not self.dragged_joint: return
        
        canvas = event.widget
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        floor_y = h - 50
        origin_x = w/2 if view_type == "front" else 100
        
        # Inverse Projection
        # py = floor_y - (sy * pix_per_mm) => sy = (floor_y - py) / pix
        sy = (floor_y - event.y) / self.pixels_per_mm
        
        # my = min_y + (sy / scale)
        if self.scale_factor == 0: return
        new_my = self.min_y + (sy / self.scale_factor)
        
        # Ratio Y
        range_y = self.max_y - self.min_y
        new_ry = (new_my - self.min_y) / range_y if range_y else 0
        
        # Get current ratios
        cur_rx, cur_ry, cur_rz = self.skeleton_ratios[self.dragged_joint]
        
        if view_type == "side":
            # Update X
            # px = origin + 50 + sx*pix
            # sx = (px - origin - 50) / pix
            sx = (event.x - origin_x - 50) / self.pixels_per_mm
            new_mx = self.min_x + (sx / self.scale_factor)
            range_x = self.max_x - self.min_x
            new_rx = (new_mx - self.min_x) / range_x if range_x else 0
            
            self.skeleton_ratios[self.dragged_joint] = (new_rx, new_ry, cur_rz)
            
        else: # Front
            # Update Z
            # px = origin + sz*pix
            sz = (event.x - origin_x) / self.pixels_per_mm
            z_center = (self.max_z + self.min_z) / 2
            new_mz = z_center + (sz / self.scale_factor)
            range_z = self.max_z - self.min_z
            new_rz = (new_mz - self.min_z) / range_z if range_z else 0.5
            
            self.skeleton_ratios[self.dragged_joint] = (cur_rx, new_ry, new_rz)
            
        self.update_calculations()

    def on_release(self, event):
        self.dragged_joint = None
        self.save_config()

    def get_config_path(self):
        # Config name = skeleton_<obj_filename_stem>.json
        # e.g. rpo.obj -> skeleton_rpo.json
        base_name = os.path.basename(self.obj_path)
        stem = os.path.splitext(base_name)[0]
        config_name = f"skeleton_{stem}.json"
        
        # Look for it in the same directory as the obj path
        # (which we enforce is the script directory in main)
        return os.path.join(os.path.dirname(self.obj_path), config_name)

    def load_config(self):
        p = self.get_config_path()
        if os.path.exists(p):
            print(f"Loading config from {p}")
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k in self.skeleton_ratios:
                            if len(v) == 2: # Migrate 2D -> 3D
                                self.skeleton_ratios[k] = (v[0], v[1], 0.5)
                            else:
                                self.skeleton_ratios[k] = tuple(v)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        p = self.get_config_path()
        try:
            with open(p, 'w') as f: json.dump(self.skeleton_ratios, f, indent=4)
            print(f"Saved config to {p}")
        except Exception as e:
            print(f"Error saving config: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mech_scaler.py <filename.obj>")
        print("Error: No OBJ file specified.")
        sys.exit(1)
        
    filename = sys.argv[1]
    # Always look for the file in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)
    
    root = tk.Tk()
    app = MechScalerApp(root, path)
    root.mainloop()
