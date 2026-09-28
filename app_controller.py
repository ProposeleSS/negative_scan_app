# app_controller.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QFileDialog
from PyQt6.QtGui import QImage, QPixmap

from engine import ImageEngine
from ui import WizardView, WorkspaceView
from app_handlers import AppHandlers
from app_ui_helpers import UIHelpers
from app_actions import AppActions

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenFilmScan")

        self.engine = ImageEngine()
        self.file_list, self.current_idx, self.output_directory = [], -1, ""

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.workspace = WorkspaceView(
            on_prev=lambda: self.navigate_image(-1), on_next=lambda: self.navigate_image(1),
            on_slider_change=self.update_pipeline, on_auto=lambda: AppActions.execute_auto_balance(self),
            on_reset=lambda: AppActions.execute_reset(self), on_mono_toggle=lambda: AppActions.toggle_monochrome(self),
            on_invert_toggle=lambda: AppActions.toggle_inversion(self), on_browse_output=self.browse_output_directory,
            on_export=self.export_processed_file, on_rotate=self.trigger_image_rotation,
            on_commit_crop=lambda: AppActions.toggle_crop_view(self)
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
        if self.engine.export_full_resolution(
            save_path, self.workspace.sld_cr.value(), self.workspace.sld_mg.value(),
            self.workspace.sld_yb.value(), self.workspace.sld_exp.value(), self.workspace.sld_contrast.value(),
            self.workspace.sld_crop_t.value(), self.workspace.sld_crop_b.value(),
            self.workspace.sld_crop_l.value(), self.workspace.sld_crop_r.value()
        ):
            self.statusBar().showMessage(f"Saved: {filename_without_ext}_positive.png", 2000)

    def display_current_image(self):
        if 0 <= self.current_idx < len(self.file_list):
            previous_crop_state = self.engine.is_crop_committed
            if self.engine.load_file(self.file_list[self.current_idx]):
                self.engine.is_crop_committed = previous_crop_state
                self.update_pipeline()

    def navigate_image(self, direction):
        new_idx = self.current_idx + direction
        if 0 <= new_idx < len(self.file_list):
            self.current_idx = new_idx
            self.display_current_image()

    def trigger_image_rotation(self):
        self.engine.rotate_image()
        self.update_pipeline()

    def update_pipeline(self):
        # Pass variables into the optimized, high-speed preview matrix handler
        img_array = self.engine.process_preview_frame(
            self.workspace.sld_cr.value(), self.workspace.sld_mg.value(),
            self.workspace.sld_yb.value(), self.workspace.sld_exp.value(),
            contrast=self.workspace.sld_contrast.value(),
            crop_t=self.workspace.sld_crop_t.value(), crop_b=self.workspace.sld_crop_b.value(),
            crop_l=self.workspace.sld_crop_l.value(), crop_r=self.workspace.sld_crop_r.value()
        )
        if img_array is not None:
            self.render_to_canvas(img_array)
            hist_arrays = self.engine.get_histogram_arrays()
            if hist_arrays: 
                self.workspace.histogram.update_data(hist_arrays)

    def render_to_canvas(self, bgr_array):
        w_canvas = max(self.workspace.lbl_canvas.width() - 10, 100)
        h_canvas = max(self.workspace.lbl_canvas.height() - 10, 100)
        
        # Extract explicit scalar dimensions from the incoming frame array shape
        h, w, ch = bgr_array.shape
        img_bytes = bgr_array.tobytes()
        
        # Safely construct the QImage using exact continuous integers
        qt_img = QImage(img_bytes, w, h, ch * w, QImage.Format.Format_BGR888)
        
        scaled_pixmap = QPixmap.fromImage(qt_img).scaled(
            w_canvas, h_canvas, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.workspace.lbl_canvas.setPixmap(scaled_pixmap)
        
        # Repaint orange bounding crop guides overlay only if not zoomed/committed
        if not self.engine.is_crop_committed:
            self.workspace.lbl_canvas.update_crop_metrics(
                self.workspace.sld_crop_t.value(), self.workspace.sld_crop_b.value(),
                self.workspace.sld_crop_l.value(), self.workspace.sld_crop_r.value()
            )
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.engine.processed_preview is not None:
            if self.engine.is_crop_committed and self.engine.processed_roi is not None: self.render_to_canvas(self.engine.processed_roi)
            else: self.render_to_canvas(self.engine.processed_preview)