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

        # Camera Control Properties
        self.camera_thread = None

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
        
        # Wire up Camera Scanner initiation hook on Wizard View
        self.wizard.btn_dslr.setEnabled(True)
        self.wizard.btn_dslr.setText("📷 Start Camera Scanner Mode")
        self.wizard.btn_dslr.clicked.connect(self.start_camera_session)

        self.workspace.lbl_canvas.cropChanged.connect(self.handle_mouse_crop_ui_only)
        self.workspace.lbl_canvas.cropReleased.connect(self.update_pipeline)
        self.workspace.lbl_canvas.baseClicked.connect(self.handle_mouse_pipette_click)

        for sld in [self.workspace.sld_crop_t, self.workspace.sld_crop_b, self.workspace.sld_crop_l, self.workspace.sld_crop_r]:
            sld.valueChanged.connect(self.update_pipeline)

        self.stack.addWidget(self.wizard)
        self.stack.addWidget(self.workspace)
        self.stack.setCurrentIndex(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.showMaximized()

    def handle_mouse_pipette_click(self, x, y):
        """Runs Gaussian-filtered mask cancellation centered precisely on the user's click coordinate."""
        if hasattr(self.engine, 'calibrate_base_from_point') and self.engine.calibrate_base_from_point(click_x=x, click_y=y):
            UIHelpers.toggle_all_sliders(self, False)
            for sld in [self.workspace.sld_cr, self.workspace.sld_mg, self.workspace.sld_yb, self.workspace.sld_exp]:
                sld.setValue(0)
            UIHelpers.toggle_all_sliders(self, True)
            self.statusBar().showMessage(f"🧪 Film Base Calibrated via Mouse Click at ({x}, {y})", 3000)
            self.update_pipeline()

    def keyPressEvent(self, event):
        if not AppHandlers.handle_keypress(self, event): super().keyPressEvent(event)

    def open_folder_dialog(self):
        AppHandlers.execute_folder_scan(self)

    def start_camera_session(self):
        """Initializes target session folders and spawns the background USB gphoto2 daemon."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select/Create Live Scan Session Folder")
        if not dir_path: return
            
        self.output_directory = os.path.join(dir_path, "converted_positives")
        self.workspace.txt_output_path.setText(self.output_directory)
        self.file_list = []
        
        from camera_worker import CameraWorker
        self.camera_thread = CameraWorker(target_download_dir=dir_path)
        self.camera_thread.status_updated.connect(lambda msg: self.statusBar().showMessage(msg, 5000))
        self.camera_thread.image_captured.connect(self.handle_incoming_camera_frame)
        self.camera_thread.start()
        
        self.stack.setCurrentIndex(1)
        self.statusBar().showMessage("📷 Camera Stream Initialized. Press Spacebar to Scan Frame.", 4000)

    def trigger_hardware_capture(self):
        """Dispatches shutter triggers to modern cameras or updates watcher profiles on older units."""
        if self.camera_thread and self.camera_thread.isRunning():
            self.statusBar().showMessage("📸 Triggering shutter capture sequence over USB...", 2000)
            self.camera_thread.trigger_usb_shutter()
        else:
            self.statusBar().showMessage("⚠️ Active camera daemon is not initialized or running.", 3000)

    def handle_incoming_camera_frame(self, filepath):
        """Callback executed whenever a new RAW file lands safely on the local hard drive."""
        filepath_str = str(filepath)
        if filepath_str not in self.file_list:
            self.file_list.append(filepath_str)
            self.file_list.sort()
            self.current_idx = self.file_list.index(filepath_str)
            self.display_current_image()
            self.statusBar().showMessage(f"✨ Fresh Frame Loaded: {os.path.basename(filepath_str)}", 3000)

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
            # SUCCESS CALLBACK PATCH: Trigger the explicit overlay toast alert
            UIHelpers.show_flash_notification(self, f" Saved: {filename_without_ext}_positive.png")

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
            if hist_arrays: self.workspace.histogram.update_data(hist_arrays)

    def render_to_canvas(self, bgr_array):
        w_canvas = max(self.workspace.lbl_canvas.width() - 10, 100)
        h_canvas = max(self.workspace.lbl_canvas.height() - 10, 100)
        h, w, ch = bgr_array.shape
        img_bytes = bgr_array.tobytes()
        qt_img = QImage(img_bytes, w, h, ch * w, QImage.Format.Format_BGR888)
        self.workspace.lbl_canvas.setPixmap(QPixmap.fromImage(qt_img).scaled(w_canvas, h_canvas, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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