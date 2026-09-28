import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QFileDialog, QMessageBox
from PyQt6.QtGui import QImage, QPixmap

from engine import ImageEngine
from ui import WizardView, WorkspaceView

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenFilmScan")
        self.setMinimumSize(1000, 750)

        self.engine = ImageEngine()
        self.file_list = []
        self.current_idx = -1
        self.output_directory = ""

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.wizard = WizardView(on_folder_click=self.open_folder_dialog)
        self.workspace = WorkspaceView(
            on_prev=lambda: self.navigate_image(-1),
            on_next=lambda: self.navigate_image(1),
            on_slider_change=self.update_pipeline,
            on_auto=self.trigger_auto_balance,
            on_reset=self.trigger_reset,
            on_mono_toggle=self.toggle_monochrome_mode,
            on_invert_toggle=self.toggle_inversion_mode,
            on_browse_output=self.browse_output_directory,
            on_export=self.export_processed_file
        )

        self.stack.addWidget(self.wizard)
        self.stack.addWidget(self.workspace)
        self.stack.setCurrentIndex(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        if self.stack.currentIndex() != 1:
            super().keyPressEvent(event)
            return

        step = 2
        key = event.key()

        if key == Qt.Key.Key_Q:
            self.workspace.sld_cr.setValue(self.workspace.sld_cr.value() + step)
        elif key == Qt.Key.Key_W:
            self.workspace.sld_mg.setValue(self.workspace.sld_mg.value() + step)
        elif key == Qt.Key.Key_E:
            self.workspace.sld_yb.setValue(self.workspace.sld_yb.value() + step)
        elif key == Qt.Key.Key_R:
            self.workspace.sld_exp.setValue(self.workspace.sld_exp.value() + step)
        elif key == Qt.Key.Key_A:
            self.workspace.sld_cr.setValue(self.workspace.sld_cr.value() - step)
        elif key == Qt.Key.Key_S:
            self.workspace.sld_mg.setValue(self.workspace.sld_mg.value() - step)
        elif key == Qt.Key.Key_D:
            self.workspace.sld_yb.setValue(self.workspace.sld_yb.value() - step)
        elif key == Qt.Key.Key_F:
            self.workspace.sld_exp.setValue(self.workspace.sld_exp.value() - step)
        elif key == Qt.Key.Key_Left:
            self.navigate_image(-1)
        elif key == Qt.Key.Key_Right:
            self.navigate_image(1)
        else:
            super().keyPressEvent(event)

    def open_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Film Roll Folder")
        if not dir_path:
            return

        valid_exts = (
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', 
            '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf'
        )
        self.file_list = []
        for f in os.listdir(dir_path):
            if f.lower().endswith(valid_exts):
                self.file_list.append(str(os.path.join(dir_path, f)))

        if not self.file_list:
            self.wizard.lbl_status.setText("⚠️ No valid RAW files or images found! Select another folder.")
            return

        self.file_list.sort()
        self.output_directory = os.path.join(dir_path, "converted_positives")
        self.workspace.txt_output_path.setText(self.output_directory)

        self.current_idx = 0
        self.display_current_image()
        self.stack.setCurrentIndex(1)

    def browse_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_directory = dir_path
            self.workspace.txt_output_path.setText(self.output_directory)

    def export_processed_file(self):
        if not self.output_directory or self.current_idx == -1:
            return
        os.makedirs(self.output_directory, exist_ok=True)
        original_name = os.path.basename(self.file_list[self.current_idx])
        filename_without_ext, _ = os.path.splitext(original_name)
        new_name = f"{filename_without_ext}_positive.png"
        save_path = os.path.join(self.output_directory, new_name)

        if self.engine.export_current_image(save_path):
            self.statusBar().showMessage(f"Saved: {new_name}", 2000)

    def display_current_image(self):
        if 0 <= self.current_idx < len(self.file_list):
            if self.engine.load_file(self.file_list[self.current_idx]):
                self.update_pipeline()

    def navigate_image(self, direction):
        new_idx = self.current_idx + direction
        if 0 <= new_idx < len(self.file_list):
            self.current_idx = new_idx
            self.display_current_image()

    def update_pipeline(self):
        # 1. Read color matrix adjustment values from UI sliders
        cr = self.workspace.sld_cr.value()
        mg = self.workspace.sld_mg.value()
        yb = self.workspace.sld_yb.value()
        exp = self.workspace.sld_exp.value()
        
        # 2. PATCH: Read the four modern independent edge-trim values
        ct = self.workspace.sld_crop_t.value()
        cb = self.workspace.sld_crop_b.value()
        cl = self.workspace.sld_crop_l.value()
        cr_val = self.workspace.sld_crop_r.value()

        # 3. Synchronize visual canvas overlay highlights
        self.workspace.lbl_canvas.update_crop_metrics(ct, cb, cl, cr_val)

        # 4. Push variables into image engine matrix pipeline
        img_array = self.engine.run_pipeline(
            cr, mg, yb, exp, 
            crop_t=ct, crop_b=cb, crop_l=cl, crop_r=cr_val
        )
        
        if img_array is not None:
            self.render_to_canvas(img_array)
            hist_arrays = self.engine.get_histogram_arrays()
            if hist_arrays:
                self.workspace.histogram.update_data(hist_arrays)

    def render_to_canvas(self, bgr_array):
        canvas_w = max(self.workspace.lbl_canvas.width() - 10, 100)
        canvas_h = max(self.workspace.lbl_canvas.height() - 10, 100)
        h, w, ch = bgr_array.shape
        bytes_per_line = ch * w
        qt_img = QImage(bgr_array.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)
        self.workspace.lbl_canvas.setPixmap(pixmap.scaled(
            canvas_w, canvas_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

    def toggle_inversion_mode(self):
        self.engine.is_inverted = not self.engine.is_inverted
        self.workspace.btn_invert.setText("🔄 Invert: Active" if self.engine.is_inverted else "⏹️ Invert: Passthrough")
        self.workspace.btn_invert.setStyleSheet(
            "background-color: #007acc; font-weight: bold; padding: 6px;" if self.engine.is_inverted 
            else "background-color: #3a3a3a; padding: 6px;"
        )
        self.update_pipeline()

    def toggle_monochrome_mode(self):
        self.engine.is_monochrome = not self.engine.is_monochrome
        self.workspace.btn_mono.setText("⚫ Mode: Monochrome (B&W)" if self.engine.is_monochrome else "🌈 Mode: Full Color")
        self.workspace.btn_mono.setStyleSheet(
            "background-color: #007acc; font-weight: bold; padding: 6px;" if self.engine.is_monochrome 
            else "background-color: #3a3a3a; padding: 6px;"
        )
        self.update_pipeline()

    def trigger_auto_balance(self):
        # Auto-balance reads data that has already been masked out by the crop pipeline
        dr, dg, db = self.engine.calculate_grey_world_offsets()
        self.toggle_ui_signals(False)
        self.workspace.sld_cr.setValue(max(-100, min(dr, 100)))
        self.workspace.sld_mg.setValue(max(-100, min(dg, 100)))
        self.workspace.sld_yb.setValue(max(-100, min(db, 100)))
        self.workspace.sld_exp.setValue(0)
        self.toggle_ui_signals(True)
        self.update_pipeline()

    def trigger_reset(self):
        self.toggle_ui_signals(False)
        self.workspace.sld_crop.setValue(0) # Reset crop back to 0%
        self.workspace.sld_cr.setValue(0)
        self.workspace.sld_mg.setValue(0)
        self.workspace.sld_yb.setValue(0)
        self.workspace.sld_exp.setValue(0)
        self.toggle_ui_signals(True)
        self.update_pipeline()

    def toggle_ui_signals(self, enable):
        sliders = [
            self.workspace.sld_cr, self.workspace.sld_mg, 
            self.workspace.sld_yb, self.workspace.sld_exp,
            self.workspace.sld_crop
        ]
        for sld in sliders:
            sld.blockSignals(not enable)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.engine.processed_img is not None:
            self.render_to_canvas(self.engine.processed_img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainApp()
    window.show()
    sys.exit(app.exec())
