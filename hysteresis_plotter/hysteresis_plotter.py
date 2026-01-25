
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pyqtgraph as pg

def calculate_hysteresis_loop(Ms, Hc, a, k, C_max=-250, T_max=550, num_points=200):
    """
    Calculates the x and y coordinates for a stress-strain hysteresis loop using a tanh model.

    Args:
        Ms (float): Yield strength (peak stress extent).
        Hc (float): Plastic slip (permanent deformation offset).
        a (float): Transition sharpness (yielding abruptness).
        k (float): Elastic compliance (derived from Young's Modulus).
        C_max (float): Maximum compression stress.
        T_max (float): Maximum tension stress.
        num_points (int): Number of points for each branch of the loop.

    Returns:
        tuple: A tuple containing two numpy arrays (x_loop, y_loop) representing strain and stress.
    """
    # Prevent division by zero if 'a' is zero
    if a == 0:
        a = 1e-9

    # Generate the stress values (y-axis) for the two branches
    y_asc = np.linspace(C_max, T_max, num_points)  # Ascending branch (compression → tension)
    y_desc = np.linspace(T_max, C_max, num_points) # Descending branch (tension → compression)

    # Calculate the strain values (x-axis) for each branch
    x_asc = Ms * np.tanh((y_asc + Hc) / a) + k * y_asc  # Loading curve
    x_desc = Ms * np.tanh((y_desc - Hc) / a) + k * y_desc  # Unloading curve

    # Concatenate the branches to form a closed loop
    x_loop = np.concatenate([x_asc, x_desc])
    y_loop = np.concatenate([y_asc, y_desc])

    return x_loop, y_loop

class HysteresisPlotter(QMainWindow):
    """
    A PyQt application that displays a hysteresis loop with interactive sliders.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Hysteresis Plotter")
        self.setGeometry(100, 100, 1200, 800)

        # --- Main Widget and Layout ---
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # --- PyQtGraph Plot Widget ---
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)

        # Configure the plot
        self.plot_widget.setYRange(-300, 600)
        self.plot_widget.setXRange(-2, 2)
        self.plot_widget.setAspectLocked(False) # Hysteresis loops aren't necessarily 1:1
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Stress (MPa)')
        self.plot_widget.setLabel('bottom', 'Strain (%)')
        self.plot_widget.setTitle("Stress-Strain Hysteresis Loop")

        # Add InfiniteLine for visually centered X and Y axes
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('k', width=1.5))) # Vertical line at x=0 (Y-axis)
        self.plot_widget.addItem(pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('k', width=1.5)))  # Horizontal line at y=0 (X-axis)

        # --- Hysteresis Loop PlotDataItem ---
        # We use a PlotDataItem which can be updated with new x,y data points.
        self.loop_item = self.plot_widget.plot(
            pen={'color': QColor(5, 150, 255), 'width': 1.5} # Thinner line
        )

        # --- Controls Layout (Sliders and Value Boxes) ---
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        main_layout.addWidget(controls_widget)
        
        sliders_layout = QHBoxLayout()

        # --- Yield Strength (Ms) Slider ---
        ms_group = QHBoxLayout()
        ms_label = QLabel("Yield Strength (M_s):")
        self.ms_slider = QSlider(Qt.Orientation.Horizontal)
        self.ms_slider.setRange(1, 20) # Range 0.1 to 9.0
        self.ms_slider.setValue(7)
        self.ms_value_box = QLineEdit()
        self.ms_value_box.setReadOnly(True)
        self.ms_value_box.setFixedWidth(50)
        ms_group.addWidget(ms_label)
        ms_group.addWidget(self.ms_slider)
        ms_group.addWidget(self.ms_value_box)
        sliders_layout.addLayout(ms_group)

        # --- Plastic Slip (Hc) Slider ---
        hc_group = QHBoxLayout()
        hc_label = QLabel("Plastic Slip (H_c):")
        self.hc_slider = QSlider(Qt.Orientation.Horizontal)
        self.hc_slider.setRange(100, 1000) # Range 10.0 to 100.0
        self.hc_slider.setValue(500)
        self.hc_value_box = QLineEdit()
        self.hc_value_box.setReadOnly(True)
        self.hc_value_box.setFixedWidth(50)
        hc_group.addWidget(hc_label)
        hc_group.addWidget(self.hc_slider)
        hc_group.addWidget(self.hc_value_box)
        sliders_layout.addLayout(hc_group)

        # --- Transition Sharpness (a) Slider ---
        a_group = QHBoxLayout()
        a_label = QLabel("Transition Sharpness (a):")
        self.a_slider = QSlider(Qt.Orientation.Horizontal)
        self.a_slider.setRange(200, 2000) # Range 20 to 200.0
        self.a_slider.setValue(1000)
        self.a_value_box = QLineEdit()
        self.a_value_box.setReadOnly(True)
        self.a_value_box.setFixedWidth(50)
        a_group.addWidget(a_label)
        a_group.addWidget(self.a_slider)
        a_group.addWidget(self.a_value_box)
        sliders_layout.addLayout(a_group)

        # --- Young's Modulus (E) Slider ---
        e_group = QHBoxLayout()
        e_label = QLabel("Young's Modulus (E):")
        self.e_slider = QSlider(Qt.Orientation.Horizontal)
        self.e_slider.setRange(100, 300) # Range 10 to 500 GPa
        self.e_slider.setValue(200)
        self.e_value_box = QLineEdit()
        self.e_value_box.setReadOnly(True)
        self.e_value_box.setFixedWidth(50)
        e_group.addWidget(e_label)
        e_group.addWidget(self.e_slider)
        e_group.addWidget(self.e_value_box)
        sliders_layout.addLayout(e_group)
        
        controls_layout.addLayout(sliders_layout)

        # --- Connect Signals to Slots ---
        self.ms_slider.valueChanged.connect(self.update_loop)
        self.hc_slider.valueChanged.connect(self.update_loop)
        self.a_slider.valueChanged.connect(self.update_loop)
        self.e_slider.valueChanged.connect(self.update_loop)

        # --- Initial Plot ---
        self.update_loop()

    def update_loop(self):
        """
        This function is called whenever a slider's value changes.
        It recalculates the loop and updates the plot.
        """
        # Get values from sliders, scaling them appropriately
        ms_val = self.ms_slider.value() / 10.0
        hc_val = self.hc_slider.value() / 10.0
        a_val = self.a_slider.value() / 10.0
        e_val_gpa = self.e_slider.value()

        # Calculate the slope k from Young's Modulus E
        # Strain = 100 * Stress / E_MPa
        # k = dx/dy = 100 / (E_GPa * 1000)
        e_val_mpa = e_val_gpa * 1000
        k_val = 100 / e_val_mpa if e_val_mpa > 0 else 0

        # Update the read-only value boxes
        self.ms_value_box.setText(f"{ms_val:.1f}")
        self.hc_value_box.setText(f"{hc_val:.1f}")
        self.a_value_box.setText(f"{a_val:.1f}")
        self.e_value_box.setText(f"{e_val_gpa} GPa")

        # Calculate the new loop data
        x_data, y_data = calculate_hysteresis_loop(ms_val, hc_val, a_val, k_val)

        # Update the plot with the new data
        self.loop_item.setData(x_data, y_data)


def main():
    """
    Main function to run the application.
    """
    app = QApplication(sys.argv)
    window = HysteresisPlotter()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
