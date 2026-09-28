# ui_views.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QGroupBox, QSizePolicy, QLineEdit, QGridLayout
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

        # Left Column - Frame Display Panel
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

        # Right Column - Compact Grid Panel Layout
        control_panel = QVBoxLayout()
        control_panel.setSpacing(4)

        # Histogram Panel
        hist_group = QGroupBox("Histogram")
        hist_layout = QVBoxLayout(hist_group)
        self.histogram = HistogramWidget()
        hist_layout.addWidget(self.histogram)
        control_panel.addWidget(hist_group)

        # Action Buttons Grid
        tools_group = QGroupBox("Toolbox Actions")
        tools_grid = QGridLayout(tools_group)
        tools_grid.setSpacing(4)
        
        self.btn_rotate = QPushButton("⟳ Rotate")
        self.btn_rotate.setStyleSheet("background-color: #3a3a3a; font-weight: bold; padding: 6px;")
        self.btn_rotate.clicked.connect(on_rotate)
        tools_grid.addWidget(self.btn_rotate, 0, 0)

        self.btn_commit_crop = QPushButton("✂️ Crop")
        self.btn_commit_crop.setCheckable(True)
        self.btn_commit_crop.setStyleSheet("background-color: #e65100; font-weight: bold; padding: 6px;")
        self.btn_commit_crop.clicked.connect(on_commit_crop)
        tools_grid.addWidget(self.btn_commit_crop, 0, 1)

        self.btn_invert = QPushButton("🔄 Invert")
        self.btn_invert.setCheckable(True)
        self.btn_invert.setChecked(True)
        self.btn_invert.setStyleSheet("background-color: #007acc; font-weight: bold; padding: 6px;")
        self.btn_invert.clicked.connect(on_invert_toggle)
        tools_grid.addWidget(self.btn_invert, 0, 2)

        self.btn_mono = QPushButton("⚫ Monochrome")
        self.btn_mono.setCheckable(True)
        self.btn_mono.setStyleSheet("background-color: #3a3a3a; font-weight: bold; padding: 6px;")
        self.btn_mono.clicked.connect(on_mono_toggle)
        tools_grid.addWidget(self.btn_mono, 1, 0)

        self.btn_auto = QPushButton("✨ Auto")
        self.btn_auto.setStyleSheet("background-color: #2e7d32; font-weight: bold; padding: 6px;")
        self.btn_auto.clicked.connect(on_auto)
        tools_grid.addWidget(self.btn_auto, 1, 1)

        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setStyleSheet("background-color: #c62828; font-weight: bold; padding: 6px;")
        self.btn_reset.clicked.connect(on_reset)
        tools_grid.addWidget(self.btn_reset, 1, 2)

        control_panel.addWidget(tools_group)

        # 4-Sided Symmetrical Crop Slicing Grid
        crop_group = QGroupBox("Mask Slicing Trim")
        crop_grid = QGridLayout(crop_group)
        crop_grid.setVerticalSpacing(2)
        crop_grid.setHorizontalSpacing(8)
        
        self.sld_crop_t = self.create_grid_slider_row(crop_grid, "Top", 0, 0, 0, 45, default_val=0)
        self.sld_crop_b = self.create_grid_slider_row(crop_grid, "Bottom", 0, 1, 0, 45, default_val=0)
        self.sld_crop_l = self.create_grid_slider_row(crop_grid, "Left", 1, 0, 0, 45, default_val=0)
        self.sld_crop_r = self.create_grid_slider_row(crop_grid, "Right", 1, 1, 0, 45, default_val=0)
        
        for sld in [self.sld_crop_t, self.sld_crop_b, self.sld_crop_l, self.sld_crop_r]:
            sld.valueChanged.connect(on_slider_change)
        control_panel.addWidget(crop_group)

        # Color Space Matrices Adjustments Grid
        slider_group = QGroupBox("Color Tuning & Processing Matrix")
        slider_grid = QGridLayout(slider_group)
        slider_grid.setVerticalSpacing(4)
        slider_grid.setHorizontalSpacing(8)
        
        self.sld_cr = self.create_grid_slider_row(slider_grid, "Cyan ◄─► Red", 0, 0, -100, 100, "Q/A")
        self.sld_mg = self.create_grid_slider_row(slider_grid, "Magenta ◄─► Green", 1, 0, -100, 100, "W/S")
        self.sld_yb = self.create_grid_slider_row(slider_grid, "Yellow ◄─► Blue", 2, 0, -100, 100, "E/D")
        self.sld_exp = self.create_grid_slider_row(slider_grid, "Exposure (Key)", 3, 0, -100, 100, "R/F")
        self.sld_contrast = self.create_grid_slider_row(slider_grid, "Contrast Scalar", 4, 0, -100, 100, "T/G")
        
        for sld in [self.sld_cr, self.sld_mg, self.sld_yb, self.sld_exp, self.sld_contrast]:
            sld.valueChanged.connect(on_slider_change)
        control_panel.addWidget(slider_group)

        # Exporter Panel
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

    def create_grid_slider_row(self, grid, label_text, row, col, min_v, max_v=100, shortcut_hint=None, default_val=0):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(1)
        
        header_text = f"{label_text} [{shortcut_hint}]" if shortcut_hint else label_text
        lbl = QLabel(header_text)
        lbl.setStyleSheet("color: #cccccc; font-size: 11px; font-weight: bold;")
        
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(min_v, max_v)
        sld.setValue(default_val)
        sld.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        layout.addWidget(lbl)
        layout.addWidget(sld)
        
        grid.addWidget(container, row, col)
        return sld