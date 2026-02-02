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
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont
import pyqtgraph as pg

class WheatstoneBridgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wheatstone Bridge Tool")
        # Set size to 16:9 ratio (e.g., 1280x720)
        self.resize(1280, 720)

        # Default values
        self.base_resistance = 120.0
        self.shunt_value = 20000.0
        self.gauge_factor = 2.0
        self.active_gauges = 1
        self.is_shunt_connected = False
        self.strain_percent = 0.0 # Full scale -100% to 100%
        
        self.specimen_width = 50.0
        self.specimen_height = 150.0
        self.gauge_length = 80.0
        self.total_strain_ratio = 0.0 # Ratio (-0.1 to 0.1)

        self.init_ui()
        self.update_calculations()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Panel: Controls ---
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel, 1)

        # Base Resistance Selector
        res_group = QGroupBox("Base Resistance (Ω)")
        res_layout = QVBoxLayout()
        self.res_120_rb = QRadioButton("120 Ω")
        self.res_120_rb.setChecked(True)
        self.res_350_rb = QRadioButton("350 Ω")
        self.res_group_btns = QButtonGroup()
        self.res_group_btns.addButton(self.res_120_rb)
        self.res_group_btns.addButton(self.res_350_rb)
        res_layout.addWidget(self.res_120_rb)
        res_layout.addWidget(self.res_350_rb)
        res_group.setLayout(res_layout)
        left_panel.addWidget(res_group)

        # Active Gauges Selector
        gauges_group = QGroupBox("Active Gauges")
        gauges_layout = QVBoxLayout()
        self.gauge_1_rb = QRadioButton("1 Active Gauge (R1)")
        self.gauge_1_rb.setChecked(True)
        self.gauge_2_rb = QRadioButton("2 Active Gauges (R1, R3)")
        self.gauge_group_btns = QButtonGroup()
        self.gauge_group_btns.addButton(self.gauge_1_rb)
        self.gauge_group_btns.addButton(self.gauge_2_rb)
        gauges_layout.addWidget(self.gauge_1_rb)
        gauges_layout.addWidget(self.gauge_2_rb)
        gauges_group.setLayout(gauges_layout)
        left_panel.addWidget(gauges_group)

        # Shunt Control
        shunt_group = QGroupBox("Shunt Calibration")
        shunt_layout = QGridLayout()
        shunt_layout.addWidget(QLabel("Shunt Resistor (Ω):"), 0, 0)
        self.shunt_input = QLineEdit("20000")
        shunt_layout.addWidget(self.shunt_input, 0, 1)
        self.shunt_btn = QPushButton("Connect Shunt")
        self.shunt_btn.setCheckable(True)
        shunt_layout.addWidget(self.shunt_btn, 1, 0, 1, 2)
        shunt_group.setLayout(shunt_layout)
        left_panel.addWidget(shunt_group)

        # Gauge Factor
        gf_group = QGroupBox("Gauge Settings")
        gf_layout = QGridLayout()
        gf_layout.addWidget(QLabel("Gauge Factor:"), 0, 0)
        self.gf_input = QLineEdit("2.0")
        gf_layout.addWidget(self.gf_input, 0, 1)
        gf_group.setLayout(gf_layout)
        left_panel.addWidget(gf_group)
        
        left_panel.addStretch()

        # --- Center Panel: Bridge Visualization ---
        center_panel = QVBoxLayout()
        main_layout.addLayout(center_panel, 2)
        
        self.bridge_view = BridgeCanvas(self)
        center_panel.addWidget(self.bridge_view)
        
        # Bottom Slider
        slider_layout = QVBoxLayout()
        self.balance_label = QLabel("Bridge Balance: 0.00 %")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_layout.addWidget(self.balance_label)
        self.balance_slider = QSlider(Qt.Orientation.Horizontal)
        # Range for -10.00% to +10.00% strain
        self.balance_slider.setRange(-1000, 1000) 
        self.balance_slider.setValue(0)
        slider_layout.addWidget(self.balance_slider)
        center_panel.addLayout(slider_layout)

        # --- Right Panel: Specimen ---
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, 1)
        
        spec_group = QGroupBox("Specimen Measurements")
        spec_layout = QGridLayout()
        spec_layout.addWidget(QLabel("Width (mm):"), 0, 0)
        self.spec_width_input = QLineEdit("50")
        spec_layout.addWidget(self.spec_width_input, 0, 1)
        spec_layout.addWidget(QLabel("Height (mm):"), 1, 0)
        self.spec_height_input = QLineEdit("150")
        spec_layout.addWidget(self.spec_height_input, 1, 1)
        spec_layout.addWidget(QLabel("Gauge Length (mm):"), 2, 0)
        self.gauge_length_input = QLineEdit("80")
        spec_layout.addWidget(self.gauge_length_input, 2, 1)
        spec_group.setLayout(spec_layout)
        right_panel.addWidget(spec_group)
        
        self.specimen_view = SpecimenCanvas(self)
        right_panel.addWidget(self.specimen_view)
        
        right_panel.addStretch()

        # Connections
        self.res_group_btns.buttonClicked.connect(self.update_calculations)
        self.gauge_group_btns.buttonClicked.connect(self.update_calculations)
        self.shunt_input.textChanged.connect(self.update_calculations)
        self.shunt_btn.clicked.connect(self.toggle_shunt)
        self.gf_input.textChanged.connect(self.update_calculations)
        self.balance_slider.valueChanged.connect(self.update_slider)
        self.spec_width_input.textChanged.connect(self.update_specimen)
        self.spec_height_input.textChanged.connect(self.update_specimen)
        self.gauge_length_input.textChanged.connect(self.update_specimen)

    def toggle_shunt(self):
        self.is_shunt_connected = self.shunt_btn.isChecked()
        self.shunt_btn.setText("Disconnect Shunt" if self.is_shunt_connected else "Connect Shunt")
        
        # When shunt is connected, reset strain to neutral
        self.balance_slider.setValue(0)
        self.strain_percent = 0.0
            
        self.update_calculations()

    def update_calculations(self):
        try:
            self.base_resistance = 120.0 if self.res_120_rb.isChecked() else 350.0
            self.shunt_value = float(self.shunt_input.text() or 20000)
            self.gauge_factor = float(self.gf_input.text() or 2.0)
            self.active_gauges = 1 if self.gauge_1_rb.isChecked() else 2
            
            # The slider represents strain in percent (%)
            strain = self.strain_percent / 100.0  # e.g., 0.01 for 1%
            
            # Calculate actual resistances
            # R1 is always active
            self.r1 = self.base_resistance * (1.0 + self.gauge_factor * strain)
            if self.is_shunt_connected:
                self.r1 = (self.r1 * self.shunt_value) / (self.r1 + self.shunt_value)
            
            self.r2 = self.base_resistance
            
            if self.active_gauges == 2:
                # Assuming R3 is the second active gauge (half bridge)
                # In common half-bridge, R1 and R3 might be active
                # If R1 and R3 are in opposite arms, they add up.
                self.r3 = self.base_resistance * (1.0 + self.gauge_factor * strain)
            else:
                self.r3 = self.base_resistance
            
            self.r4 = self.base_resistance

            # Bridge Output: Vout/Vin = R3/(R2+R3) - R4/(R1+R4)
            vout_vin = (self.r3 / (self.r2 + self.r3)) - (self.r4 / (self.r1 + self.r4))
            # Convert to mV/V
            mv_v = vout_vin * 1000.0
            
            # Calculate Total Displayed Strain
            # If shunt is connected, it adds an equivalent strain: eps_eq = -Rg / (GF * (Rg + Rs))
            # We display the sum of slider strain and shunt induced strain
            total_strain_ratio = strain
            if self.is_shunt_connected:
                induced_strain = -self.base_resistance / (self.gauge_factor * (self.base_resistance + self.shunt_value))
                total_strain_ratio += induced_strain
            
            total_strain_percent = total_strain_ratio * 100.0
            self.total_strain_ratio = total_strain_ratio
            
            # Update labels or tooltips
            self.balance_label.setText(f"Bridge Output: {mv_v:.4f} mV/V | Strain: {total_strain_percent:.4f}%")
            
            # Update slider color
            self.update_slider_style(self.balance_slider.value())
            
            self.bridge_view.update()
            self.specimen_view.update()
        except ValueError:
            pass

    def update_slider_style(self, value):
        # We want the handle to stay grey.
        # The line between center and handle should change color.
        # QSS sub-controls: add-page and sub-page can be used, but they are relative to handle.
        # For a center-based color, we need a more complex QSS or a custom slider.
        # Since we use -1000 to 1000:
        # If value > 0: part between center and handle is green.
        # If value < 0: part between center and handle is red.
        
        # A simple trick with QSS sub-page/add-page works for 0..100 sliders.
        # For -X..X, it's harder with pure QSS.
        # Let's use a background gradient on the groove that "moves" or shifts.
        
        pct = (value + 1000) / 2000.0 * 100
        center_pct = 50.0
        
        if value > 0:
            # Green between 50% and pct%
            gradient = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, \
                stop:0 gray, stop:0.499 gray, \
                stop:0.5 green, stop:{pct/100.0} green, \
                stop:{pct/100.0 + 0.001} gray, stop:1 gray)"
        elif value < 0:
            # Red between pct% and 50%
            gradient = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, \
                stop:0 gray, stop:{pct/100.0} gray, \
                stop:{pct/100.0 + 0.001} red, stop:0.5 red, \
                stop:0.501 gray, stop:1 gray)"
        else:
            gradient = "gray"

        self.balance_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {gradient};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: lightgray;
                border: 1px solid #5c5c5c;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)

    def update_slider(self, value):
        # value is -1000 to 1000, representing -10.00% to 10.00%
        # strain_percent should be in % (so divide by 100)
        self.strain_percent = value / 100.0
        self.update_calculations()

    def update_specimen(self):
        try:
            self.specimen_width = float(self.spec_width_input.text() or 50)
            self.specimen_height = float(self.spec_height_input.text() or 150)
            self.gauge_length = float(self.gauge_length_input.text() or 80)
            self.specimen_view.update()
        except ValueError:
            pass

class BridgeCanvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent
        self.setMinimumSize(400, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        size = min(w, h) * 0.7
        half_size = size / 2

        # Nodes
        p_top = (cx, cy - half_size)
        p_right = (cx + half_size, cy)
        p_bottom = (cx, cy + half_size)
        p_left = (cx - half_size, cy)

        # Drawing Bridge Lines
        pen = QPen(Qt.GlobalColor.white, 2)
        painter.setPen(pen)
        
        # R1 (Top Left): p_top to p_left
        # R2 (Top Right): p_top to p_right
        # R3 (Bottom Right): p_bottom to p_right
        # R4 (Bottom Left): p_bottom to p_left
        
        # Logic from user: top left is R1, then clockwise, R2, R3 and R4
        # This implies:
        # R1: Top to Left? No, clockwise usually means Top to Right is next.
        # Let's follow: R1(TL), R2(TR), R3(BR), R4(BL)
        # R1: Node Top to Node Left? Let's check typical diamond.
        # Nodes: Excitation at Top/Bottom. Output at Left/Right.
        # R1 is between Top and Left.
        # R2 is between Top and Right.
        # R3 is between Bottom and Right.
        # R4 is between Bottom and Left.
        
        def draw_resistor(p1, p2, label, value, active=False, shunt=False):
            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2
            
            # Zig-zag or rectangle for resistor - slightly larger to avoid text touching
            rw, rh = 65, 30
            
            # Calculate angle
            angle = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
            
            # Flip text for R1 and R4 if they look upside down
            # R1 is TL: p_top to p_left. p2(left) is p1(top) + (-half, half)
            # R4 is BL: p_bottom to p_left. p2(left) is p1(bottom) + (-half, -half)
            # Let's check the angle. If angle is in range that makes text upside down, flip it.
            text_angle = angle
            if abs(text_angle) > 90:
                text_angle += 180

            painter.save()
            painter.translate(mid_x, mid_y)
            painter.rotate(text_angle)
            
            # Resistor body
            rect = QRectF(-rw/2, -rh/2, rw, rh)
            painter.setPen(QPen(QColor(0, 255, 0) if active else QColor(255, 255, 255), 2))
            painter.setBrush(QBrush(QColor(50, 50, 50)))
            painter.drawRect(rect)
            
            # Label and Value
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{label}\n{value:.1f}Ω")
            
            if shunt:
                # Draw a parallel line for shunt
                painter.setPen(QPen(QColor(255, 255, 0), 1, Qt.PenStyle.DashLine))
                painter.drawArc(int(-rw), int(-rh*1.5), int(rw*2), int(rh*3), 0, 180*16)
                painter.drawText(int(-rw/2), int(-rh*1.5), "Shunt")
            
            painter.restore()

        # Lines
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawLine(int(p_top[0]), int(p_top[1]), int(p_left[0]), int(p_left[1]))
        painter.drawLine(int(p_top[0]), int(p_top[1]), int(p_right[0]), int(p_right[1]))
        painter.drawLine(int(p_bottom[0]), int(p_bottom[1]), int(p_right[0]), int(p_right[1]))
        painter.drawLine(int(p_bottom[0]), int(p_bottom[1]), int(p_left[0]), int(p_left[1]))

        draw_resistor(p_top, p_left, "R1", self.app.r1, active=True, shunt=self.app.is_shunt_connected)
        draw_resistor(p_top, p_right, "R2", self.app.r2)
        draw_resistor(p_bottom, p_right, "R3", self.app.r3, active=(self.app.active_gauges == 2))
        draw_resistor(p_bottom, p_left, "R4", self.app.r4)

        # Excitation/Output indicators
        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        painter.drawText(int(p_top[0]-10), int(p_top[1]-10), "V+")
        painter.drawText(int(p_bottom[0]-10), int(p_bottom[1]+20), "V-")
        
        painter.setPen(QPen(Qt.GlobalColor.cyan, 2))
        painter.drawText(int(p_left[0]-30), int(p_left[1]), "Out-")
        painter.drawText(int(p_right[0]+5), int(p_right[1]), "Out+")

class SpecimenCanvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent
        self.setMinimumSize(200, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        from PyQt6.QtGui import QLinearGradient
        
        w, h = self.width(), self.height()
        
        # Current dimensions based on strain
        strain = self.app.total_strain_ratio
        # Poisson's ratio assumption (e.g. 0.3)
        nu = 0.3
        
        # Dimensions under strain
        current_h_val = self.app.specimen_height * (1 + strain)
        current_w_val = self.app.specimen_width * (1 - nu * strain)
        current_gl_val = self.app.gauge_length * (1 + strain)
        
        # Scale to fit
        # Use initial dimensions to keep the view stable relative to window
        max_theoretical_h = self.app.specimen_height * 1.2
        scale = min(w * 0.8 / self.app.specimen_width if self.app.specimen_width > 0 else 1,
                    h * 0.8 / max_theoretical_h if max_theoretical_h > 0 else 1)
        
        sw = current_w_val * scale
        sh = current_h_val * scale
        sgl = current_gl_val * scale
        
        rect = QRectF((w - sw) / 2, (h - sh) / 2, sw, sh)
        
        # Cylindrical Shading (Linear Gradient)
        # Suggestion: Darker at edges, lighter highlight in the center
        gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
        base_color = QColor(100, 100, 100)
        edge_color = QColor(40, 40, 40)
        highlight_color = QColor(200, 200, 220)
        
        # Add subtle tint based on strain (optional logic could go here)
        # Red/Green tint could be added to highlight_color
        
        gradient.setColorAt(0.0, edge_color)
        gradient.setColorAt(0.2, base_color)
        gradient.setColorAt(0.5, highlight_color)
        gradient.setColorAt(0.8, base_color)
        gradient.setColorAt(1.0, edge_color)
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(rect)
        
        # Draw Gauge Length (Blue lines) - they move with strain
        if sgl > 0:
            painter.setPen(QPen(QColor(0, 150, 255), 3))
            y1 = h/2 - sgl/2
            y2 = h/2 + sgl/2
            painter.drawLine(int((w-sw)/2), int(y1), int((w+sw)/2), int(y1))
            painter.drawLine(int((w-sw)/2), int(y2), int((w+sw)/2), int(y2))
            
            # Label moves with the marker
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(int((w+sw)/2 + 10), int(h/2), f"GL: {current_gl_val:.2f}mm")
        
        # Add dimension labels
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        # Top width label
        painter.drawText(int(w/2 - 30), int((h-sh)/2 - 10), f"W: {current_w_val:.2f}mm")
        
        # Vertical height label
        painter.save()
        painter.translate((w-sw)/2 - 15, h/2)
        painter.rotate(-90)
        painter.drawText(0, 0, f"H: {current_h_val:.2f}mm")
        painter.restore()

def main():
    app = QApplication(sys.argv)
    # Apply a dark theme or consistent style if needed
    ex = WheatstoneBridgeApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
