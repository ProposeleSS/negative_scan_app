from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QGroupBox, QSizePolicy, QLineEdit
)
from ui_widgets import InteractiveCanvas, HistogramWidget

class WizardView(QWidget):
    def __init__(self, on_folder_click):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Film Scanning Setup Wizard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.btn_dslr = QPushButton("📷 Capture via USB DSLR (Inactive)")
        self.btn_dslr.setFixedSize(350, 50)
        self.btn_dslr.setEnabled(False)
        self.btn_dslr.setStyleSheet("background-color: #3d3d3d; color: #888888; border-radius: 5px;")
        layout.addWidget(self.btn_dslr)

        self.btn_folder = QPushButton("📁 Open Folder with RAW Files")
        self.btn_folder.setFixedSize(350, 50)
        self.btn_folder.setStyleSheet("font-weight: bold; background-color: #007acc; color: white; border-radius: 5px;")
        self.btn_folder.clicked.connect(on_folder_click)
        layout.addWidget(self.btn_folder)

        self.lbl_status = QLabel("Select an input source to begin your scanning session.")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaaaaa; font-style: italic;")
        layout.addWidget(self.lbl_status)


class WorkspaceView(QWidget):
    def __init__(self, on_prev, on_next, on_slider_change, on_auto, on_reset, on_mono_toggle, on_invert_toggle, on_browse_output, on_export, on_rotate, on_commit_crop):
        super().__init__()
        main_layout = QHBoxLayout(self)

        canvas_panel = QVBoxLayout()
        self.lbl_canvas = InteractiveCanvas()
        self.lbl_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_canvas.setMinimumSize(400, 400) 
        canvas_panel.addWidget(self.lbl_canvas, stretch=5)

        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_next = QPushButton("Next ▶")
        self.btn_prev.clicked.connect(on_prev)
        self.btn_next.clicked.connect(on_next)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        canvas_panel.addLayout(nav_layout, stretch=0)
        main_layout.addLayout(canvas_panel, stretch=7)

        control_panel = QVBoxLayout()
        control_panel.setSpacing(4)

        hist_group = QGroupBox("Live Processing Histogram")
        hist_layout = QVBoxLayout(hist_group)
        self.histogram = HistogramWidget()
        hist_layout.addWidget(self.histogram)
        control_panel.addWidget(hist_group)

        crop_group = QGroupBox("Four-Edge Frame Mask")
        crop_layout = QVBoxLayout(crop_group)
        self.sld_crop_t = self.create_slider_row(crop_layout, "Top Trim", 0, 45)
        self.sld_crop_b = self.create_slider_row(crop_layout, "Bottom Trim", 0, 45)
        self.sld_crop_l = self.create_slider_row(crop_layout, "Left Trim", 0, 45)
        self.sld_crop_r = self.create_slider_row(crop_layout, "Right Trim", 0, 45)
        control_panel.addWidget(crop_group)

        # Orientation Layout Sheet (NEW: Integrated Commit Crop View trigger)
        trans_group = QGroupBox("Orientation & Crop Commitment")
        trans_layout = QVBoxLayout(trans_group)
        
        self.btn_rotate = QPushButton("⟳ Rotate 90°")
        self.btn_rotate.setStyleSheet("background-color: #5c2d91; color: white; font-weight: bold; padding: 4px;")
        self.btn_rotate.clicked.connect(on_rotate)
        trans_layout.addWidget(self.btn_rotate)

        self.btn_commit_crop = QPushButton("✂️ Commit Crop View: Unlocked")
        self.btn_commit_crop.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 5px;")
        self.btn_commit_crop.clicked.connect(on_commit_crop)
        trans_layout.addWidget(self.btn_commit_crop)

        self.btn_invert = QPushButton("🔄 Invert: Active")
        self.btn_invert.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 4px;")
        self.btn_invert.clicked.connect(on_invert_toggle)
        trans_layout.addWidget(self.btn_invert)

        self.btn_mono = QPushButton("🌈 Mode: Full Color")
        self.btn_mono.setStyleSheet("background-color: #3a3a3a; font-weight: bold; padding: 4px;")
        self.btn_mono.clicked.connect(on_mono_toggle)
        trans_layout.addWidget(self.btn_mono)
        control_panel.addWidget(trans_group)

        slider_group = QGroupBox("Color Correction & Contrast")
        slider_layout = QVBoxLayout(slider_group)
        self.sld_cr = self.create_slider_row(slider_layout, "Cyan ◄─► Red [Q/A]", -100, 100)
        self.sld_mg = self.create_slider_row(slider_layout, "Magenta ◄─► Green [W/S]", -100, 100)
        self.sld_yb = self.create_slider_row(slider_layout, "Yellow ◄─► Blue [E/D]", -100, 100)
        self.sld_exp = self.create_slider_row(slider_layout, "Exposure (Key) [R/F]", -100, 100)
        
        # UPDATED: Extended parameter scale boundary configuration
        self.sld_contrast = self.create_slider_row(slider_layout, "Contrast Scalar [T/G]", -100, 100)
        
        for sld in [self.sld_cr, self.sld_mg, self.sld_yb, self.sld_exp, self.sld_contrast]:
            sld.valueChanged.connect(on_slider_change)
        control_panel.addWidget(slider_group)

        btn_layout = QHBoxLayout()
        self.btn_auto = QPushButton("✨ Auto")
        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_auto.setStyleSheet("background-color: #2e7d32; font-weight: bold; padding: 6px;")
        self.btn_reset.setStyleSheet("background-color: #c62828; padding: 6px;")
        self.btn_auto.clicked.connect(on_auto)
        self.btn_reset.clicked.connect(on_reset)
        btn_layout.addWidget(self.btn_auto)
        btn_layout.addWidget(self.btn_reset)
        control_panel.addLayout(btn_layout)

        export_group = QGroupBox("Output Folder & Export")
        export_layout = QVBoxLayout(export_group)
        path_layout = QHBoxLayout()
        self.txt_output_path = QLineEdit()
        self.txt_output_path.setReadOnly(True)
        self.btn_browse_output = QPushButton("...")
        self.btn_browse_output.setFixedWidth(30)
        self.btn_browse_output.clicked.connect(on_browse_output)
        path_layout.addWidget(self.txt_output_path)
        path_layout.addWidget(self.btn_browse_output)
        export_layout.addLayout(path_layout)
        
        self.btn_export = QPushButton("💾 Save Positive Image")
        self.btn_export.setStyleSheet("background-color: #ff8c00; color: black; font-weight: bold; padding: 8px;")
        self.btn_export.clicked.connect(on_export)
        export_layout.addWidget(self.btn_export)
        control_panel.addWidget(export_group)

        control_panel.addStretch()
        main_layout.addLayout(control_panel, stretch=3)

    def create_slider_row(self, layout, text, min_v=0, max_v=100):
        lbl = QLabel(text)
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(min_v, max_v)
        sld.setValue(0)
        sld.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(lbl)
        layout.addWidget(sld)
        return sld