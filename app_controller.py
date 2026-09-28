# app_controller.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QFileDialog
from PyQt6.QtGui import QImage, QPixmap

from engine import ImageEngine
from ui import WizardView, WorkspaceView
from app_handlers import AppHandlers
from app_ui_helpers import UIHelpers

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenFilmScan")

        self.engine = ImageEngine()
        self.file_list = []
        self.current_idx = -1
        self.output_directory = ""

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.workspace = WorkspaceView(
            on_prev=lambda: self.navigate_image(-1), on_next=lambda: self.navigate_image(1),
            on_slider_change=self.update_pipeline, on_auto=self.trigger_auto_balance,
            on_reset=self.trigger_reset, on_mono_toggle=self.toggle_monochrome_mode,
            on_invert_toggle=self.toggle_inversion_mode, on_browse_output=self.browse_output_directory,
            on_export=self.export_processed_file, on_rotate=self.trigger_image_rotation,
            on_commit_crop=self.toggle_crop_view_commitment
        )
        self.wizard = WizardView(on_folder_click=self.open_folder_dialog)

        self.workspace.lbl_canvas.cropChanged.connect(self.handle_mouse_crop_ui_only)
        self.workspace.lbl_canvas.cropReleased.connect(self.update_pipeline)

        for sld in [self.workspace.sld_crop_t, self.workspace.sld_crop_b, self.workspace.sld_crop_l, self.workspace.sld_crop_r]:
            sld.valueChanged.connect(self.update_pipeline)

        self.stack.addWidget(self.wizard)
        self.stack.addWidget(self.workspace)
        self.stack.setCurrentIndex(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.showMaximized()

    def keyPressEvent(self, event):
        if not AppHandlers.handle_keypress(self, event): super().keyPressEvent(event)

    def open_folder_dialog(self):
        AppHandlers.execute_folder_scan(self)

    def handle_mouse_crop_ui_only(self, edge, value):
        UIHelpers.toggle_all_sliders(self, False)
        if edge == "top": self.workspace.sld_crop_t.setValue(value)
        elif edge == "bottom": self.workspace.sld_crop_b.setValue(value)
        elif edge == "left": self.workspace.sld_crop_l.setValue(value)
        elif edge == "right": self.workspace.sld_crop_r.setValue(value)
        UIHelpers.toggle_all_sliders(self, True)
        
        self.workspace.lbl_canvas.update_crop_metrics(
            self.workspace.sld_crop_t.value(), self.workspace.sld_crop_b.value(),
            self.workspace.sld_crop_l.value(), self.workspace.sld_crop_r.value()
        )

    def browse_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_directory = dir_path
            self.workspace.txt_output_path.setText(self.output_directory)

    def export_processed_file(self):
        if not self.output_directory or self.current_idx == -1: return
        os.makedirs(self.output_directory, exist_ok=True)
        filename_without_ext, _ = os.path.splitext(os.path.basename(self.file_list[self.current_idx]))
        save_path = os.path.join(self.output_directory, f"{filename_without_ext}_positive.png")
        if self.engine.export_current_image(save_path):
            self.statusBar().showMessage(f"Saved: {filename_without_ext}_positive.png", 2000)

    def display_current_image(self):
        if 0 <= self.current_idx < len(self.file_list):
            # 1. Store the active crop view commitment state before loading the new file
            previous_crop_state = self.engine.is_crop_committed
            
            if self.engine.load_file(self.file_list[self.current_idx]):
                # 2. Force the engine to carry the view state over to the new image asset
                self.engine.is_crop_committed = previous_crop_state
                
                # 3. Process and push updates to the canvas layout
                self.update_pipeline()

    def navigate_image(self, direction):
        new_idx = self.current_idx + direction
        if 0 <= new_idx < len(self.file_list):
            self.current_idx = new_idx
            self.display_current_image()

    def trigger_image_rotation(self):
        self.engine.rotate_image()
        self.update_pipeline()

    def toggle_crop_view_commitment(self):
        self.engine.is_crop_committed = not self.engine.is_crop_committed
        if self.engine.is_crop_committed:
            self.workspace.btn_commit_crop.setText("✂️ Commit Crop View: ZOOMED")
            self.workspace.btn_commit_crop.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 5px;")
            self.workspace.lbl_canvas.hide_overlay_lines = True
        else:
            self.workspace.btn_commit_crop.setText("✂️ Commit Crop View: Unlocked")
            self.workspace.btn_commit_crop.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 5px;")
            self.workspace.lbl_canvas.hide_overlay_lines = False
        self.update_pipeline()

    def update_pipeline(self):
        img_array = self.engine.run_pipeline(
            self.workspace.sld_cr.value(), self.workspace.sld_mg.value(),
            self.workspace.sld_yb.value(), self.workspace.sld_exp.value(),
            contrast=self.workspace.sld_contrast.value(),
            crop_t=self.workspace.sld_crop_t.value(), crop_b=self.workspace.sld_crop_b.value(),
            crop_l=self.workspace.sld_crop_l.value(), crop_r=self.workspace.sld_crop_r.value()
        )
        if img_array is not None:
            self.render_to_canvas(img_array)
            hist_arrays = self.engine.get_histogram_arrays()
            if hist_arrays: self.workspace.histogram.update_data(hist_arrays)

    def render_to_canvas(self, bgr_array):
        w_canvas = max(self.workspace.lbl_canvas.width() - 10, 100)
        h_canvas = max(self.workspace.lbl_canvas.height() - 10, 100)
        h, w, ch = bgr_array.shape
        
        # FIX: Ensure memory is flat and continuous by passing native bytes
        img_bytes = bgr_array.tobytes()
        
        from PyQt6.QtGui import QImage, QPixmap
        qt_img = QImage(img_bytes, w, h, ch * w, QImage.Format.Format_BGR888)
        
        scaled_pixmap = QPixmap.fromImage(qt_img).scaled(
            w_canvas, h_canvas, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.workspace.lbl_canvas.setPixmap(scaled_pixmap)
        
        if not self.engine.is_crop_committed:
            self.workspace.lbl_canvas.update_crop_metrics(
                self.workspace.sld_crop_t.value(), self.workspace.sld_crop_b.value(),
                self.workspace.sld_crop_l.value(), self.workspace.sld_crop_r.value()
            )

    def toggle_inversion_mode(self):
        self.engine.is_inverted = not self.engine.is_inverted
        self.workspace.btn_invert.setText("🔄 Invert: Active" if self.engine.is_inverted else "⏹️ Invert: Passthrough")
        self.update_pipeline()

    def toggle_monochrome_mode(self):
        self.engine.is_monochrome = not self.engine.is_monochrome
        self.workspace.btn_mono.setText("⚫ Mode: Monochrome (B&W)" if self.engine.is_monochrome else "🌈 Mode: Full Color")
        self.update_pipeline()

    def trigger_auto_balance(self):
        dr, dg, db = self.engine.calculate_grey_world_offsets()
        UIHelpers.toggle_all_sliders(self, False)
        self.workspace.sld_cr.setValue(max(-100, min(dr, 100)))
        self.workspace.sld_mg.setValue(max(-100, min(dg, 100)))
        self.workspace.sld_yb.setValue(max(-100, min(db, 100)))
        self.workspace.sld_exp.setValue(0)
        UIHelpers.toggle_all_sliders(self, True)
        self.update_pipeline()

    def trigger_reset(self):
        UIHelpers.toggle_all_sliders(self, False)
        self.engine.is_crop_committed = False
        self.workspace.btn_commit_crop.setText("✂️ Commit Crop View: Unlocked")
        self.workspace.btn_commit_crop.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 5px;")
        self.workspace.lbl_canvas.hide_overlay_lines = False
        for sld in [self.workspace.sld_crop_t, self.workspace.sld_crop_b, self.workspace.sld_crop_l, self.workspace.sld_crop_r,
                    self.workspace.sld_cr, self.workspace.sld_mg, self.workspace.sld_yb, self.workspace.sld_exp, self.workspace.sld_contrast]:
            sld.setValue(0)
        UIHelpers.toggle_all_sliders(self, True)
        self.update_pipeline()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.engine.processed_full_view is not None:
            if self.engine.is_crop_committed and self.engine.processed_img is not None: self.render_to_canvas(self.engine.processed_img)
            else: self.render_to_canvas(self.engine.processed_full_view)