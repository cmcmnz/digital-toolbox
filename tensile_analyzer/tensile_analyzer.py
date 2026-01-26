
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSlider,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pyqtgraph as pg

from specimen_model import TensileSpecimen, GeometricProperties, MaterialProperties


class TensileAnalyzer(QMainWindow):
    """
    Main application for tensile specimen analysis and visualization.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tensile Specimen Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize specimen with default properties
        self.geometry = GeometricProperties()
        self.material = MaterialProperties()
        self.specimen = TensileSpecimen(self.geometry, self.material)
        
        # Current applied force (N)
        self.applied_force = 0.0
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create visualization grid (2x2)
        viz_layout = QGridLayout()
        main_layout.addLayout(viz_layout)
        
        # Panel A: Specimen Geometry
        self.geometry_plot = pg.PlotWidget()
        self.geometry_plot.setTitle("Specimen Geometry")
        self.geometry_plot.setLabel('left', 'Radius (mm)')
        self.geometry_plot.setLabel('bottom', 'Axial Position (mm)')
        self.geometry_plot.setAspectLocked(False)
        self.geometry_plot.showGrid(x=True, y=True, alpha=0.3)
        viz_layout.addWidget(self.geometry_plot, 0, 0)
        
        # Panel B: Stress Distribution
        self.stress_plot = pg.PlotWidget()
        self.stress_plot.setTitle("Stress Distribution")
        self.stress_plot.setLabel('left', 'Stress (MPa)')
        self.stress_plot.setLabel('bottom', 'Axial Position (mm)')
        self.stress_plot.showGrid(x=True, y=True, alpha=0.3)
        viz_layout.addWidget(self.stress_plot, 0, 1)
        
        # Panel C: Stress-Strain Curve
        self.stress_strain_plot = pg.PlotWidget()
        self.stress_strain_plot.setTitle("Stress-Strain Curve")
        self.stress_strain_plot.setLabel('left', 'Stress (MPa)')
        self.stress_strain_plot.setLabel('bottom', 'Strain (%)')
        self.stress_strain_plot.showGrid(x=True, y=True, alpha=0.3)
        viz_layout.addWidget(self.stress_strain_plot, 1, 0)
        
        # Panel D: Deformed Shape
        self.deformed_plot = pg.PlotWidget()
        self.deformed_plot.setTitle("Deformed Shape (Exaggerated)")
        self.deformed_plot.setLabel('left', 'Radius (mm)')
        self.deformed_plot.setLabel('bottom', 'Axial Position (mm)')
        self.deformed_plot.setAspectLocked(False)
        self.deformed_plot.showGrid(x=True, y=True, alpha=0.3)
        viz_layout.addWidget(self.deformed_plot, 1, 1)
        
        # Controls section
        controls_widget = QWidget()
        controls_layout = QGridLayout()
        controls_widget.setLayout(controls_layout)
        main_layout.addWidget(controls_widget)
        
        row = 0
        
        # Gauge Length
        controls_layout.addWidget(QLabel("Gauge Length (mm):"), row, 0)
        self.gauge_length_slider = QSlider(Qt.Orientation.Horizontal)
        self.gauge_length_slider.setRange(50, 200)
        self.gauge_length_slider.setValue(int(self.geometry.gauge_length))
        controls_layout.addWidget(self.gauge_length_slider, row, 1)
        self.gauge_length_box = QLineEdit(f"{self.geometry.gauge_length:.1f}")
        self.gauge_length_box.setReadOnly(True)
        self.gauge_length_box.setFixedWidth(60)
        controls_layout.addWidget(self.gauge_length_box, row, 2)
        row += 1
        
        # Gauge Diameter
        controls_layout.addWidget(QLabel("Gauge Diameter (mm):"), row, 0)
        self.gauge_diameter_slider = QSlider(Qt.Orientation.Horizontal)
        self.gauge_diameter_slider.setRange(60, 250)  # 6.0 to 25.0 mm
        self.gauge_diameter_slider.setValue(int(self.geometry.gauge_diameter * 10))
        controls_layout.addWidget(self.gauge_diameter_slider, row, 1)
        self.gauge_diameter_box = QLineEdit(f"{self.geometry.gauge_diameter:.1f}")
        self.gauge_diameter_box.setReadOnly(True)
        self.gauge_diameter_box.setFixedWidth(60)
        controls_layout.addWidget(self.gauge_diameter_box, row, 2)
        row += 1
        
        # Fillet Radius
        controls_layout.addWidget(QLabel("Fillet Radius (mm):"), row, 0)
        self.fillet_radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.fillet_radius_slider.setRange(5, 50)
        self.fillet_radius_slider.setValue(int(self.geometry.fillet_radius))
        controls_layout.addWidget(self.fillet_radius_slider, row, 1)
        self.fillet_radius_box = QLineEdit(f"{self.geometry.fillet_radius:.1f}")
        self.fillet_radius_box.setReadOnly(True)
        self.fillet_radius_box.setFixedWidth(60)
        controls_layout.addWidget(self.fillet_radius_box, row, 2)
        row += 1
        
        # Young's Modulus
        controls_layout.addWidget(QLabel("Young's Modulus (GPa):"), row, 0)
        self.youngs_modulus_slider = QSlider(Qt.Orientation.Horizontal)
        self.youngs_modulus_slider.setRange(190, 210)
        self.youngs_modulus_slider.setValue(int(self.material.youngs_modulus / 1000))
        controls_layout.addWidget(self.youngs_modulus_slider, row, 1)
        self.youngs_modulus_box = QLineEdit(f"{self.material.youngs_modulus / 1000:.0f}")
        self.youngs_modulus_box.setReadOnly(True)
        self.youngs_modulus_box.setFixedWidth(60)
        controls_layout.addWidget(self.youngs_modulus_box, row, 2)
        row += 1
        
        # Yield Strength
        controls_layout.addWidget(QLabel("Yield Strength (MPa):"), row, 0)
        self.yield_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.yield_strength_slider.setRange(250, 800)
        self.yield_strength_slider.setValue(int(self.material.yield_strength))
        controls_layout.addWidget(self.yield_strength_slider, row, 1)
        self.yield_strength_box = QLineEdit(f"{self.material.yield_strength:.0f}")
        self.yield_strength_box.setReadOnly(True)
        self.yield_strength_box.setFixedWidth(60)
        controls_layout.addWidget(self.yield_strength_box, row, 2)
        row += 1
        
        # Applied Force
        controls_layout.addWidget(QLabel("Applied Force (kN):"), row, 0)
        self.force_slider = QSlider(Qt.Orientation.Horizontal)
        self.force_slider.setRange(0, 100)  # 0 to 100 kN
        self.force_slider.setValue(0)
        controls_layout.addWidget(self.force_slider, row, 1)
        self.force_box = QLineEdit("0.0")
        self.force_box.setReadOnly(True)
        self.force_box.setFixedWidth(60)
        controls_layout.addWidget(self.force_box, row, 2)
        row += 1
        
        # Stress Concentration Factor (read-only display)
        controls_layout.addWidget(QLabel("Stress Concentration (K_t):"), row, 0)
        self.kt_box = QLineEdit()
        self.kt_box.setReadOnly(True)
        self.kt_box.setFixedWidth(60)
        controls_layout.addWidget(self.kt_box, row, 2)
        row += 1
        
        # Connect signals
        self.gauge_length_slider.valueChanged.connect(self.update_geometry)
        self.gauge_diameter_slider.valueChanged.connect(self.update_geometry)
        self.fillet_radius_slider.valueChanged.connect(self.update_geometry)
        self.youngs_modulus_slider.valueChanged.connect(self.update_material)
        self.yield_strength_slider.valueChanged.connect(self.update_material)
        self.force_slider.valueChanged.connect(self.update_force)
        
        # Initial update
        self.update_all()
    
    def update_geometry(self):
        """Update geometry from sliders."""
        self.geometry.gauge_length = float(self.gauge_length_slider.value())
        self.geometry.gauge_diameter = self.gauge_diameter_slider.value() / 10.0
        self.geometry.fillet_radius = float(self.fillet_radius_slider.value())
        
        # Update displays
        self.gauge_length_box.setText(f"{self.geometry.gauge_length:.1f}")
        self.gauge_diameter_box.setText(f"{self.geometry.gauge_diameter:.1f}")
        self.fillet_radius_box.setText(f"{self.geometry.fillet_radius:.1f}")
        
        # Recreate specimen
        self.specimen = TensileSpecimen(self.geometry, self.material)
        self.update_all()
    
    def update_material(self):
        """Update material properties from sliders."""
        self.material.youngs_modulus = self.youngs_modulus_slider.value() * 1000.0
        self.material.yield_strength = float(self.yield_strength_slider.value())
        
        # Update displays
        self.youngs_modulus_box.setText(f"{self.material.youngs_modulus / 1000:.0f}")
        self.yield_strength_box.setText(f"{self.material.yield_strength:.0f}")
        
        # Recreate specimen
        self.specimen = TensileSpecimen(self.geometry, self.material)
        self.update_all()
    
    def update_force(self):
        """Update applied force from slider."""
        self.applied_force = self.force_slider.value() * 1000.0  # Convert kN to N
        self.force_box.setText(f"{self.applied_force / 1000:.1f}")
        self.update_all()
    
    def update_all(self):
        """Update all visualizations."""
        self.plot_geometry()
        self.plot_stress_distribution()
        self.plot_stress_strain_curve()
        self.plot_deformed_shape()
        
        # Update K_t display
        kt = self.specimen.stress_concentration_factor()
        self.kt_box.setText(f"{kt:.2f}")
    
    def plot_geometry(self):
        """Plot the specimen geometry."""
        self.geometry_plot.clear()
        
        x, y = self.specimen.get_profile_coordinates()
        
        # Plot upper and lower profiles
        self.geometry_plot.plot(x, y, pen=pg.mkPen('b', width=2))
        self.geometry_plot.plot(x, -y, pen=pg.mkPen('b', width=2))
        
        # Add centerline
        self.geometry_plot.plot([x[0], x[-1]], [0, 0], pen=pg.mkPen('k', width=1, style=Qt.PenStyle.DashLine))
    
    def plot_stress_distribution(self):
        """Plot stress distribution along the specimen."""
        self.stress_plot.clear()
        
        if self.applied_force == 0:
            return
        
        x, y = self.specimen.get_profile_coordinates()
        stress = np.zeros_like(x)
        
        # Calculate stress at each point
        gauge_stress = self.specimen.calculate_stress(self.applied_force)
        kt = self.specimen.stress_concentration_factor()
        
        for i, (xi, yi) in enumerate(zip(x, y)):
            area = np.pi * yi ** 2
            if area > 0:
                stress[i] = self.applied_force / area
                
                # Apply stress concentration at transitions
                # Simplified: apply K_t in transition zones
                total_length = 2 * self.geometry.grip_length + self.geometry.gauge_length
                grip1_end = self.geometry.grip_length
                transition1_end = grip1_end + self.geometry.fillet_radius
                gauge_end = transition1_end + self.geometry.gauge_length
                transition2_end = gauge_end + self.geometry.fillet_radius
                
                if grip1_end < xi < transition1_end or gauge_end < xi < transition2_end:
                    stress[i] *= kt
        
        self.stress_plot.plot(x, stress, pen=pg.mkPen('r', width=2))
        self.stress_plot.plot([x[0], x[-1]], [self.material.yield_strength, self.material.yield_strength], 
                             pen=pg.mkPen('g', width=1, style=Qt.PenStyle.DashLine))
    
    def plot_stress_strain_curve(self):
        """Plot the stress-strain curve."""
        self.stress_strain_plot.clear()
        
        # Generate stress-strain curve
        max_stress = min(self.material.ultimate_strength, 800)
        stress_range = np.linspace(0, max_stress, 200)
        strain_range = np.zeros_like(stress_range)
        
        for i, stress in enumerate(stress_range):
            strain_range[i] = self.specimen.calculate_strain_plastic(stress) * 100  # Convert to %
        
        self.stress_strain_plot.plot(strain_range, stress_range, pen=pg.mkPen('b', width=2))
        
        # Mark yield point
        yield_strain = self.specimen.calculate_strain_elastic(self.material.yield_strength) * 100
        self.stress_strain_plot.plot([yield_strain], [self.material.yield_strength], 
                                     symbol='o', symbolSize=8, symbolBrush='g')
        
        # Mark current state if force is applied
        if self.applied_force > 0:
            current_stress = self.specimen.calculate_stress(self.applied_force)
            current_strain = self.specimen.calculate_strain_plastic(current_stress) * 100
            self.stress_strain_plot.plot([current_strain], [current_stress], 
                                        symbol='o', symbolSize=10, symbolBrush='r')
    
    def plot_deformed_shape(self):
        """Plot the deformed shape with exaggerated deformation."""
        self.deformed_plot.clear()
        
        if self.applied_force == 0:
            # Show undeformed shape
            x, y = self.specimen.get_profile_coordinates()
            self.deformed_plot.plot(x, y, pen=pg.mkPen('b', width=2, style=Qt.PenStyle.DashLine))
            self.deformed_plot.plot(x, -y, pen=pg.mkPen('b', width=2, style=Qt.PenStyle.DashLine))
            return
        
        # Calculate deformation
        stress = self.specimen.calculate_stress(self.applied_force)
        strain = self.specimen.calculate_strain_plastic(stress)
        
        # Exaggeration factor for visibility
        exaggeration = 50.0
        
        x, y = self.specimen.get_profile_coordinates()
        x_deformed = x.copy()
        y_deformed = y.copy()
        
        # Apply axial elongation (only in gauge section)
        total_length = 2 * self.geometry.grip_length + self.geometry.gauge_length
        grip1_end = self.geometry.grip_length
        transition1_end = grip1_end + self.geometry.fillet_radius
        gauge_end = transition1_end + self.geometry.gauge_length
        
        for i, xi in enumerate(x):
            if transition1_end <= xi <= gauge_end:
                # Gauge section: apply full strain
                local_elongation = (xi - transition1_end) * strain * exaggeration
                x_deformed[i] = xi + local_elongation
                
                # Apply Poisson contraction
                lateral_strain = self.specimen.calculate_lateral_strain(strain)
                y_deformed[i] = y[i] * (1 + lateral_strain * exaggeration)
        
        # Plot undeformed (dashed) and deformed (solid)
        self.deformed_plot.plot(x, y, pen=pg.mkPen('gray', width=1, style=Qt.PenStyle.DashLine))
        self.deformed_plot.plot(x, -y, pen=pg.mkPen('gray', width=1, style=Qt.PenStyle.DashLine))
        self.deformed_plot.plot(x_deformed, y_deformed, pen=pg.mkPen('r', width=2))
        self.deformed_plot.plot(x_deformed, -y_deformed, pen=pg.mkPen('r', width=2))


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = TensileAnalyzer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
