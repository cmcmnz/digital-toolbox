
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
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pyqtgraph as pg

class ChainlinkMechanics(QMainWindow):
    """
    A PyQt application that displays a chain of links forming a circle,
    with interactive controls for its geometric properties.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chainlink Mechanics")
        self.setGeometry(100, 100, 1200, 900)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        controls_widget.setFixedWidth(300)
        main_layout.addWidget(controls_widget)

        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)
        self.setup_plot()

        grid_layout = QGridLayout()
        row = 0

        grid_layout.addWidget(QLabel("Total Number of Links:"), row, 0)
        self.n_links_input = QLineEdit("22")
        grid_layout.addWidget(self.n_links_input, row, 1); row += 1

        grid_layout.addWidget(QLabel("Inner Diameter (mm):"), row, 0); row += 1
        self.inner_diameter_slider = QSlider(Qt.Orientation.Horizontal)
        self.inner_diameter_slider.setRange(300, 2000)
        grid_layout.addWidget(self.inner_diameter_slider, row, 0)
        self.inner_diameter_box = QLineEdit()
        grid_layout.addWidget(self.inner_diameter_box, row, 1); row += 1

        grid_layout.addWidget(QLabel("Green Link Length (mm):"), row, 0); row += 1
        self.green_len_slider = QSlider(Qt.Orientation.Horizontal)
        self.green_len_slider.setRange(300, 2000)
        grid_layout.addWidget(self.green_len_slider, row, 0)
        self.green_len_box = QLineEdit()
        grid_layout.addWidget(self.green_len_box, row, 1); row += 1

        grid_layout.addWidget(QLabel("Red Link Length (mm):"), row, 0)
        self.red_len_box = QLineEdit("6.35")
        grid_layout.addWidget(self.red_len_box, row, 1); row += 1

        grid_layout.addWidget(QLabel("Inner Circumference (mm):"), row, 0)
        self.inner_circ_box = QLineEdit()
        self.inner_circ_box.setReadOnly(True)
        grid_layout.addWidget(self.inner_circ_box, row, 1); row += 1
        
        controls_layout.addLayout(grid_layout)
        controls_layout.addStretch()

        self.n_links_input.editingFinished.connect(lambda: self.recalculate_and_draw(sender="n_links"))
        self.inner_diameter_slider.valueChanged.connect(self.update_from_diameter_slider)
        self.inner_diameter_box.editingFinished.connect(self.update_from_diameter_box)
        self.green_len_slider.valueChanged.connect(self.update_from_green_len_slider)
        self.green_len_box.editingFinished.connect(self.update_from_green_len_box)
        self.red_len_box.editingFinished.connect(lambda: self.recalculate_and_draw(sender="diameter"))

        self.inner_diameter_slider.setValue(800)
        self.green_len_slider.setValue(635)
        self.recalculate_and_draw(sender="diameter")

    def setup_plot(self):
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Y (mm)'); self.plot_widget.setLabel('bottom', 'X (mm)')
        self.plot_widget.setTitle("Chainlink Geometry")
        self.standard_circles_plot = pg.PlotDataItem(pen=None, brush=pg.mkBrush(100, 100, 150, 200), fillLevel=0)
        self.green_circles_plot = pg.PlotDataItem(pen=None, brush=pg.mkBrush(50, 200, 50, 200), fillLevel=0)
        self.red_circles_plot = pg.PlotDataItem(pen=None, brush=pg.mkBrush(200, 50, 50, 200), fillLevel=0)
        self.plot_widget.addItem(self.standard_circles_plot); self.plot_widget.addItem(self.green_circles_plot); self.plot_widget.addItem(self.red_circles_plot)
        self.standard_links_lines = pg.PlotDataItem(pen={'color': 'w', 'width': 1}); self.green_link_line = pg.PlotDataItem(pen={'color': 'g', 'width': 2}); self.red_link_line = pg.PlotDataItem(pen={'color': 'r', 'width': 2})
        self.plot_widget.addItem(self.standard_links_lines); self.plot_widget.addItem(self.green_link_line); self.plot_widget.addItem(self.red_link_line)
        self.inner_circle_item = pg.PlotDataItem(pen={'color': 'y', 'width': 2, 'style': Qt.PenStyle.DashLine})
        self.plot_widget.addItem(self.inner_circle_item)

    def update_from_diameter_slider(self, value):
        self.inner_diameter_box.setText(f"{value / 10.0:.2f}")
        self.recalculate_and_draw(sender="diameter")

    def update_from_diameter_box(self):
        try:
            d_inner = float(self.inner_diameter_box.text())
            self.inner_diameter_slider.blockSignals(True)
            self.inner_diameter_slider.setValue(int(np.clip(d_inner, 30, 200) * 10))
            self.inner_diameter_slider.blockSignals(False)
            self.recalculate_and_draw(sender="diameter")
        except ValueError: pass

    def update_from_green_len_slider(self, value):
        self.green_len_box.setText(f"{value / 100.0:.2f}")
        self.recalculate_and_draw(sender="green_len")

    def update_from_green_len_box(self):
        try:
            l_green = float(self.green_len_box.text())
            self.green_len_slider.blockSignals(True)
            self.green_len_slider.setValue(int(np.clip(l_green, 3, 12) * 100))
            self.green_len_slider.blockSignals(False)
            self.recalculate_and_draw(sender="green_len")
        except ValueError: pass

    def recalculate_and_draw(self, sender=None):
        try:
            total_links = int(self.n_links_input.text())
            if total_links < 2: total_links = 2; self.n_links_input.setText("2")
        except ValueError: total_links = 22; self.n_links_input.setText("22")
        
        n_standard_links = total_links - 2
        if n_standard_links < 0: n_standard_links = 0

        d_standard = 6.35
        d_interlink = 6.0
        r_small = 3.0
        d_interlink = 6.0
        r_small = 3.0
        try: l_red = float(self.red_len_box.text())
        except ValueError: l_red = 10.0
        
        if sender == "diameter":
            d_inner = self.inner_diameter_slider.value() / 10.0
            r_chain = (d_inner / 2.0) + r_small
            if r_chain > 0:
                def angle_from_chord(length, R):
                    ratio = length / (2 * R)
                    return 2 * np.arcsin(ratio) if ratio <= 1 else float('nan')
                
                angle_d_std = angle_from_chord(d_standard, r_chain)
                angle_l_red = angle_from_chord(l_red, r_chain)
                angle_d_inter = angle_from_chord(d_interlink, r_chain)

                if any(np.isnan(a) for a in [angle_d_std, angle_l_red, angle_d_inter]):
                    l_green = -1
                else:
                    angle_l_green = 2 * np.pi - (n_standard_links * angle_d_std + angle_l_red + total_links * angle_d_inter)
                    l_green = 2 * r_chain * np.sin(angle_l_green / 2.0) if angle_l_green > 0 else -1
                
                self.green_len_slider.blockSignals(True)
                self.green_len_slider.setValue(int(np.clip(l_green, 3, 20) * 100))
                self.green_len_slider.blockSignals(False)
        else: # sender is "green_len" or n_links
            l_green = self.green_len_slider.value() / 100.0
            
            def get_angle_sum(R):
                if R <= 0: return float('inf')
                lengths = [d_standard, l_green, l_red, d_interlink]
                ratios = [l / (2*R) for l in lengths]
                if any(r > 1 for r in ratios): return float('inf')
                angles = [2 * np.arcsin(r) for r in ratios]
                return n_standard_links * angles[0] + angles[1] + angles[2] + total_links * angles[3]

            low_r = max(d_standard, l_green, l_red, d_interlink) / 2.0
            high_r = 1000
            for _ in range(100):
                mid_r = (low_r + high_r) / 2
                if mid_r <= 0: break
                if get_angle_sum(mid_r) > 2 * np.pi: low_r = mid_r
                else: high_r = mid_r
            r_chain = (low_r + high_r) / 2
            
            d_inner = (r_chain - r_small) * 2
            self.inner_diameter_slider.blockSignals(True)
            self.inner_diameter_slider.setValue(int(np.clip(d_inner, 30, 200) * 10))
            self.inner_diameter_slider.blockSignals(False)

        # --- Update All Readouts ---
        d_inner_val = self.inner_diameter_slider.value() / 10.0
        l_green_val = self.green_len_slider.value() / 100.0
        self.inner_diameter_box.setText(f"{d_inner_val:.2f}")
        self.green_len_box.setText(f"{l_green_val:.2f}" if l_green_val > 0 else "Error")
        self.inner_circ_box.setText(f"{d_inner_val * np.pi:.2f}")
        
        # --- Drawing ---
        r_inner = d_inner_val / 2.0
        r_chain = r_inner + r_small
        self.standard_circles_plot.clear(); self.green_circles_plot.clear(); self.red_circles_plot.clear()
        self.standard_links_lines.clear(); self.green_link_line.clear(); self.red_link_line.clear()
        
        def angle(length, R):
            ratio = length / (2*R)
            return 2 * np.arcsin(ratio) if R > 0 and ratio <=1 else 0

        angle_d_std = angle(d_standard, r_chain)
        angle_l_green = angle(l_green_val, r_chain)
        angle_l_red = angle(l_red, r_chain)
        angle_d_inter = angle(d_interlink, r_chain)

        if l_green_val <= 0 : # Don't draw if geometry is impossible
            return

        red_link_index = total_links // 2
        circ_t = np.linspace(0, 2 * np.pi, 50)
        circ_x, circ_y = r_small * np.cos(circ_t), r_small * np.sin(circ_t)
        
        plots = {'std': self.standard_circles_plot, 'green': self.green_circles_plot, 'red': self.red_circles_plot}
        lines = {'std': self.standard_links_lines, 'green': self.green_link_line, 'red': self.red_link_line}
        data = {k: {'x': [], 'y': []} for k in plots}; line_data = {'x': [], 'y': []}

        current_angle = 0
        for i in range(total_links):
            p1 = (r_chain * np.cos(current_angle), r_chain * np.sin(current_angle))
            link_type, ang = 'std', angle_d_std
            if i == 0: link_type, ang = 'green', angle_l_green
            elif i == red_link_index: link_type, ang = 'red', angle_l_red
            current_angle += ang
            p2 = (r_chain * np.cos(current_angle), r_chain * np.sin(current_angle))

            for p in [p1, p2]:
                data[link_type]['x'].extend(p[0] + circ_x); data[link_type]['x'].append(np.nan)
                data[link_type]['y'].extend(p[1] + circ_y); data[link_type]['y'].append(np.nan)
            
            if link_type == 'std':
                line_data['x'].extend([p1[0], p2[0], np.nan]); line_data['y'].extend([p1[1], p2[1], np.nan])
            else:
                lines[link_type].setData(x=[p1[0], p2[0]], y=[p1[1], p2[1]])
            
            current_angle += angle_d_inter

        for k in data: plots[k].setData(x=data[k]['x'], y=data[k]['y'])
        lines['std'].setData(x=line_data['x'], y=line_data['y'], connect='all')
        
        theta = np.linspace(0, 2 * np.pi, 200)
        self.inner_circle_item.setData(r_inner * np.cos(theta), r_inner * np.sin(theta))

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = ChainlinkMechanics()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
