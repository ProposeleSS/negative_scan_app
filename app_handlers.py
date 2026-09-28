import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog

class AppHandlers:
    @staticmethod
    def handle_keypress(window, event):
        """Processes keystroke adjustments mapped to sliders."""
        if window.stack.currentIndex() != 1:
            return False

        step = 2
        key = event.key()

        # Row 1: QWER (Increase)
        if key == Qt.Key.Key_Q:
            window.workspace.sld_cr.setValue(window.workspace.sld_cr.value() + step)
        elif key == Qt.Key.Key_W:
            window.workspace.sld_mg.setValue(window.workspace.sld_mg.value() + step)
        elif key == Qt.Key.Key_E:
            window.workspace.sld_yb.setValue(window.workspace.sld_yb.value() + step)
        elif key == Qt.Key.Key_R:
            window.workspace.sld_exp.setValue(window.workspace.sld_exp.value() + step)
        elif key == Qt.Key.Key_T:
            window.workspace.sld_contrast.setValue(window.workspace.sld_contrast.value() + 1)
        
        # Row 2: ASDF (Decrease)
        elif key == Qt.Key.Key_A:
            window.workspace.sld_cr.setValue(window.workspace.sld_cr.value() - step)
        elif key == Qt.Key.Key_S:
            window.workspace.sld_mg.setValue(window.workspace.sld_mg.value() - step)
        elif key == Qt.Key.Key_D:
            window.workspace.sld_yb.setValue(window.workspace.sld_yb.value() - step)
        elif key == Qt.Key.Key_F:
            window.workspace.sld_exp.setValue(window.workspace.sld_exp.value() - step)
        elif key == Qt.Key.Key_G:
            window.workspace.sld_contrast.setValue(window.workspace.sld_contrast.value() - 1)
            
        # Navigation Roll Controls
        elif key == Qt.Key.Key_Left:
            window.navigate_image(-1)
        elif key == Qt.Key.Key_Right:
            window.navigate_image(1)
            
        # NEW HOTKEY: Press 'S' or 'Ctrl + S' to instantly save the image
        elif key == Qt.Key.Key_S or (key == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            window.export_processed_file()
            return True
            
        else:
            return False
        return True

    @staticmethod
    def execute_folder_scan(window):
        """Triggers local directory lookups for camera RAW assets."""
        dir_path = QFileDialog.getExistingDirectory(window, "Select Film Roll Folder")
        if not dir_path:
            return

        valid_exts = (
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', 
            '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf'
        )
        window.file_list = []
        for f in os.listdir(dir_path):
            if f.lower().endswith(valid_exts):
                window.file_list.append(str(os.path.join(dir_path, f)))

        if not window.file_list:
            window.wizard.lbl_status.setText("⚠️ No valid RAW files found! Select another folder.")
            return

        window.file_list.sort()
        window.output_directory = os.path.join(dir_path, "converted_positives")
        window.workspace.txt_output_path.setText(window.output_directory)

        window.current_idx = 0
        window.display_current_image()
        window.stack.setCurrentIndex(1)