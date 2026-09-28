from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QGroupBox, QSizePolicy, QLineEdit, QGridLayout
)
from ui_widgets import InteractiveCanvas, HistogramWidget

class WorkspaceView(QWidget):
    def __init__(self, on_prev, on_next, on_slider_change, on_auto, on_reset, on_mono_toggle, on_invert_toggle, on_browse_output, on_export, on_rotate, on_commit_crop):
        super().__init__()
        main_layout = QHBoxLayout(self)

        # Left Column - Display Panel
        canvas_panel = QVBoxLayout()
        self.lbl_canvas = InteractiveCanvas()
        self.lbl_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_canvas.setMinimumSize(400, 400) 
        canvas_panel.addWidget(self.lbl_canvas, stretch=5)

        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_next = QPushButton("Next ▶")
        self.btn_prev.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_next.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        nav_btn_style = "background-color: #222222; color: #cccccc; border: 1px solid #333333; padding: 8px; font-weight: bold; border-radius: 4px;"
        self.btn_prev.setStyleSheet(nav_btn_style)
        self.btn_next.setStyleSheet(nav_btn_style)
        
        self.btn_prev.clicked.connect(on_prev)
        self.btn_next.clicked.connect(on_next)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        canvas_panel.addLayout(nav_layout, stretch=0)
        main_layout.addLayout(canvas_panel, stretch=7)

        # Right Column - Dark Charcoal Control Sidebar
        control_panel = QVBoxLayout()
        control_panel.setSpacing(4)

        # Histogram Panel
        hist_group = QGroupBox("Histogram")
        hist_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; }")
        hist_layout = QVBoxLayout(hist_group)
        self.histogram = HistogramWidget()
        hist_layout.addWidget(self.histogram)
        control_panel.addWidget(hist_group)

        # Action Buttons Uniform Grid
        tools_group = QGroupBox("Toolbox Actions")
        tools_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; }")
        tools_grid = QGridLayout(tools_group)
        tools_grid.setSpacing(4)
        
        uniform_btn_style = "background-color: #2b2b2b; color: #dddddd; border: 1px solid #3d3d3d; font-weight: bold; padding: 6px; border-radius: 4px;"
        
        self.btn_rotate = QPushButton("⟳ Rotate")
        self.btn_rotate.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_rotate.setStyleSheet(uniform_btn_style)
        self.btn_rotate.clicked.connect(on_rotate)
        tools_grid.addWidget(self.btn_rotate, 0, 0)

        self.btn_commit_crop = QPushButton("✂️ Crop")
        self.btn_commit_crop.setCheckable(True)
        self.btn_commit_crop.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_commit_crop.setStyleSheet(uniform_btn_style)
        self.btn_commit_crop.clicked.connect(on_commit_crop)
        tools_grid.addWidget(self.btn_commit_crop, 0, 1)

        self.btn_invert = QPushButton("🔄 Invert")
        self.btn_invert.setCheckable(True)
        self.btn_invert.setChecked(True)
        self.btn_invert.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_invert.setStyleSheet(uniform_btn_style)
        self.btn_invert.clicked.connect(on_invert_toggle)
        tools_grid.addWidget(self.btn_invert, 0, 2)

        self.btn_mono = QPushButton("⚫ Monochrome")
        self.btn_mono.setCheckable(True)
        self.btn_mono.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_mono.setStyleSheet(uniform_btn_style)
        self.btn_mono.clicked.connect(on_mono_toggle)
        tools_grid.addWidget(self.btn_mono, 1, 0)

        self.btn_auto = QPushButton("✨ Auto")
        self.btn_auto.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_auto.setStyleSheet(uniform_btn_style)
        self.btn_auto.clicked.connect(on_auto)
        tools_grid.addWidget(self.btn_auto, 1, 1)

        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_reset.setStyleSheet(uniform_btn_style)
        self.btn_reset.clicked.connect(on_reset)
        tools_grid.addWidget(self.btn_reset, 1, 2)

        control_panel.addWidget(tools_group)

        # 4-Sided Mask Trim Pair Grid
        crop_group = QGroupBox("Mask Slicing Trim")
        crop_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; }")
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
        slider_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; }")
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
        export_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; }")
        export_layout = QVBoxLayout(export_group)
        path_layout = QHBoxLayout()
        
        self.txt_output_path = QLineEdit()
        self.txt_output_path.setReadOnly(True)
        self.txt_output_path.setStyleSheet("background-color: #1a1a1a; color: #aaaaaa; border: 1px solid #333333; padding: 4px; border-radius: 4px;")
        
        self.btn_browse_output = QPushButton("...")
        self.btn_browse_output.setFixedWidth(30)
        self.btn_browse_output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_browse_output.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #444444; border-radius: 4px; padding: 4px;")
        self.btn_browse_output.clicked.connect(on_browse_output)
        path_layout.addWidget(self.txt_output_path)
        path_layout.addWidget(self.btn_browse_output)
        export_layout.addLayout(path_layout)
        
        self.btn_export = QPushButton("💾 Save Positive Image [Enter]")
        self.btn_export.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_export.setStyleSheet("background-color: #333333; color: #ffffff; border: 1px solid #555555; font-weight: bold; padding: 10px; border-radius: 4px;")
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
        lbl.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold;")
        
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(min_v, max_v)
        sld.setValue(default_val)
        sld.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sld.setStyleSheet(
            "QSlider::groove:horizontal { height: 4px; background: #333333; border-radius: 2px; }"
            "QSlider::handle:horizontal { background: #888888; width: 12px; margin-top: -4px; margin-bottom: -4px; border-radius: 6px; }"
        )
        
        layout.addWidget(lbl)
        layout.addWidget(sld)
        grid.addWidget(container, row, col)
        return sld